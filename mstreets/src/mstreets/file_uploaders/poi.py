import os
import json

from abc import ABC, abstractmethod
import math
from typing import Dict, List, Tuple

from pyproj import Transformer
from datetime import datetime

from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from mstreets.models import Poi, Poi_Resource, Campaign


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

    def __init__(self, file_path: str, form_data: Dict[str, any]) -> None:
        self.file_path = file_path
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

    def _get_filename(self, filename: str) -> str:
        # if self.is_file_folder_prefix:
        #     return self.file_folder + "/" + filename

        return filename

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


class CSVv2PoiUploader(PoiUploader):

    def __date_time_to_datetime(self, date: str, time: str) -> datetime:
        year, month, day = map(int, date.split('-'))
        hour, min, sec = map(int, map(float, time.replace('\r', '').replace('\n', '').split(':')))
        return make_aware(datetime(year, month, day, hour, min, sec))

    def __line_to_poi_and_resources(self, line: str) -> None:
        filename, _, x, y, altitude, roll, pitch, pan, _, _, _, _, _, _, _, _, _, date, time = line.split(',')
        file = ''
        suffix = ''
        file_type = ''
        if self.has_laterals:
            split_filename = filename.split(self.spherical_suffix_separator)
            file = self.spherical_suffix_separator.join(split_filename[:-1])
            suffix, file_type = split_filename[-1].split('.')
        if not self.has_laterals or suffix == self.spherical_suffix:
            self.filenames.append(str(filename))
            self.formats.append(None)
            self.types.append('PANO')
            self.dates.append(self.__date_time_to_datetime(date, time))
            self.altitudes.append(float(altitude))
            self.rolls.append(float(roll))
            self.pitchs.append(float(pitch))
            self.pans.append(float(pan))
            self.folders.append('10_Sphericals')
            self.tags.append(None)
            self.configs.append(None)
            self.lngs.append(float(x))
            self.lats.append(float(y))
            self.resources.append([])
        else:
            poi_name = f'{file}{self.spherical_suffix_separator}{self.spherical_suffix}.{file_type}'
            if poi_name not in self.filenames:
                print(f"El POI {poi_name} no existeix")
                return

            resource_filename = self._get_filename(filename)
            folder = self.RESOURCES_DIRS[suffix]
            resource_folder = self._get_folder(folder)
            index = self.filenames.index(poi_name)
            self.resources[index].append({
                'campaign': self.campaign,
                'poi': None,
                'filename': resource_filename,
                'format': 'JPG',
                'pitch': float(pitch),
                'pan': float(pan),
                'folder': resource_folder,
                'tag': None
            })

    def read_file(self) -> None:
        self.file_to_upload.readline()
        [self.__line_to_poi_and_resources(line) for line in self.file_to_upload.readlines()]


class GeoJSONPoiUploader(PoiUploader):

    def __validate_feature(self, feature: Dict[str, any]) -> Tuple[Dict[str, any], List[float]]:
        assert feature is not None, 'Hi ha una feature sense dades'

        geometry = feature.get('geometry')
        properties = feature.get('properties')
        is_valid = isinstance(properties, dict) and isinstance(geometry, dict)
        assert is_valid, 'Totes les features han de tenir les claus properties i geometry com a objectes'

        geometry_type = geometry.get("type")
        assert geometry_type and geometry_type.lower() == 'point', f'El tipus de geometria ha de ser Point enlloc de {geometry_type}'

        coordinates = geometry.get('coordinates')
        assert isinstance(coordinates, list), 'Les geometries han de tenir una clau coordinates amb un llistat de coordenades'

        return properties, coordinates

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
        properties, coordinates = self.__validate_feature(feature)

        self.filenames.append(properties.get('filename'))
        self.formats.append(None)
        self.types.append(properties.get('type'))
        date_string = properties.get("date")
        if date_string:
            date = make_aware(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ"))
            self.dates.append(date)
        self.altitudes.append(float(properties.get('altitude', 0)))
        self.rolls.append(float(properties.get('roll', 0)))
        self.pitchs.append(float(properties.get('pitch', 0)))
        self.pans.append(float(properties.get('pan', 0)))
        self.folders.append(properties.get('folder'))
        self.tags.append(properties.get('tag'))
        self.configs.append(None)
        self.lngs.append(float(coordinates[0]))
        self.lats.append(float(coordinates[1]))
        self.resources.append(self.__get_resources(properties))

    def read_file(self) -> None:
        content = self.file_to_upload.read()
        geojson = json.loads(content)
        [self.__load_feature(feature) for feature in geojson.get('features')]
