
import logging

from django.utils import timezone

from djapp import models
from sync import osapi

from . import base

LOG = logging.getLogger(__name__)


def _convert_volume_from_os2db(db_obj, os_obj, user=None, project=None):
    """ OpenStack Volume to_dict:
    {
        'id': 'acc5260b-af73-4295-9439-f7bf406bf104',
        'status': 'in-use',
        'size': 1,
        'availability_zone': 'nova',
        'created_at': '2021-11-22T02:09:53.000000',
        'updated_at': '2021-11-22T02:27:20.000000',
        'name': '1',
        'description': None,
        'volume_type': 'ssd',
        'snapshot_id': None,
        'source_volid': None,
        'metadata': {},
        'links': [
            {'rel': 'self', 'href': 'http://10.210.8.177:8776/v3/a0e1d03c2aa34b538f2bb420542dfb5e/volumes/acc5260b-af73-4295-9439-f7bf406bf104'},
            {'rel': 'bookmark', 'href': 'http://10.210.8.177:8776/a0e1d03c2aa34b538f2bb420542dfb5e/volumes/acc5260b-af73-4295-9439-f7bf406bf104'}
        ],
        'user_id': 'f4e124ef1eea4ad8bf3c6e0983275dad',
        'bootable': 'false',
        'encrypted': False,
        'replication_status': None,
        'consistencygroup_id': None,
        'multiattach': False,
        'attachments': [{
            'id': 'acc5260b-af73-4295-9439-f7bf406bf104',
            'attachment_id': 'e3ac6e6a-4bef-4e79-9a91-63f2263bd895',
            'volume_id': 'acc5260b-af73-4295-9439-f7bf406bf104',
            'server_id': 'b8a5030a-06a7-4f8c-a3b6-723a1f92c35f',
            'host_name': 'control',
            'device': '/dev/vdd',
            'attached_at': '2021-11-22T02:27:18.000000'
        }],
        'migration_status': None,
        'os-vol-host-attr:host': 'control@lvm-1#lvm-1',
        'os-vol-mig-status-attr:migstat': None,
        'os-vol-mig-status-attr:name_id': None,
        'os-vol-tenant-attr:tenant_id': '752df3ea70724f44acc088a0f0313579'
    }
    """
    db_obj.id = os_obj.get('id')
    db_obj.name = os_obj.get('name')
    db_obj.description = os_obj.get('description')
    db_obj.project_id = os_obj.get('os-vol-tenant-attr:tenant_id')

    if user:
        # UUM user:
        db_obj.user_id = user.get('userId')
        db_obj.user_name = user.get('userName')
        # OpenStack user:
        db_obj.rel_user_id = user.get('relUserId')
        db_obj.rel_user_name = user.get('relUserName')

    if project:
        db_obj.tenant_id = project.get('tenantId')
        db_obj.tenant_name = project.get('tenantName')

    # db_obj.volume_used

    db_obj.is_bootable = \
        False if os_obj.get('bootable', 'false').lower() == 'false' else True

    db_obj.volume_type = os_obj.get('volume_type')
    db_obj.size = os_obj.get('size')
    db_obj.status = os_obj.get('status')

    attachments = os_obj.get('attachments', [])
    if len(attachments) >= 1:
        attachment = attachments[0]
        db_obj.device = attachment.get('device')
        db_obj.attach_status = 'attached'

        db_obj.server_id = attachment.get('server_id')
        # db_obj.server_name

    else:
        db_obj.attach_status = 'detached'

    db_obj.attachments = attachments
    db_obj.cluster_name = os_obj.get('os-vol-host-attr:host')

    db_obj.created_at = timezone.now()
    db_obj.updated_at = timezone.now()


def do_volumes_sync(user=None, project=None):
    project_id = project.get('id') if project else osapi.get_project_id()
    # get project volumes:
    db_objects = models.Volume.objects.filter(project_id=project_id)
    os_objects = base.cinder_api().get_volumes(project_id=project_id)

    os_objects = (os_obj.to_dict() for os_obj in os_objects)
    os_objects = [os_obj for os_obj in os_objects
                  if os_obj.get('os-vol-tenant-attr:tenant_id') == project_id]

    LOG.info("Start to syncing Volumes for project: %s ..." % project_id)

    def _remove_volume(db_obj):
        LOG.info("Remove unknown volume: %s" % db_obj.id)
        db_obj.delete()

    def _create_volume(os_obj):
        LOG.info("Create a new volume: %s" % os_obj.get('id'))
        db_obj = models.Volume()
        _convert_volume_from_os2db(db_obj, os_obj, user, project)
        # save to db:
        db_obj.save()

    def _update_volume(db_obj, os_obj):
        LOG.info("Update existed volume: %s" % db_obj.id)
        _convert_volume_from_os2db(db_obj, os_obj, user, project)
        # update to db:
        db_obj.save()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_volume,
                  update_db_fn=_update_volume,
                  remove_db_fn=_remove_volume)


def db_get_volume(volume_id):
    try:
        return models.Volume.objects.get(pk=volume_id)
    except models.Volume.DoesNotExist:
        return None


def sync_volume_by_id(volume_id):
    db_obj = db_get_volume(volume_id)
    if db_obj is None:
        # Pass process newly info
        LOG.warning("Could not found volume: %s info in db, pass sync it ..."
                    % volume_id)
        return

    os_obj = base.cinder_api().show_volume(volume_id=volume_id)
    if not os_obj:
        # Remove untracked info
        LOG.error("Unknown volume: %s in openstack, remove db object!" % volume_id)
        db_obj.delete()
        return

    # Update existed info
    _convert_volume_from_os2db(db_obj, os_obj)
    db_obj.save()

