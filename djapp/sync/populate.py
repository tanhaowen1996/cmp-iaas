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

        LOG.info("Start to do images syncing ...")

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


# KeyPair
class KeyPairSyncer(Syncer):

    def do(self):
        # TODO: now only admin's key pairs to be synced
        self.do_key_pairs_sync()

    def do_key_pairs_sync(self):
        """Sync db objects with openstack information."""
        db_objects = models.Keypair.objects.all()
        os_objects = osapi.NovaAPI.create().get_keypairs()

        LOG.info("Start to do Key pairs syncing ...")

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


# Volume
class VolumeSyncer(Syncer):

    def do(self):
        self.do_volume_types_sync()
        self.do_volumes_sync()

    def do_volume_types_sync(self):
        db_objects = models.VolumeType.objects.all()
        os_objects = osapi.CinderAPI.create().get_volume_types()
        os_objects = [os_obj.to_dict() for os_obj in os_objects]

        LOG.info("Start to do volume types syncing ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj.id),
                  create_db_fn=self.create_volume_type,
                  update_db_fn=self.update_volume_type,
                  remove_db_fn=self.remove_volume_type)

    def _convert_volume_type_from_os2db(self, db_obj, os_obj):
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

    def create_volume_type(self, os_obj):
        LOG.info("Create a new volume type: %s" % os_obj['id'])
        db_obj = models.VolumeType()
        self._convert_volume_type_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def update_volume_type(self, db_obj, os_obj):
        LOG.info("Update existed volume type: %s" % db_obj.id)
        self._convert_volume_type_from_os2db(db_obj, os_obj)
        # update to db
        db_obj.save()

    def remove_volume_type(self, db_obj):
        LOG.info("Remove unknown volume type: %s" % db_obj.id)
        db_obj.delete()

    def do_volumes_sync(self):
        db_objects = models.Volume.objects.all()
        os_objects = osapi.CinderAPI.create().get_volumes()
        os_objects = [os_obj.to_dict() for os_obj in os_objects]

        LOG.info("Start to do volumes syncing ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj['id'],
                  create_db_fn=self._create_volume,
                  update_db_fn=self._update_volume,
                  remove_db_fn=self._remove_volume)

    def _convert_volume_from_os2db(self, db_obj, os_obj):
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

        # db_obj.user_id
        # db_obj.user_name
        # db_obj.tenant_id
        # db_obj.tenant_name

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
        db_obj.created_at = os_obj.get('created_at')
        db_obj.updated_at = os_obj.get('updated_at')

    def _create_volume(self, os_obj):
        LOG.info("Create a new volume: %s" % os_obj.get('id'))
        db_obj = models.Volume()
        self._convert_volume_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_volume(self, db_obj, os_obj):
        LOG.info("Update existed volume: %s" % db_obj.id)
        self._convert_volume_from_os2db(db_obj, os_obj)
        # update to db:
        db_obj.save()

    def _remove_volume(self, db_obj):
        LOG.info("Remove unknown volume: %s" % db_obj.id)
        db_obj.delete()


