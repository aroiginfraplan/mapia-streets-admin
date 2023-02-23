from django.urls import path
from django.views.i18n import JavaScriptCatalog

from mstreets.api import animation_list, campaign_list, config_list, pc_list, poi_list, search, zone_list
from mstreets.views import (
    add_default_config,
    UploadCampaignFileView, UploadPCFileView, UploadPOIFileView,
    panoramas_files_server
)


urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view()),
    path('api/config', config_list),
    path('api/campaign', campaign_list),
    path('api/zone', zone_list),
    path('api/poi', poi_list),
    path('api/pc', pc_list),
    path('api/search', search),
    path('api/animation', animation_list),
    path('files/<path:path>', panoramas_files_server, name='panoramas-files'),
    path('add_default_config', add_default_config, name='mstreets-add-default-config'),
    path('upload_poi_file', UploadPOIFileView().view, name='mstreets-upload-poi-file'),
    path('upload_pc_file', UploadPCFileView().view, name='mstreets-upload-pc-file'),
    path('upload_campaign_file', UploadCampaignFileView().view, name='mstreets-upload-campaign-file')
]
