"""
This Blueprint code aims to show dependant dropdowns
"""
from common.methods import set_progress
from infrastructure.models import CustomField
from resources.models import Resource
from utilities.models.models import ConnectionInfo
import requests

# a function generate_options_for_xxxxxx  (where xxxxx is an input name)
def generate_options_for_car_manufs(**kwargs):
    """Generate a drop down list of car manufacturers

    Returns:
        dropdown: list
    """
    options = []
    initial = "------"
    options.append(initial)
    # here is our query to find all Car Models
    cmanuf = []
    car_manufs = Resource.objects.filter(resource_type__name="car_manufacturer").all()
    for car_manuf in car_manufs:
        # car_manufid = car_manuf.manufid
        if car_manuf.name not in cmanuf:
            display_val = str(car_manuf.name)
            # options.append((car_modelid, display_value)) double brackets for value and display
            options.append((str(car_manuf.id), display_val))
            cmanuf.append(car_manuf.name)
    return options

# a function generate_options_for_xxxxxx  (where xxxxx is an input name)
def generate_options_for_car_models(**kwargs):
    """Generate a drop down list of car models

    Returns:
        dropdown: list
    """
    options = []
    initial = "------"
    options.append(initial)
    # here is our query to find all Car Models

    car_models = Resource.objects.filter(resource_type__name="car_model").all()
    for car_model in car_models:
        # car_manufid = car_manuf.manufid
        display_val = "(" + str(car_model.manuf) + ") - " + car_model.name
        # options.append((car_modelid, display_value)) double brackets for value and display
        options.append((str(car_model.id), display_val))
    return options


def run(**kwargs):
    car_manuf = "{{ car_manufs }}"
    if car_manuf:
        car_model = "{{ car_models }}"
    
    
    
    return "SUCCESS", "", ""
    