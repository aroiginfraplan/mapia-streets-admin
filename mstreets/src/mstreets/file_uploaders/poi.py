from abc import ABC, abstractmethod
import math
from pyproj import Transformer
from datetime import datetime

from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware

from mstreets.models import Poi, Poi_Resource


class PoiUploader(ABC):
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
        self.campaign = form_data['campaign']
        self.epsg_transformer = Transformer.from_crs(form_data['epsg'], 'EPSG:4326')
        self.x_translation = form_data['x_translation']
        self.y_translation = form_data['y_translation']
        self.z_translation = form_data['z_translation']
        self.file_folder = form_data['file_folder']
        self.is_file_folder_prefix = form_data['is_file_folder_prefix']
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
        self.set_file_folder()
        self.merge_arrays_to_create_pois()

    def modify_pois_with_form_corrections(self):
        pass

    def create_geoms(self):
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
            self.folders = [
                self.file_folder if folder is None else self.file_folder + '/' + folder
                for folder in self.folders
            ]

    def merge_arrays_to_create_pois(self):
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
            self.pois = [Poi(**poi) for poi in self.pois]
            [poi.save() for poi in self.pois]
            return True
        except Exception as e:
            return False


class CSVPoiUploader(PoiUploader):
    def __line_to_poi(self, line):
        filename, _, _, _, _, _, x, y, altitude, roll, pitch, pan, _ = line.decode('utf-8').split(',')

        self.filenames.append(str(filename))
        self.formats.append(None)
        self.types.append('PANO')
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


class CSVv2PoiUploader(PoiUploader):
    def __date_time_to_datetime(self, date, time):
        year, month, day = map(int, date.split('-'))
        hour, min, sec = map(int, map(float, time.replace('\r', '').replace('\n', '').split(':')))
        return make_aware(datetime(year, month, day, hour, min, sec))

    def __line_to_poi(self, line):
        filename, _, x, y, altitude, roll, pitch, pan, _, _, _, _, _, _, _, _, _, date, time = line.decode('utf-8').split(',')
        filename = filename[:-4] + '_sp' + filename[-4:]
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

    def read_file(self):
        self.file_to_upload.readline()
        [self.__line_to_poi(line) for line in self.file_to_upload.readlines()]
    

class IMLPoiUploader(PoiUploader):
    resources = {}

    def __read_iml(self, iml):
        lines = self.file_to_upload.readlines()
        for line in lines:
            line = line.decode('UTF-8')
            if '=' in line:
                column, value = line.split('=')
                iml[column].append(value.replace("\n", "").replace("\r", ""))
        
        for xyz in iml['Xyz']:
            x, y, z = xyz.split(' ')
            iml['x'].append(x)
            iml['y'].append(y)
            iml['z'].append(z)

        for hrp in iml['Hrp']:
            h, r, p = hrp.split(' ')
            iml['pan'].append(h)
            iml['roll'].append(r)
            iml['pitch'].append(p)
        
        return iml

    def __set_poi_fields(self, iml, i):
        self.filenames.append(str(iml['Image'][i]))
        self.formats.append(None)
        self.types.append('PANO')
        self.dates.append(None)
        self.altitudes.append(float(iml['z'][i]))
        self.rolls.append(float(iml['roll'][i]))
        self.pitchs.append(float(iml['pitch'][i]))
        self.pans.append(float(iml['pan'][i]))
        self.folders.append('spherical')
        self.tags.append(None)
        self.configs.append(None)
        self.lngs.append(float(iml['x'][i]))
        self.lats.append(float(iml['y'][i]))
        self.resources[str(iml['Image'][i])] = []
    
    def __set_resources_dict(self, iml, i):
        poi_filename = str(iml['Image'][i])[:-6] + 'sp.jpg'
        if poi_filename in self.resources:
            folder = 'L0' + iml['Camera'][i]
            if self.is_file_folder_prefix:
                filename = self.file_folder + '/' + str(iml['Image'][i])
            else:
                filename = str(iml['Image'][i])
            if self.file_folder:
                folder = self.file_folder + '/' + folder
            self.resources[poi_filename].append({
                'campaign': self.campaign,
                'poi': None,
                'filename': filename,
                'format': 'JPG',
                'pitch': float(iml['pitch'][i]),
                'pan': float(iml['pan'][i]),
                'folder': folder,
                'tag': None
            })

    def __iml_to_pois_and_resources(self, iml):
        for i in range(len(iml['Image'])):
            if iml['Camera'][i] == '0':
                self.__set_poi_fields(iml, i)
            else:
                self.__set_resources_dict(iml, i)

    def read_file(self):
        iml = {
            'Image': [],
            'Time': [],
            'Xyz': [],
            'x': [],
            'y': [],
            'z': [],
            'Hrp': [],
            'pan': [],
            'roll': [],
            'pitch': [],
            'Camera': [],
            'Quality': [],
            'Line': [],
            'Color': [],
            'AccuracyXyz': []
        }
        iml = self.__read_iml(iml)
        self.__iml_to_pois_and_resources(iml)

    def __create_poi_resource(self, resource, poi):
        resource['poi'] = poi
        Poi_Resource(**resource).save()

    def __create_poi_resources(self, poi):
        poi_name = getattr(poi, 'filename').split('/')[-1]
        [self.__create_poi_resource(resource, poi) for resource in self.resources[poi_name]]

    def __create_pois_resources(self):
        [self.__create_poi_resources(poi) for poi in self.pois]

    def upload_file(self):
        if super().upload_file():
            self.__create_pois_resources()
            return True
        else:
            return False
