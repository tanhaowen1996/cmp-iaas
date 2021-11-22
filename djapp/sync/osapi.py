import os

import keystoneauth1
from keystoneauth1 import loading

from keystoneauth1.identity import v3 as v3_auth
from keystoneauth1 import session as ks_session

from novaclient import client as nova_client
from novaclient import api_versions as nova_api_versions
from glanceclient import client as glance_client
from cinderclient import client as cinder_client
from neutronclient.v2_0 import client as neutron_client


NOVA_API_VERSION = "2.53"
nova_extensions = [ext for ext in
                   nova_client.discover_extensions(NOVA_API_VERSION)
                   if ext.name in ("list_extensions",)]

GLANCE_API_VERSION = "2"
VOLUME_API_VERSION = "3.0"


def _get_session(auth_url, username, password,
                 project_name, user_domain_name, project_domain_name,
                 auth_type='password', insecure=False):
    loader = keystoneauth1.loading.get_plugin_loader(auth_type)
    auth = loader.load_from_options(
        auth_url=auth_url,
        username=username,
        password=password,
        project_name=project_name,
        user_domain_name=user_domain_name,
        project_domain_name=project_domain_name,
    )
    session_loader = keystoneauth1.loading.session.Session()
    keystone_session = session_loader.load_from_options(
        auth=auth, insecure=insecure)
    return keystone_session


def _get_session1(auth_url, username, password,
                  project_name, user_domain_name, project_domain_name):
    auth = v3_auth.Password(
        auth_url=auth_url,
        username=username,
        password=password,
        project_name=project_name,
        user_domain_name=user_domain_name,
        project_domain_name=project_domain_name,
    )
    return ks_session.Session(auth=auth)


def _make_session_from_env():
    return _get_session1(
        auth_url=os.getenv('OS_AUTH_URL'),
        username=os.getenv('OS_USERNAME'),
        password=os.getenv('OS_PASSWORD'),
        project_name=os.getenv('OS_PROJECT_NAME'),
        user_domain_name=os.getenv('OS_USER_DOMAIN_NAME'),
        project_domain_name=os.getenv('OS_PROJECT_DOMAIN_NAME'))


_SESSION = None
_REGION_NAME = None


def _session():
    global _SESSION
    if not _SESSION:
        _SESSION = _make_session_from_env()
    return _SESSION


def _region_name():
    global _REGION_NAME
    if not _REGION_NAME:
        _REGION_NAME = os.getenv('OS_REGION_NAME')
    return _REGION_NAME


def get_project_id():
    return _session().get_project_id()


def get_user_id():
    return _session().get_user_id()


class NovaAPI(object):

    def __init__(self, client=None):
        self.client = client

    @classmethod
    def create(cls,
               session=None, region_name=None,
               endpoint_type='internal', service_type='compute',
               insecure=False, timeout=None):
        if not session:
            session = _session()
        if not region_name:
            region_name = _region_name()
        client = nova_client.Client(
            nova_api_versions.APIVersion(NOVA_API_VERSION),
            session=session,
            insecure=insecure,
            timeout=timeout,
            region_name=region_name,
            endpoint_type=endpoint_type,
            service_type=service_type,
            extensions=nova_extensions)
        return cls(client)

    def get_servers(self, all_tenants=True):
        opts = {
            'all_tenants': all_tenants
        }
        # LOG.info('Fetch Server list...')
        return self.client.servers.list(detailed=True, search_opts=opts)

    def get_server_interfaces(self, instance_id):
        return self.client.servers.interface_list(instance_id)

    def get_flavors(self):
        return self.client.flavors.list()

    def get_flavor_access(self, flavor_id):
        return self.client.flavor_access.list(flavor=flavor_id)

    def get_keypairs(self):
        return self.client.keypairs.list()

    def get_user_keypairs(self, user_id):
        return self.client.keypairs.list(user_id)


class GlanceAPI(object):

    def __init__(self, client=None):
        self.client = client

    @classmethod
    def create(cls,
               session=None, region_name=None,
               service_type='image', interface='internal'):
        if not session:
            session = _session()
        if not region_name:
            region_name = _region_name()
        client = glance_client.Client(GLANCE_API_VERSION,
                                      session=session,
                                      service_type=service_type,
                                      region_name=region_name,
                                      interface=interface)
        return cls(client)

    def get_images(self):
        return self.client.images.list()


