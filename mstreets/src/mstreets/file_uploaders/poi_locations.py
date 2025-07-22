import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from django.contrib.gis.geos import LineString, Point, Polygon
from mstreets.file_uploaders.utils import float_or_none
from mstreets.models import Poi, Poi_Locations, Poi_Resource
from pyproj import Transformer


class PoiLocationsUploader(ABC):
    campaign = None
    epsg = None
    x_translation = None
    y_translation = None
    z_translation = None
    tag = None
    color = None

    def __init__(
        self, file_path: str, form_data: Dict[str, any], required_fields: List[str]
    ) -> None:
        self.file_path = file_path
        self.required_fields = required_fields
        self.file_to_upload = file_path
        self.campaign = form_data["campaign"]
        self.epsg_transformer = Transformer.from_crs(form_data["epsg"], "EPSG:4326")
        self.x_translation = form_data["x_translation"]
        self.y_translation = form_data["y_translation"]
        self.z_translation = form_data["z_translation"]
        self.tag = form_data["tag"]
        self.color = form_data["color"]
        self.tags = []
        self.colors = []
        self.geoms = []
        self.pois = []
        self.types = []
        self.coords = []

    def __has_missing_data(self, data: Dict[str, any]) -> bool:
        missing_fields = [
            field for field in self.required_fields if data.get(field) is None
        ]

        return len(missing_fields) > 0

    def _load_data(self, data: Dict[str, any]) -> None:
        if self.__has_missing_data(data):
            return False

        tag = self.tag or data.get("tag")
        self.tags.append(tag)
        color = self.color or data.get("color")
        self.colors.append(color)
        self.types.append(data.get("type"))
        self.coords.append(data.get("coords"))

        return True

    def upload_file(self) -> bool:
        self.read_file()
        self.create_pois()
        return self.save_pois()

    def remove_file(self) -> None:
        os.remove(self.file_path)

    @abstractmethod
    def read_file(self) -> None:
        pass

    def create_pois(self) -> None:
        self.create_geoms()
        self.merge_arrays_to_create_pois()

    def translate_point_coordinates(self, coords: List[float]) -> None:
        if self.x_translation and self.x_translation != 0:
            coords[0] += self.x_translation
        if self.y_translation and self.y_translation != 0:
            coords[1] += self.y_translation
        if self.z_translation and self.z_translation != 0:
            coords[2] += self.z_translation if len(coords) > 2 else 0

        return coords

    def create_point_geom(self, coords: List[float]) -> Point:
        coords = self.translate_point_coordinates(coords)
        if self.epsg != "EPSG:4326":
            coords = self.epsg_transformer.transform(*coords)
        lng, lat = coords

        return Point(lng, lat, srid=4326)

    def create_line_geom(self, coords: List[List[float]]) -> LineString:
        coords = [self.translate_point_coordinates(coord) for coord in coords]
        if self.epsg != "EPSG:4326":
            coords = [self.epsg_transformer.transform(*coord) for coord in coords]

        return LineString([Point(lng, lat, srid=4326) for lng, lat in coords])

    def create_polygon_geom(self, coords: List[List[List[float]]]) -> Polygon:
        rings = [
            [self.translate_point_coordinates(coord) for coord in ring]
            for ring in coords
        ]
        if self.epsg != "EPSG:4326":
            rings = [
                [self.epsg_transformer.transform(*coord) for coord in ring]
                for ring in rings
            ]
        rings_points = [
            [Point(lng, lat, srid=4326) for lng, lat in ring] for ring in rings
        ]

        return Polygon(rings_points[0], *rings_points[1:])

    def create_geoms(self) -> None:
        for index, coords in enumerate(self.coords):
            geom_type = self.types[index].lower()
            if geom_type == "point":
                self.geoms.append(self.create_point_geom(coords))

            elif geom_type == "linestring":
                self.geoms.append(self.create_line_geom(coords))

            elif geom_type == "polygon":
                self.geoms.append(self.create_polygon_geom(coords))

    def merge_arrays_to_create_pois(self) -> None:
        self.pois = [
            {
                "campaign": self.campaign,
                "tag": tag,
                "color": color,
                "geom": geom,
            }
            for (
                tag,
                color,
                geom,
            ) in zip(
                self.tags,
                self.colors,
                self.geoms,
            )
        ]

    def __create_poi(
        self, poi: Dict[str, any]
    ) -> Tuple[Poi, List[Poi_Resource]]:
        return Poi_Locations(**poi)

    def save_pois(self) -> None:
        try:
            poi_list = [self.__create_poi(poi) for poi in self.pois]
            Poi_Locations.objects.bulk_create(poi_list, batch_size=1000)  # Up to 2000
            return True
        except Exception as e:
            print(e)
            return False


class GeoJSONPoiLocationsUploader(PoiLocationsUploader):

    def __load_feature(self, feature: Dict[str, any]) -> None:
        properties = feature.get("properties")
        geom_type = feature.get("geometry").get("type")
        coordinates = feature.get("geometry").get("coordinates")
        data = {
            "tag": properties.get("tag"),
            "color": properties.get("color"),
            "type": geom_type,
        }
        if geom_type.lower() == "point":
            data.update({
                "coords": list(map(float_or_none, coordinates)),
            })
        elif geom_type.lower() == "linestring":
            data.update({
                "coords": [list(map(float_or_none, coord)) for coord in coordinates],
            })
        elif geom_type.lower() == "polygon":
            data.update({
                "coords": [
                    [list(map(float_or_none, coord)) for coord in ring]
                    for ring in coordinates
                ]
            })
        self._load_data(data)

    def read_file(self) -> None:
        content = self.file_to_upload.read()
        geojson = json.loads(content)
        [self.__load_feature(feature) for feature in geojson.get("features")]
