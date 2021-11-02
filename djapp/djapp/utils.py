from django.conf import settings
import openstack


openstack.enable_logging(debug=settings.DEBUG)


class OpenstackMixin:

    @staticmethod
    def get_conn():
        return openstack.connect()
