import json


yhcloud_data = json.loads("""{
	"code": 2000,
	"descr": "操作成功",
	"status": true,
	"data": [
		{
			"userId": 5,
			"userName": "yhcloud",
			"relUserId": "ac0997f1e0ff40f7936411a96a93a2c0",
			"relUserName": "yhcloud",
			"projects": [
				{
					"userId": 5,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				},
				{
					"userId": 5,
					"id": "e07c873ff7604b9890e616a002116b6f",
					"name": "永辉大科技",
					"tenantId": 5,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 5,
					"id": "aeefd69d22f04216a3b71e7aaad331f8",
					"name": "yunchaoit",
					"tenantId": 29,
					"tenantName": "yunchaoit"
				},
				{
					"userId": 5,
					"id": "65ea31f7d7834d0cbfb2752c2cac082e",
					"name": "tclin",
					"tenantId": 32,
					"tenantName": "tclin"
				}
			]
		}
	]
}""")


prod_data = json.loads("""{
	"code": 2000,
	"descr": "操作成功",
	"status": true,
	"data": [
		{
			"userId": 5,
			"userName": "yhcloud",
			"relUserId": "ac0997f1e0ff40f7936411a96a93a2c0",
			"relUserName": "yhcloud",
			"projects": [
				{
					"userId": 5,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				},
				{
					"userId": 5,
					"id": "e07c873ff7604b9890e616a002116b6f",
					"name": "永辉大科技",
					"tenantId": 5,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 5,
					"id": "aeefd69d22f04216a3b71e7aaad331f8",
					"name": "yunchaoit",
					"tenantId": 29,
					"tenantName": "yunchaoit"
				},
				{
					"userId": 5,
					"id": "65ea31f7d7834d0cbfb2752c2cac082e",
					"name": "tclin",
					"tenantId": 32,
					"tenantName": "tclin"
				}
			]
		},
		{
			"userId": 8,
			"userName": "wcctest",
			"relUserId": "5937d795c3024560ac5795430c39154a",
			"relUserName": "wcctest",
			"projects": [
				{
					"userId": 8,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				},
				{
					"userId": 8,
					"id": "c80d8354a12a4bf6874c503342a3c528",
					"name": "测试租户2",
					"tenantId": 17,
					"tenantName": "测试租户2"
				},
				{
					"userId": 8,
					"id": "b56145a3872e49d7a469448f00c94a32",
					"name": "测试租户1",
					"tenantId": 14,
					"tenantName": "测试租户1"
				}
			]
		},
		{
			"userId": 11,
			"userName": "test1",
			"relUserId": "27139212ad2e490a8c4c3408e313df8f",
			"relUserName": "lctest",
			"projects": [
				{
					"userId": 11,
					"id": "8a22841338974315af6cd2eac730aa4a",
					"name": "永辉test1",
					"tenantId": 20,
					"tenantName": "永辉test1"
				}
			]
		},
		{
			"userId": 14,
			"userName": "test123",
			"relUserId": "3cc39f4e002b4e55bc8569e12422d53f",
			"relUserName": "test123",
			"projects": [
				{
					"userId": 14,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				}
			]
		},
		{
			"userId": 20,
			"userName": "林天成",
			"relUserId": "90453b4d651a4dd292779162ebfc0147",
			"relUserName": "80679689",
			"projects": [
				{
					"userId": 20,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				},
				{
					"userId": 20,
					"id": "e07c873ff7604b9890e616a002116b6f",
					"name": "永辉大科技",
					"tenantId": 5,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 20,
					"id": "574e466abf9d407f8b04635e05a8e2b3",
					"name": "测试",
					"tenantId": 8,
					"tenantName": "测试"
				}
			]
		},
		{
			"userId": 17,
			"userName": "林斌",
			"relUserId": "df183191eca844289d02e2cbc449be4d",
			"relUserName": "80620692",
			"projects": [
				{
					"userId": 17,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				},
				{
					"userId": 17,
					"id": "e07c873ff7604b9890e616a002116b6f",
					"name": "永辉大科技",
					"tenantId": 5,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 17,
					"id": "574e466abf9d407f8b04635e05a8e2b3",
					"name": "测试",
					"tenantId": 8,
					"tenantName": "测试"
				}
			]
		},
		{
			"userId": 23,
			"userName": "吴兴源",
			"relUserId": "759677fe15b747d0ad84bd233f2583e3",
			"relUserName": "80671396",
			"projects": [
				{
					"userId": 23,
					"id": "c5932d611fc44661854dc865a46599a7",
					"name": "永辉测试",
					"tenantId": 11,
					"tenantName": "永辉测试"
				}
			]
		}
	]
}
""")


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

        self.test_data = [{
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
        # return self.test_data
        # return self.prod_response_data['data']
        return yhcloud_data['data']

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(client=None)


if __name__ in '__main__':
    print(prod_data['data'])
