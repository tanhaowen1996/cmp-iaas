from rest_framework import serializers
from ipaddress import IPv4Address


class IPAddressField(serializers.IPAddressField):

    def to_representation(self, value):
        return super().to_representation(
            value.ip if isinstance(value, IPv4Address) else value)