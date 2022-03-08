
import logging

from celery import shared_task
from djapp import models

from . import base

LOG = logging.getLogger(__name__)


def _convert_port_from_os2db(db_obj, os_obj, creator_id=None):
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

    if creator_id:
        db_obj.creater_id = creator_id
    else:
        db_obj.creater_id = -1

    db_obj.created = os_obj.get('created_at')
    db_obj.modified = os_obj.get('updated_at')


def _do_network_ports_sync(network_id, creator_id=None):
    db_objects = models.Port.objects.filter(network_id=network_id)
    os_objects = base.neutron_api().get_ports(network_id=network_id)

    LOG.info("Start to syncing Ports of Network: %s ..." % network_id)

    def _create_network_port(os_obj):
        LOG.info("Create a network: %s port: %s" % (network_id, os_obj.get('id')))
        db_obj = models.Port()
        _convert_port_from_os2db(db_obj, os_obj, creator_id)
        # save to db:
        db_obj.save()

    def _update_network_port(db_obj, os_obj):
        LOG.info("Update existed network: %s port: %s" % (network_id, db_obj.id))
        _convert_port_from_os2db(db_obj, os_obj, creator_id)
        # update to db:
        db_obj.save()

    def _remove_network_port(db_obj):
        LOG.info("Remove unknown network: %s port: %s" % (network_id, db_obj.id))
        db_obj.delete()

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_network_port,
                  update_db_fn=_update_network_port,
                  remove_db_fn=_remove_network_port)


def _convert_network_from_os2db(db_obj, os_obj, creator_id=None):
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

    subnets = os_obj.get('subnets')
    if not subnets:
        raise base.SyncPass("Network subnets is empty!")

    db_obj.os_subnet_id = subnets[0]

    subnet = base.neutron_api().show_subnet(db_obj.os_subnet_id)
    cidr = subnet.get('cidr')
    if not cidr:
        raise base.SyncPass("CIDR is empty!")
    db_obj.cidr = cidr

    cidr_num = int(cidr.split('/')[1])
    num_addresses = pow(2, 32 - cidr_num)
    db_obj.total_interface = num_addresses - 2

    # db_obj.tenants =
    db_obj.category = models.Network.CATEGORY_CLUSTER

    db_obj.name = os_obj.get('name')
    db_obj.vlan_id = os_obj.get('provider:segmentation_id')
    db_obj.is_shared = os_obj.get('shared')

    if creator_id:
        db_obj.creater_id = creator_id
    else:
        db_obj.creater_id = -1

    # add project_id:
    db_obj.project_id = os_obj.get('tenant_id')

    db_obj.created = os_obj.get('created_at')
    db_obj.modified = os_obj.get('updated_at')


def _clear_network_port(db_obj):
    for port_db_obj in db_obj.port_set.all():
        port_db_obj.delete()


@shared_task
def do_networks_sync(creator_id=None):
    # filter by user_id and project_id
    db_objects = models.Network.objects.filter()
    os_objects = base.neutron_api().get_networks()

    LOG.info("Start to sync all networks ...")

    def _remove_network(db_obj):
        LOG.info("Remove unknown network: %s" % db_obj.id)
        # remove network ports first:
        _clear_network_port(db_obj)
        # remove network db:
        db_obj.delete()

    def _create_network(os_obj):
        LOG.info("Create a new network: %s" % os_obj.get('id'))
        db_obj = models.Network()
        _convert_network_from_os2db(db_obj, os_obj, creator_id)
        # save to db:
        db_obj.save()

        # sync network ports:
        _do_network_ports_sync(db_obj.id, creator_id)

    def _update_network(db_obj, os_obj):
        LOG.info("Update existed network: %s" % db_obj.id)
        _convert_network_from_os2db(db_obj, os_obj, creator_id)
        # update to db:
        db_obj.save()

        # sync network ports:
        _do_network_ports_sync(db_obj.id, creator_id)

    base.alg_sync(db_objects=db_objects,
                  db_obj_key_fn=lambda obj: str(obj.id),
                  os_objects=os_objects,
                  os_obj_key_fn=lambda obj: obj.get('id'),
                  create_db_fn=_create_network,
                  update_db_fn=_update_network,
                  remove_db_fn=_remove_network)


def db_get_port(port_id):
    try:
        return models.Port.objects.get(pk=port_id)
    except models.Port.DoesNotExist:
        return None


def db_get_network(network_id):
    try:
        return models.Network.objects.get(pk=network_id)
    except models.Network.DoesNotExist:
        return None


@shared_task
def sync_port_delete(port_id):
    db_obj = db_get_port(port_id)
    if db_obj is None:
        LOG.warning("Could not found port %s in db, pass to update..."
                    % port_id)
        return

    # delete port
    db_obj.delete()


@shared_task
def sync_port_create(port_id):
    db_obj = db_get_port(port_id)
    if db_obj:
        LOG.warning("Port %s already exist, pass to create..." % port_id)
        return

    os_obj = base.neutron_api().show_port(port_id=port_id)
    if not os_obj:
        LOG.error("Unknown port: %s in openstack..." % port_id)
        return

    # create port
    db_obj = models.Port()
    _convert_port_from_os2db(db_obj, os_obj)
    db_obj.save()


@shared_task
def sync_port_update(port_id):
    db_obj = db_get_port(port_id)
    if db_obj is None:
        LOG.warning("Could not found port %s in db, pass to update..."
                    % port_id)
        return

    os_obj = base.neutron_api().show_port(port_id=port_id)
    if not os_obj:
        LOG.error("Unknown port: %s in openstack, will remove residual db data..." % port_id)
        db_obj.delete()
        return

    # Update existed info
    _convert_port_from_os2db(db_obj, os_obj)
    db_obj.save()


@shared_task
def sync_network_delete(network_id):
    db_obj = db_get_network(network_id)
    if db_obj is None:
        LOG.warning("Could not found network %s in db, pass to delete..."
                    % network_id)
        return

    # clear network ports
    _clear_network_port(db_obj)
    # delete network
    db_obj.delete()


@shared_task
def sync_network_create(network_id):
    db_obj = db_get_network(network_id)
    if db_obj:
        LOG.warning("Network %s already exist, pass to create..."
                    % network_id)
        return

    os_obj = base.neutron_api().show_network(network_id=network_id)
    if not os_obj:
        LOG.error("Unknown network %s in openstack..." % network_id)
        return

    # create network
    db_obj = models.Network()
    _convert_network_from_os2db(db_obj, os_obj)
    db_obj.save()

    # sync network ports
    _do_network_ports_sync(network_id)


@shared_task
def sync_network_update(network_id):
    db_obj = db_get_network(network_id)
    if db_obj is None:
        LOG.warning("Could not found network %s in db, pass to update..."
                    % network_id)
        return

    os_obj = base.neutron_api().show_network(network_id=network_id)
    if not os_obj:
        LOG.error("Unknown network %s in openstack, will remove residual db data..." % network_id)
        db_obj.delete()
        return

    # Update existed info
    _convert_network_from_os2db(db_obj, os_obj)
    db_obj.save()

    # sync network ports
    _do_network_ports_sync(network_id)
