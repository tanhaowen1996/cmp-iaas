import json
import requests
from .utils import auth_url, auth_key, sms_email_header, sms_url, email_url, email_account, email_password


class Communication:
    def auth_key(self):
        auth_res = requests.post(url=auth_url, data=json.dumps(auth_key), headers=sms_email_header)
        key = json.loads(auth_res.text)['result']
        key.update(sms_email_header)
        return key

    def sms(self, content_list):
        sms_auth_key = self.auth_key()
        sms_data = {
            "sign": '永辉超市',
            "smsList": content_list,
        }
        requests.post(url=sms_url, headers=sms_auth_key, data=json.dumps(sms_data))

    def email(self, subject, content, to):
        email_auth_key = self.auth_key()
        email_data = {
            "subject": subject,
            "content": content,
            "to": to,
            "account": email_account,
            "password": email_password,
        }
        requests.post(url=email_url, headers=email_auth_key, data=json.dumps(email_data))
