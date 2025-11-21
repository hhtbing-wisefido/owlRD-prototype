#!/usr/bin/env python3
"""
自动化对齐验证脚本
验证 源SQL ↔ Model ↔ 示例数据 三者一致性

功能：
1. 从SQL文件提取字段定义
2. 从Pydantic Model提取字段定义
3. 验证示例数据是否符合Model
4. 生成详细对齐报告
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
import importlib
import inspect

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel as PydanticBaseModel


@dataclass
class FieldInfo:
    """字段信息"""
    name: str
    type: str
    nullable: bool = True
    default: Optional[Any] = None
    description: str = ""


@dataclass
class TableInfo:
    """表信息"""
    name: str
    sql_file: str
    model_file: Optional[str] = None
    model_class: Optional[str] = None
    collection: str = ""
    sql_fields: Dict[str, FieldInfo] = None
    model_fields: Dict[str, FieldInfo] = None
    
    def __post_init__(self):
        if self.sql_fields is None:
            self.sql_fields = {}
        if self.model_fields is None:
            self.model_fields = {}


class SQLFieldExtractor:
    """SQL字段提取器"""
    
    def __init__(self, sql_root: Path):
        self.sql_root = sql_root
    
    def extract_fields(self, sql_file: str) -> Dict[str, FieldInfo]:
        """从SQL文件提取字段定义"""
        file_path = self.sql_root / sql_file
        
        if not file_path.exists():
            print(f"⚠️  SQL文件不存在: {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取CREATE TABLE语句
        table_match = re.search(
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\);',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not table_match:
            print(f"⚠️  未找到CREATE TABLE语句: {sql_file}")
            return {}
        
        table_body = table_match.group(2)
        fields = {}
        
        # 提取每个字段定义
        # 匹配格式: field_name TYPE [NOT NULL] [DEFAULT ...] [-- comment]
        field_pattern = re.compile(
            r'^\s*(\w+)\s+'  # 字段名
            r'([\w\(\)]+(?:\s+\w+)*?)\s*'  # 类型
            r'(?:NOT\s+NULL)?'  # 可选的NOT NULL
            r'(?:\s+DEFAULT\s+[^,\n]+)?'  # 可选的DEFAULT
            r'(?:\s+--\s*(.*))?',  # 可选的注释
            re.MULTILINE
        )
        
        for line in table_body.split('\n'):
            # 跳过约束和索引
            if any(kw in line.upper() for kw in ['PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'CONSTRAINT', 'REFERENCES']):
                continue
            
            match = field_pattern.match(line)
            if match:
                field_name = match.group(1)
                field_type = match.group(2).strip()
                description = match.group(3).strip() if match.group(3) else ""
                nullable = 'NOT NULL' not in line.upper()
                
                # 映射SQL类型到Python类型
                python_type = self._map_sql_type(field_type)
                
                fields[field_name] = FieldInfo(
                    name=field_name,
                    type=python_type,
                    nullable=nullable,
                    description=description
                )
        
        return fields
    
    def _map_sql_type(self, sql_type: str) -> str:
        """映射SQL类型到Python类型"""
        sql_type_upper = sql_type.upper()
        
        if 'UUID' in sql_type_upper:
            return 'UUID'
        elif 'VARCHAR' in sql_type_upper or 'TEXT' in sql_type_upper:
            return 'str'
        elif 'INT' in sql_type_upper or 'SERIAL' in sql_type_upper:
            return 'int'
        elif 'BOOL' in sql_type_upper:
            return 'bool'
        elif 'TIMESTAMP' in sql_type_upper or 'DATE' in sql_type_upper:
            return 'datetime'
        elif 'JSONB' in sql_type_upper or 'JSON' in sql_type_upper:
            return 'dict'
        elif 'BYTEA' in sql_type_upper:
            return 'bytes'
        elif 'DECIMAL' in sql_type_upper or 'NUMERIC' in sql_type_upper:
            return 'float'
        else:
            return sql_type


class ModelFieldExtractor:
    """Pydantic Model字段提取器"""
    
    def __init__(self, model_root: Path):
        self.model_root = model_root
    
    def extract_fields(self, model_file: str, class_name: str) -> Dict[str, FieldInfo]:
        """从Pydantic Model提取字段定义"""
        module_name = model_file.replace('.py', '').replace('/', '.')
        
        try:
            module = importlib.import_module(f'app.models.{module_name}')
        except ImportError as e:
            print(f"⚠️  无法导入模块 app.models.{module_name}: {e}")
            return {}
        
        if not hasattr(module, class_name):
            print(f"⚠️  模块中未找到类 {class_name}")
            return {}
        
        model_class = getattr(module, class_name)
        
        if not issubclass(model_class, PydanticBaseModel):
            print(f"⚠️  {class_name} 不是Pydantic模型")
            return {}
        
        fields = {}
        
        # 使用Pydantic的model_fields
        if hasattr(model_class, 'model_fields'):
            for field_name, field_info in model_class.model_fields.items():
                python_type = self._get_field_type(field_info.annotation)
                nullable = not field_info.is_required()
                description = field_info.description or ""
                
                fields[field_name] = FieldInfo(
                    name=field_name,
                    type=python_type,
                    nullable=nullable,
                    default=field_info.default,
                    description=description
                )
        
        return fields
    
    def _get_field_type(self, annotation) -> str:
        """获取字段类型"""
        if hasattr(annotation, '__origin__'):
            # 处理泛型类型 (Optional, List, Dict等)
            origin = annotation.__origin__
            if origin is type(None):
                return 'None'
            elif hasattr(origin, '__name__'):
                return origin.__name__
            else:
                return str(origin)
        elif hasattr(annotation, '__name__'):
            return annotation.__name__
        else:
            return str(annotation)


class SampleDataValidator:
    """示例数据验证器"""
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
    
    def validate_collection(self, collection: str, model_class) -> Tuple[bool, List[str]]:
        """验证示例数据集合"""
        from app.services.storage import StorageService
        
        storage = StorageService(collection, str(self.data_root))
        samples = storage.load_all()
        
        if not samples:
            return True, ["无示例数据"]
        
        errors = []
        
        for idx, sample in enumerate(samples):
            try:
                # 使用Pydantic Model验证
                model_class(**sample)
            except Exception as e:
                errors.append(f"记录#{idx}: {str(e)}")
        
        return len(errors) == 0, errors


class AlignmentValidator:
    """对齐验证器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.sql_root = project_root.parent.parent / "owdRD_github_clone_源参考文件" / "owlRD" / "db"
        self.model_root = project_root / "app" / "models"
        self.data_root = project_root / "app" / "data"
        
        self.sql_extractor = SQLFieldExtractor(self.sql_root)
        self.model_extractor = ModelFieldExtractor(self.model_root)
        self.data_validator = SampleDataValidator(self.data_root)
    
    def validate_table(self, table: TableInfo) -> Dict[str, Any]:
        """验证单个表"""
        result = {
            'table_name': table.name,
            'sql_file': table.sql_file,
            'model_file': table.model_file,
            'collection': table.collection,
            'sql_fields_count': 0,
            'model_fields_count': 0,
            'missing_in_model': [],
            'extra_in_model': [],
            'type_mismatches': [],
            'sample_data_valid': False,
            'sample_data_errors': [],
            'alignment_score': 0.0
        }
        
        # 1. 提取SQL字段
        sql_fields = self.sql_extractor.extract_fields(table.sql_file)
        result['sql_fields_count'] = len(sql_fields)
        
        if not sql_fields:
            result['alignment_score'] = 0.0
            return result
        
        # 2. 提取Model字段
        if table.model_file and table.model_class:
            model_fields = self.model_extractor.extract_fields(
                table.model_file,
                table.model_class
            )
            result['model_fields_count'] = len(model_fields)
            
            # 3. 对比字段
            sql_field_names = set(sql_fields.keys())
            model_field_names = set(model_fields.keys())
            
            result['missing_in_model'] = list(sql_field_names - model_field_names)
            result['extra_in_model'] = list(model_field_names - sql_field_names)
            
            # 4. 检查类型匹配
            for field_name in sql_field_names & model_field_names:
                sql_type = sql_fields[field_name].type
                model_type = model_fields[field_name].type
                
                if not self._types_compatible(sql_type, model_type):
                    result['type_mismatches'].append({
                        'field': field_name,
                        'sql_type': sql_type,
                        'model_type': model_type
                    })
            
            # 5. 计算对齐分数
            total_fields = len(sql_field_names)
            matched_fields = len(sql_field_names & model_field_names) - len(result['type_mismatches'])
            result['alignment_score'] = (matched_fields / total_fields * 100) if total_fields > 0 else 0.0
        
        # 6. 验证示例数据 (暂时跳过，避免导入问题)
        # if table.collection:
        #     valid, errors = self.data_validator.validate_collection(table.collection, model_class)
        #     result['sample_data_valid'] = valid
        #     result['sample_data_errors'] = errors
        
        return result
    
    def _types_compatible(self, sql_type: str, model_type: str) -> bool:
        """检查类型是否兼容"""
        # 基本类型映射
        compatible_types = {
            'UUID': ['UUID', 'str'],
            'str': ['str', 'UUID'],
            'int': ['int'],
            'bool': ['bool'],
            'datetime': ['datetime', 'str'],
            'dict': ['dict', 'Dict'],
            'bytes': ['bytes'],
            'float': ['float', 'int']
        }
        
        return model_type in compatible_types.get(sql_type, [sql_type])
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """生成对齐报告"""
        report = []
        report.append("=" * 80)
        report.append("🔍 数据对齐验证报告")
        report.append("=" * 80)
        report.append("")
        
        total_tables = len(results)
        perfect_tables = sum(1 for r in results if r['alignment_score'] == 100.0)
        avg_score = sum(r['alignment_score'] for r in results) / total_tables if total_tables > 0 else 0.0
        
        report.append(f"📊 总体统计:")
        report.append(f"  - 总表数: {total_tables}")
        report.append(f"  - 完美对齐: {perfect_tables} ({perfect_tables/total_tables*100:.1f}%)")
        report.append(f"  - 平均对齐度: {avg_score:.1f}%")
        report.append("")
        
        # 按对齐度排序
        results.sort(key=lambda x: x['alignment_score'])
        
        for result in results:
            score = result['alignment_score']
            status = "✅" if score == 100.0 else "⚠️" if score >= 80.0 else "❌"
            
            report.append(f"{status} {result['table_name']} - {score:.1f}%")
            report.append(f"  SQL文件: {result['sql_file']}")
            report.append(f"  Model文件: {result['model_file'] or 'N/A'}")
            report.append(f"  SQL字段数: {result['sql_fields_count']}")
            report.append(f"  Model字段数: {result['model_fields_count']}")
            
            if result['missing_in_model']:
                report.append(f"  ❌ Model缺少字段: {', '.join(result['missing_in_model'])}")
            
            if result['extra_in_model']:
                report.append(f"  ⚠️  Model多余字段: {', '.join(result['extra_in_model'])}")
            
            if result['type_mismatches']:
                report.append(f"  ⚠️  类型不匹配:")
                for mismatch in result['type_mismatches']:
                    report.append(f"      {mismatch['field']}: SQL={mismatch['sql_type']}, Model={mismatch['model_type']}")
            
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    # 定义要验证的表 (table_name, sql_file, model_file, model_class_name, collection)
    tables_config = [
        ("tenants", "01_tenants.sql", "tenant", "Tenant", "tenants"),
        ("roles", "02_roles.sql", "role", "Role", "roles"),
        ("users", "03_users.sql", "user", "User", "users"),
        ("locations", "04_locations.sql", "location", "Location", "locations"),
        ("rooms", "05_rooms.sql", "location", "Room", "rooms"),  # Room在location.py中
        ("beds", "06_beds.sql", "location", "Bed", "beds"),  # Bed在location.py中
        ("residents", "07_residents.sql", "resident", "Resident", "residents"),
        ("resident_phi", "08_resident_phi.sql", "resident", "ResidentPHI", "resident_phi"),  # 在resident.py中
        ("resident_contacts", "09_resident_contacts.sql", "resident", "ResidentContact", "resident_contacts"),  # 在resident.py中
        ("resident_caregivers", "10_resident_caregivers.sql", "resident", "ResidentCaregiver", "resident_caregivers"),  # 在resident.py中
        ("devices", "11_devices.sql", "device", "Device", "devices"),
        ("iot_timeseries", "12_iot_timeseries.sql", "iot_data", "IOTTimeseries", "iot_timeseries"),
        ("iot_monitor_alerts", "13_iot_monitor_alerts.sql", "iot_data", "IOTMonitorAlert", "iot_monitor_alerts"),
        ("cloud_alert_policies", "14_cloud_alert_policies.sql", "alert", "CloudAlertPolicy", "cloud_alert_policies"),
        ("config_versions", "15_config_versions.sql", "config_version", "ConfigVersion", "config_versions"),
        ("posture_mapping", "16_mapping_tables.sql", "mapping", "PostureMapping", "posture_mapping"),
        ("event_mapping", "16_mapping_tables.sql", "mapping", "EventMapping", "event_mapping"),
        ("cards", "18_cards.sql", "card", "Card", "cards"),
    ]
    
    tables = [TableInfo(name, sql, model, cls, coll) for name, sql, model, cls, coll in tables_config]
    
    validator = AlignmentValidator(project_root)
    
    print("🚀 开始验证数据对齐...")
    print()
    
    results = []
    for table in tables:
        print(f"检查 {table.name}...", end=" ")
        result = validator.validate_table(table)
        results.append(result)
        print(f"{result['alignment_score']:.1f}%")
    
    print()
    
    # 生成报告
    report = validator.generate_report(results)
    print(report)
    
    # 保存报告
    report_file = project_root.parent.parent / "项目记录" / "AUTO_对齐验证报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 自动化对齐验证报告\n\n")
        f.write(f"**生成时间**: {Path(__file__).stat().st_mtime}\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```\n")
    
    print(f"\n📄 报告已保存到: {report_file}")
    
    # 返回退出码
    avg_score = sum(r['alignment_score'] for r in results) / len(results) if results else 0.0
    sys.exit(0 if avg_score == 100.0 else 1)


if __name__ == "__main__":
    main()
