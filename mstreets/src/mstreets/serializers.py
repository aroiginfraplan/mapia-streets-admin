from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mstreets.models import PC, Animation, Campaign, Config, Metadata, Poi, Poi_Resource, Zone


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('variable', 'value')


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = ('sensor', 'precision', 'company', 'contact')


class CampaignSerializer(serializers.ModelSerializer):
    metadata = MetadataSerializer(many=False)

    class Meta:
        model = Campaign
        fields = ('id', 'zones', 'metadata', 'active', 'name',
                  'date_start', 'date_fi', 'folder_pano',
                  'folder_img', 'folder_pc', 'config', 'geom')


class ZoneSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Zone
        geo_field = 'geom'
        fields = ('id', 'name', 'description', 'active', 'folder_pano',
                  'folder_img', 'folder_pc', 'geom')


class Poi_ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poi_Resource
        fields = ('filename', 'format', 'pan', 'pitch', 'folder', 'tag')


class PoiSerializer(GeoFeatureModelSerializer):
    resources = Poi_ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Poi
        geo_field = 'geom'
        fields = ('id', 'campaign', 'filename', 'format', 'type', 'date', 'altitude',
                  'roll', 'pitch', 'pan', 'folder', 'tag', 'config', 'geom', 'resources')


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
