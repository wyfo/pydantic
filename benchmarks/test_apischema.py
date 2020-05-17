import json
import sys

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, NewType, Optional, Tuple, Union

import apischema
import importlib_metadata
from apischema import (
    ValidationError,
    deserializer,
    schema,
    serialize,
    deserialize,
    serializer,
)

PositiveInt = NewType("PositiveInt", int)
schema(exc_min=0)(PositiveInt)

if sys.version_info < (3, 7):  # Especially for Pypy
    DateTime = NewType("DateTime", str)
    schema(format="date-time")(DateTime)

    @deserializer
    def to_datetime(s: DateTime) -> datetime:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

    @serializer
    def from_datetime(obj: datetime) -> DateTime:
        return DateTime(obj.strftime("%Y-%m-%dT%H:%M:%S"))


# Defined on top level in order to be able to evaluate annotations
@dataclass
class Location:
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class Skill:
    subject: str
    subject_id: int
    category: str
    qual_level: str
    qual_level_id: int
    qual_level_ranking: float = 0


@dataclass
class Model:
    id: int
    client_name: str = field(metadata=schema(max_len=255))
    sort_index: float
    # must be before fields with default value
    grecaptcha_response: str = field(metadata=schema(min_len=20, max_len=1000))
    client_phone: Optional[str] = field(default=None, metadata=schema(max_len=255))
    location: Optional[Location] = None
    contractor: Optional[PositiveInt] = None
    upstream_http_referrer: Optional[str] = field(
        default=None, metadata=schema(max_len=1023)
    )
    last_updated: Optional[datetime] = None
    skills: List[Skill] = field(default_factory=list)


class TestApischema:
    package = apischema.__name__
    version = importlib_metadata.version("apischema")

    def __init__(self, allow_extra: bool):
        self.allow_extra = allow_extra
        self.cls = Model

    def validate(self, data: Any) -> Tuple[bool, Union[Model, ValidationError]]:
        try:
            result = deserialize(
                self.cls, data, additional_properties=self.allow_extra, coercion=True,
            )
            return True, result
        except ValidationError as e:
            return False, e

    def to_json(self, model: Model) -> str:
        return json.dumps(serialize(model, exclude_unset=False))
