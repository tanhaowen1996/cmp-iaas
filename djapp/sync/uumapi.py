
class UumAPI(object):

    def __init__(self, client=None):
        self.client = client

        self.prod_response_data = {
            "code": 2000,
            "descr": "操作成功",
            "status": True,
            "data": [
                {
                    "userId": 5,
                    "userName": "yhcloud",
                    "relUserId": "ac0997f1e0ff40f7936411a96a93a2c0",
                    "relUserName": "yhcloud",
                    "projects": [
                        {
                            "id": "c5932d611fc44661854dc865a46599a7",
                            "name": "永辉测试",
                            "tenantId": 11,
                            "tenantName": "永辉测试"
                        }
                    ]
                }
            ]
        }

        self.test_response_data = [{
            "userId": 152,
            "userName": "admin",
            "relUserId": "f4e124ef1eea4ad8bf3c6e0983275dad",
            "relUserName": "cloud-rd@yonghui.cn",
            "project": [{
                "id": "752df3ea70724f44acc088a0f0313579",
                "name": "大科技",
                "tenantId": 59,
                "tenantName": "永辉大科技",
            }]
        }]

    def get_users(self):
        _ = self.client
        return self.prod_response_data['data']

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(client=None)
