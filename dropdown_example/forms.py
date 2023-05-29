from django import forms

from common.forms import C2Form

from xui.dropdown_example.shared import (
    generate_options_for_resource_handlers,
)


class ResourceHandlerForm(C2Form):
    """
    Simple form for choosing a Resource Handler.
    """
    rh_choices = generate_options_for_resource_handlers()
    myattrs = {"style": "width:60%"}
    resourceHandler = forms.CharField(
        label="Choose a Resource Handler",
        required=True,
        widget=forms.Select(choices=rh_choices, attrs=myattrs),
    )

    def save(self, request):
        """
        Validates posted form.
        """

        resourceHandler = self.cleaned_data.get("resourceHandler")

        return True
