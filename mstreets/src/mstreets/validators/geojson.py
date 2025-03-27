import json
from typing import Any, Dict, List


class FeatureValidator:
    is_valid = False
    properties = None
    coordinates = None
    error = None

    def __init__(self, feature: Dict[str, any] = None, required_properties: List[str] = None) -> None:
        if not feature:
            return

        self.assert_is_dictionary(feature)
        self.assert_has_properties_and_geometry(feature)
        self.assert_has_coordinate_list(feature)
        self.assert_is_valid_geometry(feature)
        self.properties = feature.get("properties")
        self.assert_required_properties(feature, required_properties)
        self.is_valid = True
        self.error = None
        self.coordinates = feature.get("geometry").get("coordinates")

    def assert_is_dictionary(self, feature: Dict[str, any]) -> None:
        assert isinstance(feature, dict), "La feature ha de ser un objecte."

    def assert_has_properties_and_geometry(self, feature: Dict[str, any]) -> None:
        geometry = feature.get("geometry")
        properties = feature.get("properties")
        is_valid = isinstance(properties, dict) and isinstance(geometry, dict)
        assert (
            is_valid
        ), "Totes les features han de tenir les claus properties i geometry com a objectes."

    def assert_has_coordinate_list(self, feature: Dict[str, any]) -> None:
        geometry = feature.get("geometry")
        coordinates = geometry.get("coordinates")
        assert isinstance(
            coordinates, list
        ), "Les geometries han de tenir una clau coordinates amb un llistat de coordenades."

    def assert_is_valid_geometry(self, feature: Dict[str, any]) -> None:
        return True

    def assert_required_properties(self, feature: Dict[str, any], required_properties: List[str]) -> None:
        if not required_properties:
            return

        feature_properties = list(feature.get("properties").keys())
        sub_keys = list(set(property.split('.')[0]
                            for property in required_properties
                            if '.' in property))
        for key in sub_keys:
            value = feature.get('properties').get(key)
            # Si hi ha un valor, afegeix les propietats existents de la feature
            if value:
                if isinstance(value, list):
                    value = value[0]
                sub_properties = [f'{key}.{property}' for property in value.keys()]
                feature_properties += sub_properties
            # Si no hi ha un valor, elimina les propietats requerides d'aquella clau
            else:
                required_properties = [property
                                       for property in required_properties
                                       if f'{key}.' not in property]

        missing = set(required_properties) - set(feature_properties)
        assert len(missing) == 0, f"Les propietats {', '.join(missing)} són obligatòries."


class PointValidator(FeatureValidator):

    def assert_is_valid_geometry(self, feature: Dict[str, any]) -> None:
        self.assert_has_valid_coordinates(feature)
        self.assert_has_two_coordinates(feature)

    def assert_has_valid_coordinates(self, feature: Dict[str, any]) -> None:
        coordinates = feature.get("geometry").get("coordinates")
        assert (
            isinstance(coordinates, list)
        ), "Els punts han de tenir una llista de coordenades."

    def assert_has_two_coordinates(self, feature: Dict[str, any]) -> None:
        coordinates = feature.get("geometry").get("coordinates")
        assert len(coordinates) == 2, "Els punts han de tenir dues coordenades."


class PolygonValidator(FeatureValidator):

    def assert_is_valid_geometry(self, feature: Dict[str, any]) -> None:
        self.assert_has_linear_rings(feature)
        self.assert_has_at_least_three_coordinates(feature)
        self.assert_first_and_last_coordinates_are_the_same(feature)

    def assert_has_linear_rings(self, feature: Dict[str, any]) -> None:
        coordinates = feature.get("geometry").get("coordinates")[0][0]
        assert isinstance(
            coordinates, list
        ), "La clau coordinates ha de ser una llista de linear rings."

    def assert_has_at_least_three_coordinates(self, feature: Dict[str, any]) -> None:
        coordinates = feature.get("geometry").get("coordinates")[0]
        assert (
            len(coordinates) >= 3
        ), "Els linear rings han de tenir com a mínim tres coordenades."

    def assert_first_and_last_coordinates_are_the_same(
        self, feature: Dict[str, any]
    ) -> None:
        coordinates = feature.get("geometry").get("coordinates")[0]
        assert (
            coordinates[0] == coordinates[-1]
        ), "Les coordenades inicial i final del linear ring han de ser les mateixes."


class GeoJSONValidator:
    FEATURE_VALIDATORS = {
        None: FeatureValidator,
        "Point": PointValidator,
        "Polygon": PolygonValidator,
    }
    allowed_feature_types = None
    geojson_types = ["FeatureCollection"]
    is_valid = False
    features = None

    def __init__(
        self,
        file: Any,
        allowed_feature_types: List[str] = None,
        required_properties: List[str] = None,
    ) -> None:
        self.allowed_feature_types = allowed_feature_types
        self.required_properties = required_properties
        if file:
            content = file.read().decode('utf-8')
            file.seek(0)
            self.validate_content(content)

    def validate_content(
        self,
        content: str,
    ) -> None:
        geojson = self.assert_is_dictionary(content)
        self.assert_has_valid_type(geojson)
        features = self.assert_has_valid_features(geojson)
        self.validate_first_feature(features)

        self.is_valid = True
        self.features = features

    def validate_first_feature(self, features: Dict[str, any]) -> None:
        feature = features[0]
        geometry = self.assert_feature_has_geometry(feature)
        feature_type = geometry.get('type')
        allowed_string = ', '.join(self.allowed_feature_types)
        assert feature_type in self.allowed_feature_types, f"El tipus {feature_type} no és admès. Només {allowed_string} ho són."
        validator_class = self.FEATURE_VALIDATORS.get(feature_type)
        validator_class(feature, required_properties=self.required_properties)

    def assert_is_dictionary(self, content: str) -> Dict[str, any]:
        try:
            if isinstance(content, str):
                return json.loads(content)

            if isinstance(content, dict):
                return content

            raise AssertionError("El contingut ha de ser un dict o un str.")
        except json.JSONDecodeError as ex:
            raise AssertionError("El geojson ha de ser un objecte JSON vàlid.") from ex

    def assert_has_valid_type(self, geojson: Dict[str, any]) -> None:
        geojson_type = geojson.get("type")
        allowed_types = " o ".join(self.geojson_types)
        assert (
            geojson_type in self.geojson_types and "features" in geojson
        ), f"El geojson ha de tenir la clau type amb valor {allowed_types}, no {geojson_type}."

    def assert_has_valid_features(self, geojson: Dict[str, any]) -> Dict[str, any]:
        features = geojson.get("features")
        assert isinstance(
            features, list
        ), "El geojson ha de tenir una clau features amb una llista de features."
        assert len(features) > 0, "El geojson ha de tenir com a mínim una feature."

        return features

    def assert_feature_has_geometry(self, feature: Dict[str, any]) -> Dict[str, any]:
        geometry = feature.get("geometry")
        assert geometry, "La clau geometry no existeix."

        return geometry
