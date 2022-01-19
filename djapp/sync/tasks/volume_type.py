
import logging

from celery import shared_task

from djapp import models

from . import base

LOG = logging.getLogger(__name__)


def _convert_volume_type_from_os2db(db_obj, os_obj):
    """OpenStack volume type to_dict:
    {
        'id': '267115ef-e790-48f8-af29-f3e4b21d2c4a',
        'name': 'high-ssd',
        'is_public': True,
        'description': None,
        'extra_specs': {},
        'qos_specs_id': None,
        'os-volume-type-access:is_public': True
    }
    """
    db_obj.id = os_obj.get('id')
    db_obj.name = os_obj.get('name')
    db_obj.description = os_obj.get('description')
    db_obj.is_public = os_obj.get('is_public')
    # db_obj.created_at
    # db_obj.updated_at


@shared_task
def do_volume_types_sync():
    db_objects = models.VolumeType.objects.all()
    os_objects = base.cinder_api().get_volume_types()
    os_objects = [os_obj.to_dict() for os_obj in os_objects]

    LOG.info("Start to syncing VolumeTypes  ...")

    def _remove_volume_type(db_obj):
        LOG.info("Remove unknown volume type: %s" % db_obj.id)
        db_obj.delete()

    def _create_volume_type(os_obj):
        LOG.info("Create a new volume type: %s" % os_obj['id'])
        db_obj = models.VolumeType()
        _convert_volume_type_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_volume_type(db_obj, os_obj):
        LOG.info("Update existed volume type: %s" % db_obj.id)
        _convert_volume_type_from_os2db(db_obj, os_obj)
        # update to db
        db_obj.save()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_volume_type,
                  update_db_fn=_update_volume_type,
                  remove_db_fn=_remove_volume_type)
