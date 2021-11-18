from rest_framework import serializers
from .models import Topic, Message


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = (
            'id',
            'creater_id',
            'creater_name',
            'tenant',
            'subject',
            'latest_message_content',
            'created',
            'modified'
        )
        read_only_fields = (
            'id', 'tenant',
            'latest_message',
            'creater_id', 'created_name',
            'created', 'modified',
        )


class TopicCreationSerializer(TopicSerializer):
    content = serializers.CharField()

    class Meta(TopicSerializer.Meta):
        fields = TopicSerializer.Meta.fields + (
            'content',
        )

    def save(self, creater=None, tenant=None, **kwargs):
        self.instance = Topic.objects.create(
            creater=creater,
            tenant=tenant,
            subject=self.validated_data['subject'])
        message = Message.objects.create(
            creater=creater,
            topic=self.instance,
            content=self.validated_data['content'])
        self.instance.content = message.content
        return self.instance


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = (
            'id',
            'creater_id',
            'creater_name',
            'topic_id',
            'content',
            'created',
            'modified'
        )
        read_only_fields = (
            'id',
            'creater_id', 'created_name',
            'topic_id',
            'created', 'modified',
        )
