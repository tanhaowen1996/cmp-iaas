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

test_data = json.loads("""
{
	"code": 2000,
	"descr": "操作成功",
	"status": true,
	"data": [
		{
			"userId": 152,
			"userName": "管理员",
			"relUserId": "f4e124ef1eea4ad8bf3c6e0983275dad",
			"relUserName": "cloud-rd@yonghui.cn",
			"projects": [
				{
					"userId": 152,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 152,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 152,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 156,
			"userName": "汪畅畅",
			"relUserId": "768257e3e3ff4d34be77f6159d1e0bab",
			"relUserName": "wcc",
			"projects": [
				{
					"userId": 156,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 156,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 156,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 155,
			"userName": "测试用户",
			"relUserId": "d6c4befaf3b14816b599794f1e1fcc7c",
			"relUserName": "123",
			"projects": [
				{
					"userId": 155,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 155,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 158,
			"userName": "test007",
			"relUserId": "155e19fa4d20459f8b558ff645bbdabc",
			"relUserName": "test007",
			"projects": [
				{
					"userId": 158,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 158,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 158,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 5,
			"userName": "",
			"relUserId": "678733d1d81a403eb48ce9c17c890b95",
			"relUserName": "yhcloud",
			"projects": []
		},
		{
			"userId": 159,
			"userName": "wcctest",
			"relUserId": "2ca06d8554064a3db021a0fe09c8f6a4",
			"relUserName": "wcctest",
			"projects": [
				{
					"userId": 159,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 159,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 159,
					"id": "b7a9101b0349422fa61d6f48a7de617c",
					"name": "测试租户wcctest",
					"tenantId": 61,
					"tenantName": "测试租户wcctest"
				},
				{
					"userId": 159,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 160,
			"userName": "test008",
			"relUserId": "e45150f825ad4c88820549478e31a3b0",
			"relUserName": "test008",
			"projects": [
				{
					"userId": 160,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 160,
					"id": "b7a9101b0349422fa61d6f48a7de617c",
					"name": "测试租户wcctest",
					"tenantId": 61,
					"tenantName": "测试租户wcctest"
				}
			]
		},
		{
			"userId": 153,
			"userName": "11",
			"relUserId": "f3cb3da4318a42639d02c819727d15d5",
			"relUserName": "11111",
			"projects": [
				{
					"userId": 153,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 163,
			"userName": "dingzhihao",
			"relUserId": "783a7bdd2a4c431b896a6c06eca70264",
			"relUserName": "dingzhihao",
			"projects": [
				{
					"userId": 163,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 163,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 164,
			"userName": "test11",
			"relUserId": "d8790827e7844907ae6dc3afd6f5b0db",
			"relUserName": "test11",
			"projects": [
				{
					"userId": 164,
					"id": "b7a9101b0349422fa61d6f48a7de617c",
					"name": "测试租户wcctest",
					"tenantId": 61,
					"tenantName": "测试租户wcctest"
				},
				{
					"userId": 164,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 157,
			"userName": "wcc1",
			"relUserId": "810d41de34fd499d93d18477d5850421",
			"relUserName": "wcc1",
			"projects": [
				{
					"userId": 157,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 157,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 162,
			"userName": "测试用户111",
			"relUserId": "51c172e56681489589f94e8ded5af85a",
			"relUserName": "aaaaa",
			"projects": [
				{
					"userId": 162,
					"id": "b7a9101b0349422fa61d6f48a7de617c",
					"name": "测试租户wcctest",
					"tenantId": 61,
					"tenantName": "测试租户wcctest"
				},
				{
					"userId": 162,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 154,
			"userName": "租户测试001",
			"relUserId": "0b33f10d4eb342419647731f3b0f72cb",
			"relUserName": "test001",
			"projects": [
				{
					"userId": 154,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 154,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 166,
			"userName": "d.user.t02",
			"relUserId": "1eb47bb6491e45b0b40edb5080891bf9",
			"relUserName": "d.user.t02",
			"projects": [
				{
					"userId": 166,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				},
				{
					"userId": 166,
					"id": "2da97a134f3f454eb9d7c8ecea1c7e24",
					"name": "d.project.t01",
					"tenantId": 63,
					"tenantName": "d.project.t01"
				}
			]
		},
		{
			"userId": 165,
			"userName": "d.user.t01",
			"relUserId": "2e74b2c7b0974eb69f0dee6932228fd0",
			"relUserName": "d.user.t01",
			"projects": [
				{
					"userId": 165,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				},
				{
					"userId": 165,
					"id": "2da97a134f3f454eb9d7c8ecea1c7e24",
					"name": "d.project.t01",
					"tenantId": 63,
					"tenantName": "d.project.t01"
				}
			]
		},
		{
			"userId": 171,
			"userName": "Wtest116",
			"relUserId": "bc99a2f5d82b4151bd28e268dee873a8",
			"relUserName": "Wtest116",
			"projects": [
				{
					"userId": 171,
					"id": "2da97a134f3f454eb9d7c8ecea1c7e24",
					"name": "d.project.t01",
					"tenantId": 63,
					"tenantName": "d.project.t01"
				}
			]
		},
		{
			"userId": 174,
			"userName": "测试用户2021",
			"relUserId": "8d216f7a380a463ca591f3806f78f617",
			"relUserName": "bbbbb",
			"projects": [
				{
					"userId": 174,
					"id": "c3d7fc32accc44b08a44dc3d5d7432ef",
					"name": "测试租户2021",
					"tenantId": 65,
					"tenantName": "测试租户2021"
				}
			]
		},
		{
			"userId": 152,
			"userName": "管理员",
			"relUserId": "d9c6f46f41ff494da4aba44b90401dcd",
			"relUserName": null,
			"projects": [
				{
					"userId": 152,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 152,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 152,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 155,
			"userName": "测试用户",
			"relUserId": "c09417303e1f4693916e720dcc3979f9",
			"relUserName": null,
			"projects": [
				{
					"userId": 155,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 155,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
				}
			]
		},
		{
			"userId": 156,
			"userName": "汪畅畅",
			"relUserId": "8e20f79127164960b5d5f1aa82474888",
			"relUserName": null,
			"projects": [
				{
					"userId": 156,
					"id": "752df3ea70724f44acc088a0f0313579",
					"name": "永辉大科技",
					"tenantId": 59,
					"tenantName": "永辉大科技"
				},
				{
					"userId": 156,
					"id": "acb6ba73605246e0af67bc48bdcd6df9",
					"name": "wccteste",
					"tenantId": 60,
					"tenantName": "wccteste"
				},
				{
					"userId": 156,
					"id": "ee20df23d79b48c2bfc0df46af28190d",
					"name": "测试租户2",
					"tenantId": 62,
					"tenantName": "测试租户2"
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
        # return prod_data['data']
        return test_data['data']

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(client=None)


if __name__ in '__main__':
    print(prod_data['data'])
