import abc
import logging
import oslo_messaging

from djapp import models

from sync.tasks import instance as instance_tasks
from sync.tasks import network as network_tasks
from sync.tasks import volume as volume_tasks

from . import payloads

LOG = logging.getLogger(__name__)


INSTANCE_ACTION_NOTIFICATIONS = (
    # 'instance.delete.start',
    'instance.delete.end',
    # 'instance.pause.start',
    'instance.pause.end',
    # 'instance.unpause.start',
    'instance.unpause.end',
    # 'instance.resize.start',
    'instance.resize.end',
    'instance.resize.error',
    # 'instance.suspend.start',
    'instance.suspend.end',
    # 'instance.power_on.start',
    'instance.power_on.end',
    # 'instance.power_off.start',
    'instance.power_off.end',
    # 'instance.reboot.start',
    'instance.reboot.end',
    'instance.reboot.error',
    # 'instance.shutdown.start',
    'instance.shutdown.end',
    # 'instance.shelve.start',
    # 'instance.shelve.end',
    # 'instance.resume.start',
    # 'instance.resume.end',
    # 'instance.restore.start',
    'instance.restore.end',
    'instance.evacuate',
    # 'instance.resize_finish.start',
    'instance.resize_finish.end',
    # 'instance.live_migration_pre.start',
    # 'instance.live_migration_pre.end',
    # 'instance.live_migration_abort.start',
    # 'instance.live_migration_abort.end',
    # 'instance.live_migration_post.start',
    # 'instance.live_migration_post.end',
    # 'instance.live_migration_post_dest.start',
    # 'instance.live_migration_post_dest.end',
    # 'instance.live_migration_rollback.start',
    # 'instance.live_migration_rollback.end',
    # 'instance.live_migration_rollback_dest.start',
    # 'instance.live_migration_rollback_dest.end',
    # 'instance.resize_confirm.start',
    'instance.resize_confirm.end',
    # 'instance.resize_revert.start',
    'instance.resize_revert.end',
    # 'instance.live_migration_force_complete.start',
    # 'instance.live_migration_force_complete.end',
    # 'instance.shelve_offload.start',
    # 'instance.shelve_offload.end',
    # 'instance.soft_delete.start',
    'instance.soft_delete.end',
    # 'instance.trigger_crash_dump.start',
    # 'instance.trigger_crash_dump.end',
    # 'instance.unrescue.start',
    # 'instance.unrescue.end',
    # 'instance.unshelve.start',
    # 'instance.unshelve.end',
    'instance.lock',
    'instance.unlock',
)

INSTANCE_ACTION_INTERFACE_NOTIFICATIONS = (
    # 'instance.interface_attach.start',
    'instance.interface_attach.end',
    'instance.interface_attach.error',
    # 'instance.interface_detach.start',
    'instance.interface_detach.end',
)

INSTANCE_ACTION_VOLUME_NOTIFICATIONS = (
    # 'instance.volume_attach.start',
    'instance.volume_attach.end',
    'instance.volume_attach.error',
    # 'instance.volume_detach.start',
    'instance.volume_detach.end',
)

INSTANCE_CREATE_NOTIFICATIONS = (
    # 'instance.create.start',
    'instance.create.end',
    'instance.create.error',
)

INSTANCE_ACTION_RESIZE_PREP_NOTIFICATIONS = (
    'instance.resize_prep.start',
    'instance.resize_prep.end',
)

INSTANCE_ACTION_SNAPSHOT_NOTIFICATIONS = (
    'instance.snapshot.start',
    'instance.snapshot.end',
)

INSTANCE_EXISTS_NOTIFICATIONS = (
    'instance.exists',
)

INSTANCE_UPDATE_NOTIFICATIONS = (
    'instance.update',
)

INSTANCE_NOTIFICATIONS = (
    *INSTANCE_ACTION_NOTIFICATIONS,
    *INSTANCE_CREATE_NOTIFICATIONS,
    *INSTANCE_UPDATE_NOTIFICATIONS,
    *INSTANCE_EXISTS_NOTIFICATIONS,
    *INSTANCE_ACTION_SNAPSHOT_NOTIFICATIONS,
    *INSTANCE_ACTION_RESIZE_PREP_NOTIFICATIONS,
    *INSTANCE_ACTION_INTERFACE_NOTIFICATIONS,
    *INSTANCE_ACTION_VOLUME_NOTIFICATIONS,
)


