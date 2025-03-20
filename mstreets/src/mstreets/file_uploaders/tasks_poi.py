from celery import shared_task

from .poi import CSVPoiUploader, IMLPoiUploader, CSVv2PoiUploader, GeoJSONPoiUploader


FileUploader = {
    'iml': IMLPoiUploader,
    'csv2': CSVv2PoiUploader,
    'csv': CSVPoiUploader,
    'xyz': CSVPoiUploader,
    'geojson': GeoJSONPoiUploader,
}


@shared_task()
def async_handle_uploaded_file(tmp_file_path, form_data):
    file_format = form_data['file_format']
    file_uploader = FileUploader[file_format](tmp_file_path, form_data)
    file_uploader.upload_file()
    file_uploader.remove_file()