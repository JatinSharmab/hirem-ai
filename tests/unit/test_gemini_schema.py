import json

import pytest
from pydantic import ValidationError

from hireme_ai.providers.live import ExtractedProfile
from hireme_ai.providers.llm.gemini import generation_schema


def test_portable_schema_keeps_structure_and_local_bounds() -> None:
    original = ExtractedProfile.model_json_schema()
    portable = generation_schema(original)
    assert "maxLength" not in json.dumps(portable)
    assert "maximum" not in json.dumps(portable)
    assert portable["required"] == original["required"]
    assert portable["$defs"]["ExtractedFact"]["properties"]["source_text"]["type"] == "string"
    assert "maxLength" in json.dumps(original)
    with pytest.raises(ValidationError):
        ExtractedProfile(name="x" * 201, summary="", experience_years=0, locations=[], facts=[])