# Network/Subnet/Port
class NetworkSyncer(Syncer):

    def do(self):
        self.do_networks_sync()
        self.do_ports_sync()
        # TODO:
        # self.do_networks_total_interface_sync()

    def do_networks_sync(self):
        db_objects = models.Network.objects.all()
        os_objects = osapi.NeutronAPI.create().get_networks()

        LOG.info("Start to do networks syncing ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj.id),
                  create_db_fn=self._create_network,
                  update_db_fn=self._update_network,
                  remove_db_fn=self._remove_network)

    def _convert_network_from_os2db(self, db_obj, os_obj):
        """OpenStack network dict:
        {
            'id': '275d3a55-bb1c-41a5-bc41-d1b286681e58',
            'name': 'stringasdfs',
            'tenant_id': 'a0e1d03c2aa34b538f2bb420542dfb5e',
            'admin_state_up': True,
            'mtu': 1450,
            'status': 'ACTIVE',
            'subnets': ['ecb07b17-232b-4c0f-80c6-96d4ccf67db4'],
            'shared': False,
            'availability_zone_hints': [],
            'availability_zones': ['nova'],
            'ipv4_address_scope': None,
            'ipv6_address_scope': None,
            'router:external': False,
            'description': '',
            'port_security_enabled': True,
            'tags': [],
            'created_at': '2021-11-02T03:48:58Z',
            'updated_at': '2021-11-02T03:48:59Z',
            'revision_number': 2,
            'project_id': 'a0e1d03c2aa34b538f2bb420542dfb5e',
            'provider:network_type': 'vxlan',
            'provider:physical_network': None,
            'provider:segmentation_id': 439
        }

        subnet to dict:
        {
            'id': '00597457-455a-42cb-8312-4dec9d9f64d2',
            'name': 'stringassd',
            'tenant_id': '752df3ea70724f44acc088a0f0313579',
            'network_id': '11267a42-57a2-483d-9593-296e28e64662',
            'ip_version': 4,
            'subnetpool_id': None,
            'enable_dhcp': True,
            'ipv6_ra_mode': None,
            'ipv6_address_mode': None,
            'gateway_ip': '10.22.36.1',
            'cidr': '10.22.36.0/24',
            'allocation_pools': [{'start': '10.22.36.2', 'end': '10.22.36.254'}],
            'host_routes': [],
            'dns_nameservers': [],
            'description': '',
            'service_types': [],
            'tags': [],
            'created_at': '2021-11-09T07:26:20Z',
            'updated_at': '2021-11-09T07:26:20Z',
            'revision_number': 0,
            'project_id': '752df3ea70724f44acc088a0f0313579'
        }
        """
        db_obj.id = os_obj.get('id')
        db_obj.os_network_id = os_obj.get('id')
        # TODO: subnets may empty!
        db_obj.os_subnet_id = os_obj.get('subnets')[0]

        subnet = osapi.NeutronAPI.create().get_subnet(db_obj.os_subnet_id)
        db_obj.cidr = subnet.get('cidr')
        # db_obj.tenants =

        db_obj.name = os_obj.get('name')
        # db_obj.total_interface =
        db_obj.vlan_id = os_obj.get('provider:segmentation_id')
        # db_obj.category =
        db_obj.is_shared = os_obj.get('shared')

        # db_obj.creater

        db_obj.created = os_obj.get('created_at')
        db_obj.modified = os_obj.get('updated_at')

    def _create_network(self, os_obj):
        LOG.info("Create a new network: %s" % os_obj.get('id'))
        db_obj = models.Network()
        self._convert_network_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_network(self, db_obj, os_obj):
        LOG.info("Update existed network: %s" % db_obj.id)
        self._convert_network_from_os2db(db_obj, os_obj)
        # update to db:
        db_obj.save()

    def _remove_network(self, db_obj):
        LOG.info("Remove unknown network: %s" % db_obj.id)
        db_obj.delete()

    def do_ports_sync(self):
        db_objects = models.Port.objects.all()
        os_objects = osapi.NeutronAPI.create().get_ports()

        LOG.info("Start to do network ports syncing ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj.id),
                  create_db_fn=self._create_network_port,
                  update_db_fn=self._update_network_port,
                  remove_db_fn=self._remove_network_port)

    def _convert_port_from_os2db(self, db_obj, os_obj):
        """OpenStack port dict:
        {
            'id': '0779769c-3420-42e7-aecc-3faa69c9d285',
            'name': '',
            'network_id': '92a1cbed-a8e7-4c67-aaab-76fa67b6ea5f',
            'tenant_id': '752df3ea70724f44acc088a0f0313579',
            'mac_address': 'fa:16:3e:52:66:81',
            'admin_state_up': True,
            'status': 'ACTIVE',
            'device_id': 'b8a5030a-06a7-4f8c-a3b6-723a1f92c35f',
            'device_owner': 'compute:nova',
            'fixed_ips': [{'subnet_id': '221e5f89-8000-4bdc-b03b-099b6dee910c', 'ip_address': '10.20.30.222'}],
            'allowed_address_pairs': [],
            'extra_dhcp_opts': [],
            'security_groups': ['ecd4e25a-e706-491e-9504-3e0e6b46faa7'],
            'description': '',
            'binding:vnic_type': 'normal',
            'binding:profile': {},
            'binding:host_id': 'control',
            'binding:vif_type': 'ovs',
            'binding:vif_details': {'connectivity': 'l2', 'port_filter': True, 'ovs_hybrid_plug': True, 'datapath_type': 'system', 'bridge_name': 'br-int'},
            'port_security_enabled': True,
            'tags': [],
            'created_at': '2021-11-15T02:54:25Z',
            'updated_at': '2021-11-19T11:47:42Z',
            'revision_number': 8,
            'project_id': '752df3ea70724f44acc088a0f0313579'
        }
        """
        db_obj.id = os_obj.get('id')
        db_obj.os_port_id = os_obj.get('id')
        # network -> TODO: network may need exist first!
        db_obj.network_id = os_obj.get('network_id')
        db_obj.name = os_obj.get('name')
        db_obj.ip_address = os_obj.get('fixed_ips', [])[0].get('ip_address')
        db_obj.mac_address = os_obj.get('mac_address')
        # db_obj.is_external
        db_obj.created = os_obj.get('created_at')
        db_obj.modified = os_obj.get('updated_at')

    def _create_network_port(self, os_obj):
        LOG.info("Create a network port: %s" % os_obj.get('id'))
        db_obj = models.Port()
        self._convert_port_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_network_port(self, db_obj, os_obj):
        LOG.info("Update existed network port: %s" % db_obj.id)
        self._convert_port_from_os2db(db_obj, os_obj)
        # update to db:
        db_obj.save()

    def _remove_network_port(self, db_obj):
        LOG.info("Remove unknown network port: %s" % db_obj.id)
        db_obj.delete()

