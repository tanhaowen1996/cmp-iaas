import logging

from django.core.management.base import BaseCommand

# from sync import populate
from sync.tasks import user as user_tasks

LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync Tenants' resources from OpenStack"

    def handle(self, *args, **kwargs):
        LOG.info("Start to Sync Tenants' resources from OpenStack ...")
        user_tasks.do_tenants_sync()
