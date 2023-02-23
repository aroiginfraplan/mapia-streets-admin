from abc import ABC, abstractmethod
from pyproj import Transformer

from django.contrib.gis.geos import Polygon

from mstreets.models import PC


class PCUploader(ABC):
    campaign = None
    file_format = None
    file = None
    epsg = None
    file_folder = None

    def __init__(self, file_to_upload, form_data):
        self.file_to_upload = file_to_upload
        self.campaign = form_data['campaign']
        self.epsg_transformer = Transformer.from_crs(form_data['epsg'], 'EPSG:4326')
        self.file_folder = form_data['file_folder']

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

    def create_pcs(self):
        self.create_geoms()
        self.set_file_folder()
        self.merge_arrays_to_create_pcs()

    def transform_coordinates(self, polygons):
        return [self.epsg_transformer.transform(polygon[0], polygon[1])[::-1] for polygon in polygons]

    def create_geoms(self):
        if self.epsg != 'EPSG:4326':
            self.geoms = [
                Polygon(self.transform_coordinates(polygon), srid=4326)
                for polygon in self.polygons
            ]
        else:
            self.geoms = [Polygon(polygon, srid=4326) for polygon in self.polygons]

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
            [PC(**pc).save() for pc in self.pcs]
            return True
        except Exception as e:
            return False


class CSVPCUploader(PCUploader):
    def __calculate_polygon(self, x_min, x_max, y_min, y_max):
        return [
            [x_min, y_min],
            [x_max, y_min],
            [x_max, y_max],
            [x_min, y_max],
            [x_min, y_min]
        ]

    def __line_to_pc(self, line):
        filename, x_min, x_max, y_min, y_max = line.decode('utf-8').replace('\r', '').replace('\n', '').split(',')
        self.names.append(str(filename))
        self.filenames.append(str(filename))
        self.is_locals.append(False)
        self.is_downloadables.append(False)
        self.formats.append('POTREE2')
        self.folders.append('')
        self.tags.append(None)
        self.configs.append(None)
        polygon = self.__calculate_polygon(int(x_min), int(x_max), int(y_min), int(y_max))
        self.polygons.append(polygon)

    def read_file(self):
        try:
            self.file_to_upload.readline()
            [self.__line_to_pc(line) for line in self.file_to_upload.readlines()]
        except ValueError:
            print('Invalid CSV field type')
