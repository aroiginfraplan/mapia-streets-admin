import json

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from pyproj import Transformer

from django.contrib.gis.geos import Polygon

from mstreets.file_uploaders.utils import float_or_none
from mstreets.models import PC


class PCUploader(ABC):
    campaign = None
    file_format = None
    file = None
    epsg = None
    file_folder = None

    def __init__(self, file_to_upload, form_data, required_fields):
        self.file_to_upload = file_to_upload
        self.required_fields = required_fields
        self.campaign = form_data['campaign']
        self.epsg_transformer = Transformer.from_crs(form_data['epsg'], 'EPSG:4326')
        self.file_folder = form_data['file_folder']
        self.pc_format = form_data['pc_format']

        self.polygons = []

        self.names = []
        self.filenames = []
        self.is_locals = []
        self.is_downloadables = []
        self.formats = []
        self.folders = []
        self.tags = []
        self.configs = []
        self.geoms = []
        self.pcs = []

    def upload_file(self):
        self.read_file()
        self.create_pcs()
        return self.save_pcs()

    @abstractmethod
    def read_file(self):
        pass

    def __has_missing_data(self, data: Dict[str, any]) -> bool:
        missing_fields = [
            field for field in self.required_fields if data.get(field) is None
        ]

        return len(missing_fields) > 0

    def _load_data(self, data: Dict[str, Any]) -> None:
        if self.__has_missing_data(data):
            return

        self.names.append(data.get('filename'))
        self.filenames.append(data.get('filename'))
        self.is_locals.append(data.get('is_local'))
        self.is_downloadables.append(data.get('is_downloadable'))
        self.formats.append(data.get('format'))
        self.folders.append(data.get('folder'))
        self.tags.append(data.get('tag'))
        self.configs.append(data.get('config'))
        self.polygons.append(data.get('polygon'))

    def create_pcs(self):
        self.create_geoms()
        self.set_file_folder()
        self.merge_arrays_to_create_pcs()

    def transform_coordinates(self, ring):
        return [
            self.epsg_transformer.transform(coordinates[1], coordinates[0])[::-1]
            for coordinates in ring
        ]

    def create_geoms(self):
        if self.epsg != 'EPSG:4326':
            for polygon in self.polygons:
                linear_rings = [self.transform_coordinates(ring) for ring in polygon]
                self.geoms.append(Polygon(*linear_rings, srid=4326))
        else:
            self.geoms = [Polygon(*polygon, srid=4326) for polygon in self.polygons]

    def set_file_folder(self):
        if not self.file_folder:
            return
        self.folders = [
            self.file_folder if folder is None else self.file_folder + '/' + folder
            for folder in self.folders
        ]

    def merge_arrays_to_create_pcs(self):
        self.pcs = [
            {
                'campaign': self.campaign,
                'name': name,
                'filename': filename,
                'is_local': is_local,
                'is_downloadable': is_downloadable,
                'format': format,
                'folder': folder,
                'tag': tag,
                'config': config,
                'geom': geom,
            }
            for (
                name, filename, is_local, is_downloadable, format, folder, tag, config, geom
            ) in zip(
                self.names, self.filenames, self.is_locals, self.is_downloadables,
                self.formats, self.folders, self.tags, self.configs, self.geoms
            )
        ]

    def save_pcs(self):
        try:
            pc_objects = [PC(**pc) for pc in self.pcs]
            PC.objects.bulk_create(pc_objects, batch_size=1000)
            return True
        except Exception as e:
            return False


class CSVPCUploader(PCUploader):
    def __calculate_polygon(self, x_min, x_max, y_min, y_max):
        if not all([x_min, x_max, y_min, y_max]):
            return None

        return [
            [
                [x_min, y_min],
                [x_max, y_min],
                [x_max, y_max],
                [x_min, y_max],
                [x_min, y_min],
            ]
        ]

    @classmethod
    def get_line_data(cls, line: str) -> Tuple[str, str, str, str, str]:
        filename, x_min, x_max, y_min, y_max = line.split(",")
        return filename, x_min, x_max, y_min, y_max

    def __line_to_pc(self, line):
        line = line.decode("utf-8").replace("\r", "").replace("\n", "")
        filename, x_min, x_max, y_min, y_max = self.get_line_data(line)
        polygon = self.__calculate_polygon(
            float_or_none(x_min),
            float_or_none(x_max),
            float_or_none(y_min),
            float_or_none(y_max),
        )
        data = {
            'name': filename,
            'filename': filename,
            'is_local': False,
            'is_downloadable': False,
            'format': self.pc_format,
            'folder': '',
            'tag': None,
            'config': None,
            'polygon': polygon,
        }
        self._load_data(data)

    def read_file(self):
        try:
            self.file_to_upload.readline()
            [self.__line_to_pc(line) for line in self.file_to_upload.readlines()]
        except ValueError:
            print('Invalid CSV field type')


class GeoJSONPCUploader(PCUploader):

    def __get_folder(self, folder: str) -> str:
        if self.file_folder:
            folder = self.file_folder + '/' + folder
            return folder.replace('//', '/')

        return folder

    def __feature_to_pc(self, feature):
        properties = feature.get('properties')
        coordinates = feature.get('geometry').get('coordinates')
        filename = properties.get('filename')
        data = {
            'name': filename,
            'filename': filename,
            'is_local': properties.get('is_local', False),
            'is_downloadable': properties.get('is_downloadable', False),
            'format': self.pc_format,
            'folder': self.__get_folder(properties.get('folder')),
            'tag': properties.get('tag'),
            'config': properties.get('config'),
            'polygon': coordinates,
        }
        self._load_data(data)

    def read_file(self):
        content = self.file_to_upload.read()
        geojson = json.loads(content)
        [self.__feature_to_pc(feature) for feature in geojson.get('features')]
