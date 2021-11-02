from django.conf import settings
import openstack


openstack.enable_logging(debug=settings.DEBUG)

os_conn = openstack.connect()
