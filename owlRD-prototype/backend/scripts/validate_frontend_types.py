#!/usr/bin/env python3
"""
前端TypeScript类型验证脚本
自动对比 TypeScript接口 ↔ Python Pydantic Model

功能：
1. 解析TypeScript接口定义
2. 从Python Model提取字段
3. 对比字段名和类型
4. 生成对齐报告
5. 集成到检查清单
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import importlib

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TypeScriptParser:
    """TypeScript接口解析器"""
    
    def __init__(self, ts_file: Path):
        self.ts_file = ts_file
        
    def parse_interfaces(self) -> Dict[str, Dict[str, str]]:
        """解析所有接口定义"""
        with open(self.ts_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        interfaces = {}
        
        # 正则匹配接口定义
        # export interface InterfaceName {
        #   field: type
        # }
        pattern = r'export\s+interface\s+(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            interface_name = match.group(1)
            interface_body = match.group(2)
            
            fields = self._parse_fields(interface_body)
            interfaces[interface_name] = fields
        
        return interfaces
    
    def _parse_fields(self, body: str) -> Dict[str, str]:
        """解析接口字段"""
        fields = {}
        
        # 匹配字段定义：field_name?: type  // comment
        field_pattern = r'^\s*(\w+)(\?)?\s*:\s*([^\n\/]+)'
        
        for line in body.split('\n'):
            # 跳过注释行
            if line.strip().startswith('//'):
                continue
            
            match = re.match(field_pattern, line.strip())
            if match:
                field_name = match.group(1)
                is_optional = match.group(2) == '?'
                field_type = match.group(3).strip()
                
                # 清理类型（移除注释）
                if '//' in field_type:
                    field_type = field_type.split('//')[0].strip()
                
                fields[field_name] = {
                    'type': field_type,
                    'optional': is_optional
                }
        
        return fields


class FrontendTypeValidator:
    """前端类型验证器"""
    
    # TypeScript ↔ Python 类型映射
    TYPE_MAPPINGS = {
        'string': ['str', 'UUID', 'EmailStr', 'datetime', 'date'],
        'number': ['int', 'float', 'Decimal'],
        'boolean': ['bool'],
        'Record<string, any>': ['Dict', 'dict', 'Dict[str, Any]'],
        'any': ['Any', 'Dict', 'dict'],
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ts_file = project_root.parent / "frontend" / "src" / "types" / "index.ts"
        self.parser = TypeScriptParser(self.ts_file)
    
    def validate_type_alignment(self, ts_interface: str, py_model_file: str, py_model_class: str) -> Dict:
        """验证单个类型对齐"""
        result = {
            'ts_interface': ts_interface,
            'py_model': f"{py_model_file}.{py_model_class}",
            'ts_fields_count': 0,
            'py_fields_count': 0,
            'missing_in_ts': [],
            'missing_in_py': [],
            'type_mismatches': [],
            'alignment_score': 0.0,
            'status': ''
        }
        
        # 1. 解析TypeScript接口
        ts_interfaces = self.parser.parse_interfaces()
        if ts_interface not in ts_interfaces:
            result['status'] = f"❌ TypeScript接口 {ts_interface} 不存在"
            return result
        
        ts_fields = ts_interfaces[ts_interface]
        result['ts_fields_count'] = len(ts_fields)
        
        # 2. 导入Python Model
        try:
            module = importlib.import_module(f'app.models.{py_model_file}')
            if not hasattr(module, py_model_class):
                result['status'] = f"❌ Python Model {py_model_class} 不存在"
                return result
            
            model_class = getattr(module, py_model_class)
            
            # 获取Model字段
            py_fields = {}
            if hasattr(model_class, 'model_fields'):
                for field_name, field_info in model_class.model_fields.items():
                    py_fields[field_name] = {
                        'type': str(field_info.annotation),
                        'optional': not field_info.is_required()
                    }
            
            result['py_fields_count'] = len(py_fields)
        
        except Exception as e:
            result['status'] = f"❌ 导入Python Model失败: {e}"
            return result
        
        # 3. 对比字段
        ts_field_names = set(ts_fields.keys())
        py_field_names = set(py_fields.keys())
        
        # 排除合理的额外字段（主键/外键/时间戳）
        reasonable_extras = {
            'tenant_id', 'created_at', 'updated_at',
            'resident_id', 'device_id', 'user_id', 'location_id',
            'room_id', 'bed_id', 'phi_id', 'alert_id', 'card_id',
            'version_id', 'mapping_id', 'alert_config_id', 'contact_id'
        }
        
        missing_in_ts = (py_field_names - ts_field_names) - reasonable_extras
        missing_in_py = ts_field_names - py_field_names
        
        result['missing_in_ts'] = list(missing_in_ts)
        result['missing_in_py'] = list(missing_in_py)
        
        # 4. 检查类型匹配
        common_fields = ts_field_names & py_field_names
        for field in common_fields:
            ts_type = ts_fields[field]['type']
            py_type_str = py_fields[field]['type']
            
            if not self._types_compatible(ts_type, py_type_str):
                result['type_mismatches'].append({
                    'field': field,
                    'ts_type': ts_type,
                    'py_type': py_type_str
                })
        
        # 5. 计算对齐分数
        if result['py_fields_count'] > 0:
            matched = len(common_fields) - len(result['type_mismatches'])
            result['alignment_score'] = (matched / result['py_fields_count']) * 100
        
        # 6. 状态评估
        if result['alignment_score'] == 100 and not missing_in_ts and not missing_in_py:
            result['status'] = '✅ 完美对齐'
        elif result['alignment_score'] >= 90:
            result['status'] = '⚠️ 良好对齐'
        elif result['alignment_score'] >= 70:
            result['status'] = '⚠️ 部分对齐'
        else:
            result['status'] = '❌ 严重不对齐'
        
        return result
    
    def _types_compatible(self, ts_type: str, py_type: str) -> bool:
        """检查TypeScript和Python类型是否兼容"""
        # 移除Optional/Union包装
        py_type_clean = py_type.replace('Optional[', '').replace(']', '').replace('Union[', '').split(',')[0].strip()
        
        # 检查映射表
        for ts_base, py_bases in self.TYPE_MAPPINGS.items():
            if ts_type.startswith(ts_base):
                for py_base in py_bases:
                    if py_base in py_type_clean:
                        return True
        
        return False
    
    def generate_report(self, results: List[Dict]) -> str:
        """生成对齐报告"""
        lines = []
        lines.append("=" * 80)
        lines.append("🔍 前端类型对齐验证报告")
        lines.append("=" * 80)
        lines.append("")
        
        total = len(results)
        perfect = sum(1 for r in results if r['alignment_score'] == 100 and not r['missing_in_ts'] and not r['missing_in_py'])
        good = sum(1 for r in results if 90 <= r['alignment_score'] < 100)
        partial = sum(1 for r in results if 70 <= r['alignment_score'] < 90)
        poor = sum(1 for r in results if r['alignment_score'] < 70)
        
        avg_score = sum(r['alignment_score'] for r in results) / total if total > 0 else 0
        
        lines.append(f"📊 总体统计:")
        lines.append(f"  - 总类型数: {total}")
        lines.append(f"  - 完美对齐: {perfect} ({perfect/total*100:.1f}%)")
        lines.append(f"  - 良好对齐: {good} ({good/total*100:.1f}%)")
        lines.append(f"  - 部分对齐: {partial} ({partial/total*100:.1f}%)")
        lines.append(f"  - 严重不对齐: {poor} ({poor/total*100:.1f}%)")
        lines.append(f"  - 平均对齐度: {avg_score:.1f}%")
        lines.append("")
        
        # 按对齐度排序
        results.sort(key=lambda x: x['alignment_score'])
        
        for result in results:
            lines.append(f"{result['status']} {result['ts_interface']} - {result['alignment_score']:.1f}%")
            lines.append(f"  TypeScript: {result['ts_fields_count']} fields")
            lines.append(f"  Python Model: {result['py_fields_count']} fields")
            
            if result['missing_in_ts']:
                lines.append(f"  ⚠️  TS缺少字段: {', '.join(result['missing_in_ts'][:5])}")
                if len(result['missing_in_ts']) > 5:
                    lines.append(f"      ... 等共{len(result['missing_in_ts'])}个")
            
            if result['missing_in_py']:
                lines.append(f"  ⚠️  Python缺少字段: {', '.join(result['missing_in_py'][:5])}")
                if len(result['missing_in_py']) > 5:
                    lines.append(f"      ... 等共{len(result['missing_in_py'])}个")
            
            if result['type_mismatches']:
                lines.append(f"  ⚠️  类型不匹配:")
                for m in result['type_mismatches'][:3]:
                    lines.append(f"      {m['field']}: TS={m['ts_type']}, Py={m['py_type']}")
                if len(result['type_mismatches']) > 3:
                    lines.append(f"      ... 等共{len(result['type_mismatches'])}个")
            
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    # 定义要验证的类型映射
    type_mappings = [
        ("Tenant", "tenant", "Tenant"),
        ("Role", "role", "Role"),
        ("User", "user", "User"),
        ("Resident", "resident", "Resident"),
        ("ResidentPHI", "resident", "ResidentPHI"),
        ("Device", "device", "Device"),
        ("IoTData", "iot_data", "IOTTimeseries"),
        ("Alert", "alert", "Alert"),
        ("CloudAlertPolicy", "alert", "CloudAlertPolicy"),
        ("ConfigVersion", "config", "ConfigVersion"),
        ("PostureMapping", "mapping", "PostureMapping"),
        ("EventMapping", "mapping", "EventMapping"),
        ("Card", "card", "Card"),
    ]
    
    validator = FrontendTypeValidator(project_root)
    
    print("🚀 开始验证前端类型对齐...")
    print()
    
    results = []
    for ts_interface, py_model_file, py_model_class in type_mappings:
        print(f"检查 {ts_interface}...", end=" ")
        result = validator.validate_type_alignment(ts_interface, py_model_file, py_model_class)
        results.append(result)
        print(f"{result['alignment_score']:.1f}%")
    
    print()
    
    # 生成报告
    report = validator.generate_report(results)
    print(report)
    
    # 保存报告
    report_file = project_root.parent.parent / "项目记录" / "AUTO_前端类型对齐报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 前端类型对齐验证报告\n\n")
        f.write(f"**生成时间**: {Path(__file__).stat().st_mtime}\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```\n")
    
    print(f"\n📄 报告已保存到: {report_file}")
    
    # 返回退出码
    avg_score = sum(r['alignment_score'] for r in results) / len(results) if results else 0
    sys.exit(0 if avg_score == 100.0 else 1)


if __name__ == "__main__":
    main()
