from django.conf import settings
from ncclient import manager, operations
import openstack


openstack.enable_logging(debug=settings.DEBUG)


class OpenstackMixin:

    @staticmethod
    def get_conn():
        return openstack.connect()


class NetConf:
    OPERATION_CREATE = 'create'
    OPERATION_DELETE = 'delete'
    OPERATION_MERGE = 'merge'
    xmlns = "http://www.h3c.com/netconf/data:1.0"
    _xmlns_xc = "urn:ietf:params:xml:ns:netconf:base:1.0"
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

    def create_static_routing(self, conn):
        return self.edit_static_routing(conn, self.OPERATION_CREATE)

    def delete_static_routing(self, conn):
        return self.edit_static_routing(conn, self.OPERATION_DELETE)

    def edit_static_routing(self, conn, operation):
        xml = f'''<config xmlns:xc="{ self._xmlns_xc }">
            <StaticRoute xmlns="{ self.xmlns }">
                <Ipv4StaticRouteConfigurations>
                    <RouteEntry xc:operation="{ operation }">
                        <DestVrfIndex>{ self.dest_vrf_index }</DestVrfIndex>
                        <DestTopologyIndex>{ self.dest_topology_index }</DestTopologyIndex>
                        <Ipv4Address>{ self.destination_subnet.network_address }</Ipv4Address>
                        <Ipv4PrefixLength>{ self.destination_subnet.prefixlen }</Ipv4PrefixLength>
                        <NexthopVrfIndex>{ self.next_hop_vrf_index }</NexthopVrfIndex>
                        <NexthopIpv4Address>{ self.ip_next_hop_address.ip }</NexthopIpv4Address>
                        <IfIndex>{ self.if_index }</IfIndex>
                    </RouteEntry>
                </Ipv4StaticRouteConfigurations>
            </StaticRoute>
        </config>'''
        try:
            ret = conn.edit_config(target=self.target_running, config=xml)
        except operations.rpc.RPCError as exc:
            return False, str(exc)
        else:
            return ret.ok, ret.errors
