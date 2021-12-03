from django.conf import settings
from ncclient import manager
import openstack


openstack.enable_logging(debug=settings.DEBUG)


class OpenstackMixin:

    @staticmethod
    def get_conn():
        return openstack.connect()


class NetConfMixin:
    xmlns = "http://www.h3c.com/netconf/data:1.0"
    target_running = 'running'
    max_rule_id = 50000
    timeout = 30
    device_name = 'h3c'
    is_allowed = True

    @classmethod
    def get_netconf_conn(cls):
        return manager.connect(
            host=settings.FIREWALL_HOST,
            port=settings.FIREWALL_PORT,
            username=settings.FIREWALL_USERNAME,
            password=settings.FIREWALL_PASSWORD,
            hostkey_verify=False,
            look_for_keys=False,
            manager_params={'timeout': cls.timeout},
            device_params={'name': cls.device_name})

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
