
import logging

from sync.tasks import network as network_tasks

from . import base

LOG = logging.getLogger(__name__)


class NetworkEndpoint(base.NotificationEndpoint):
    """Network Notification Process Endpoint."""

    event_types = [
        'network.*',
        'subnet.*',
        'port.*',
    ]

    @staticmethod
    def _get_network_id(payload):
        net_id = payload.get('network_id', None)
        if not net_id:
            net_id = payload.get('network', {}).get('id')
        return net_id

    @staticmethod
    def _get_port_id(payload):
        port_id = payload.get('id', None)
        if not port_id:
            port_id = payload.get('port', {}).get('id')
        if not port_id:
            port_id = payload.get('port_id', None)
        return port_id

    def process(self, publisher_id, event_type, payload):
        LOG.info('Start to process notification: %s ...' % event_type)

        resource = event_type.split('.')[0]

        if resource in ['network', 'subnet']:
            network_id = self._get_network_id(payload)
            if not network_id:
                LOG.error("Failed to got `network_id` from notification: %s payload: %s"
                          % (event_type, payload))
                return

            # delete network
            if event_type in ['network.delete.end']:
                LOG.info("Delete network: %s" % network_id)
                network_tasks.sync_network_delete.delay(network_id)
                return

            # create network
            if event_type in ['network.create.end', 'network.create.error']:
                LOG.info("Create network: %s" % network_id)
                network_tasks.sync_network_create.delay(network_id)
                return

            # update network
            LOG.info("Update network: %s" % network_id)
            network_tasks.sync_network_update.delay(network_id)

        if resource == 'port':
            port_id = self._get_port_id(payload)
            if not port_id:
                LOG.error("Failed to got `port_id` from notification: %s payload: %s"
                          % (event_type, payload))
                return

            # delete port
            if event_type in ['port.delete.end']:
                LOG.info("Delete port: %s" % port_id)
                network_tasks.sync_port_delete.delay(port_id)
                return

            # create port
            if event_type in ['port.create.end', 'port.create.error']:
                LOG.info("Create port: %s" % port_id)
                network_tasks.sync_port_create.delay(port_id)
                return

            # update port
            LOG.info("Update port: %s" % port_id)
            network_tasks.sync_port_update.delay(port_id)

