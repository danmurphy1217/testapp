from typing import Any

import xmltodict

from ..models import OFACEntity
from .base import BaseResource


class OFACEntitiesResource(BaseResource):
    @property
    def resource(self) -> str:
        return "/entities"

    async def get_latest_ofac_list(self) -> list[OFACEntity]:
        response = await self.get(self.resource, headers=self.headers)
        doc = xmltodict.parse(await response.text())
        raw_entities = self.parse_entities(doc["sanctionsData"]["entities"]["entity"])
        return [OFACEntity.model_validate(entity) for entity in raw_entities]

    @staticmethod
    def _filter_latin_translation(names: dict[str, Any]) -> list[dict[str, Any]]:
        return list(
            filter(
                lambda x: x["script"]["#text"] == "Latin",
                names["translations"]["translation"],
            )
        )

    @staticmethod
    def _parse_name_list(entity: dict[str, Any]) -> dict[str, Any]:
        result = dict()
        if not isinstance(entity["names"]["name"], list):
            names = [entity["names"]["name"]]
        else:
            names = entity["names"]["name"]

        names_list = []

        for name in names:
            translations = name["translations"]["translation"]
            if not isinstance(translations, list):
                translations = [translations]

            for translation in translations:
                if translation["script"]["#text"] == "Latin":
                    names_list.append(
                        " ".join(
                            [
                                (translation.get("formattedFirstName") or "").title(),
                                (translation.get("formattedLastName") or "").title(),
                            ]
                        )
                    )

        result["names"] = names_list

        return result

    @staticmethod
    def _parse_features(entity: dict[str, Any]) -> dict[str, Any]:
        result = dict()
        if features := entity.get("features", {}).get("feature"):
            if not isinstance(features, list):
                features = [features]

            for feature in features:
                result[feature["type"]["#text"]] = feature.get("value")

        return result

    def _parse_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        result = {
            "id": entity["@id"],
            **self._parse_features(entity),
        } | self._parse_name_list(entity)
        return result

    @staticmethod
    def _filter_individuals(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return list(
            filter(
                lambda x: x["generalInfo"]["entityType"]["#text"] == "Individual",
                entities,
            )
        )

    def parse_entities(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        filtered = self._filter_individuals(entities)
        return [self._parse_entity(entity) for entity in filtered]