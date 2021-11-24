
class UumAPI(object):

    def __init__(self, client=None):
        self.client = client

    def get_users(self):
        _ = self.client
        return [{
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

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(client=None)
