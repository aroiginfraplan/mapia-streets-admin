import mimetypes
import os
import stat

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404, HttpResponseNotModified
from django.utils.http import http_date
from django.shortcuts import render, redirect
from django.views.static import was_modified_since

import boto3
from botocore.client import Config

from mstreets.forms import DefaultConfigForm, UploadPoiFileForm, config_help_text
from mstreets.models import Config as ConfigModel
from .settings import (AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME, AWS_S3_ENDPOINT_URL,
                       AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, PANORAMAS_ROOT)


def panoramas_files_server(request, path):
    if not request.user.is_authenticated:
        raise PermissionDenied

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
        return redirect('/admin/mstreets/config')

    form = DefaultConfigForm
    context = {
        'form': form
    }
    return render(
        request,
        'admin/mstreets/config/form_defaults.html',
        context
    )


def handle_uploaded_file(file, config):
    # read_file
    # save_pois_resources
    pass


def upload_poi_file(request):
    fields = [
        'format', 'zone', 'campaign',
        'epsg', 'x_translation', 'y_translation', 'z_translation',
        'file_folder', 'is_file_folder_prefix',
        'tag', 'date',
        'angle_format', 'asimuth_correction'
    ]
    if request.method == 'POST':
        form = UploadPoiFileForm(request.POST, request.FILES)
        if form.is_valid():
            config = {field: form.cleaned_data[field] or '' for field in fields}
            handle_uploaded_file(request.FILES['file'], config)
            return redirect('/admin/mstreets/poi')
    else:
        form = UploadPoiFileForm()
    return render(
        request,
        'admin/mstreets/poi/form_upload_poi_file.html',
        {'form': form}
    )
