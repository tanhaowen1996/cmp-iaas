
from django.db import models


class Project(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name='tenant_id')
    project_id = models.CharField(
        max_length=255,
        null=False)
    project_name = models.CharField(
        max_length=255,
        null=True)
    tenant_id = models.IntegerField(
        null=False)
    tenant_name = models.CharField(
        max_length=255,
        null=True)

    @staticmethod
    def convert_from_uum(db_obj, uum_obj):
        """
        uum tenant dict:
        {
            "id": "752df3ea70724f44acc088a0f0313579",
            "name": "大科技",
            "tenantId": 59,
            "tenantName": "永辉大科技",
        }
        """
        db_obj.project_id = uum_obj.get('id')
        db_obj.project_name = uum_obj.get('name')
        db_obj.tenant_id = uum_obj.get('tenantId')
        db_obj.tenant_name = uum_obj.get('tenantName')
        # set id
        db_obj.id = db_obj.tenant_id

    @staticmethod
    def get(pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    @classmethod
    def create_or_get(cls, uum_obj):
        db_obj = cls.get(pk=uum_obj.get('tenantId'))
        if not db_obj:
            db_obj = cls()
        db_obj.update(uum_obj)
        db_obj.save()
        return db_obj

    def update(self, uum_obj):
        self.convert_from_uum(self, uum_obj)

    def to_dict(self):
        return {
            'id': self.project_id,
            'name': self.project_name,
            'tenantId': self.tenant_id,
            'tenantName': self.tenant_name,
        }

    def first_user(self):
        return self.user_set.first()


class User(models.Model):
    id = models.IntegerField(
        primary_key=True,
        verbose_name='account_id')
    user_id = models.CharField(
        max_length=255,
        null=False)
    username = models.CharField(
        max_length=255,
        null=True)
    account_id = models.IntegerField(
        null=False)
    account_name = models.CharField(
        max_length=255,
        null=True)

    projects = models.ManyToManyField(Project)

    @staticmethod
    def convert_from_uum(db_obj, uum_obj):
        """
        uum account dict:
        {
            "userId": 5,
            "userName": "yhcloud",
            "relUserId": "ac0997f1e0ff40f7936411a96a93a2c0",
            "relUserName": "yhcloud",
            "projects": []
        }
        """
        db_obj.user_id = uum_obj.get('relUserId')
        db_obj.username = uum_obj.get('relUserName')
        db_obj.account_id = uum_obj.get('userId')
        db_obj.account_name = uum_obj.get('userName')
        # set id
        db_obj.id = db_obj.account_id

    @staticmethod
    def get(pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    @classmethod
    def create_or_get(cls, uum_obj):
        db_obj = User.get(pk=uum_obj.get('userId'))
        if not db_obj:
            db_obj = cls()
        db_obj.update(uum_obj)
        db_obj.save()

        # build user project relationship:
        # 1) clear before:
        db_obj.projects.clear()
        # 2) build new:
        for project in uum_obj.get('projects', []):
            project_db = Project.create_or_get(project)
            project_db.save()
            db_obj.projects.add(project_db)

        return db_obj

    def update(self, uum_obj):
        self.convert_from_uum(self, uum_obj)

    def to_dict(self):
        projects = [p.to_dict() for p in self.projects.all()]
        return {
            'userId': self.account_id,
            'userName': self.account_name,
            'relUserId': self.user_id,
            'relUserName': self.username,
            'projects': projects,
        }

    def first_project(self):
        return self.projects.first()

    @staticmethod
    def all(to_dict=False):
        users = User.objects.all()
        if to_dict:
            return [u.to_dict() for u in users]
        return users
