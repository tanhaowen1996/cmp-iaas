
import logging

from sync.tasks import instance as instance_tasks

from . import base

LOG = logging.getLogger(__name__)


INSTANCE_ACTION_EVENTS = (
    'compute.instance.pause.end',
    'compute.instance.unpause.end',
    'compute.instance.resize.end',
    'compute.instance.resize.error',
    'compute.instance.suspend.end',
    'compute.instance.power_on.end',
    'compute.instance.power_off.end',
    'compute.instance.reboot.end',
    'compute.instance.reboot.error',
    'compute.instance.shutdown.end',
    'compute.instance.restore.end',
    'compute.instance.evacuate',
    'compute.instance.resize_finish.end',
    'compute.instance.resize_confirm.end',
    'compute.instance.resize_revert.end',
    'compute.instance.lock',
    'compute.instance.unlock',
)

INSTANCE_DELETE_EVENTS = (
    'compute.instance.delete.end',
    'compute.instance.soft_delete.end',
)

INSTANCE_ACTION_INTERFACE_EVENTS = (
    'compute.instance.interface_attach.end',
    'compute.instance.interface_attach.error',
    'compute.instance.interface_detach.end',
)

INSTANCE_ACTION_VOLUME_EVENTS  = (
    'compute.instance.volume_attach.end',
    'compute.instance.volume_attach.error',
    'compute.instance.volume_detach.end',
)

INSTANCE_CREATE_START_EVENTS = (
    'compute.instance.create.start',
)

INSTANCE_CREATE_EVENTS = (
    'instance.create.end',
    'instance.create.error',
    'compute.instance.create.end',
    'compute.instance.create.error',
)

INSTANCE_RESIZE_PREP_EVENTS = (
    'instance.resize_prep.start',
    'instance.resize_prep.end',
    'compute.instance.resize_prep.start',
    'compute.instance.resize_prep.end',
)

INSTANCE_SNAPSHOT_EVENTS = (
    'instance.snapshot.start',
    'instance.snapshot.end',
    'compute.instance.snapshot.start',
    'compute.instance.snapshot.end',
)

INSTANCE_EXISTS_EVENTS = (
    'compute.instance.exists',
)

INSTANCE_UPDATE_EVENTS = (
    'compute.instance.update',
)

INSTANCE_EVENTS = (
    *INSTANCE_ACTION_EVENTS,
    *INSTANCE_DELETE_EVENTS,
    *INSTANCE_ACTION_INTERFACE_EVENTS,
    *INSTANCE_ACTION_VOLUME_EVENTS,
    *INSTANCE_CREATE_START_EVENTS,
    *INSTANCE_CREATE_EVENTS,
    *INSTANCE_RESIZE_PREP_EVENTS,
    *INSTANCE_SNAPSHOT_EVENTS,
    *INSTANCE_EXISTS_EVENTS,
    *INSTANCE_UPDATE_EVENTS,
)


class InstanceEndpoint(base.NotificationEndpoint):
    """Instance Notification Process Endpoint."""

    event_types = [
        'compute.instance.*',
        'instance.*'
    ]

    def process(self, publisher_id, event_type, payload):
        """Process Instance Notifications."""
        if event_type not in INSTANCE_EVENTS:
            LOG.warning('event_type: %s pass to process...' % event_type)
            return

        instance_id = payload.get('instance_id')
        if not instance_id:
            LOG.error("Failed to got `instance_id` from event: %s payload: %s"
                      % (event_type, payload))
            return

        LOG.info("Start to process instance: %s notification: %s ..."
                 % (instance_id, event_type))

        # delete instance
        if event_type in INSTANCE_DELETE_EVENTS:
            LOG.info("Delete instance: %s" % instance_id)
            instance_tasks.sync_instance_delete.delay(instance_id)
            return

        # create instance
        if event_type in INSTANCE_CREATE_START_EVENTS:
            # create instance:
            LOG.info("Create instance: %s" % instance_id)
            instance_tasks.sync_instance_create.delay(instance_id)
            return

        # update instance
        instance_tasks.sync_instance_update.delay(instance_id)
