from locust import HttpUser, task, between

class CampusUser(HttpUser):
    # 模拟真实用户的行为：在页面停留 1 到 3 秒之间再点下一个链接
    wait_time = between(1, 3)

    @task(3)  # 权重为 3，代表访问首页的概率最大
    def view_home(self):
        # 模拟访问系统首页
        self.client.get("/")

    @task(1)  # 权重为 1
    def view_search(self):
        # 模拟使用搜索功能（假设搜索“手机”）
        self.client.get("/listings/search/?q=手机")