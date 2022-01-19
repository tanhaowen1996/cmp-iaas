
import logging

from celery import shared_task
from djapp import models
from sync import osapi

from . import base


LOG = logging.getLogger(__name__)


def _convert_instance_from_os2db(db_obj, os_obj, user=None, project=None):
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

    flavor = os_obj.get('flavor', {})
    flavor_name = flavor.get('original_name')

    # get flavor detail info:
    os_flavor = base.nova_api().get_flavor_by_name(flavor_name)
    if not os_flavor:
        LOG.warning("get flavor by name: %s failed!" % flavor_name)
    else:
        db_obj.flavor_id = os_flavor.get('id')

    db_obj.flavor = flavor_name

    # db_obj.ip_intranet =
    # db_obj.ip_internet =

    db_obj.status = os_obj.get('status')

    if project:
        db_obj.tenant_id = project.get('tenantId')
        db_obj.tenant_name = project.get('tenantName')

    # db_obj.admin_password

    user_id = os_obj.get('user_id')
    key_name = os_obj.get('key_name')
    if key_name:
        keypair = base.nova_api().get_user_keypair_by_name(
            user_id=user_id, name=key_name)
        if keypair:
            db_obj.keypair_id = keypair.get('id')
        else:
            LOG.warning("Get keypair: %s for user: %s failed..." % (key_name, user_id))

    db_obj.keypair_name = key_name

    db_obj.project_id = os_obj.get('tenant_id')

    image = os_obj.get('image', {})
    if isinstance(image, dict):
        image_id = image.get('id')
        # get image detail info:
        image = base.glance_api().get_image(image_id)
        if image:
            db_obj.os_type = image.get('os_type')
        else:
            LOG.warning("Get image: %s failed..." % image_id)
        db_obj.image_id = image_id

    # // db.updater_id =
    # // db.updater_name =
    # // db_obj.creator_id
    # // db_obj.creator_name
    # db_obj.update_time = os_obj.get('updated')
    # db_obj.create_time = os_obj.get('created')
    db_obj.deleted = 1 if db_obj.status == 'DELETED' else 0


def _clear_instance_port_by_id(instance_id):
    for port_obj in models.InstancePort.objects.filter(server_id=instance_id):
        port_obj.delete()


@shared_task
def do_instances_sync(user=None, project=None):
    project_id = project.get('id') if project else osapi.get_project_id()

    db_objects = models.Instance.objects.filter(project_id=project_id)
    os_objects = base.nova_api().get_servers(project_id=project_id)
    os_objects = [os_obj.to_dict() for os_obj in os_objects]

    LOG.info("Start to syncing Instances for project: %s..." % project_id)

    def _remove_instance(db_obj):
        LOG.info("Remove unknown instance: %s" % db_obj.id)
        # remove instance ports db first
        _clear_instance_port_by_id(db_obj.id)
        # remove instance db:
        db_obj.delete()

    def _create_instance(os_obj):
        LOG.info("Create a new instance: %s" % os_obj.get('id'))
        db_obj = models.Instance()
        _convert_instance_from_os2db(db_obj, os_obj, user, project)
        # save to db:
        db_obj.save()

        # sync instance ports:
        _do_sync_instance_ports(db_obj.id)

    def _update_instance(db_obj, os_obj):
        LOG.info("Update existed instance: %s" % db_obj.id)
        _convert_instance_from_os2db(db_obj, os_obj, user, project)
        # update to db:
        db_obj.save()

        # sync instance ports:
        _do_sync_instance_ports(db_obj.id)

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_instance,
                  update_db_fn=_update_instance,
                  remove_db_fn=_remove_instance)


def _convert_instance_port_from_os2db(server_id, db_obj, os_obj):
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


def _do_sync_instance_ports(server_id):
    db_objects = models.InstancePort.objects.filter(server_id=server_id)
    os_objects = base.nova_api().get_server_interfaces(server_id)
    os_objects = [os_obj.to_dict() for os_obj in os_objects]

    LOG.info("Start to syncing Ports of Instance: %s ..." % server_id)

    def _remove_instance_port(db_obj):
        LOG.info("Remove unknown instance: %s port: %s" % (server_id, db_obj.id))
        db_obj.delete()

    def _create_instance_port(os_obj):
        LOG.info("Create instance: %s port: %s" % (server_id, os_obj.get('port_id')))
        db_obj = models.InstancePort()
        _convert_instance_port_from_os2db(server_id, db_obj, os_obj)
        # save to db:
        db_obj.save()

    def _update_instance_port(db_obj, os_obj):
        LOG.info("Update existed instance: %s port: %s" % (server_id, db_obj.id))
        _convert_instance_port_from_os2db(server_id, db_obj, os_obj)
        # update to db:
        db_obj.save()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('port_id'),
                  create_db_fn=_create_instance_port,
                  update_db_fn=_update_instance_port,
                  remove_db_fn=_remove_instance_port)


def db_get_instance(instance_id):
    try:
        return models.Instance.objects.get(pk=instance_id)
    except models.Instance.DoesNotExist:
        return None


@shared_task
def sync_instance_delete(instance_id):
    db_obj = db_get_instance(instance_id)
    if not db_obj:
        LOG.warning("Cloud not found instance %s in db, pass to delete..."
                    % instance_id)
        return
    # clear instance port first
    _clear_instance_port_by_id(instance_id)
    # delete instance
    db_obj.delete()


@shared_task
def sync_instance_create(instance_id):
    db_obj = db_get_instance(instance_id)
    if db_obj:
        LOG.warning("Instance %s already exist, pass to create..."
                    % instance_id)
        return

    os_obj = base.nova_api().show_server(instance_id=instance_id)
    if not os_obj:
        LOG.error("Unknown instance %s in openstack..." % instance_id)
        return

    # create instance
    db_obj = models.Instance()
    _convert_instance_from_os2db(db_obj, os_obj.to_dict())
    db_obj.save()


@shared_task
def sync_instance_update(instance_id):
    db_obj = db_get_instance(instance_id)
    if not db_obj:
        LOG.warning("Could not found instance %s in db, pass to update ..."
                    % instance_id)
        return

    os_obj = base.nova_api().show_server(instance_id=instance_id)
    if not os_obj:
        LOG.error("Unknown instance %s in openstack, will remove residual db data..." % instance_id)
        db_obj.delete()
        return

    # update instance
    _convert_instance_from_os2db(db_obj, os_obj.to_dict())
    db_obj.save()
