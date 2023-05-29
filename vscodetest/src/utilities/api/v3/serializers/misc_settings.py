from copy import copy

from api.v3.serializers import (
    HALModelSerializer,
    MetaValidatingSerializer,
    UpdateOrCreateModelSerializer,
)
from api.v3.validators import validate_max_length
from utilities.api.v3.validators import (
    validate_allowed_fields_gp,
    validate_boolean,
    validate_only_digits,
    validate_not_none,
    validate_addressing_scheme,
    validate_show_recipient_field_choices,
    validate_user_profile_display_options,
    validate_catalog_view_choices,
    validate_global_role_options,
)
from utilities.models import GlobalPreferences


class MiscSettingsSerializer(
    UpdateOrCreateModelSerializer, HALModelSerializer, MetaValidatingSerializer
):
    class Meta(object):
        model = GlobalPreferences
        base_path = "/api/v3/cmp/miscellaneousSettings/"
        fields = [
            "a_la_carte_servers",
            "enable_password_toggle",
            "enable_original_password_field",
            "enable_set_challenge_question",
            "auto_generate_user_passwords",
            "enable_email_verification",
            "enable_social_feature",
            "show_user_avatars",
            "restrict_new_environments",
            "reuse_historical_hostnames",
            "fast_track_decom",
            "enforce_single_session",
            "show_rates_when_ordering",
            "show_video_tips",
            "enable_cost_preview_per_env",
            "allow_exceeding_quotas",
            "hostname_case_sensitivity",
            "inherit_group_parameters",
            "auto_login_sso",
            "embedded_mode",
            "allowed_roles_in_embedded_mode",
            "security_message",
            "help_url",
            "cbadmin_email",
            "generic_error_message",
            "default_redirect",
            "inactivity_timeout_minutes",
            "remote_script_dir_unix",
            "remote_script_dir_windows",
            "default_addressing_scheme",
            "bypass_proxy_domains",
            "external_url_whitelist",
            "frame_ancestors",
            "job_timeout",
            "default_user_display_scheme",
            "group_name_levels_to_show",
            "catalog_viewing_mode",
            "show_recipient_field_on_order_form",
            "disabled_reports_list",
            "disabled_recent_activity_categories",
            "legal_notice_text",
            "legal_notice_every_login",
        ]
        # This prevents the id from getting automatically included in the serialization, which we want
        # since it will always be 1 for the singleton
        basic_attributes = copy(fields)
        # Needed to avoid Swagger complaining about this having the same name as the v2 Serializer
        ref_name = "v3MiscellaneousSettings"

        global_validators = [validate_allowed_fields_gp, validate_max_length]
        field_validators = {
            "a_la_carte_servers": [validate_boolean],
            "enable_password_toggle": [validate_boolean],
            "enable_original_password_field": [validate_boolean],
            "enable_set_challenge_question": [validate_boolean],
            "auto_generate_user_passwords": [validate_boolean],
            "enable_email_verification": [validate_boolean],
            "enable_social_feature": [validate_boolean],
            "show_user_avatars": [validate_boolean],
            "restrict_new_environments": [validate_boolean],
            "reuse_historical_hostnames": [validate_boolean],
            "fast_track_decom": [validate_boolean],
            "enforce_single_session": [validate_boolean],
            "show_rates_when_ordering": [validate_boolean],
            "show_video_tips": [validate_boolean],
            "enable_cost_preview_per_env": [validate_boolean],
            "allow_exceeding_quotas": [validate_boolean],
            "hostname_case_sensitivity": [validate_boolean],
            "inherit_group_parameters": [validate_boolean],
            "auto_login_sso": [validate_boolean],
            "embedded_mode": [validate_boolean],
            "allowed_roles_in_embedded_mode": [validate_global_role_options],
            "inactivity_timeout_minutes": [validate_only_digits],
            "job_timeout": [validate_only_digits],
            "group_name_levels_to_show": [validate_only_digits],
            "generic_error_message": [validate_not_none],
            "default_redirect": [validate_not_none],
            "default_addressing_scheme": [
                validate_not_none,
                validate_addressing_scheme,
            ],
            "frame_ancestors": [validate_not_none],
            "default_user_display_scheme": [
                validate_not_none,
                validate_user_profile_display_options,
            ],
            "catalog_viewing_mode": [validate_not_none, validate_catalog_view_choices],
            "show_recipient_field_on_order_form": [
                validate_not_none,
                validate_show_recipient_field_choices,
            ],
            "disabled_reports_list": [validate_not_none],
            "disabled_recent_activity_categories": [validate_not_none],
            "legal_notice_every_login": [validate_boolean],
            "legal_notice_text": [validate_not_none],
        }

        # BestPractice: Use snake_case even for the desired key label here. Converting it to camelCase is
        # handled by the parser/ renderer, outside of the serializer scope
        fields_key_overwrite = {
            "disabled_reports_list": "disabled_out_of_the_box_reports",
            "a_la_carte_servers": "new_server_button",
            "enable_password_toggle": "password_toggle",
            "enable_original_password_field": "original_password_verification",
            "enable_set_challenge_question": "password_reset_question",
            "enable_email_verification": "require_user_email_verification",
            "enable_social_feature": "social",
            "show_user_avatars": "avatars",
            "fast_track_decom": "fast_track_server_deletion",
            "enable_cost_preview_per_env": "show_cost_preview_when_ordering",
            "hostname_case_sensitivity": "hostnames_case_sensitive",
            "allowed_roles_in_embedded_mode": "allowed_global_roles_in_embedded_mode",
            "auto_login_sso": "automatically_login_to_sso",
            "help_url": "url_for_site_specific_help",
            "legal_notice_every_login": "display_legal_notice_on_every_login",
        }

    def resource_href(self, obj):
        """
        Override the default link because of the singleton nature of GlobalPreferences
        """
        href = super().resource_href(obj)
        href["href"] = self.base_path
        href["title"] = "Miscellaneous Settings"
        return href
