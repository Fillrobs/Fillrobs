from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors import SwaggerAutoSchema, FieldInspector


class CustomFieldInspector(FieldInspector):
    # The API path can be inspected via the self.path field.

    """
    Change the type of the workspace field from integer to string.
    """

    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(result, openapi.Schema.OR_REF):
            schema = openapi.resolve_ref(result, self.components)
            if (
                "title" in schema
                and schema["title"] == "Workspace"
                and "description" in schema
                and schema["description"] == "Workspace URL"
                and schema["type"] == openapi.TYPE_INTEGER
            ):
                schema["type"] = openapi.TYPE_STRING
        return result


class CustomSwaggerSettings(SwaggerAutoSchema):
    field_inspectors = [
        CustomFieldInspector
    ] + swagger_settings.DEFAULT_FIELD_INSPECTORS
