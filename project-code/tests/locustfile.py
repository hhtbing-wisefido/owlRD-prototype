"""
Locust性能测试配置

运行方式：
    locust -f tests/locustfile.py
    
然后访问 http://localhost:8089 配置并发用户数和测试时长
"""

from locust import HttpUser, task, between

class OwlRDUser(HttpUser):
    """owlRD系统用户行为模拟"""
    
    wait_time = between(1, 3)
    host = "http://localhost:8000"
    
    def on_start(self):
        """测试开始时执行"""
        pass
    
    @task(3)
    def get_users(self):
        """获取用户列表（权重3）"""
        self.client.get("/api/v1/users/", params={
            'tenant_id': '10000000-0000-0000-0000-000000000001'
        })
    
    @task(5)
    def get_alerts(self):
        """获取告警列表（权重5）"""
        self.client.get("/api/v1/alerts/")
    
    @task(2)
    def get_devices(self):
        """获取设备列表（权重2）"""
        self.client.get("/api/v1/devices/", params={
            'tenant_id': '10000000-0000-0000-0000-000000000001'
        })
    
    @task(2)
    def get_residents(self):
        """获取住户列表（权重2）"""
        self.client.get("/api/v1/residents/", params={
            'tenant_id': '10000000-0000-0000-0000-000000000001'
        })
    
    @task(1)
    def get_iot_data(self):
        """查询IoT数据（权重1）"""
        self.client.get("/api/v1/iot-data/query")
    
    @task(1)
    def health_check(self):
        """健康检查（权重1）"""
        self.client.get("/health")
