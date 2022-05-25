from rest_framework import serializers

from mstreets.models import PC, Campaign, Config, Metadata, Poi, Poi_Resource, Zone


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('variable', 'value')


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = ('sensor', 'precision', 'company', 'contact')


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ('id', 'code', 'name', 'description', 'zone', 'date_start', 'date_end',
                  'folder_panorama', 'folder_images', 'folder_point_cloud', 'layer_panorama')


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ('id', 'name', 'description', 'active', 'folder_pano',
                  'folder_img', 'folder_pc', 'geom')


class Poi_ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poi_Resource
        fields = ('filename', 'format', 'pan', 'pitch', 'folder', 'tag')


class PoiSerializer(serializers.ModelSerializer):
    resources = Poi_ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Poi
        fields = ('filename', 'format', 'type', 'date', 'altitude', 'roll',
                  'pitch', 'pan', 'folder', 'tag', 'config', 'geom', 'resources')


class PCSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ('id', 'zone', 'campaign', 'name', 'filename', 'is_local',
                  'is_downloadable', 'format', 'folder', 'tag', 'config', 'geom')
