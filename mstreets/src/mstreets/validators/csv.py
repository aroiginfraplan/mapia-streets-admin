from typing import Any

class CSVValidator:
    is_valid = False
    uploader = None

    def __init__(self, file: Any, uploader: Any) -> None:
        self.header = file.readline().decode("utf-8").replace("\r", "").replace("\n", "")
        file.seek(0)
        self.uploader = uploader
        self.validate_header()

    def validate_header(self) -> None:
        self.assert_is_comma_separated(self.header)
        self.assert_has_required_columns(self.header, self.uploader)

    @classmethod
    def assert_is_comma_separated(cls, line: str) -> None:
        assert ',' in line, 'Els camps han d\'estar separats per comes.'

    @classmethod
    def assert_has_required_columns(cls, line: str, uploader: Any) -> None:
        try:
            uploader.get_line_data(line)
        except Exception as ex:
            print(ex)
            raise AssertionError('La capçalera del CSV no té els camps requerits per aquest format de CSV.') from ex
