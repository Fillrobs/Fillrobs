from common.fields import form_field_for_cf
from common.forms import C2Form
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _lazy
from infrastructure.models import CustomField, Environment
from orders.models import CustomFieldValue
from utilities.logger import ThreadLogger

from xui.maxis_server_utilization_report.shared import (
    generate_options_for_maxis_customer,
)

logger = ThreadLogger(__name__)


class MaxisCustomerForm(C2Form):
    def __init__(self, *args, **kwargs):
        # self.request = kwargs.pop("request", None)
        # self.profile = kwargs.pop("profile", None)

        # self.profile = kwargs["profile"]

        initial = kwargs.get("initial")
        if initial:
            # public_cloud_choices = initial.get("aws_public_cloud")
            my_profile_id = initial.get("my_profile_id")
        else:
            my_profile_id = kwargs.pop("my_profile_id")

        maxis_customer_choices = generate_options_for_maxis_customer(my_profile_id)

        super().__init__(*args, **kwargs)
        # logger.info("public_cloud_choices=", public_cloud_choices)

        """
        Simple form for choosing a Maxis Customer.
        """
        # helper = FormHelper()

        # grp_choices = generate_options_for_pr_aws_sg_edit_group()

        myattrs = {"style": "width:60%"}
        # pr_aws_sg_edit_group = forms.CharField(
        #    label="Group",
        #    required=True,
        #    widget=forms.Select(choices=grp_choices, attrs=myattrs),
        # )
        # logger.info(f"selected group {pr_aws_sg_edit_group}")

        self.fields["maxis_customer"] = forms.CharField(
            label="Maxis Customer",
            required=True,
            widget=forms.Select(choices=maxis_customer_choices, attrs=myattrs),
            help_text="Select a Maxis Customer",
        )
        self.fields["start_date"] = forms.DateField(
            label="Start Date",
            required=True,
            widget=forms.DateInput(attrs={"type": "date"}),
            help_text="Select a Start Date",
        )
        self.fields["end_date"] = forms.DateField(
            label="End Date",
            required=True,
            widget=forms.DateInput(attrs={"type": "date"}),
            help_text="Select an End Date",
        )

        self.fields["my_profile_id"] = forms.CharField(
            label="my_profile_id",
            required=True,
            widget=forms.HiddenInput(),
        )

    def save(self):
        logger.info(f"self={self}")
        """
        Validates posted form.
        """

        maxis_customer = self.cleaned_data.get["maxis_customer"]
        my_profile_id = self.cleaned_data.get["my_profile_id"]
        start_date = self.cleaned_data.get["start_date"]
        end_date = self.cleaned_data.get["end_date"]

        return maxis_customer, my_profile_id, start_date, end_date
