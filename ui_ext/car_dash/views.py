from django.shortcuts import render
from extensions.views import dashboard_extension
from common.methods import columnify
from resources.models import Resource
from accounts.models import Group, UserProfile
from django.utils.safestring import mark_safe


def show_image(fn):
    img_file = "/static/uploads/images/car_logos/" + fn + ".JPG"
    dimensions = "width=50px"
    return mark_safe("<img src='{}' {} />".format(img_file, dimensions))


@dashboard_extension(title="car_dash_dashboard_0", description="Car Manufacturers")
def car_dash(request):
    
    profile = request.get_user_profile()
    print(profile)
    
    # get all car stock
    carstock = Resource.objects.filter(resource_type__name="car").all()
    # create an empty array for unique models and all stock
    car_stock_unique_models = []
    car_stock_models = []
    # iterate through car stock build a unique array of models
    for car in carstock:
        # check for status and get only ACTIVE records
        st = car.get_resource_dict()["status"]
        if st == "ACTIVE":
            # this try catch ignores records without a modelid attribute
            try:
                car_stock_models.append(car.car_modelid)
                # look to see if the record already exists within the array
                if car.car_modelid not in car_stock_unique_models:
                    # add it if not  and set the count to 1
                    car_stock_unique_models.append(car.car_modelid)

            except AttributeError:
                print("")

    carmanufname = []
    manuftotals = {}
    # iterate through unique model ids and retrieve the manufacturer name and store within it's own array
    for stockmodelid in car_stock_unique_models:

        if stockmodelid == "None":
            print("None found")
        else:
            # first count the models in stock
            currentstock = 0
            for mdid in car_stock_models:
                if mdid == stockmodelid:
                    currentstock += 1

            manufname = Resource.objects.filter(
                resource_type__name="car_model", id=stockmodelid
            ).first()
            try:

                if manufname.manuf not in carmanufname:
                    carmanufname.append(manufname.manuf)
                manuftotals[manufname.manuf] = (
                    manuftotals.get(manufname.manuf, 0) + currentstock
                )
            except AttributeError:
                print("")

    car_manufs = []

    # iterate through the manuftotals list
    for key, val in manuftotals.items():

        car_details_logo = key.lower()
        car_details_logo = car_details_logo.replace(" ", "")
        car_details_final_logo = show_image(car_details_logo)
        carm = key
        carcnt = str(val)
        car_manufs.append(
            {
                "manuf": carm,
                "carcnt": carcnt,
                "logo": car_details_final_logo,
            }
        )
    # spit out the data
    return render(
        request,
        "car_dash/templates/table.html",
        dict(
            columns=columnify(car_manufs, 2),
        ),
    )
