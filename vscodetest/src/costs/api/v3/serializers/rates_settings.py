from copy import copy

from api.v3.serializers import (
    HALModelSerializer,
    UpdateOrCreateModelSerializer,
    MetaValidatingSerializer,
)
from api.v3.validators import (
    validate_max_length,
    validate_not_null,
    validate_not_empty_string,
)
from utilities.api.v3.validators import (
    validate_allowed_fields_gp,
    validate_rate_time_unit_choices,
)
from utilities.models import GlobalPreferences


class RatesSettingsSerializer(
    UpdateOrCreateModelSerializer, HALModelSerializer, MetaValidatingSerializer
):
    class Meta(object):
        model = GlobalPreferences
        base_path = "/api/v3/cmp/rates/settings/"
        fields = [
            "rate_currency_unit",
            "rate_time_unit",
        ]
        # This prevents the id from getting automatically included in the serialization, which we want
        # since it will always be 1 for the singleton
        basic_attributes = copy(fields)
        # Needed to avoid Swagger complaining about this having the same name as the v2 Serializer
        ref_name = "v3RatesSettings"

        global_validators = [validate_allowed_fields_gp, validate_max_length]

        field_validators = {
            "rate_currency_unit": [validate_not_null, validate_not_empty_string],
            "rate_time_unit": [validate_rate_time_unit_choices],
        }

    def resource_href(self, obj):
        """
        Override the default link because of the singleton nature of GlobalPreferences
        """
        href = super().resource_href(obj)
        href["href"] = self.base_path
        href["title"] = "Rates Settings"
        return href
