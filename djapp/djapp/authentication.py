from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import (
    authentication,
    exceptions
)
from base64 import b64decode
from keystoneauth1 import session
from keystoneauth1.identity import v3
from .utils import openstack
import logging
import json


logger = logging.getLogger(__package__)


class OSAuthentication(authentication.BaseAuthentication):
    OS_TOKEN_KEY = settings.OS_TOKEN_KEY
    ACCOUNT_INFO_KEY = settings.ACCOUNT_INFO_KEY

    def authenticate(self, request):
        try:
            if self.OS_TOKEN_KEY not in request.headers:
                raise KeyError(f"{self.OS_TOKEN_KEY} is missing")

            if self.ACCOUNT_INFO_KEY not in request.headers:
                raise KeyError(f"{self.ACCOUNT_INFO_KEY} is missing")

            account_info = json.loads(b64decode(request.headers[self.ACCOUNT_INFO_KEY]))
            os_auth = v3.Token(
                auth_url=settings.OS_AUTH_URL,
                token=request.headers[self.OS_TOKEN_KEY],
                project_id=account_info['currentTenantCloudRel']['projectId'],
                project_domain_name=settings.OS_PROJECT_DOMAIN_NAME,
            )
            request.os_conn = openstack.connection.Connection(
                session=session.Session(auth=os_auth),
                identity_api_version=settings.OS_IDENTITY_API_VERSION,
                interface=settings.OS_INTERFACE,
                region_name=settings.OS_REGION_NAME,
            )
        except Exception as exc:
            msg = f"invalid request header: {exc}"
            logger.error(msg)
            raise exceptions.AuthenticationFailed(msg)
        else:
            user, created = User.objects.update_or_create(
                id=account_info['id'], defaults={
                    'username': account_info['loginName'],
                    'first_name': account_info['accountName'],
                    'is_staff': bool(account_info['isPlatform'])
                })
            request.account_info = account_info
            return (user, None)
