import importlib

from django.conf import settings

from ..apps import get_package_name


def get_tenant():
    # return 'missing'
    if not settings.APP_CLIENT_NAME:
        return

    return settings.APP_CLIENT_NAME


def get_tenant_app():
    tenant = get_tenant()
    try:
        return importlib.import_module(tenant)
    except Exception as ex:
        print(ex)
        return None


def get_tenant_module(module_name: str = None):
    tenant = get_tenant()
    package = get_package_name()
    try:
        return importlib.import_module(f'.tenants.{tenant}.{module_name}', package=package)
    except Exception as ex:
        return None


def import_tenant_attribute(function_name: str, module_name: str = None):
    if module_name:
        obj = get_tenant_module(module_name)
    else:
        obj = get_tenant_app()

    return getattr(obj, function_name, None) if obj else None
