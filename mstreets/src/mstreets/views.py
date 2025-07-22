import mimetypes
import os
import stat
from datetime import datetime

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.forms import Form
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404, HttpResponseNotModified
from django.utils.http import http_date
from django.shortcuts import render, redirect
from django.views.static import was_modified_since

import boto3
from botocore.client import Config

from mstreets.forms import (
    DefaultConfigForm, UploadPCFileForm, UploadPoi_LocationsFileForm, UploadPoiFileForm,
    config_help_text, 
)
from mstreets.models import Config as ConfigModel
from .settings import (AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME, AWS_S3_ENDPOINT_URL,
                       AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, PANORAMAS_ROOT)
from mstreets.file_uploaders import (
    async_handle_uploaded_file,
    CSVPCUploader,
    GeoJSONPCUploader,
    GeoJSONPoiLocationsUploader,
)


def panoramas_files_server(request, path):
    fullpath = os.path.realpath(os.path.join(PANORAMAS_ROOT, path))
    if not os.path.exists(fullpath):
        if AWS_STORAGE_BUCKET_NAME:
            return panoramas_files_s3(request, path)
        else:
            raise Http404('"{0}" does not exist'.format(path))

    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    content_type = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'

    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(content_type=content_type)

    response = HttpResponse(open(fullpath, 'rb').read(), content_type=content_type)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    # filename = os.path.basename(path)
    # response['Content-Disposition'] = smart_str(u'attachment; filename={0}'.format(filename))
    return response


def panoramas_files_s3(request, path):
    s3 = boto3.client(
        service_name='s3',
        region_name=AWS_S3_REGION_NAME,
        endpoint_url=AWS_S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(s3={'addressing_style': 'virtual'})
    )
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        ExpiresIn=3600,
        Params={
            "Bucket": AWS_STORAGE_BUCKET_NAME,
            "Key": path,
        },
    )
    return HttpResponseRedirect(url)


def add_default_config(request):
    if 'apply' in request.POST:
        fields = [
            'api_url', 'api_info_url', 'folder_poi', 'folder_img', 'folder_pc',
            'page_panellum', 'page_no_img', 'page_potree',
            'wms_locations', 'wms_zones', 'wms_campaigns',
            'epsg_pc', 'radius', 'camera_height',
            'hotspots_add', 'hotspots_dist_min', 'hotspots_dist_max', 'hotspots_height_max',
            'pc_ini_color', 'pc_ini_point_size', 'category',
        ]
        for field in fields:
            variable = field
            description = config_help_text[field]

            value = request.POST.get(field) or ''
            if field == 'hotspots_add':
                value = 'true' if request.POST.get(field) else 'false'

            config = ConfigModel(variable=variable, value=str(value), description=description)
            config.save()
        return redirect('../../admin/mstreets/config')

    form = DefaultConfigForm
    context = {
        'form': form
    }
    return render(
        request,
        'admin/mstreets/config/form_defaults.html',
        context
    )


class UploadPOIFileView():
    def view(self, request):
        if request.method == 'POST':
            form = UploadPoiFileForm(request.POST, request.FILES)
            if form.is_valid():
                self.handle_uploaded_file(request.FILES['file'], form)
                return render(request, 'admin/mstreets/poi/uploading_poi_file.html', {})
        else:
            form = UploadPoiFileForm()
        return render(
            request,
            'admin/mstreets/poi/form_upload_poi_file.html',
            {'form': form}
        )

    def handle_uploaded_file(self, file, form):
        tmp_dir = settings.MEDIA_ROOT + '/mstreets/tmp/'
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        tmp_file_path = tmp_dir + datetime.now().strftime("%m-%d-%Y-%H:%M:%S.%f")
        with open(tmp_file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
            f.close()
        fields = [
            'file_format', 'campaign',
            'epsg', 'x_translation', 'y_translation', 'z_translation',
            'file_folder',  # 'is_file_folder_prefix',
            'tag', 'date', 'has_laterals', 'spherical_suffix', 'spherical_suffix_separator',
            'angle_format', 'pan_correction'
        ]
        form_data = {field: form.cleaned_data[field] or '' for field in fields}
        form_data['campaign'] = form_data['campaign'].pk
        async_handle_uploaded_file.delay(tmp_file_path, form_data, form.REQUIRED_FIELDS)


class UploadPoi_LocationsFileView():

    def view(self, request):
        if request.method == "POST":
            form = UploadPoi_LocationsFileForm(request.POST, request.FILES)
            if form.is_valid():
                self.handle_uploaded_file(request.FILES['file'], form)
                return redirect('../../admin/mstreets/poi_locations')
                # return render(request, "admin/mstreets/poi/uploading_poi_file.html", {})
        else:
            form = UploadPoi_LocationsFileForm()
        return render(
            request, 'admin/mstreets/poi_locations/form_upload_file.html', {'form': form}
        )

    def handle_uploaded_file(self, file: UploadedFile, form: Form) -> bool:
        fields = ["file", "epsg", "tag", "campaign", "color", "x_translation", "y_translation", "z_translation"]
        form_data = {field: form.cleaned_data[field] or "" for field in fields}
        file_uploader = GeoJSONPoiLocationsUploader(
            file,
            form_data,
            form.REQUIRED_FIELDS,
        )
        return file_uploader.upload_file()


class UploadPCFileView():
    FileUploader = {
        "csv": CSVPCUploader,
        "geojson": GeoJSONPCUploader,
    }

    def view(self, request):
        if request.method == 'POST':
            form = UploadPCFileForm(request.POST, request.FILES)
            if form.is_valid():
                if self.handle_uploaded_file(request.FILES['file'], form):
                    return redirect('../../admin/mstreets/pc')
        else:
            form = UploadPCFileForm()
        return render(
            request,
            'admin/mstreets/pc/form_upload_pc_file.html',
            {'form': form}
        )

    def handle_uploaded_file(self, file: UploadedFile, form: Form) -> bool:
        fields = [
            'file_format', 'file', 'campaign', 'epsg', 'file_folder', 'pc_format'
        ]
        form_data = {field: form.cleaned_data[field] or '' for field in fields}
        file_format = form_data['file_format']
        file_uploader = self.FileUploader[file_format](
            file,
            form_data,
            form.REQUIRED_FIELDS,
        )
        return file_uploader.upload_file()
