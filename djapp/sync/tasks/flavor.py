
import logging

from djapp import models
from sync import osapi

from . import base

LOG = logging.getLogger(__name__)


def _convert_flavor_from_os2db(db_obj, os_obj, is_public=True):
    """OpenStack flavor dict:
    {
        'id': '4512c284-ba72-4e74-bc8a-f27c4e3a706e',
        'name': '4c4g60g',
        'ram': 4096,
        'disk': 60,
        'swap': '',
        'OS-FLV-EXT-DATA:ephemeral': 0,
        'OS-FLV-DISABLED:disabled': False,
        'vcpus': 4,
        'os-flavor-access:is_public': True,
        'rxtx_factor': 1.0,
        'links': [
            {'rel': 'self',
             'href': 'http://10.210.8.177:8774/v2.1/flavors/4512c284-ba72-4e74-bc8a-f27c4e3a706e'
            },
            {'rel': 'bookmark',
             'href': 'http://10.210.8.177:8774/flavors/4512c284-ba72-4e74-bc8a-f27c4e3a706e'
            }
        ]
    }

    {"flavor_access": [
        {
            "flavor_id": "a16fa604-121a-4e70-ae43-271eb209f4ab",
            "tenant_id": "b587cd6ac342420bbb4badd61c1a5852"
        }
    ]}
    """
    db_obj.id = os_obj.get('id')
    db_obj.name = os_obj.get('name')
    db_obj.memory = os_obj.get('ram')
    db_obj.cpu = os_obj.get('vcpus')
    db_obj.disk = os_obj.get('disk')

    if not is_public:
        flavor_access = osapi.NovaAPI.create().get_flavor_access(db_obj.id)
        if flavor_access:
            db_obj.creator_id = flavor_access[0].get('tenant_id')

    db_obj.deleted = 0
    # db_obj.update_time =


def do_flavors_sync():
    db_objects = models.Flavor.objects.all()
    os_objects = base.nova_api().get_flavors()
    os_objects = [os_obj.to_dict() for os_obj in os_objects]

    LOG.info("Start to syncing all public Flavors ...")

    def _remove_flavor(db_obj):
        LOG.info("Remove unknown flavor: %s" % db_obj.id)
        db_obj.save()

    def _create_flavor(os_obj):
        LOG.info("Create a new flavor: %s" % os_obj.get('id'))
        db_obj = models.Flavor()
        _convert_flavor_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_flavor(db_obj, os_obj):
        LOG.info("Update existed flavor: %s" % db_obj.id)
        _convert_flavor_from_os2db(db_obj, os_obj)
        # update to db:
        db_obj.save()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_flavor,
                  update_db_fn=_update_flavor,
                  remove_db_fn=_remove_flavor)

