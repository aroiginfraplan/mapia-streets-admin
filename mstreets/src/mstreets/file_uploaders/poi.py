import os
import json

from abc import ABC, abstractmethod
import math
from typing import Dict, List, Tuple, Union

from pyproj import Transformer
from datetime import datetime

from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from mstreets.models import Poi, Poi_Resource, Campaign
from mstreets.file_uploaders.utils import float_or_none


class PoiUploader(ABC):
    RESOURCES_DIRS = {
        "01": "20_L1",
        "02": "30_L4",
        "03": "40_L3",
        "04": "50_L4",
    }

    campaign = None
    epsg = None
    has_laterals = False
    spherical_suffix = 'sp'
    spherical_suffix_separator = '_'
    x_translation = None
    y_translation = None
    z_translation = None
    file_folder = None
    # is_file_folder_prefix = None
    tag = None
    date = None
    angle_format = None
    pan_correction = None

    def __init__(
        self, file_path: str, form_data: Dict[str, any], required_fields: List[str]
    ) -> None:
        self.file_path = file_path
        self.required_fields = required_fields
        self.file_to_upload = open(file_path, 'r')
        self.has_laterals = form_data['has_laterals']
        self.spherical_suffix = form_data['spherical_suffix']
        self.spherical_suffix_separator = form_data['spherical_suffix_separator']
        self.campaign = Campaign.objects.get(pk=form_data['campaign'])
        self.epsg_transformer = Transformer.from_crs(form_data['epsg'], 'EPSG:4326')
        self.x_translation = form_data['x_translation']
        self.y_translation = form_data['y_translation']
        self.z_translation = form_data['z_translation']
        self.file_folder = form_data['file_folder']
        # self.is_file_folder_prefix = form_data['is_file_folder_prefix']
        self.tag = form_data['tag']
        self.date = form_data['date']
        self.angle_format = form_data['angle_format']
        self.pan_correction = form_data['pan_correction']
        self.filenames = []
        self.formats = []
        self.types = []
        self.dates = []
        self.altitudes = []
        self.rolls = []
        self.pitchs = []
        self.pans = []
        self.folders = []
        self.tags = []
        self.configs = []
        self.lngs = []
        self.lats = []
        self.geoms = []
        self.pois = []
        self.resources = []

    def __has_missing_data(self, data: Dict[str, any]) -> bool:
        missing_fields = [
            field for field in self.required_fields if data.get(field) is None
        ]

        return len(missing_fields) > 0

    def _load_data(self, data: Dict[str, any]) -> None:
        if self.__has_missing_data(data):
            return False

        self.filenames.append(data.get('filename'))
        self.formats.append(data.get('format'))
        self.types.append(data.get('type'))
        self.dates.append(data.get('date'))
        self.altitudes.append(data.get('altitude'))
        self.rolls.append(data.get('roll'))
        self.pitchs.append(data.get('pitch'))
        self.pans.append(data.get('pan'))
        self.folders.append(data.get('folder'))
        self.tags.append(data.get('tag'))
        self.configs.append(data.get('config'))
        self.lngs.append(data.get('lng'))
        self.lats.append(data.get('lat'))
        return True

    def _get_folder(self, folder: str) -> str:
        if self.file_folder:
            return self.file_folder + "/" + folder

        return folder

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
        self.correct_altitude()
        self.convert_pan_to_degrees()
        self.correct_pan()
        self.set_file_folder()
        self.merge_arrays_to_create_pois()

    def modify_pois_with_form_corrections(self) -> None:
        pass

    def create_geoms(self) -> None:
        if self.x_translation and self.x_translation != 0:
            self.lngs = [lng + self.x_translation for lng in self.lngs]

        if self.y_translation and self.y_translation != 0:
            self.lats = [lat + self.y_translation for lat in self.lats]

        if self.epsg != 'EPSG:4326':
            self.geoms = [
                Point(self.epsg_transformer.transform(lng, lat)[::-1], srid=4326)
                for lng, lat in zip(self.lngs, self.lats)
            ]
        else:
            self.geoms = [Point(lng, lat, srid=4326) for lng, lat in zip(self.lngs, self.lats)]

    def correct_altitude(self) -> None:
        if self.z_translation and self.z_translation != 0:
            self.altitudes = [altitude + self.z_translation for altitude in self.altitudes]

    def correct_pan(self) -> None:
        if self.pan_correction and self.pan_correction != 0:
            self.pans = [pan + self.pan_correction for pan in self.pans]

    def convert_pan_to_degrees(self) -> None:
        conversion_factor = 1
        if self.angle_format == 'rad':
            conversion_factor = 180 / math.PI
        elif self.angle_format == 'gra':
            conversion_factor = 0.9  # 180 / 200
        elif self.angle_format == 'sex':
            return
        self.pans = [pan * conversion_factor for pan in self.pans]

    def set_file_folder(self) -> None:
        if not self.file_folder:
            return
        # if self.is_file_folder_prefix:
        #     self.filenames = [self.file_folder + '/' + filename for filename in self.filenames]
        # else:
        self.folders = [
            self.file_folder if folder is None else self.file_folder + '/' + folder
            for folder in self.folders
        ]

    def merge_arrays_to_create_pois(self) -> None:
        self.pois = [
            {
                'campaign': self.campaign,
                'filename': filename,
                'format': format,
                'type': type,
                'date': self.date if date is None else date,
                'altitude': altitude,
                'roll': roll,
                'pitch': pitch,
                'pan': pan,
                'folder': folder,
                'tag': tag,
                'config': config,
                'geom': geom,
                'resources': resources,
            }
            for (
                filename, format, type, date, altitude, roll, pitch, pan,
                folder, tag, config, geom, resources
            ) in zip(
                self.filenames, self.formats, self.types, self.dates, self.altitudes,
                self.rolls, self.pitchs, self.pans, self.folders, self.tags, self.configs, self.geoms,
                self.resources
            )
        ]

    def __create_poi_and_resources_objects(self, poi: Dict[str, any]) -> Tuple[Poi, List[Poi_Resource]]:
        resources = poi.pop("resources", None)
        poi = Poi(**poi)
        if not resources:
            return poi, []

        poi_resources = []
        for resource in resources:
            resource['poi'] = poi
            poi_resources.append(Poi_Resource(**resource))

        return poi, poi_resources

    def save_pois(self) -> None:
        try:
            poi_list = []
            poi_resources_list = []
            for poi in self.pois:
                poi_object, poi_resources_objects = (
                    self.__create_poi_and_resources_objects(poi)
                )
                poi_list.append(poi_object)
                poi_resources_list += poi_resources_objects

            Poi.objects.bulk_create(poi_list, batch_size=1000)  # Up to 2000
            Poi_Resource.objects.bulk_create(poi_resources_list, batch_size=1000)  # Up to 4000
            return True
        except Exception as e:
            print(e)
            return False


