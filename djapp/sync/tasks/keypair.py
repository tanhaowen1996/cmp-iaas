
import logging

from celery import shared_task

from djapp import models
from sync import osapi

from . import base

LOG = logging.getLogger(__name__)


def _convert_keypair_from_os2_db(db_obj, os_obj, user=None, project=None):
    """OpenStack keypair dict:
    {
        'name': '111',
        'public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/7YmNX/5hbu7MDgXJmK9doQxmYKaEkE1zFCH16FMGl7dMYMwn3B3CsdPOY+gueGOIsj2Yg1Bsg95AT76joWABxQNQDxfpmpoPOnPTjHS/N6NrrlfL/OKkEkqj6tA2907W61crkEbnlUm9ZVFkKzcBDrgKxUY4tk1334eUf8J5TfsMj7MlHtwHcIs1SGtfmF2Epgq7nMV7PNX0jhvSZIi3YesOGTiAaI1W9MT/NLJJz2r9GsVLzaJuQCYDMEaIyoCTWHZNQdyJULUMoACu5dj0HwHc3vdCyJCHgIWk/Ctwoe97JPi531sjynEPe+oT7MVNBWWjTMEGZMLMs2DvChpb Generated-by-Nova',
        'fingerprint': '8a:79:00:88:aa:ad:21:89:5e:98:1b:31:34:4a:9d:37',
        'type': 'ssh'
    }
    """
    db_obj.name = os_obj.name
    # description
    db_obj.fingerprint = os_obj.fingerprint
    db_obj.public_key = os_obj.public_key
    db_obj.type = os_obj.type

    if project:
        db_obj.project_id = project.get('id')
        db_obj.tenant_id = project.get('tenantId')
        db_obj.tenant_name = project.get('tenantName')

    if user:
        # uum user:
        db_obj.user_id = user.get('userId')
        db_obj.user_name = user.get('userName')
        # openstack user:
        db_obj.rel_user_id = user.get("relUserId")
        db_obj.rel_user_name = user.get("relUserName")

    # created_at
    # updated_at


@shared_task
def do_key_pairs_sync(user=None, project=None):
    """Sync db objects with openstack information."""
    rel_user_id = user.get('relUserId') if user else osapi.get_user_id()
    # filter by openstack user id:
    db_objects = models.Keypair.objects.filter(rel_user_id=rel_user_id)
    os_objects = base.nova_api().get_user_keypairs(user_id=rel_user_id)

    LOG.info("Start to syncing Keypairs for user: %s ..." % rel_user_id)

    def _remove_keypair(db_obj):
        LOG.info("Remove unknown keypair %s" % db_obj.name)
        db_obj.delete()

    def _create_keypair(os_obj):
        LOG.info("Create a new keypair: %s" % os_obj)
        db_obj = models.Keypair()
        _convert_keypair_from_os2_db(db_obj, os_obj, user, project)
        # save to db:
        db_obj.save()

    def _update_keypair(db_obj, os_obj):
        LOG.info("Update existed keypair %s from %s" % (db_obj.name, os_obj.name))
        _convert_keypair_from_os2_db(db_obj, os_obj, user, project)
        # update to db:
        db_obj.save()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: obj.name,
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.name,
                  create_db_fn=_create_keypair,
                  update_db_fn=_update_keypair,
                  remove_db_fn=_remove_keypair)

