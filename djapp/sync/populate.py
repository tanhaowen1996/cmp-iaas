import abc
import logging

from djapp import models
from . import osapi

LOG = logging.getLogger(__name__)


def _alg_sync(db_objects, db_obj_key_fn, os_objects, os_obj_key_fn,
              create_db_fn, update_db_fn, remove_db_fn,
              remove_allowed=False):
    """Generic sync Resources method."""
    # Objects to Dicts
    exist_objects = {db_obj_key_fn(db_obj): db_obj for db_obj in db_objects}
    new_objects = {os_obj_key_fn(os_obj): os_obj for os_obj in os_objects}

    LOG.info("Want %s, Got %s" % (len(exist_objects), len(new_objects)))

    LOG.debug("exist set: %s" % set(exist_objects))
    LOG.debug("new set: %s" % set(new_objects))

    for existed in exist_objects.values():
        if db_obj_key_fn(existed) in set(exist_objects) - set(new_objects):
            # Remove previously unknown resource.
            if not remove_allowed:
                LOG.warning("Will not remove unknown resource: %s" % db_obj_key_fn(existed))
                continue
            try:
                remove_db_fn(existed)
                LOG.info("Removed previously unknown resource: %s" % db_obj_key_fn(existed))
            except Exception as e:
                LOG.exception(e)
        else:
            # Update tracked resources.
            new_value = new_objects[db_obj_key_fn(existed)]
            update_db_fn(existed, new_value)
            LOG.info("Updated tracked resource: %s" % db_obj_key_fn(existed))

    # Track newly discovered resources.
    for os_obj in [os_obj for os_obj in new_objects.values() if
                   os_obj_key_fn(os_obj) in set(new_objects) - set(exist_objects)]:
        create_db_fn(os_obj)
        LOG.info("Tracked newly discovered resource: %s" % os_obj_key_fn(os_obj))


class Syncer(object):

    @abc.abstractmethod
    def do(self):
        """sync action"""


