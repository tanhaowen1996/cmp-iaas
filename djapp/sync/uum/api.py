
import requests

from django.conf import settings


def user_list():
    url = '%s/tenantManager/queryRelCloudUser' % settings.UUM_URL
    response = requests.get(url)
    body = response.json()
    if not body.get('status'):
        raise Exception('Get `%s` failed,for: %s'
                        % (url, body.get('descr')))
    return body['data']

