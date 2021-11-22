import logging

from django.core.management.base import BaseCommand

from sync import populate

LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync All Resources from OpenStack"

    def handle(self, *args, **kwargs):
        LOG.info("Start to Sync OpenStack Resources ...")
        populate.do_all_sync()
