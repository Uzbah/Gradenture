from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """Base for every request and response schema.

    ``use_enum_values`` keeps the payloads the CRUD layer builds JSON-serializable:
    a schema field typed as one of the enums in ``backend.common.enums`` holds the
    plain string after validation, which is what PostgREST expects.
    """

    model_config = ConfigDict(use_enum_values=True)
