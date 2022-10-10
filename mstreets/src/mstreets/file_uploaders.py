from abc import ABC, abstractmethod
import math

from django.contrib.gis.geos import Point
from django.contrib.gis.gdal import DataSource

from .models import Poi


class PoiUploader(ABC):
    file_to_upload = ''
    filenames = []
    formats = []
    types = []
    dates = []
    altitudes = []
    rolls = []
    pitchs = []
    pans = []
    folders = []
    tags = []
    configs = []
    lngs = []
    lats = []
    geoms = []

    pois = []

    zone = None
    campaign = None
    epsg = None
    x_translation = None
    y_translation = None
    z_translation = None
    file_folder = None
    is_file_folder_prefix = None
    tag = None
    date = None
    angle_format = None
    pan_correction = None

    def __init__(self, file_to_upload, form_data):
        self.file_to_upload = file_to_upload
        self.zone = form_data['zone']
        self.campaign = form_data['campaign']
        self.epsg = form_data['epsg']
        self.x_translation = form_data['x_translation']
        self.y_translation = form_data['y_translation']
        self.z_translation = form_data['z_translation']
        self.file_folder = form_data['file_folder']
        self.is_file_folder_prefix = form_data['is_file_folder_prefix']
        self.tag = form_data['tag']
        self.date = form_data['date']
        self.angle_format = form_data['angle_format']
        self.pan_correction = form_data['pan_correction']

    def upload_file(self):
        self.read_file()
        self.create_pois()
        return self.save_pois()

    @abstractmethod
    def read_file(self):
        pass

    def create_pois(self):
        self.create_geoms()
        self.correct_altitude()
        self.convert_pan_to_degrees()
        self.correct_pan()
        self.merge_arrays_to_create_pois()
        self.set_file_folder()

    def modify_pois_with_form_corrections(self):
        pass

    def create_geoms(self):
        if self.x_translation and self.x_translation != 0:
            self.lngs = [lng + self.x_translation for lng in self.lngs]

        if self.y_translation and self.y_translation != 0:
            self.lats = [lat + self.y_translation for lat in self.lats]

        self.geoms = [Point(lng, lat, srid=int(self.epsg)).transform(4326, clone=True) for lng, lat in zip(self.lngs, self.lats)]

    def correct_altitude(self):
        if self.z_translation and self.z_translation != 0:
            self.altitudes = [altitude + self.z_translation for altitude in self.altitudes]

    def correct_pan(self):
        if self.pan_correction and self.pan_correction != 0:
            self.pans = [pan + self.pan_correction for pan in self.pans]

    def convert_pan_to_degrees(self):
        conversion_factor = 1
        if self.angle_format == 'rad':
            conversion_factor = 180 / math.PI
        elif self.angle_format == 'gra':
            conversion_factor = 0.9  # 180 / 200
        elif self.angle_format == 'sex':
            return
        self.pans = [pan * conversion_factor for pan in self.pans]

    def set_file_folder(self):
        if not self.file_folder:
            return
        if self.is_file_folder_prefix:
            self.filenames = [self.file_folder + '/' + filename for filename in self.filenames]
        else:
            self.folders = [self.file_folder for folder in self.folders]

    def merge_arrays_to_create_pois(self):
        self.pois = [
            {
                'zone': self.zone,
                'campaign': self.campaign,
                'filename': filename,
                'format': format,
                'type': 'PANO' if type is None else type,
                'date': self.date if date is None else date,
                'altitude': altitude,
                'roll': roll,
                'pitch': pitch,
                'pan': pan,
                'folder': folder,
                'tag': tag,
                'config': config,
                'geom': geom
            }
            for (
                filename, format, type, date, altitude, roll, pitch, pan,
                folder, tag, config, geom
            ) in zip(
                self.filenames, self.formats, self.types, self.dates, self.altitudes,
                self.rolls, self.pitchs, self.pans, self.folders, self.tags, self.configs, self.geoms
            )
        ]

    def save_pois(self):
        try:
            [Poi(**poi).save() for poi in self.pois]
            return True
        except Exception as e:
            return False


class CSVPoiUploader(PoiUploader):
    def __line_to_poi(self, line):
        filename, _, _, _, _, _, x, y, altitude, roll, pitch, pan, _ = line.decode('utf-8').split(',')

        self.filenames.append(str(filename))
        self.formats.append(None)
        self.types.append(None)
        self.dates.append(None)
        self.altitudes.append(float(altitude))
        self.rolls.append(float(roll))
        self.pitchs.append(float(pitch))
        self.pans.append(float(pan))
        self.folders.append(None)
        self.tags.append(None)
        self.configs.append(None)
        self.lngs.append(float(x))
        self.lats.append(float(y))

    def read_file(self):
        try:
            self.file_to_upload.readline()
            [self.__line_to_poi(line) for line in self.file_to_upload.readlines()]
        except ValueError:
            print('Invalid CSV field type')
