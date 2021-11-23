
class UumAPI(object):

    def __init__(self, client=None):
        self.client = client

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(client=None)

    def get_users(self):
        _ = self.client
        return [{
            "userId": "f4e124ef1eea4ad8bf3c6e0983275dad",
            "userName": "admin",
            "projects": [{
                    "id": "752df3ea70724f44acc088a0f0313579",
                    "name": "大科技"
            }]
        }]
