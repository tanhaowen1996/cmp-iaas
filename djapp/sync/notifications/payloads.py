
import logging

LOG = logging.getLogger(__name__)


_payload_register = {}


def payload_register(cls):
    global _payload_register
    _payload_register[cls.__name__] = cls
    return cls


class PayloadNotRegistryException(Exception):
    pass


class Payload(object):

    def __init__(self, payload):
        self._object_data = payload.get('nova_object.data', {})

    def get(self, name, default=None):
        return self._object_data.get(name, default)

    def set(self, name, value):
        self._object_data[name] = value

    @staticmethod
    def create(payload_dict):
        name = payload_dict.get('nova_object.name', None)

        cls = _payload_register.get(name, None)
        if not cls:
            msg = "Payload %s not registry, could not been process..." % payload_dict
            LOG.warning(msg)
            raise PayloadNotRegistryException(msg)

        return cls(payload_dict)


@payload_register
class ExceptionPayload(Payload):
    """
    payload:
    {
        "exception": "FlavorDiskTooSmall",
        "exception_message": "The created instance's disk would be too small.",
        "function_name": "_build_resources",
        "module_name": "nova.tests.functional.notification_sample_tests.test_instance",
        "traceback": "Traceback (most recent call last):\n  File \"nova/compute/manager.py\", line ..."
    }
    """

    @property
    def exception(self):
        return self.get('exception')

    @property
    def exception_message(self):
        return self.get('exception_message')

    @property
    def function_name(self):
        return self.get('function_name')

    @property
    def module_name(self):
        return self.get('module_name')

    @property
    def traceback(self):
        return self.get('traceback')


@payload_register
class KeypairPayload(Payload):
    """
    payload:
    {
        "fingerprint": "1e:2c:9b:56:79:4b:45:77:f9:ca:7a:98:2c:b0:d5:3c",
        "name": "my-key",
        "public_key": "ssh-rsa AAAAB...== Generated-by-Nova",
        "type": "ssh",
        "user_id": "fake"
    }
    """

    @property
    def name(self):
        return self.get('name')

    @property
    def type(self):
        return self.get('type')

    @property
    def user_id(self):
        return self.get('user_id')

    @property
    def public_key(self):
        return self.get('public_key')

    @property
    def fingerprint(self):
        return self.get('fingerprint')


@payload_register
class BlockDevicePayload(Payload):
    """
    payload:
    {
        "boot_index": null,
        "delete_on_termination": false,
        "device_name": "/dev/sdb",
        "tag": null,
        "volume_id": "a07f71dc-8151-4e7d-a0cc-cd24a3f11113"
    }
    """

    @property
    def volume_id(self):
        return self.get('volume_id')

    @property
    def boot_index(self):
        return self.get('boot_index')

    @property
    def delete_on_termination(self):
        return self.get('delete_on_termination')

    @property
    def tag(self):
        return self.get('tag')


@payload_register
class FlavorPayload(Payload):
    """
    payload:
    {
        "description": null,
        "disabled": false,
        "ephemeral_gb": 0,
        "extra_specs": {
            "hw:watchdog_action": "disabled"
        },
        "flavorid": "2",
        "is_public": true,
        "memory_mb": 2048,
        "name": "m1.small",
        "projects": null,
        "root_gb": 20,
        "rxtx_factor": 1.0,
        "swap": 0,
        "vcpu_weight": 0,
        "vcpus": 1
    }
    """

    @property
    def id(self):
        return self.get('flavorid')

    @property
    def name(self):
        return self.get('name')

    @property
    def description(self):
        return self.get('description')

    @property
    def disabled(self):
        return self.get('disabled')

    @property
    def is_public(self):
        return self.get('is_public')

    @property
    def memory_mb(self):
        return self.get('memory_mb')

    @property
    def vcpus(self):
        return self.get('vcpus')

    @property
    def root_gb(self):
        return self.get('root_gb')


@payload_register
class IpPayload(Payload):
    """
    payload:
    {
        "address": "192.168.1.3",
        "device_name": "tapce531f90-19",
        "label": "private",
        "mac": "fa:16:3e:4c:2c:30",
        "meta": {},
        "port_uuid": "ce531f90-199f-48c0-816c-13e38010b442",
        "version": 4
    }
    """

    @property
    def port_id(self):
        return self.get('port_uuid')

    @property
    def address(self):
        return self.get('address')

    @property
    def device_name(self):
        return self.get('device_name')

    @property
    def label(self):
        return self.get('label')

    @property
    def mac(self):
        return self.get('mac')

    @property
    def meta(self):
        return self.get('meta')


