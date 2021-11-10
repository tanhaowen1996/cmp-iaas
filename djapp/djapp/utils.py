from django.conf import settings
import openstack
from keystoneauth1.identity import v3
from keystoneauth1 import session
from glanceclient import Client
import os


openstack.enable_logging(debug=settings.DEBUG)


class OpenstackMixin:

    @staticmethod
    def get_conn():
        return openstack.connect()

def sess_image():
    auth = v3.Password(auth_url=os.getenv('OS_AUTH_URL'),
                       username=os.getenv('OS_USERNAME'),
                       password=os.getenv('OS_PASSWORD'),
                       project_name=os.getenv('OS_PROJECT_NAME'),
                       user_domain_name=os.getenv('OS_USER_DOMAIN_NAME'),
                       project_domain_name=os.getenv("OS_PROJECT_DOMAIN_NAME"))
    sess = session.Session(auth=auth)
    sess_client = Client('2', session=sess)
    return sess_client