class CSVPoiUploader(PoiUploader):

    @classmethod
    @abstractmethod
    def get_line_data(cls, line: str) -> Tuple[str, str, str, str, str, str, str, str, str]:
        pass

    def __split_filename_extension(self, filename: str) -> str:
        split_filename = filename.split(".")
        extension = split_filename[-1]
        return ".".join(split_filename[:-1]), extension

    def __get_lateral_type(self, filename: str) -> Union[str, None]:
        filename_without_extension, _ = self.__split_filename_extension(filename)
        filename_parts = filename_without_extension.split(
            self.spherical_suffix_separator
        )
        for key in self.RESOURCES_DIRS.keys():
            if key in filename_parts:
                return key

    def __get_resource_folder(self, filename: str) -> str:
        lateral_type = self.__get_lateral_type(filename)
        return self._get_folder(self.RESOURCES_DIRS.get(lateral_type))

    def __is_spherical_file(self, filename: str) -> bool:
        filename, _ = self.__split_filename_extension(filename)
        return self.spherical_suffix in filename.split(self.spherical_suffix_separator)

    def __get_spherical_filename(self, filename: str) -> str:
        lateral_type = self.__get_lateral_type(filename)
        filename, extension = self.__split_filename_extension(filename)
        spherical_filename = filename.replace(
            f"{self.spherical_suffix_separator}{lateral_type}",
            f"{self.spherical_suffix_separator}{self.spherical_suffix}",
        )
        return f"{spherical_filename}.{extension}"

    def __date_time_to_datetime(self, date: str, time: str) -> datetime:
        year, month, day = map(int, date.split('-'))
        hour, min, sec = map(int, map(float, time.replace('\r', '').replace('\n', '').split(':')))
        return make_aware(datetime(year, month, day, hour, min, sec))

    def __line_to_poi_and_resources(self, line: str) -> None:
        filename, x, y, altitude, roll, pitch, pan, date, time = self.get_line_data(line)
        if not self.has_laterals or self.__is_spherical_file(filename):
            data = {
                'filename': filename,
                'format': None,
                'type': 'PANO',
                'date': self.__date_time_to_datetime(date, time),
                'altitude': float_or_none(altitude),
                'roll': float_or_none(roll),
                'pitch': float_or_none(pitch),
                'pan': float_or_none(pan),
                'folder': '10_Sphericals',
                'tag': None,
                'config': None,
                'lng': float_or_none(x),
                'lat': float_or_none(y),
            }
            loaded = self._load_data(data)
            if loaded:
                self.resources.append([])
        else:
            poi_name = self.__get_spherical_filename(filename)
            if poi_name not in self.filenames:
                print(f"El POI {poi_name} no existeix")
                return

            resource_folder = self.__get_resource_folder(filename)
            index = self.filenames.index(poi_name)
            self.resources[index].append({
                'campaign': self.campaign,
                'poi': None,
                'filename': filename,
                'format': 'JPG',
                'pitch': float(pitch),
                'pan': float(pan),
                'folder': resource_folder,
                'tag': None
            })

    def read_file(self) -> None:
        self.file_to_upload.readline()
        [self.__line_to_poi_and_resources(line) for line in self.file_to_upload.readlines()]


