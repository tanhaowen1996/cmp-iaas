from django.conf import settings
from django.template import Context, Template
from ncclient import manager, operations
import openstack
import logging


openstack.enable_logging(debug=settings.DEBUG)


logger = logging.getLogger(__package__)


class OpenstackMixin:

    @staticmethod
    def get_conn():
        return openstack.connect()


class NetConf:
    OPERATION_CREATE = 'create'
    OPERATION_DELETE = 'delete'
    OPERATION_MERGE = 'merge'
    xmlns = "http://www.h3c.com/netconf/data:1.0"
    xmlns_xc = "urn:ietf:params:xml:ns:netconf:base:1.0"
    target_running = 'running'
    max_rule_id = 50000
    timeout = 30
    device_name = 'h3c'
    is_allowed = True

    @classmethod
    def get_netconf_conn(cls):
        return manager.connect(
            host=settings.NETCONF_HOST,
            port=settings.NETCONF_PORT,
            username=settings.NETCONF_USERNAME,
            password=settings.NETCONF_PASSWORD,
            hostkey_verify=False,
            look_for_keys=False,
            manager_params={'timeout': cls.timeout},
            device_params={'name': cls.device_name})


class FirewallMixin(NetConf):

    def preset_security_policy_id(self, conn):
        xml = f'''<top xmlns="{ self.xmlns }">
            <SecurityPolicies>
                <GetRules>
                    <Rule>
                        <ID></ID>
                    </Rule>
                </GetRules>
            </SecurityPolicies>
        </top>'''
        ret = conn.get(filter=('subtree', xml))
        id_eles = ret.data.xpath('//n:GetRules/n:Rule/n:ID', namespaces={'n': self.xmlns})
        if id_eles:
            self.id = int(id_eles[-1].text) + 1
            if self.id >= self.max_rule_id:
                raise Exception(f'security policy ipv4 rule id:{ self.id } is out of range')

        else:
            raise Exception('no security policy ipv4 rules, please check device')

    def create_security_policy_rule(self, conn):
        xml = f'''<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="create">
                <SecurityPolicies>
                    <IPv4Rules>
                        <Rule>
                            <ID>{ self.id }</ID>
                            <RuleName>{ self.name }</RuleName>
                            <Action>{ 2 if self.is_allowed else 1 }</Action>
                        </Rule>
                    </IPv4Rules>
                    <IPv4SrcSecZone>
                        <SrcSecZone>
                            <ID>{ self.id }</ID>
                            <SeqNum>1</SeqNum>
                            <IsIncrement>true</IsIncrement>
                            <NameList>
                                <NameItem>{ self.source_network.name }</NameItem>
                            </NameList>
                        </SrcSecZone>
                    </IPv4SrcSecZone>
                    <IPv4DestSecZone>
                        <DestSecZone>
                            <ID>{ self.id }</ID>
                            <SeqNum>1</SeqNum>
                            <IsIncrement>true</IsIncrement>
                            <NameList>
                                <NameItem>{ self.destination_network.name }</NameItem>
                            </NameList>
                        </DestSecZone>
                    </IPv4DestSecZone>
                </SecurityPolicies>
            </top>
        </config>'''
        ret = conn.edit_config(target=self.target_running, config=xml)
        return (ret.ok, ret.errors)

    def delete_security_policy_rule(self, conn):
        xml = f'''<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <SecurityPolicies>
                    <IPv4Rules>
                        <Rule xc:operation="delete">
                            <ID>{ self.id }</ID>
                        </Rule>
                    </IPv4Rules>
                </SecurityPolicies>
            </top>
        </config>'''
        ret = conn.edit_config(target=self.target_running, config=xml)
        return ret.ok, ret.errors


class StaticRoutingNetConfMixin(NetConf):
    dest_vrf_index = 0
    dest_topology_index = 0
    next_hop_vrf_index = 0
    if_index = 0
    xml_template = Template('''<config xmlns:xc="{{ cls.xmlns_xc }}">
    <StaticRoute xmlns="{{ cls.xmlns }}">
        <Ipv4StaticRouteConfigurations xc:operation="{{ operation }}">
            {% for obj in obj_list %}
            <RouteEntry>
                <DestVrfIndex>{{ obj.dest_vrf_index }}</DestVrfIndex>
                <DestTopologyIndex>{{ obj.dest_topology_index }}</DestTopologyIndex>
                <Ipv4Address>{{ obj.destination_subnet.network_address }}</Ipv4Address>
                <Ipv4PrefixLength>{{ obj.destination_subnet.prefixlen }}</Ipv4PrefixLength>
                <NexthopVrfIndex>{{ obj.next_hop_vrf_index }}</NexthopVrfIndex>
                <NexthopIpv4Address>{{ obj.ip_next_hop_address.ip }}</NexthopIpv4Address>
                <IfIndex>{{ obj.if_index }}</IfIndex>
            </RouteEntry>
            {% endfor %}
        </Ipv4StaticRouteConfigurations>
    </StaticRoute>
</config>''')

    def create_static_routing(self, conn):
        return self.edit_static_routing(conn, self.OPERATION_CREATE)

    def delete_static_routing(self, conn):
        return self.edit_static_routing(conn, self.OPERATION_DELETE)

    def edit_static_routing(self, conn, operation):
        xml = self.xml_template.render(Context({
            'cls': self.__class__,
            'operation': operation,
            'obj_list': [self],
        }))
        try:
            ret = conn.edit_config(target=self.target_running, config=xml)
        except operations.rpc.RPCError as exc:
            return False, str(exc)
        else:
            return ret.ok, ret.errors

    @classmethod
    def batch_create_static_routings(cls, conn, obj_list):
        return cls.batch_edit_static_routings(conn, cls.OPERATION_CREATE, obj_list)

    @classmethod
    def batch_delete_static_routings(cls, conn, obj_list):
        return cls.batch_edit_static_routings(conn, cls.OPERATION_DELETE, obj_list)

    @classmethod
    def batch_edit_static_routings(cls, conn, operation, obj_list):
        xml = cls.xml_template.render(Context({
            'cls': cls,
            'operation': operation,
            'obj_list': obj_list,
        }))
        try:
            ret = conn.edit_config(target=cls.target_running, config=xml)
        except operations.rpc.RPCError as exc:
            logger.error(f"netconf edit config:{xml}, result: {exc}")
            return False, str(exc)
        else:
            logger.info(f"netconf edit config:{xml}, result: ok")
            return ret.ok, ret.errors
