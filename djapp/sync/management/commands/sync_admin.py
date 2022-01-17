
import logging

from django.core.management.base import BaseCommand

# from sync import populate
from sync.tasks import user as user_tasks

LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync Admin's Resources from OpenStack"

    def handle(self, *args, **kwargs):
        LOG.info("Start to Sync Admin's resources from OpenStack ...")
        user_tasks.do_admin_sync()
