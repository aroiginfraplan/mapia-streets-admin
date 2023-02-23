import json
from abc import ABC, abstractmethod
from pyproj import Transformer
from datetime import datetime

from django.contrib.gis.geos import GEOSGeometry
from django.utils.timezone import make_aware

from mstreets.models import Campaign


class CampaignUploader(ABC):
    def __init__(self, file_to_upload, form_data):
        self.file_to_upload = file_to_upload
        self.zones = form_data["zones"]
        self.metadata = form_data["metadata"]
        self.folder_pano = form_data["folder_pano"]
        self.folder_img = form_data["folder_img"]
        self.folder_pc = form_data["folder_pc"]
        self.campaign = None

    def upload_file(self):
        self.read_file()
        return self.save_campaign()

    @abstractmethod
    def read_file(self):
        pass

    def save_campaign(self):
        try:
            campaign = Campaign(**self.campaign)
            campaign.save()
            for zone in self.zones:
                campaign.zones.add(zone)
            return True
        except Exception as e:
            return False


class JSONCampaignUploader(CampaignUploader):
    def read_file(self):
        try:
            file_txt = self.file_to_upload.read().decode('utf-8').replace('\r', '').replace('\n', '').replace('\t', '')
            campaign_geojson = json.loads(file_txt)
            feature = campaign_geojson['features'][0]
            geom = GEOSGeometry(json.dumps(feature['geometry']))
            campaign = feature['properties']
            campaign['metadata'] = self.metadata or None
            campaign['geom'] = geom
            campaign['date_start'] = self.str_to_date(campaign['date_start'])
            campaign['date_fi'] = self.str_to_date(campaign['date_fi'])
            campaign['folder_pano'] = self.get_param(campaign, 'folder_pano')
            campaign['folder_img'] = self.get_param(campaign, 'folder_img')
            campaign['folder_pc'] = self.get_param(campaign, 'folder_pc')
            campaign['active'] = campaign['active'].lower() == 'true'
            self.campaign = campaign
        except ValueError:
            print('Invalid JSON field type')

    def str_to_date (self, str_date):
        year, month, day = map(int, str_date.split('-'))
        return datetime(year, month, day)

    def get_param(self, campaign, param):
        if param in campaign and campaign[param]:
            return campaign[param]
        else:
            return self.folder_pc
