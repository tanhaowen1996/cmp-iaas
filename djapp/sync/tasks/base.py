
import logging

from sync import osapi


LOG = logging.getLogger(__name__)

_NOVA_API = None
_CINDER_API = None
_NEUTRON_API = None
_GLANCE_API = None


def nova_api():
    global _NOVA_API

    if not _NOVA_API:
        _NOVA_API = osapi.NovaAPI.create()

    return _NOVA_API


def glance_api():
    global _GLANCE_API

    if not _GLANCE_API:
        _GLANCE_API = osapi.GlanceAPI.create()

    return _GLANCE_API


def cinder_api():
    global _CINDER_API

    if not _CINDER_API:
        _CINDER_API = osapi.CinderAPI.create()

    return _CINDER_API


def neutron_api():
    global _NEUTRON_API

    if not _NEUTRON_API:
        _NEUTRON_API = osapi.NeutronAPI.create()

    return _NEUTRON_API


class SyncPass(Exception):
    pass


def alg_sync(db_objects, db_obj_key_fn, os_objects, os_obj_key_fn,
             create_db_fn, update_db_fn, remove_db_fn,
             remove_allowed=True):
    """Generic sync Resources method."""
    # Objects to Dicts
    exist_objects = {db_obj_key_fn(db_obj): db_obj for db_obj in db_objects}
    new_objects = {os_obj_key_fn(os_obj): os_obj for os_obj in os_objects}

    LOG.info("Want %s, Got %s" % (len(exist_objects), len(new_objects)))

    LOG.info("exist set: %s" % set(exist_objects))
    LOG.info("new set: %s" % set(new_objects))

    for existed in exist_objects.values():
        if db_obj_key_fn(existed) in set(exist_objects) - set(new_objects):
            # Remove previously unknown resource.
            if not remove_allowed:
                LOG.warning("Will not remove unknown resource: %s" % db_obj_key_fn(existed))
                continue
            try:
                existed_id = db_obj_key_fn(existed)
                remove_db_fn(existed)
                LOG.info("Removed previously unknown resource: %s" % existed_id)
            except Exception as ex:
                LOG.exception(ex)
        else:
            # Update tracked resources.
            new_value = new_objects[db_obj_key_fn(existed)]
            try:
                update_db_fn(existed, new_value)
                LOG.info("Updated tracked resource: %s" % db_obj_key_fn(existed))
            except SyncPass as ex:
                LOG.warning("Pass update resource: %s for: %s" % (db_obj_key_fn(existed), ex))
            except Exception as ex:
                LOG.exception(ex)

    # Track newly discovered resources.
    for os_obj in [os_obj for os_obj in new_objects.values() if
                   os_obj_key_fn(os_obj) in set(new_objects) - set(exist_objects)]:
        try:
            create_db_fn(os_obj)
            LOG.info("Tracked newly discovered resource: %s" % os_obj_key_fn(os_obj))
        except SyncPass as ex:
            LOG.warning("Pass create resource: %s for: %s" % (os_obj_key_fn(os_obj), ex))
        except Exception as ex:
            LOG.exception(ex)
