
import logging

from djapp import models
from sync import osapi

from . import base

LOG = logging.getLogger(__name__)


def _convert_image_from_os2db(db_obj, os_obj, user=None, project=None):
    """
    OpenStack Image Model:
    {
        'description': 'wewqrw',
        'os_type': 'ubuntu',
        'owner_specified.openstack.md5': '',
        'owner_specified.openstack.object': 'images/j',
        'owner_specified.openstack.sha256': '',
        'name': 'j',
        'disk_format': 'qcow2',
        'container_format': 'bare',
        'visibility': 'shared',
        'size': None,
        'virtual_size': None,
        'status': 'queued',
        'checksum': None,
        'protected': True,
        'min_ram': 0,
        'min_disk': 0,
        'owner': 'a0e1d03c2aa34b538f2bb420542dfb5e',
        'os_hidden': False,
        'os_hash_algo': None,
        'os_hash_value': None,
        'id': 'b1f0d40c-7d9a-428a-a728-a1bd3e809eff',
        'created_at': '2021-11-09T07:31:13Z',
        'updated_at': '2021-11-09T07:31:13Z',
        'tags': [],
        'file': '/v2/images/b1f0d40c-7d9a-428a-a728-a1bd3e809eff/file',
        'schema': '/v2/schemas/image'
    }
    """
    db_obj.id = os_obj.get('id')
    db_obj.name = os_obj.get('name')
    db_obj.description = os_obj.get('description')

    db_obj.size = os_obj.get('size')
    db_obj.status = os_obj.get('status')
    os_type = os_obj.get('os_type', None)
    if not os_type:
        os_type = os_obj.get('yh_os_type', 'others')
    db_obj.os_type = os_type

    db_obj.owner = os_obj.get('owner')
    db_obj.disk_format = os_obj.get('disk_format')
    db_obj.container_format = os_obj.get('container_format')
    db_obj.visibility = os_obj.get('visibility')

    db_obj.created_at = os_obj.get('created_at')
    db_obj.updated_at = os_obj.get('updated_at')

    if user:
        db_obj.user_name = user.get('userName')
        db_obj.user_id = user.get('userId')

    if project:
        db_obj.tenant_id = project.get('tenantId')
        db_obj.tenant_name = project.get('tenantName')


def do_images_sync(user=None, project=None):
    """Sync db objects with openstack information."""
    project_id = project.get('id') if project else osapi.get_project_id()
    # filter by project_id
    db_objects = models.Image.objects.filter(owner=project_id)
    os_objects = base.glance_api().get_images()
    os_objects = [os_obj for os_obj in os_objects
                  if os_obj.get('owner') == project_id]

    LOG.info("Start to syncing Images of project: %s ..." % project_id)

    def _remove_image(db_obj):
        LOG.info("Remove Unknown Image: %s" % db_obj)
        db_obj.delete()

    def _create_image(os_obj):
        LOG.info("Create a new image: %s" % os_obj.get('id'))
        # create db obj:
        db_obj = models.Image()
        _convert_image_from_os2db(db_obj, os_obj, user, project)
        # save to db:
        db_obj.save()

    def _update_image(db_obj, os_obj):
        LOG.info("Update existed image: %s" % db_obj.id)
        _convert_image_from_os2db(db_obj, os_obj, user, project)
        # update to db:
        db_obj.save()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj['id']),
                  create_db_fn=_create_image,
                  update_db_fn=_update_image,
                  remove_db_fn=_remove_image)

