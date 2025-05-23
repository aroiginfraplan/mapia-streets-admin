from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mstreets.models import PC, Animation, Campaign, Campaign_Category, Config, Metadata, Poi, Poi_Resource, Zone


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('variable', 'value')


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = ('sensor', 'method', 'precision', 'company', 'contact')


class Campaign_CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign_Category
        fields = ('name', 'order')


class CampaignSerializer(serializers.ModelSerializer):
    metadata = MetadataSerializer(many=False)
    category = Campaign_CategorySerializer(many=False)

    class Meta:
        model = Campaign
        fields = ('id', 'zones', 'metadata', 'category', 'active', 'name',
                  'date_start', 'date_fi', 'folder_pano',
                  'folder_img', 'folder_pc', 'epsg', 'sync_pano',
                  'config', 'geom')


class ZoneSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Zone
        geo_field = 'geom'
        fields = ('id', 'name', 'description', 'active', 'folder_pano', 'folder_img',
                  'folder_pc', 'poi_permission', 'pc_permission', 'geom')


class Poi_ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poi_Resource
        fields = ('filename', 'format', 'pan', 'pitch', 'folder', 'tag')


class PoiSerializer(GeoFeatureModelSerializer):
    resources = Poi_ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Poi
        geo_field = 'geom'
        fields = ('id', 'campaign', 'filename', 'format', 'type', 'date', 'altitude', 'has_mini',
                  'roll', 'pitch', 'pan', 'angle_width', 'angle_height', 'angle_height_offset',
                  'folder', 'tag', 'config', 'geom', 'resources')


class PCSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PC
        geo_field = 'geom'
        fields = ('id', 'campaign', 'name', 'filename', 'is_local',
                  'is_downloadable', 'format', 'folder', 'tag', 'config', 'geom')


class AnimationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animation
        fields = ('campaign', 'name', 'tag', 'geom_source', 'geom_target')