# Image
class ImageSyncer(Syncer):
    """Do Images Sync from OpenStack.
    """

    def do(self):
        self.do_sync_images()

    def do_sync_images(self):
        """Sync db objects with openstack information."""
        db_objects = models.Image.objects.all()
        os_objects = osapi.GlanceAPI.create().get_images()

        LOG.info("Update images ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj['id']),
                  create_db_fn=self.create_image,
                  update_db_fn=self.update_image,
                  remove_db_fn=self.remove_image)

    def remove_image(self, db_obj):
        LOG.info("Remove Unknown Image: %s" % db_obj)
        db_obj.delete()

    def create_image(self, os_obj):
        """Create Image from OpenStack.

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
        LOG.info("Create a new image: %s" % os_obj)

        # create db obj:
        db_obj = models.Image()

        db_obj.id = os_obj.get('id')
        db_obj.name = os_obj.get('name')
        db_obj.description = os_obj.get('description')

        db_obj.size = os_obj.get('size')
        db_obj.status = os_obj.get('status')
        db_obj.os_type = os_obj.get('os_type', 'unknown')

        db_obj.owner = os_obj.get('owner')
        db_obj.disk_format = os_obj.get('disk_format')
        db_obj.container_format = os_obj.get('container_format')
        os_obj.visibility = os_obj.get('visibility')

        db_obj.created_at = os_obj.get('created_at')
        db_obj.updated_at = os_obj.get('updated_at')

        # user_name = os_obj.user
        # user_id = os_obj.user.id
        # tenant_id = os_obj.account_info.get('tenantId'),
        # tenant_name = os_obj

        # save to db:
        db_obj.save()

    def update_image(self, db_obj, os_obj):
        LOG.info("Update db image: %s from os image: %s" % (db_obj.id, os_obj['id']))

        db_obj.name = os_obj.get('name')
        db_obj.description = os_obj.get('description')

        db_obj.size = os_obj.get('size')
        db_obj.status = os_obj.get('status')
        db_obj.os_type = os_obj.get('os_type', 'unknown')

        db_obj.owner = os_obj.get('owner')
        db_obj.disk_format = os_obj.get('disk_format')
        db_obj.container_format = os_obj.get('container_format')
        os_obj.visibility = os_obj.get('visibility')

        db_obj.created_at = os_obj.get('created_at')
        db_obj.updated_at = os_obj.get('updated_at')

        # update to db:
        db_obj.save()


# Network/Subnet/Port
class NetworkSyncer(Syncer):

    def do(self):
        pass


# KeyPair
class KeyPairSyncer(Syncer):

    def do(self):
        # TODO: now only admin's key pairs to be synced
        self.do_key_pairs_sync()

    def do_key_pairs_sync(self):
        """Sync db objects with openstack information."""
        db_objects = models.Keypair.objects.all()
        os_objects = osapi.NovaAPI.create().get_keypairs()

        LOG.info("Update Key pairs ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: obj.name,
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.name,
                  create_db_fn=self.create_keypair,
                  update_db_fn=self.update_keypair,
                  remove_db_fn=self.remove_keypair)

    def create_keypair(self, os_obj):
        """
        os keypair dict:
        {
            'keypair': {
                'name': '111',
                'public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/7YmNX/5hbu7MDgXJmK9doQxmYKaEkE1zFCH16FMGl7dMYMwn3B3CsdPOY+gueGOIsj2Yg1Bsg95AT76joWABxQNQDxfpmpoPOnPTjHS/N6NrrlfL/OKkEkqj6tA2907W61crkEbnlUm9ZVFkKzcBDrgKxUY4tk1334eUf8J5TfsMj7MlHtwHcIs1SGtfmF2Epgq7nMV7PNX0jhvSZIi3YesOGTiAaI1W9MT/NLJJz2r9GsVLzaJuQCYDMEaIyoCTWHZNQdyJULUMoACu5dj0HwHc3vdCyJCHgIWk/Ctwoe97JPi531sjynEPe+oT7MVNBWWjTMEGZMLMs2DvChpb Generated-by-Nova',
                'fingerprint': '8a:79:00:88:aa:ad:21:89:5e:98:1b:31:34:4a:9d:37',
                'type': 'ssh'
            }
        }
        """
        LOG.info("Create a new keypair: %s" % os_obj)
        db_obj = models.Keypair()

        db_obj.name = os_obj.name
        # description
        db_obj.fingerprint = os_obj.fingerprint
        db_obj.public_key = os_obj.public_key
        db_obj.type = os_obj.type

        db_obj.project_id = osapi.get_project_id()
        db_obj.user_id = osapi.get_user_id()

        # user_name
        # tenant_id
        # tenant_name

        # created_at
        # updated_at

        # save to db:
        db_obj.save()

    def update_keypair(self, db_obj, os_obj):
        LOG.info("Update existed keypair %s from %s" % (db_obj.name, os_obj.name))

        db_obj.name = os_obj.name
        db_obj.fingerprint = os_obj.fingerprint
        db_obj.public_key = os_obj.public_key
        db_obj.type = os_obj.type

        # update to db:
        db_obj.save()

    def remove_keypair(self, db_obj):
        LOG.info("Remove unknown keypair %s" % db_obj.name)
        db_obj.delete()


# Instance
class InstanceSyncer(Syncer):

    def do(self):
        self.update_instances()
        self.update_flavors()

    def update_flavors(self):
        """Sync db objects with openstack information."""
        db_objects = models.Flavor.objects.all()
        os_objects = self.client.list_flavors()

        LOG.info("Update Flavors: got %s, want %s" % (len(db_objects), len(os_objects)))

        # Objects to Dicts
        exist_objects = {obj.id: obj for obj in db_objects}
        new_objects = {obj.id: obj for obj in os_objects}

        for existed in db_objects:
            if existed.id in set(exist_objects) - set(new_objects):
                # 1) Remove previously unknown resource.
                LOG.info("Remove Flavor: %s " % existed)
                try:
                    # existed.delete()
                    pass
                except Exception as e:
                    LOG.exception(e)
            else:
                # 2) Update tracked resources.
                new_value = new_objects[existed.id]
                LOG.info("Update Flavor: %s to %s" % (existed, new_value))
                existed.update(new_value)
                existed.save()

        # 3) Track newly discovered resources.
        for obj in [obj for obj in os_objects if
                    obj.id in set(new_objects) - set(exist_objects)]:
            newly = models.Flavor.create(obj)
            LOG.info("Add Flavor: %s - %s" % (newly.id, newly.name))
            newly.save()

    def update_instances(self):
        """Sync db objects with openstack information."""
        db_objects = models.Instance.objects.all()
        os_objects = self.client.list_instances()

        LOG.info("Update Instances: got %s, want %s" % (len(db_objects), len(os_objects)))

        # Objects to Dicts
        exist_objects = {obj.id: obj for obj in db_objects}
        new_objects = {obj.id: obj for obj in os_objects}

        for existed in db_objects:
            if existed.id in set(exist_objects) - set(new_objects):
                # 1) Remove previously unknown resource.
                LOG.info("Remove Instance: %s " % existed)
                try:
                    # existed.delete()
                    pass
                except Exception as e:
                    LOG.exception(e)
            else:
                # 2) Update tracked resources.
                new_value = new_objects[existed.id]
                LOG.info("Update Instance: %s to %s" % (existed, new_value))
                existed.update(new_value)
                existed.save()

        # 3) Track newly discovered resources.
        for obj in [obj for obj in os_objects if
                    obj.id in set(new_objects) - set(exist_objects)]:
            newly = models.Instance.create(obj)
            LOG.info("Add Instance: %s - %s" % (newly.id, newly.name))
            newly.save()


# Volume
class VolumeSyncer(Syncer):

    def do(self):
        self.update_volumes()

    def update_volumes(self):
        """Sync db objects with openstack information."""
        db_objects = models.Volume.objects.all()
        os_objects = self.client.list_volumes()

        LOG.info("Update Volumes: got %s, want %s" % (len(db_objects), len(os_objects)))

        # Objects to Dicts
        exist_objects = {obj.id: obj for obj in db_objects}
        new_objects = {obj.id: obj for obj in os_objects}

        for existed in db_objects:
            if existed.id in set(exist_objects) - set(new_objects):
                # 1) Remove previously unknown resource.
                LOG.info("Remove Volume: %s " % existed)
                try:
                    # existed.delete()
                    pass
                except Exception as e:
                    LOG.exception(e)
            else:
                # 2) Update tracked resources.
                new_value = new_objects[existed.id]
                LOG.info("Update Volume: %s to %s" % (existed, new_value))
                existed.update(new_value)
                existed.save()

        # 3) Track newly discovered resources.
        for obj in [obj for obj in os_objects if
                    obj.id in set(new_objects) - set(exist_objects)]:
            newly = models.Volume.create(obj)
            LOG.info("Add Volume: %s - %s" % (newly.id, newly.name))
            newly.save()


def do_all_sync():
    # image_sync = ImageSyncer()
    # image_sync.do()

    key_pair_sync = KeyPairSyncer()
    key_pair_sync.do()

    """
    for cls in Syncer.__subclasses__():
        LOG.info('Start %s ...' % cls.__name__)
        try:
            cls(client).do()
        except Exception as e:
            LOG.exception(e)
    """


if __name__ == '__main__':
    do_all_sync()