class FlavorSyncer(Syncer):

    def do(self):
        self.do_flavors_sync()

    def do_flavors_sync(self):
        db_objects = models.Flavor.objects.all()
        os_objects = osapi.NovaAPI.create().get_flavors()
        os_objects = [os_obj.to_dict() for os_obj in os_objects]

        LOG.info("Start to do flavors sync ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj.id),
                  create_db_fn=self._create_flavor,
                  update_db_fn=self._update_flavor,
                  remove_db_fn=self._remove_flavor)

    def _convert_flavor_from_os2db(self, db_obj, os_obj):
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
                {'rel': 'self', 'href': 'http://10.210.8.177:8774/v2.1/flavors/4512c284-ba72-4e74-bc8a-f27c4e3a706e'},
                {'rel': 'bookmark', 'href': 'http://10.210.8.177:8774/flavors/4512c284-ba72-4e74-bc8a-f27c4e3a706e'}
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

        flavor_access = osapi.NovaAPI.create().get_flavor_access(db_obj.id)
        if flavor_access:
            db_obj.creator_id = flavor_access[0].get('tenant_id')
        db_obj.deleted = 0
        # db_obj.update_time =

    def _create_flavor(self, os_obj):
        LOG.info("Create a new flavor: %s" % os_obj.get('id'))
        db_obj = models.Flavor()
        self._convert_flavor_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_flavor(self, db_obj, os_obj):
        LOG.info("Update existed flavor: %s" % db_obj.id)
        self._convert_flavor_from_os2db(db_obj, os_obj)
        # update to db:
        db_obj.save()

    def _remove_flavor(self, db_obj):
        LOG.info("Remove unknown flavor: %s" % db_obj.id)
        db_obj.save()


