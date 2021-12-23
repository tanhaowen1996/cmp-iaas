from rest_framework import serializers

from .models import Inform


class InformSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inform
        fields = "__all__"
