
import logging

from django.contrib.auth.models import User

from celery import shared_task

from sync import osapi
from sync.uum import api as uum_api
from sync import models

from . import flavor
from . import volume_type
from . import image
from . import network
from . import keypair
from . import instance
from . import volume

LOG = logging.getLogger(__name__)


def _make_admin_user_info():
    admin_user_id = osapi.get_user_id()
    admin_project_id = osapi.get_project_id()
    return {
        'userId': -1,
        'userName': "admin_syncer",
        "relUserId": admin_user_id,
        "relUserName": "admin",
        "projects": [{
            "id": admin_project_id,
            "name": "admin",
            "tenantId": "admin",
            "tenantName": "admin"
        }]
    }


def _create_auth_user(user):
    user_id = user.get('userId')
    user_name = user.get('userName')
    LOG.info("Create Auth user: %s / %s" % (user_id, user_name))
    # save to db:
    User.objects.get_or_create(
        id=user_id,
        defaults={'username': user_name})


@shared_task
def do_admin_sync():
    """Sync admin/global resources"""
    admin_user = _make_admin_user_info()
    admin_project = admin_user.get('projects', [])[0]

    # create or get admin auth user
    _create_auth_user(admin_user)

    # sync flavors: [global]
    flavor.do_flavors_sync()

    # sync volume types: [global]
    volume_type.do_volume_types_sync()

    # sync images: [global]
    image.do_images_sync()

    # sync networks: [global]
    network.do_networks_sync()

    # sync admin resources:
    _sync_user_project_resources(admin_user, admin_project)


def _sync_user_project_resources(user, project):
    """Sync user/project resources"""
    # sync keypairs
    keypair.do_key_pairs_sync(user, project)
    # sync instances
    instance.do_instances_sync(user, project)
    # sync volumes
    volume.do_volumes_sync(user, project)


@shared_task
def sync_user_projects_from_uum():
    try:
        users = uum_api.user_list()
    except Exception as ex:
        LOG.exception(ex)
        return

    # extract data to db
    for user in users:
        models.User.create_or_get(user)


@shared_task
def do_tenants_sync():
    """Sync uum mapped tenants resources"""
    synced_projects = set()

    def _sync_user_resources(user):
        if not user:
            LOG.warning("User info is None, pass to sync...")
            return

        projects = user.get('projects', [])
        if projects is None:
            LOG.error("User:%s 's projects is not mapped, skip to sync..."
                      % user)
            return

        LOG.debug("Got %s projects for user: %s"
                  % (len(projects), user.get('relUserId')))

        for project in projects:
            project_id = project.get('id')
            if project_id in synced_projects:
                LOG.warning("Project: %s already synced, pass ..."
                            % project_id)
                continue

            # sync user resources by project
            _sync_user_project_resources(user, project)
            # record synced project
            synced_projects.add(project_id)

    # sync from uum to db
    sync_user_projects_from_uum()
    # get all from db
    users = models.User.all(to_dict=True)
    for user in users:
        user_id = user.get('userId')
        user_name = user.get('userName')
        if user_name is None:
            LOG.warning("user: %s name is None, could not sync info..." % user_id)
            continue
        # create or get tenant auth user
        _create_auth_user(user)
        # sync user resources
        _sync_user_resources(user)


@shared_task
def do_all_sync():
    LOG.info("Start to sync global and admin resources...")
    do_admin_sync.delay()

    LOG.info("Start to sync tenants' resources...")
    do_tenants_sync.delay()

    LOG.info("Sync Done!")
