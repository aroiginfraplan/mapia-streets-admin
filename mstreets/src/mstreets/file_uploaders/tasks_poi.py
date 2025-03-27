from celery import shared_task

from .poi import CSVv2PoiUploader, CSVv3PoiUploader, GeoJSONPoiUploader


FileUploader = {
    'csv2': CSVv2PoiUploader,
    'csv3': CSVv3PoiUploader,
    # 'xyz': CSVPoiUploader,
    'geojson': GeoJSONPoiUploader,
}


@shared_task()
def async_handle_uploaded_file(tmp_file_path, form_data, required_fields):
    file_format = form_data['file_format']
    file_uploader = FileUploader[file_format](
        tmp_file_path, form_data, required_fields
    )
    file_uploader.upload_file()
    file_uploader.remove_file()