@payload_register
class InstancePayload(Payload):
    """
    fields = {
        'uuid': fields.UUIDField(),
        'user_id': fields.StringField(nullable=True),
        'tenant_id': fields.StringField(nullable=True),
        'reservation_id': fields.StringField(nullable=True),
        'display_name': fields.StringField(nullable=True),
        'display_description': fields.StringField(nullable=True),
        'host_name': fields.StringField(nullable=True),
        'host': fields.StringField(nullable=True),
        'node': fields.StringField(nullable=True),
        'os_type': fields.StringField(nullable=True),
        'architecture': fields.StringField(nullable=True),
        'availability_zone': fields.StringField(nullable=True),

        'flavor': fields.ObjectField('FlavorPayload'),
        'image_uuid': fields.StringField(nullable=True),

        'key_name': fields.StringField(nullable=True),

        'kernel_id': fields.StringField(nullable=True),
        'ramdisk_id': fields.StringField(nullable=True),

        'created_at': fields.DateTimeField(nullable=True),
        'launched_at': fields.DateTimeField(nullable=True),
        'terminated_at': fields.DateTimeField(nullable=True),
        'deleted_at': fields.DateTimeField(nullable=True),
        'updated_at': fields.DateTimeField(nullable=True),

        'state': fields.InstanceStateField(nullable=True),
        'power_state': fields.InstancePowerStateField(nullable=True),
        'task_state': fields.InstanceTaskStateField(nullable=True),
        'progress': fields.IntegerField(nullable=True),

        'ip_addresses': fields.ListOfObjectsField('IpPayload'),
        'block_devices': fields.ListOfObjectsField('BlockDevicePayload',
                                                   nullable=True),

        'metadata': fields.DictOfStringsField(),
        'locked': fields.BooleanField(),
        'auto_disk_config': fields.DiskConfigField(),

        'request_id': fields.StringField(nullable=True),
        'action_initiator_user': fields.StringField(nullable=True),
        'action_initiator_project': fields.StringField(nullable=True),
        'locked_reason': fields.StringField(nullable=True),
    }
    """

    def __init__(self, payload):
        super(InstancePayload, self).__init__(payload)
        self._build_flavor()
        self._build_ip_addresses()
        self._build_block_devices()

    def _build_flavor(self):
        payload = self.get('flavor', {})
        self.set('flavor', FlavorPayload(payload))

    def _build_ip_addresses(self):
        payloads = self.get('ip_addresses', [])
        ip_addresses = []
        for payload in payloads:
            ip_addresses.append(IpPayload(payload))
        self.set('ip_addresses', ip_addresses)

    def _build_block_devices(self):
        payloads = self.get('block_devices', [])
        block_devices = []
        for payload in payloads:
            block_devices.append(BlockDevicePayload(payload))
        self.set('block_devices', block_devices)

    @property
    def instance_id(self):
        return self.get('uuid')

    @property
    def user_id(self):
        return self.get('user_id')

    @property
    def tenant_id(self):
        return self.get('tenant_id')

    @property
    def name(self):
        return self.get('display_name')

    @property
    def description(self):
        return self.get('display_description')

    @property
    def host_name(self):
        return self.get('host_name')

    @property
    def host(self):
        return self.get('host')

    @property
    def node(self):
        return self.get('node')

    @property
    def os_type(self):
        return self.get('os_type')

    @property
    def architecture(self):
        return self.get('architecture')

    @property
    def availability_zone(self):
        return self.get('availability_zone')

    @property
    def flavor(self):
        return self.get('flavor')

    @property
    def image_id(self):
        return self.get('image_uuid')

    @property
    def kernel_id(self):
        return self.get('kernel_id')

    @property
    def ramdisk_id(self):
        return self.get('ramdisk_id')

    @property
    def key_name(self):
        return self.get('key_name')

    @property
    def created_at(self):
        return self.get('created_at')

    @property
    def updated_at(self):
        return self.get('updated_at')

    @property
    def launched_at(self):
        return self.get('launched_at')

    @property
    def terminated_at(self):
        return self.get('terminated_at')

    @property
    def deleted_at(self):
        return self.get('deleted_at')

    @property
    def state(self):
        return self.get('state')

    @property
    def power_state(self):
        return self.get('power_state')

    @property
    def task_state(self):
        return self.get('task_state')

    @property
    def ip_addresses(self):
        return self.get('ip_addresses')

    @property
    def block_devices(self):
        return self.get('block_devices')

    @property
    def metadata(self):
        return self.get('metadata')

    @property
    def locked(self):
        return self.get('locked')

    @property
    def locked_reason(self):
        return self.get('locked_reason')