class NotificationEndpoint(object):
    """Base Endpoint for plugins that support the notification API."""

    event_types = []
    """List of strings to filter messages on."""

    def __init__(self, forwarder=None):
        if self.event_types:
            self.filter_rule = oslo_messaging.NotificationFilter(
                event_type='|'.join(self.event_types))
        self.forwarder = forwarder

    @abc.abstractmethod
    def process(self, publisher_id, event_type, payload):
        """Return a sequence of Counter instances for the given message.

        :param publisher_id: Publisher.
        :param event_type: Event type.
        :param payload: Message to process.
        """

    def _process_notifications(self, context, publisher_id, event_type, payload, metadata):
        """RPC endpoint for all notification level"""
        _, _ = context, metadata
        try:
            LOG.info("Received: %s -- %s" % (publisher_id, event_type))
            self.process(publisher_id, event_type, payload)
        except Exception as e:
            LOG.exception(e)
            pass

    audit = _process_notifications
    critical = _process_notifications
    debug = _process_notifications
    error = _process_notifications
    info = _process_notifications
    sample = _process_notifications
    warn = _process_notifications


class ImageEndpoint(NotificationEndpoint):
    """Image Notification Process Endpoint."""

    event_types = [
        'image.create',
        'image.update',
        'image.upload',
        'image.delete',
        'image.send'
    ]

    def process(self, publisher_id, event_type, payload):
        pass


class InstanceEndpoint(NotificationEndpoint):
    """Instance Notification Process Endpoint."""

    event_types = [
        'compute.instance.*',
        'instance.*'
    ]

    def process(self, publisher_id, event_type, payload):
        """Process Instance Notifications."""
        payload = payloads.Payload.create(payload)

        instance_id = payload.instance_id
        LOG.info("Start to process instance: %s notification: %s ..."
                 % (instance_id, event_type))

        if event_type not in INSTANCE_NOTIFICATIONS:
            LOG.warning('event_type: % pass to process...')
            return

        if event_type in INSTANCE_ACTION_INTERFACE_NOTIFICATIONS:
            # update port
            for ip_address in payload.ip_addresses:
                network_tasks.sync_port_by_id(ip_address.port_id)

        if event_type in INSTANCE_ACTION_VOLUME_NOTIFICATIONS:
            # update volume
            volume_tasks.sync_volume_by_id(payload.volume_id)

        # update instance
        instance_tasks.sync_instance_by_id(instance_id)


class VolumeEndpoint(NotificationEndpoint):
    """Volume Notification Process Endpoint."""

    event_types = [
        'volume.transfer.*',
        'volume.exists',
        'volume.retype',
        'volume.create.*',
        'volume.delete.*',
        'volume.resize.*',
        'volume.attach.*',
        'volume.detach.*',
        'volume.update.*',
    ]

    def process(self, publisher_id, event_type, payload):
        LOG.info("Start process volume notification: %s" % event_type)
        volume_id = payload.get('volume_id', None)
        if not volume_id:
            LOG.error("Failed to got `volume_id` from notification: %s payload: %s "
                      % (event_type, payload))
            return
        # update volume:
        volume_tasks.sync_volume_by_id(volume_id)


class NetworkEndpoint(NotificationEndpoint):
    """Network Notification Process Endpoint."""

    event_types = [
        'network.*',
        'subnet.*',
        'port.*',
    ]

    def process(self, publisher_id, event_type, payload):
        def _get_network_id():
            net_id = payload.get('network_id', None)
            if net_id is None:
                net_id = payload.get('network', {}).get('id')
            return net_id

        LOG.info('Start to process notification: %s ...' % event_type)

        event_type = event_type.split('.')[0]

        if event_type in ['network', 'subnet']:
            network_id = _get_network_id()
            if not network_id:
                LOG.error("Failed to got `network_id` from notification: %s payload: %s"
                          % (event_type, payload))
                return
            # update network:
            network_tasks.sync_network_by_id(network_id)

        if event_type == 'port':
            port_id = payload.get('port_id', None)
            if not port_id:
                LOG.error("Failed to got `port_id` from notification: %s payload: %s"
                          % (event_type, payload))
                return
            # update port:
            network_tasks.sync_port_by_id(port_id)

