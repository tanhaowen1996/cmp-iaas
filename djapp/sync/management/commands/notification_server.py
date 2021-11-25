import logging

from django.core.management.base import BaseCommand

from sync.rabbitmq import notifications


LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s.%(funcName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Waiting to receiving notifications and process"

    def handle(self, *args, **kwargs):
        LOG.info("Server starting ...")
        # waiting to receive notifications and process
        notifications.start_listener()