class CSVv2PoiUploader(CSVPoiUploader):
    @classmethod
    def get_line_data(cls, line: str) -> Tuple[str, str, str, str, str, str, str, str, str]:
        filename, _, x, y, altitude, roll, pitch, pan, _, _, _, _, _, _, _, _, _, date, time = line.split(',')
        return filename, x, y, altitude, roll, pitch, pan, date, time


class CSVv3PoiUploader(CSVPoiUploader):
    @classmethod
    def get_line_data(cls, line: str) -> Tuple[str, str, str, str, str, str, str, str, str]:
        filename, _, x, y, altitude, _, _, _, _, pan, roll, pitch, _, _, _, _, _, _, _, _, _, date, time, _ = line.split(',')
        return filename, x, y, altitude, roll, pitch, pan, date, time


class GeoJSONPoiUploader(PoiUploader):

    def __get_resources(self, properties: Dict[str, any]) -> Dict[str, any]:
        resources = properties.get('resources')
        if not isinstance(resources, list):
            return []

        for resource in resources:
            resource.update(
                {
                    'campaign': self.campaign,
                    'filename': resource.get('filename'),
                    'folder': resource.get('folder'),
                    'format': "JPG",
                }
            )

        return resources

    def __load_feature(self, feature: Dict[str, any]) -> None:
        properties = feature.get("properties")
        coordinates = feature.get("geometry").get("coordinates")
        date_string = properties.get("date")
        date = None
        if date_string:
            date = make_aware(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ"))
        data = {
            'filename': properties.get('filename'),
            'format': None,
            'type': properties.get('type'),
            'date': date,
            'altitude': float_or_none(properties.get('altitude')),
            'roll': float_or_none(properties.get('roll')),
            'pitch': float_or_none(properties.get('pitch')),
            'pan': float_or_none(properties.get('pan')),
            'folder': properties.get('folder'),
            'tag': properties.get('tag'),
            'config': properties.get('config'),
            'lng': float_or_none(coordinates[0]),
            'lat': float_or_none(coordinates[1]),
        }
        loaded = self._load_data(data)
        if loaded:
            self.resources.append(self.__get_resources(properties))

    def read_file(self) -> None:
        content = self.file_to_upload.read()
        geojson = json.loads(content)
        [self.__load_feature(feature) for feature in geojson.get('features')]