@payload_register
class InstanceActionPayload(InstancePayload):
    """
    add fields:
    - fault: None or {}
    - request_id: ""
    """

    def __init__(self, payload):
        super(InstanceActionPayload, self).__init__(payload)
        self._build_fault()

    def _build_fault(self):
        payload = self.get('fault', {})
        if payload:
            self.set('fault', ExceptionPayload(payload))

    @property
    def is_failed(self):
        return bool(self.fault)

    @property
    def fault(self):
        return self.get('fault')

    @property
    def request_id(self):
        return self.get('request_id')


@payload_register
class InstanceActionVolumePayload(InstanceActionPayload):
    """
    add fields:
    - volume_id: <uuid>
    """

    @property
    def volume_id(self):
        return self.get('volume_id')


@payload_register
class InstanceCreatePayload(InstanceActionPayload):
    """
    add fields:
    - keypairs: []
    - tags: []
    - trusted_image_certificates: []
    - instance_name: ''
    """

    def __init__(self, payload):
        super(InstanceCreatePayload, self).__init__(payload)
        self._build_keypairs()

    def _build_keypairs(self):
        payloads = self.get('keypairs', [])
        keypairs = []
        for payload in payloads:
            keypairs.append(KeypairPayload(payload))
        self.set('keypairs', keypairs)

    @property
    def keypairs(self):
        return self.get('keypairs')

    @property
    def instance_name(self):
        return self.get('instance_name')

    @property
    def tags(self):
        return self.get('tags')


@payload_register
class InstanceActionResizePrepPayload(InstanceActionPayload):
    """
    add fields:
    - new_flavor: {}
    """

    def __init__(self, payload):
        super(InstanceActionResizePrepPayload, self).__init__(payload)
        self._build_new_flavor()

    def _build_new_flavor(self):
        payload = self.get('new_flavor', {})
        self.set('new_flavor', FlavorPayload(payload))

    @property
    def new_flavor(self):
        return self.get('new_flavor')


@payload_register
class InstanceStateUpdatePayload(Payload):
    """
    payload:
    {
        'old_state': '',
        'state': '',
        'old_task_state': '',
        'new_task_state': '',
    }
    """

    @property
    def old_state(self):
        return self.get('old_state')

    @property
    def state(self):
        return self.get('state')

    @property
    def old_task_state(self):
        return self.get('old_task_state')

    @property
    def new_task_state(self):
        return self.get('new_task_state')


@payload_register
class InstanceUpdatePayload(InstancePayload):
    """
    add fields:
    - state_update: <InstanceStateUpdatePayload>
    - old_display_name: <str>
    - tags: <str>[]
    """

    def __init__(self, payload):
        super(InstanceUpdatePayload, self).__init__(payload)
        self._build_state_update()

    def _build_state_update(self):
        payload = self.get('state_update', {})
        self.set('state_update', InstanceStateUpdatePayload(payload))

    @property
    def state_update(self):
        return self.get('state_update')

    @property
    def old_display_name(self):
        return self.get('old_display_name')

    @property
    def tags(self):
        return self.get('tags')


@payload_register
class InstanceExistsPayload(InstancePayload):
    """
    add fields:
    - audit_period: <AuditPeriodPayload>
    - bandwidth: <BandwidthPayload>[]
    """


@payload_register
class InstanceActionSnapshotPayload(InstanceActionPayload):
    """
    add fields:
    - snapshot_image_id: <uuid>
    """

    @property
    def snapshot_image_id(self):
        return self.get('snapshot_image_id')