# Instance
class InstanceSyncer(Syncer):

    def do(self):
        self.do_instances_sync()

    def do_instances_sync(self):
        db_objects = models.Instance.objects.all()
        os_objects = osapi.NovaAPI.create().get_servers()
        os_objects = [os_obj.to_dict() for os_obj in os_objects]

        LOG.info("Start to do instances sync ...")

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: str(obj.id),
                  create_db_fn=self._create_instance,
                  update_db_fn=self._update_instance,
                  remove_db_fn=self._remove_instance)

    def _convert_instance_from_os2db(self, db_obj, os_obj):
        """OpenStack instance dict:
        {
            'id': '30a9c89f-2d43-45e0-b499-94c5bf70389c',
            'name': 'qwer-2',
            'status': 'ACTIVE',
            'tenant_id': '752df3ea70724f44acc088a0f0313579',
            'user_id': 'f4e124ef1eea4ad8bf3c6e0983275dad',
            'metadata': {},
            'hostId': 'ff468d616ca468fbb7b7be7d2bd2857a1dd62a50fece17d5cf15dccb',
            'image': '',
            'flavor': {'vcpus': 1, 'ram': 1024, 'disk': 10, 'ephemeral': 0, 'swap': 0, 'original_name': '1c1g10g', 'extra_specs': {}},
            'created': '2021-11-11T09:02:16Z',
            'updated': '2021-11-11T09:02:31Z',
            'addresses': {'thw-net': [{'version': 4, 'addr': '10.10.1.195', 'OS-EXT-IPS:type': 'fixed', 'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:f7:d9:62'}]},
            'accessIPv4': '',
            'accessIPv6': '',
            'links': [{'rel': 'self', 'href': 'http://10.210.8.177:8774/v2.1/servers/30a9c89f-2d43-45e0-b499-94c5bf70389c'}, {'rel': 'bookmark', 'href': 'http://10.210.8.177:8774/servers/30a9c89f-2d43-45e0-b499-94c5bf70389c'}],
            'OS-DCF:diskConfig': 'MANUAL',
            'progress': 0,
            'OS-EXT-AZ:availability_zone': 'nova',
            'config_drive': '',
            'key_name': None,
            'OS-SRV-USG:launched_at': '2021-11-11T09:02:31.000000',
            'OS-SRV-USG:terminated_at': None,
            'OS-EXT-SRV-ATTR:host': 'control',
            'OS-EXT-SRV-ATTR:instance_name': 'instance-00000010',
            'OS-EXT-SRV-ATTR:hypervisor_hostname': 'control',
            'OS-EXT-SRV-ATTR:reservation_id': 'r-sz2ca9ml',
            'OS-EXT-SRV-ATTR:launch_index': 1,
            'OS-EXT-SRV-ATTR:hostname': 'qwer-2',
            'OS-EXT-SRV-ATTR:kernel_id': '',
            'OS-EXT-SRV-ATTR:ramdisk_id': '',
            'OS-EXT-SRV-ATTR:root_device_name': '/dev/vda',
            'OS-EXT-SRV-ATTR:user_data': 'I2Nsb3VkLWNvbmZpZwpjaHBhc3N3ZDoKICAgbGlzdDogfAogICAgICAgcm9vdDpAMTIzNHF3ZXIKICAgZXhwaXJlOiBmYWxzZQpzc2hfcHdhdXRoOiB0cnVl',
            'OS-EXT-STS:task_state': None,
            'OS-EXT-STS:vm_state': 'active',
            'OS-EXT-STS:power_state': 1,
            'os-extended-volumes:volumes_attached': [{'id': '8b480305-1c74-4bb8-8d88-b94ed5640864', 'delete_on_termination': True}],
            'locked': False,
            'description': 'qwer',
            'tags': [],
            'host_status': 'UP',
            'security_groups': [{'name': 'default'}]
        }

        'image': {
            'id': '60dadf62-5ca9-425c-9ab6-77783479b63c',
            'links': [{'rel': 'bookmark', 'href': 'http://10.210.8.177:8774/images/60dadf62-5ca9-425c-9ab6-77783479b63c'}]
        },
        """
        db_obj.id = os_obj.get('id')
        db_obj.name = os_obj.get('name')
        # db_obj.flavor =
        # db_obj.flavor_id =

        # db_obj.ip_intranet =
        # db_obj.ip_internet =

        # db.updater_id =
        # db.updater_name =
        db_obj.update_time = os_obj.get('updated')
        db_obj.deleted = 0
        db_obj.status = os_obj.get('status')

        db_obj.tenant_id = os_obj.get('tenant_id')
        # db_obj.tenant_name

        # db_obj.admin_password

        # db_obj.keypair_id =
        db_obj.keypair_name = os_obj.get('key_name')
        db_obj.project_id = os_obj.get('tenant_id')

        # db_obj.os_type =

        # db_obj.creator_id
        # db_obj.creator_name

        db_obj.image_id = os_obj.get('image', {}).get('id')

    def _create_instance(self, os_obj):
        LOG.info("Create a new instance: %s" % os_obj.get('id'))
        db_obj = models.Instance()
        self._convert_instance_from_os2db(db_obj, os_obj)
        # save to db:
        db_obj.save()

        # sync instance ports:
        self._do_sync_instance_ports(db_obj.id)

    def _update_instance(self, db_obj, os_obj):
        LOG.info("Update existed instance: %s" % db_obj.id)
        self._convert_instance_from_os2db(db_obj, os_obj)
        # update to db:
        db_obj.save()

        # sync instance ports:
        self._do_sync_instance_ports(db_obj.id)

    def _remove_instance(self, db_obj):
        LOG.info("Remove unknown instance: %s" % db_obj.id)
        # remove instance ports first
        for db_port in models.InstancePort.objects.get(server_id=db_obj.id):
            LOG.info("Remove unknown instance: %s port: %s" % (db_obj.id, db_port.id))
            db_port.delete()
        # remove instance from db:
        db_obj.delete()

    def _convert_instance_port_from_os2db(self, server_id, db_obj, os_obj):
        """OpenStack Instance Interface dict:
        {
            'net_id': '92a1cbed-a8e7-4c67-aaab-76fa67b6ea5f',
            'port_id': '0779769c-3420-42e7-aecc-3faa69c9d285',
            'mac_addr': 'fa:16:3e:52:66:81',
            'port_state': 'ACTIVE',
            'fixed_ips': [{
                'subnet_id': '221e5f89-8000-4bdc-b03b-099b6dee910c',
                'ip_address': '10.20.30.222'
            }]
        }
        """
        db_obj.id = os_obj.get('port_id')
        db_obj.server_id = server_id
        db_obj.port_id = os_obj.get('port_id')
        # db_obj.created
        # db_obj.modified

    def _do_sync_instance_ports(self, server_id):
        db_objects = models.InstancePort.objects(server_id=server_id)
        os_objects = osapi.NovaAPI.create().get_server_interfaces(server_id)
        os_objects = [os_obj.to_dict() for os_obj in os_objects]

        LOG.info("Start to syncing ports of instance: %s ..." % server_id)

        def _create_instance_port(os_obj):
            LOG.info("Create instance: %s port: %s" % (server_id, os_obj.get('port_id')))
            db_obj = models.InstancePort()
            self._convert_instance_port_from_os2db(server_id, db_obj, os_obj)
            # save to db:
            db_obj.save()

        def _update_instance_port(db_obj, os_obj):
            LOG.info("Update existed instance: %s port: %s" % (server_id, db_obj.id))
            self._convert_instance_from_os2db(db_obj, os_obj)
            # update to db:
            db_obj.save()

        def _remove_instance_port(db_obj):
            LOG.info("Remove unknown instance: %s port: %s" % (server_id, db_obj.id))
            db_obj.delete()

        _alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: obj.id,
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_instance_port,
                  update_db_fn=_update_instance_port,
                  remove_db_fn=_remove_instance_port)


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
