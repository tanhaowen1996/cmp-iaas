from rest_framework.response import Response
from rest_framework import viewsets
from djapp.authentication import OSAuthentication
from .communication import Communication
from .filters import PlatformInformFilter
from . import models
from .models import Inform
from .serializers import InformSerializer
import json
import requests
from .utils import all_user_url, all_user_header
from django.db.models import Q


class InformViewSet(viewsets.ModelViewSet):
    authentication_classes = (OSAuthentication,)
    filterset_class = PlatformInformFilter
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(Q(info__user_id=self.request.account_info['id']) | Q(inform_tenant=self.request.account_info['tenantId']))
        return qs

    def create(self, request, *args, **kwargs):
        if request.data['inform_object_type'] == "全平台":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                name=request.data['name'],
                inform_object_type=request.data['inform_object_type'],
                inform_tenant='全平台',
                inform_user=['全平台'],
                details=request.data['details'],
                sms_way=request.data['sms_way'],
                email_way=request.data['email_way'],
                wecom_way=request.data['wecom_way'],
                inside_way=request.data['inside_way'],
                initiator_id=request.user.id,
                initiator_name=request.user
            )
            res = requests.get(url=all_user_url, headers=all_user_header)
            user_info_all = json.loads(res.text)['data']['records']
            for user_info in user_info_all:
                models.InformUser.objects.create(informs_id=serializer.data['id'],
                                                 user_id=user_info['id'],
                                                 name=user_info['accountName'],
                                                 phone=user_info['phone'],
                                                 email=user_info['email'])
            if request.data['email_way'] == 1:
                email_list = []
                for user_info in user_info_all:
                    if user_info['email'] is not None:
                        email_list.append(user_info['email'])
                Communication().email(request.data['name'], request.data['details'], email_list)
            if request.data['sms_way'] == 1:
                sms_list = []
                for user_info in user_info_all:
                    sms_dict = {}
                    sms_dict['phoneNumber'] = user_info['phone']
                    sms_dict['content'] = "(云业务)  " + request.data['name'] + ">>>" + request.data['details'] + '，回复TD退订'
                    sms_list.append(sms_dict)
                Communication().sms(sms_list)
            return Response(serializer.data)
        elif request.data['inform_object_type'] == "租户":
            user_name_list = []
            for inform_tenant in request.data['inform_user']:
                user_name_list.append(inform_tenant['accountName'])
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                name=request.data['name'],
                inform_object_type=request.data['inform_object_type'],
                inform_tenant=request.data['inform_tenant'],
                inform_user=user_name_list,
                details=request.data['details'],
                sms_way=request.data['sms_way'],
                email_way=request.data['email_way'],
                wecom_way=request.data['wecom_way'],
                inside_way=request.data['inside_way'],
                initiator_id=request.user.id,
                initiator_name=request.user
            )
            for user_info in request.data['inform_user']:
                models.InformUser.objects.create(informs_id=serializer.data['id'], user_id=user_info['id'],
                                                 name=user_info['accountName'], phone=user_info['phone'],
                                                 email=user_info['email'])
            if request.data['email_way'] == 1:
                email_list = []
                for user_info in request.data['inform_user']:
                    if user_info['email'] is not None:
                        email_list.append(user_info['email'])
                Communication().email(request.data['name'], request.data['details'], email_list)
            if request.data['sms_way'] == 1:
                sms_list = []
                for user_info in request.data['inform_user']:
                    sms_dict = {}
                    sms_dict['phoneNumber'] = user_info['phone']
                    sms_dict['content'] = "(云业务)  "+request.data['name'] + ">>>" + request.data['details'] + '，回复TD退订'
                    sms_list.append(sms_dict)
                Communication().sms(sms_list)
            return Response(serializer.data)
