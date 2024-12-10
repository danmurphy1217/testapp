from pydantic import BaseModel, Field

from .enums import OFACGender


class OFACEntity(BaseModel):
    id: str = Field(alias="id")
    birthdate: str | None = Field(alias="Birthdate", default=None)
    gender: OFACGender | None = Field(alias="Gender", default=None)
    place_of_birth: str | None = Field(alias="Place of Birth", default=None)
    secondary_sanctions_risk: str | None = Field(
        alias="Secondary sanctions risk:", default=None
    )
    names: list[str] = Field(alias="names")