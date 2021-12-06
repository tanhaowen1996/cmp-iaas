import json
import requests


class Communication:
    def sms(self, content_list):
        self.auth_url = 'http://10.214.214.3:10080/auth/secret/user'
        self.sms_url = 'http://10.214.214.3:10080/?Action=market&Service=sms'
        header = {
            'Content-Type': 'application/json'
        }
        auth_key = {
            "secretId": "2c2a03cd64fd48ff9c28e70e40361071",
            "secretKey": "1c92ac73943c49bfb1c0e0f351fe47ee"
        }
        auth_res = requests.post(url=self.auth_url, data=json.dumps(auth_key), headers=header)
        key = json.loads(auth_res.text)['result']
        key.update(header)
        sms_data = {
            "sign": '永辉超市',
            "smsList": content_list,
        }
        a = requests.post(url=self.sms_url, headers=key, data=json.dumps(sms_data))
        print(a.text)

    def email(self, subject, content, to):
        auth_url = 'http://10.214.214.3:10080/auth/secret/user'
        email_url = 'http://10.214.214.3:10080/?Action=sendMail&Service=mail'
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
        email_data = {
            "subject": subject,
            "content": content,
            "to": to,
            "account": "itwork@yonghui.cn",
            "password": "l*rgV$K&eikhan3D",
        }
        requests.post(url=email_url, headers=key, data=json.dumps(email_data))