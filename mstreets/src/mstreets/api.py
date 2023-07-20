import math

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mstreets.models import PC, Animation, Campaign, Config, Poi, Zone, ZoneGroupPermission
from mstreets.serializers import (
    AnimationSerializer, CampaignSerializer, ConfigSerializer,
    PCSerializer, PoiSerializer, ZoneSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def config_list(request):
    queryset = Config.objects.all()

    variable_name = request.GET.get('n')
    if variable_name:
        try:
            queryset = queryset.get(variable=variable_name)
        except Config.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ConfigSerializer(queryset)
        return Response(serializer.data)

    serializer = ConfigSerializer(queryset, many=True)
    return Response(serializer.data)


def get_permitted_zones_ids(request):
    groups = request.user.groups.all()
    zone_groups = ZoneGroupPermission.objects.filter(group__in=groups)
    return Zone.objects.filter(
        Q(public=True) | Q(pk__in=list(zone_groups.values_list('zone', flat=True)))
    ).exclude(active=False)


def get_permitted_zones_by_geom(request, point, radius):
    groups = request.user.groups.all()
    zone_groups = ZoneGroupPermission.objects.filter(group__in=groups)
    buffer_width = radius / 40000000. * 360. / math.cos(point.y / 360. * math.pi)
    circle = point.buffer(buffer_width)
    return Zone.objects.filter(
            geom__intersects=circle
        ).filter(
            Q(public=True) | Q(pk__in=list(zone_groups.values_list('zone', flat=True)))
        ).exclude(active=False)


def transform_geom_epsg(queryset, request):
    if request.GET.get('epsg'):
        try:
            epsg = int(request.GET.get('epsg'))
            [obj.geom.transform(epsg) for obj in queryset]
        except ValueError:
            return 'ERROR: there is an error in EPSG parameter. Must be integer numer, p.e. 25831'
    return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def campaign_list(request):
    permitted_zones = get_permitted_zones_ids(request)
    queryset = Campaign.objects.filter(zones__in=permitted_zones)

    id = request.GET.get('id')
    if id:
        try:
            queryset = queryset.get(pk=id)
        except Campaign.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        transform_geom_epsg(queryset, request)
        serializer = CampaignSerializer(queryset)
        return Response(serializer.data)

    zone = request.GET.get('z')
    if zone:
        queryset = queryset.filter(zone=zone)

    transform_geom_epsg(queryset, request)
    serializer = CampaignSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def zone_list(request):
    queryset = get_permitted_zones_ids(request)

    id = request.GET.get('id')
    if id:
        try:
            queryset = queryset.get(pk=id)
        except Zone.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        transform_geom_epsg(queryset, request)
        serializer = ZoneSerializer(queryset)
        return Response(serializer.data)

    transform_geom_epsg(queryset, request)
    serializer = ZoneSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def poi_list(request):
    permitted_zones = get_permitted_zones_ids(request).filter(poi_permission=True)
    queryset = Poi.objects.filter(geom__in=permitted_zones)
    id = request.GET.get('id')
    if not id:
        msg = 'ERROR: missing id parameter'
        return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

    try:
        queryset = queryset.get(pk=id)
    except Poi.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    transform_geom_epsg(queryset, request)
    serializer = PoiSerializer(queryset)
    return Response(serializer.data)


def get_response_params_id_z_c(Model, Serializer, request):
    permitted_zones = get_permitted_zones_ids(request)
    if Model == PC:
        permitted_zones = permitted_zones.filter(poi_permission=True)
    queryset = Model.objects.filter(zone__in=permitted_zones)

    id = request.GET.get('id')
    if id:
        try:
            queryset = queryset.get(pk=id)
        except Model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = Serializer(queryset)
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

    transform_geom_epsg(queryset, request)
    serializer = Serializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def pc_list(request):
    return get_response_params_id_z_c(PC, PCSerializer, request)


@api_view(['GET'])
@permission_classes([AllowAny])
def animation_list(request):
    return get_response_params_id_z_c(Animation, AnimationSerializer, request)


def get_point_radius(request):
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

    point = Point(latlon[1], latlon[0], srid=4326)
    return point, radius


def params_filter(queryset, request):
    filters = [
        {'param': 't', 'field': 'tag'},
        {'param': 'z', 'field': 'zone'},
        {'param': 'c', 'field': 'campaign'}
    ]
    filters = {f['field']: request.GET.get(f['param']) for f in filters if request.GET.get(f['param'])}
    queryset = queryset.filter(**filters)
    return queryset


def filter_by_multiple_polygons(Model, queryset, polygons):
    filtered_queryset = Model.objects.none()
    for polygon in polygons:
        filtered_queryset = filtered_queryset | queryset.filter(geom__intersects=polygon.geom)
    return filtered_queryset


def filter_by_campaigns(queryset, zones):
    campaigns = Campaign.objects.filter(zones__in=zones).exclude(active=False)
    return queryset.filter(campaign__in=campaigns)


def get_pois(request, point, radius):
    pois = Poi.objects.filter(
        geom__distance_lte=(point, D(m=radius))
    ).annotate(
        distance=Distance(point, 'geom')
    ).order_by('distance')
    permitted_zones = get_permitted_zones_by_geom(request, point, radius).filter(poi_permission=True)
    pois = filter_by_multiple_polygons(Poi, pois, permitted_zones)
    pois = filter_by_campaigns(pois, permitted_zones)
    pois = params_filter(pois, request)
    if request.GET.get('fpp'):
        fpp = request.GET.get('fpp').upper()
        pois = pois.filter(format=fpp)
    
    transform_geom_epsg(pois, request)
    return pois


def get_pcs(request, point, radius=50):
    buffer_width = radius / 40000000. * 360. / math.cos(point.y / 360. * math.pi)
    circle = point.buffer(buffer_width)
    pcs = PC.objects.filter(
        geom__intersects=circle
    )
    permitted_zones = get_permitted_zones_by_geom(request, point, radius).filter(pc_permission=True)
    pcs = filter_by_multiple_polygons(PC, pcs, permitted_zones)
    pcs = filter_by_campaigns(pcs, permitted_zones)
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

    transform_geom_epsg(pcs, request)
    return pcs


@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    point_radius = get_point_radius(request)
    if isinstance(point_radius, Response):
        return point_radius
    point, radius = point_radius

    response = {}

    filter_output = request.GET.get('f')
    if not filter_output or filter_output.lower() == 'poi':
        pois = get_pois(request, point, radius)
        response['poi'] = PoiSerializer(pois, many=True).data

    if not filter_output or filter_output.lower() == 'pc':
        pcs = get_pcs(request, point, radius)
        response['pc'] = PCSerializer(pcs, many=True).data

    return Response(response)
