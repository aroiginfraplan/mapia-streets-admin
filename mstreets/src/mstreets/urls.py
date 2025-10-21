from django.urls import path
from django.views.i18n import JavaScriptCatalog

from mstreets.api import (
    animation_list,
    campaign_list,
    config_list,
    pc_list,
    poi_list,
    search,
    zone_list,
    points_route,
    context_info_api,
)
from mstreets.views import (
    UploadPoi_LocationsFileView,
    add_default_config,
    UploadPCFileView, UploadPOIFileView,
    panoramas_files_server
)


urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view()),
    path('api/config', config_list),
    path('api/campaign', campaign_list),
    path(
        'api/campaign/<int:campaign_pk>/context-info',
        context_info_api,
        name='mstreets-context-info',
    ),
    path('api/zone', zone_list),
    path('api/poi', poi_list),
    path('api/pc', pc_list),
    path('api/search', search),
    path('api/animation', animation_list),
    path('api/points_route', points_route),
    path('files/<path:path>', panoramas_files_server, name='panoramas-files'),
    path('add_default_config', add_default_config, name='mstreets-add-default-config'),
    path('upload_poi_file', UploadPOIFileView().view, name='mstreets-upload-poi-file'),
    path('upload_pc_file', UploadPCFileView().view, name='mstreets-upload-pc-file'),
    path(
        'upload_poi_locations_file',
        UploadPoi_LocationsFileView().view,
        name='mstreets-upload-poi-locations-file',
    ),
]
