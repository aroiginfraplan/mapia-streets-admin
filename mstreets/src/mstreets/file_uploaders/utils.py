from typing import Union


def float_or_none(value: Union[str, float, None]) -> Union[float, None]:
    if value in [None, '']:
        return None

    return float(value)
