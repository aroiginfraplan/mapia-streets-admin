from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mstreets.models import PC, Animation, Campaign, Config, Poi, Zone, ZoneGroupPermission
from mstreets.serializers import (
    AnimationSerializer, CampaignSerializer, ConfigSerializer,
    PCSerializer, PoiSerializer, ZoneSerializer
)


@api_view(['GET'])
def config_list(request):
    queryset = Config.objects.all()
    serializer = ConfigSerializer(queryset, many=True)
    return Response(serializer.data)


def get_permitted_zones(request):
    groups = request.user.groups.all()
    zone_groups = ZoneGroupPermission.objects.filter(group__in=groups)
    return Zone.objects.filter(pk__in=list(zone_groups.values_list('pk', flat=True)))


@api_view(['GET'])
def campaign_list(request):
    permitted_zones = get_permitted_zones(request)
    queryset = Campaign.objects.filter(zone__in=permitted_zones)
    serializer = CampaignSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def zone_list(request):
    queryset = get_permitted_zones(request)
    serializer = ZoneSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def poi_list(request):
    permitted_zones = get_permitted_zones(request)
    queryset = Poi.objects.filter(zone__in=permitted_zones)
    id = request.GET.get('id')
    if not id:
        msg = 'ERROR: missing id parameter'
        return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

    try:
        queryset = queryset.get(pk=id)
    except Poi.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PoiSerializer(queryset, many=True)
    return Response(serializer.data)


def get_response_params_id_z_c(Model, Serializer, request):
    permitted_zones = get_permitted_zones(request)
    queryset = Model.objects.filter(zone__in=permitted_zones)

    id = request.GET.get('id')
    if id:
        try:
            queryset = queryset.get(pk=id)
        except Model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PCSerializer(queryset, many=True)
        return Response(serializer.data)

    zone = request.GET.get('z')
    if zone:
        queryset = queryset.filter(zone=zone)

    campaign = request.GET.get('c')
    if campaign:
        queryset = queryset.filter(campaign=campaign)

    if not id and not zone and not campaign:
        msg = 'ERROR: missing one parameter: id, z or c'
        return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

    serializer = Serializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pc_list(request):
    return get_response_params_id_z_c(PC, PCSerializer, request)


@api_view(['GET'])
def animation_list(request):
    return get_response_params_id_z_c(Animation, AnimationSerializer, request)


def get_geom_radius(request):
    latlon = None
    p = request.GET.get('p')
    if p:
        try:
            latlon = p.split(',')
            latlon = list(map(float, latlon))
        except Exception:
            msg = 'ERROR: invalid p parameter'
    else:
        msg = 'ERROR: missing p parameter'
    if not latlon:
        return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

    radius = None
    r = request.GET.get('r')
    if r:
        try:
            radius = int(r)
        except Exception:
            msg = 'ERROR: invalid r parameter'
    else:
        msg = 'ERROR: missing r parameter'
    if not radius:
        return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

    geom = Point(latlon[1], latlon[0], srid=4326)
    return geom, radius


def params_filter(queryset, request):
    filters = [
        {'param': 't', 'field': 'tag'},
        {'param': 'z', 'field': 'zone'},
        {'param': 'c', 'field': 'campaign'}
    ]
    filters = {f['field']: request.GET.get(f['param']) for f in filters if request.GET.get(f['param'])}
    queryset = queryset.filter(**filters)
    return queryset


def get_pois(request, geom, radius):
    permitted_zones = get_permitted_zones(request)
    pois = Poi.objects.filter(zone__in=permitted_zones)
    pois = pois.filter(
        geom__distance_lte=(geom, D(m=radius))
    ).annotate(
        distance=Distance(geom, 'geom')
    ).order_by('distance')
    pois = params_filter(pois, request)
    if request.GET.get('fpp'):
        fpp = request.GET.get('fpp').upper()
        pois = pois.filter(format=fpp)
    return pois


def get_pcs(request, geom):
    permitted_zones = get_permitted_zones(request)
    pcs = PC.objects.filter(zone__in=permitted_zones)
    pcs = pcs.filter(
        geom__contains=geom
    )
    pcs = params_filter(pcs, request)

    if request.GET.get('fpc'):
        fpc = request.GET.get('fpc').upper()
        pcs = pcs.filter(format=fpc)

    if request.GET.get('l'):
        is_local = request.GET.get('l')
        is_local = is_local.lower() == 'true' or is_local.lower() == 't'
        pcs = pcs.filter(is_local=is_local)

    if request.GET.get('d'):
        is_downloadable = request.GET.get('d')
        is_downloadable = is_downloadable.lower() == 'true' or is_downloadable.lower() == 't'
        pcs = pcs.filter(is_downloadable=is_downloadable)

    return pcs


@api_view(['GET'])
def search(request):
    geom_radius = get_geom_radius(request)
    if isinstance(geom_radius, Response):
        return geom_radius
    geom, radius = geom_radius

    response = {}

    filter_output = request.GET.get('f')
    if not filter_output or filter_output == 'POI':
        pois = get_pois(request, geom, radius)
        response['poi'] = PoiSerializer(pois, many=True).data

    if not filter_output or filter_output == 'PC':
        pcs = get_pcs(request, geom)
        response['pc'] = PCSerializer(pcs, many=True).data

    return Response(response)
