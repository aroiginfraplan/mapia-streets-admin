from django.contrib import admin

from mstreets.models import PC, Campaign, Config, Metadata, Poi_Locations, Zone


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    pass


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    pass


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    pass


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    pass


@admin.register(Poi_Locations)
class Poi_LocationsAdmin(admin.ModelAdmin):
    pass


@admin.register(PC)
class PCAdmin(admin.ModelAdmin):
    pass
