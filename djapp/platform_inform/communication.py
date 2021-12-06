import json
import requests
auth_url = 'http://itservice-prod.it-service-gateway.gw.yonghui.cn/auth/secret/user'
sms_url = 'http://itservice-prod.it-service-gateway.gw.yonghui.cn/?Action=market&Service=sms'
email_url = 'http://itservice-prod.it-service-gateway.gw.yonghui.cn/?Action=sendMail&Service=mail'
header = {
    'Content-Type': 'application/json'
}
auth_key = {
    "secretId": "2c2a03cd64fd48ff9c28e70e40361071",
    "secretKey": "1c92ac73943c49bfb1c0e0f351fe47ee"
}
auth_res = requests.post(url=auth_url, data=json.dumps(auth_key), headers=header)
key = json.loads(auth_res.text)['result']
key.update(header)


class Communication:
    def sms(self, content_list):
        sms_data = {
            "sign": '永辉超市',
            "smsList": content_list,
        }
        requests.post(url=sms_url, headers=key, data=json.dumps(sms_data))

    def email(self, subject, content, to):
        email_data = {
            "subject": subject,
            "content": content,
            "to": to,
            "account": "itwork@yonghui.cn",
            "password": "l*rgV$K&eikhan3D",
        }
        requests.post(url=email_url, headers=key, data=json.dumps(email_data))