class CinderAPI(object):

    def __init__(self, client):
        self.client = client

    @classmethod
    def create(cls,
               session=None, region_name=None,
               service_type='volumev3', interface='internal'):
        if not session:
            session = _session()
        if not region_name:
            region_name = _region_name()
        client = cinder_client.Client(VOLUME_API_VERSION,
                                      session=session,
                                      region_name=region_name,
                                      service_type=service_type,
                                      interface=interface)
        return cls(client)

    def get_volumes(self, all_tenants=True):
        return self.client.volumes.list(detailed=True, search_opts={
            "all_tenants": all_tenants
        })

    def get_volume_types(self):
        return self.client.volume_types.list()


class NeutronAPI(object):

    def __init__(self, client):
        self.client = client

    @classmethod
    def create(cls,
               session=None, region_name=None,
               service_type='network', interface='internal',
               insecure=False):
        if not session:
            session = _session()
        if not region_name:
            region_name = _region_name()
        client = neutron_client.Client(session=session,
                                       service_type=service_type,
                                       interface=interface,
                                       region_name=region_name,
                                       insecure=insecure)
        return cls(client)

    def get_networks(self):
        return self.client.list_networks(retrieve_all=True).get('networks', [])

    def get_subnets(self):
        return self.client.list_subnets(retrieve_all=True).get('subnets', [])

    def get_subnet(self, subnet_id):
        return self.client.show_subnet(subnet_id)

    def get_ports(self):
        return self.client.list_ports(retrieve_all=True).get('ports', [])


if __name__ == '__main__':

    def test_image():
        print("List Images:")
        glance_api = GlanceAPI.create()
        for image in glance_api.get_images():
            print(image)
        print('----------------------------------')


    def test_volume():
        print("List Volumes:")
        cinder_api = CinderAPI.create()
        # for volume in cinder_api.get_volumes():
        #    print(volume)

        """
        volume = cinder_api.get_volumes()[0]
        print('type: %s' % type(volume))
        print('dir: %s' % dir(volume))
        print('----------------------------------')
        print('to_dict: %s' % volume.to_dict())
        """
        for volume_type in cinder_api.get_volume_types():
            print(volume_type.to_dict())

    def test_instance():
        nova_api = NovaAPI.create()

        """
        print("List Flavors:")
        for flavor in nova_api.get_flavors():
            print(flavor.to_dict())
        print('----------------------------------')
        """

        """
        print("List Instances:")
        for instance in nova_api.get_servers():
            print(instance.to_dict())
        print('----------------------------------')
        """

        """
        print("List Key Pairs:")
        for key_pair in nova_api.get_keypairs():
            print(key_pair)
        print('----------------------------------')
        """

        interfaces = nova_api.get_server_interfaces('b8a5030a-06a7-4f8c-a3b6-723a1f92c35f')
        for interface in interfaces:
            print(interface.to_dict())

    def test_network():
        neutron_api = NeutronAPI.create()

        print("List Networks:")
        for network in neutron_api.get_networks():
            print(network)
        print('----------------------------------')

        print("List Subnets:")
        for subnet in neutron_api.get_subnets():
            print("", subnet)
        print('----------------------------------')

        print("List Ports:")
        for port in neutron_api.get_ports():
            print("", port)
        print('----------------------------------')

    # test_image()
    test_instance()
    # test_volume()
    # test_network()

    def test_keypair():
        nova_api = NovaAPI.create()

        keypair = nova_api.get_keypairs()[0]

        print('type: %s' % type(keypair))
        print('dir: %s' % dir(keypair))
        print('dict: %s' % keypair.to_dict())
        print('--------------')
        print('name: %s' % keypair.name)
        print('id: %s' % keypair.id)
        print('fingerprint: %s' % keypair.fingerprint)
        print('public_key: %s' % keypair.public_key)
        print('type: %s' % keypair.type)


    # test_keypair()

    # print('project_id: %s' % _session().get_project_id())
