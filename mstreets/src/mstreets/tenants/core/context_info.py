from abc import ABC, abstractmethod
from typing import Dict, List, Union

import requests

from requests.exceptions import ConnectionError

from ..utils import import_tenant_attribute


class RemoteServiceUnavailable(ConnectionError):
    def __init__(self):
        super().__init__('Remote service unavailable')


class ContextInfoAPI(ABC):
    id = None
    label = None
    subtitle = None
    data_fields = None

    def __init__(self, *args, **kwargs):
        required = ('id', 'label', 'subtitle', 'data_fields')
        missing = [attribute for attribute in required if not getattr(self, attribute)]
        if missing:
            raise NotImplementedError(
                f'ERROR: Missing attributes in {self.__class__.__name__}: {", ".join(missing)}'
            )

    @abstractmethod
    def get_url(self, lat: str, lng: str):
        """Return the URL to be requested."""

    @abstractmethod
    def get_values(self, response: requests.Response) -> List[Union[str, int, float]]:
        """Return the values for each of the data_fields of the instance.

        The list should contain the value sin the same order the data_fields were provided.
        """

    def get(self, lat: float, lng: float) -> Dict:
        url = self.get_url(lat, lng)
        try:
            api_response = requests.get(url)
        except requests.exceptions.ConnectionError as ex:
            raise RemoteServiceUnavailable() from ex
        values = self.get_values(api_response)
        return self.get_response_object(values)

    def get_response_object(self, values: List[Union[str, int, float]] = None) -> Dict:
        context_data = [
            {'label': label, 'value': value}
            for label, value in zip(self.data_fields, values)
        ]
        return {
            'status': 'ok',
            'response': {
                'data': [
                    {
                        'title': self.label,
                        'subtitle': self.subtitle,
                        'data': context_data,
                    }
                ]
            },
        }


class ICGCRoadPK(ContextInfoAPI):
    id = "pk2"
    label = 'Xarxa viària'
    subtitle = 'Mostra el codi de carretera i punt kilomètric'
    data_fields = ('Codi de carretera', 'Punt kilomètric')

    def get_url(self, lat: float, lng: float) -> str:
        api_url = 'https://eines.icgc.cat/geocodificador/invers'
        return f'{api_url}?lon={lng},&lat={lat}&size=1&layers=pk'

    def get_values(self, response: requests.Response) -> List[Union[str, int, float]]:
        if response.status_code >= 200 and response.status_code < 300:
            geojson = response.json()
            features = geojson.get('features')
            if not features:
                return [None, None]

            properties = features[0].get('properties')
            return [
                properties.get('via'),
                properties.get('km'),
            ]
        return [None, None]


def get_tenant_context_info_apis() -> tuple:
    """Return the list of available context info API choices for a particular tenant."""
    choices = import_tenant_attribute('CONTEXT_INFO_CHOICES', 'context_info') or []

    choice_ids = [choice.id for choice in choices]
    for choice in CORE_CONTEXT_INFO_CHOICES:
        if choice.id not in choice_ids:
            choices.append(choice)

    return choices


CORE_CONTEXT_INFO_CHOICES = (ICGCRoadPK,)
