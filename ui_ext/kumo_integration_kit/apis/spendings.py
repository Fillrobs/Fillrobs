import json
import collections
import functools
import operator
import traceback
from datetime import (
    date,
    datetime,
    timedelta
)
from django.http import HttpResponse

from utilities.decorators import json_view
from resourcehandlers.aws.models import AWSHandler
from resourcehandlers.azure_arm.models import AzureARMHandler
from resourcehandlers.models import ResourceHandler
from xui.kumo_integration_kit.constants import (
    UNUSED_SERVICES,
    UNOPTIMIZED_SERVICES,
)
from xui.kumo_integration_kit.utils import (
    ApiResponse,
    check_for_cache,
    get_cache_data,
    set_cache_data
)


def generate_chart_data(api_data, name, dictionary, rh_type=None):
    """
    To struture the api response data in desired format
    """
    dictionary[name] = {"labels": [], "values": []}
    if rh_type == "AZURE":
        for row in api_data["chart_data"]["categories"][0]["category"]:
            dictionary[name]["labels"].append(row["label"])
            dictionary[name]["values"].append(row["value"])
    else:
        for row in api_data["chart_data"]:
            dictionary[name]["labels"].append(row["label"])
            dictionary[name]["values"].append(row["value"])


@json_view
def charts_data_rh_json(request):
    """
    To get the cost reporting data from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    payload = json.loads(request.body)
    rh = ResourceHandler.objects.get(id=payload['rh_id']).cast()
    charts_data = {}
    output_data_dict = {}
    rh_file_name = f'chart_data_{payload["rh_id"]}'

    should_fetch = check_for_cache(rh_file_name)
    print(f'--------------{rh_file_name}---------------')
    print(should_fetch)

    if should_fetch:
        if isinstance(rh, AWSHandler):
            print('======== IN AWS ========')
            
            response = ApiResponse(
                payload, 
                'report_dashboard').fetch_response()
            if response and 'response' in response.json().keys():
                api_data = response.json()["response"]["report_dashboard"]

                for x in api_data:
                    if 'overview_data' in list(x.keys()):
                        charts_data['thirty_days_ri_overview'] = {
                            "used_reservations": x['overview_data']['utilization']['grid_data']['used_reservations'],
                            "unused_reservations": x['overview_data']['utilization']['grid_data']['unused_reservations'],
                        }
                    else:
                        charts_data['thirty_days_ri_overview'] = {
                            "used_reservations": 0,
                            "unused_reservations": 0
                        }
            else:
                charts_data['thirty_days_ri_overview'] = {
                    "used_reservations": 0,
                    "unused_reservations": 0
                }

            response = ApiResponse(
                payload, 
                'misc_details').fetch_response()
            if response:
                api_data = response.json()
                charts_data['month_to_date'] = api_data['month_to_date_details']['month_to_date_cost']
                charts_data['year_to_date'] = api_data['year_to_date_details']['year_to_date_cost']
                charts_data['year_forecast'] = api_data['year_to_date_details']['current_year_forecast']
            else:
                charts_data['month_to_date'] = 0
                charts_data['year_to_date'] = 0
                charts_data['year_forecast'] = 0

            payload['type'] = 'last_30_days'
            response = ApiResponse(
                payload, 
                'cost_by_days').fetch_response()
            if response:
                if 'message' in response.json():
                    charts_data['message'] = "no billing adapter"
                else:
                    generate_chart_data(
                        response.json(), 'cost_by_day_chart_data', charts_data)
                    charts_data['average_daily_cost'] = response.json()[
                        'grid_data']['avarage_cost']
                    charts_data['previous_spend'] = response.json()[
                        'grid_data']['previous_spend']
            else:
                charts_data['average_daily_cost'] = 0
                charts_data['previous_spend'] = 0
                charts_data['cost_by_day_chart_data'] = {}

            payload['type'] = 'last_12_months'
            response = ApiResponse(
                payload, 
                'cost_by_months').fetch_response()
            if response:
                generate_chart_data(
                    response.json(), 'cost_by_year_chart_data', charts_data)
                charts_data['average_monthly_cost'] = response.json()[
                    'grid_data']['avarage_cost']
            else:
                charts_data['average_monthly_cost'] = 0
                charts_data['cost_by_year_chart_data'] = {}

            payload['type'] = 'last_30_days'
            response = ApiResponse(
                payload, 
                'cost_by_services').fetch_response()
            if response:
                generate_chart_data(
                    response.json(), 'cost_by_service_chart_data', charts_data)
                charts_data['total_spend'] = response.json()['grid_data']
            else:
                charts_data['total_spend'] = 0
                charts_data['cost_by_service_chart_data'] = {}

            # To calculate the diff in yesterdays cost day on day
            if charts_data['cost_by_day_chart_data'] and 'values' in charts_data['cost_by_day_chart_data'].keys():
                day_before_yesterday_cost = charts_data['cost_by_day_chart_data']['values'][-2]
                charts_data['day_cost_diff'] \
                    = ((charts_data['previous_spend']/day_before_yesterday_cost)-1) * 100
            else:
                charts_data['day_cost_diff'] = 0

            if charts_data['cost_by_year_chart_data'] and 'values' in charts_data['cost_by_year_chart_data'].keys():
                # To calculate the diff in month wise cost
                last_month_cost = charts_data['cost_by_year_chart_data']['values'][-2]
                charts_data['month_cost_diff'] \
                    = ((charts_data['month_to_date']/last_month_cost)-1) * 100
            else:
                charts_data['month_cost_diff'] = 0

        elif isinstance(rh, AzureARMHandler):
            print('======== IN AZURE ========')

            response = ApiResponse(
                payload, 
                'azure_misc_details').fetch_response()
            if response:
                api_data = response.json()
                charts_data['month_to_date'] = api_data['month_to_date_details']['month_to_date_cost']
                charts_data['year_to_date'] = api_data['year_to_date_details']['year_to_date_cost']
                charts_data['year_forecast'] = api_data['year_to_date_details']['current_year_forecast']
            else:
                charts_data['month_to_date'] = 0
                charts_data['year_to_date'] = 0
                charts_data['year_forecast'] = 0

            payload['type'] = 'last_30_days'
            response = ApiResponse(
                payload, 
                'azure_cost_by_days').fetch_response()
            if response:
                if 'message' in response.json():
                    charts_data['message'] = "no billing adapter"
                else:
                    generate_chart_data(
                        response.json(), 'cost_by_day_chart_data', charts_data)
                    charts_data['average_daily_cost'] = response.json()[
                        'grid_data']['avarage_cost']
                    charts_data['previous_spend'] = response.json()[
                        'grid_data']['previous_spend']
            else:
                charts_data['average_daily_cost'] = 0
                charts_data['previous_spend'] = 0
                charts_data['cost_by_day_chart_data'] = {}

            payload['type'] = 'last_12_months'
            response = ApiResponse(
                payload, 
                'azure_cost_by_months').fetch_response()
            if response:
                generate_chart_data(
                    response.json(), 'cost_by_year_chart_data', charts_data)
                charts_data['average_monthly_cost'] = response.json()[
                    'grid_data']['avarage_cost']
            else:
                charts_data['average_monthly_cost'] = 0
                charts_data['cost_by_year_chart_data'] = {}

            payload['type'] = 'last_30_days'
            response = ApiResponse(
                payload, 
                'azure_cost_by_services').fetch_response()
            if response:
                generate_chart_data(
                    response.json(), 'cost_by_service_chart_data', charts_data)
                charts_data['total_spend'] = response.json()['grid_data']
            else:
                charts_data['total_spend'] = 0
                charts_data['cost_by_service_chart_data'] = {}

            if charts_data['cost_by_day_chart_data'] and 'values' in charts_data['cost_by_day_chart_data'].keys():
                # To calculate the diff in yesterdays cost day on day
                day_before_yesterday_cost = charts_data['cost_by_day_chart_data']['values'][-2]
                charts_data['day_cost_diff'] \
                    = ((charts_data['previous_spend']/day_before_yesterday_cost)-1) * 100
            else:
                charts_data['day_cost_diff'] = 0

            if charts_data['cost_by_year_chart_data'] and 'values' in charts_data['cost_by_year_chart_data'].keys():
                # To calculate the diff in month wise cost
                last_month_cost = charts_data['cost_by_year_chart_data']['values'][-2]
                charts_data['month_cost_diff'] \
                    = ((charts_data['month_to_date']/last_month_cost)-1) * 100
            else:
                charts_data['month_cost_diff'] = 0

            if all(map((lambda value: True if value else False), (
                charts_data["month_to_date"], charts_data["year_to_date"], 
                charts_data["year_forecast"], charts_data["average_daily_cost"], 
                charts_data["previous_spend"], charts_data["cost_by_day_chart_data"], 
                charts_data["average_monthly_cost"], charts_data["cost_by_year_chart_data"], 
                charts_data["total_spend"], charts_data["cost_by_service_chart_data"]))):
                set_cache_data(rh_file_name, charts_data)

        if all(map((lambda value: True if value else False), (
                charts_data["month_to_date"], charts_data["year_to_date"],
                charts_data["year_forecast"], charts_data["average_daily_cost"],
                charts_data["previous_spend"], charts_data["cost_by_day_chart_data"],
                charts_data["average_monthly_cost"],
                charts_data["cost_by_year_chart_data"], charts_data["total_spend"],
                charts_data["cost_by_service_chart_data"]))):
            set_cache_data(rh_file_name, charts_data)

    else:
        charts_data = get_cache_data(rh_file_name)

    if isinstance(rh, AWSHandler):
        output_data_dict.update({
            "used_reservations": round(charts_data['thirty_days_ri_overview']['used_reservations'] or 0, 2),
            "unused_reservations": round(charts_data['thirty_days_ri_overview']['unused_reservations'] or 0, 2),
        })

    if 'message' in charts_data:
        output_data_dict.update({'message': 'no billing adapter'})

    output_data_dict.update({
        "cost_by_service_chart_data": charts_data['cost_by_service_chart_data'],
        "cost_by_day_chart_data": charts_data['cost_by_day_chart_data'],
        "cost_by_year_chart_data": charts_data['cost_by_year_chart_data'],
        "yesterday_spend": round(charts_data['previous_spend'] or 0, 2),
        "total_spend": round(charts_data['total_spend'] or 0, 2),
        "month_to_date": round(charts_data['month_to_date'] or 0, 2),
        "year_to_date": round(charts_data['year_to_date'] or 0, 2),
        "year_forecast": round(charts_data['year_forecast'] or 0, 2),
        "day_cost_diff": round(charts_data['day_cost_diff'] or 0, 2),
        "month_cost_diff": round(charts_data['month_cost_diff'] or 0, 2),
    })

    return output_data_dict


@json_view
def cost_adviser_overview_for_rh(request):
    """
    To get the service adviser data from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    charts_data = {}
    payload = json.loads(request.body)
    rh = ResourceHandler.objects.get(id=payload['rh_id']).cast()

    response = ApiResponse(
                payload, 
                'service_type_count').fetch_response()
    if response:           
        if 'message' in response.json():
            charts_data['service_type_summary'] = []
        else:
            charts_data['service_type_summary'] = response.json(
                )['service_type_count']
    else:
        charts_data['service_type_summary'] = []

    if isinstance(rh, AWSHandler):

        response = ApiResponse(
                payload, 
                'ec2_rightsize').fetch_response()
        if response:
            charts_data['service_type_summary'].append({
                'type': 'ec2_right_sizings',
                'count': response.json()['meta_data']['instance_count'],
                'cost_sum': response.json()['meta_data']['total_saving'],
            })
        else:
            pass

        response = ApiResponse(
                payload, 
                'ignored_services').fetch_response()
        if response:
            charts_data['service_type_summary'].append({
                "type": "ignore_services",
                "count": response.json()['count'],
                "cost_sum": response.json()['service_cost_sum'],
            })
        else:
            pass

    cost_efficiency = {}
    format_cost_efficiency_data(charts_data, cost_efficiency)

    return cost_efficiency


def format_cost_efficiency_data(charts_data, cost_efficiency):
    """
    To consolidate the unused, unoptimized and ignored services
    """
    unused_cost_sum = 0
    unused_count = 0
    unoptimized_cost_sum = 0
    unoptimized_count = 0
    ignored_cost_sum = 0
    ignored_count = 0
    for data in charts_data['service_type_summary']:
        if data['type'] in UNUSED_SERVICES:
            unused_count = unused_count + data['count']
            unused_cost_sum = unused_cost_sum + float(data['cost_sum'])

        elif data['type'] in UNOPTIMIZED_SERVICES:
            unoptimized_count = unoptimized_count + data['count']
            unoptimized_cost_sum = unoptimized_cost_sum + \
                float(data['cost_sum'])

        elif data['type'] == 'ignore_services':
            ignored_cost_sum = float(data['cost_sum'])
            ignored_count = data['count']

    cost_efficiency['data'] = ({
        'unused_count': unused_count,
        'unused_cost_sum': unused_cost_sum,
        'unoptimized_count': unoptimized_count,
        'unoptimized_cost_sum': unoptimized_cost_sum,
        'ignored_count': ignored_count,
        'ignored_cost_sum': ignored_cost_sum,
        'potential_benefit': (unused_cost_sum
                              + unoptimized_cost_sum
                              + ignored_cost_sum)
    })


@json_view
def aws_ri_recommendations_for_rh_json(request):
    """
    To fetch the AWS RI recommendation data from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    payload = json.loads(request.body)

    response = ApiResponse(
        payload, 
        'aws_ri_purchase_recommendations',
        request_type="POST").fetch_response()
    if response:
        response = response.json()['summary']

    return response


@json_view
def azure_ri_recommendations_for_rh_json(request):
    """
    To fetch the Azure RI recommendation data from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    payload = json.loads(request.body)

    response = ApiResponse(
        payload, 
        'azure_ri_purchase_recommendations'
        ).fetch_response()
    if response:
        response = response.json()

    return response


@json_view
def spend_details_for_rh_json(request):
    """
    To fetch last 30 days cost/spend data from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    chart_data = {}
    payload = json.loads(request.body)
    rh = ResourceHandler.objects.get(id=payload['report']['rh_id']).cast()
    
    if isinstance(rh, AWSHandler):
        response = ApiResponse(
                payload, 
                'get_chart_data',
                request_type="POST").fetch_response()
        if response:
            response = response.json()['response']

    elif isinstance(rh, AzureARMHandler):
        response = ApiResponse(
                payload, 
                'azure_get_chart_data',
                request_type="POST").fetch_response()
        if response:
            response = response.json()['report']

    if response:
        if (payload['report']['multi_series']):
            multi_series_chart = []
            for x in response["chart_data"]["dataset"]:
                data = []
                for y in (x['data']):
                    data.append(y['value'])
                serie_name = x['seriesname'] if 'seriesname' in x else 'Others'
                multi_series_chart.append(
                    {'name': serie_name, 'data': data})

            chart_data = {}
            chart_data = {"labels": [], "values": multi_series_chart,
                        "total_cost": response['grid_data']['total']}
            for row in response["chart_data"]["categories"][0]["category"]:
                chart_data["labels"].append(row["label"])

            multiseries_data_list = [
                data_list['data'][-1] if data_list['data'] else 0 for data_list in chart_data['values']]

            chart_data['previous_spend'] = sum(
                multiseries_data_list) if multiseries_data_list else 0
                    
            if payload['report']['monthly'] == True:
                chart_data['average_daily_cost'] = (chart_data['total_cost'] / \
                    len(chart_data['labels']))/30 if chart_data['labels'] else 0
            
                chart_data['average_monthly_cost'] = chart_data['total_cost'] / \
                    len(chart_data['labels']) if chart_data['labels'] else 0
                
            else:
                chart_data['average_daily_cost'] = chart_data['total_cost'] / \
                    len(chart_data['labels']) if chart_data['labels'] else 0
            
                chart_data['average_monthly_cost'] = 30 * chart_data['total_cost'] / \
                    len(chart_data['labels']) if chart_data['labels'] else 0
                
        else:
            chart_data = {
                "labels": [],
                "values": [],
                "total_cost": response['grid_data']['total']
            }
            for row in response["chart_data"]["categories"][0]["category"]:
                chart_data["labels"].append(row["label"])
                chart_data["values"].append(row["value"])

            chart_data['previous_spend'] = chart_data["values"][-1] if chart_data["values"] else 0
            
            if payload['report']['monthly'] == True:
                chart_data['average_daily_cost'] = (sum(
                    chart_data["values"])/len(chart_data["values"]))/30 if chart_data["values"] else 0
                
                chart_data['average_monthly_cost'] = sum(
                    chart_data["values"])/len(chart_data["values"]) if chart_data["values"] else 0
                
            else:
                chart_data['average_daily_cost'] = sum(
                    chart_data["values"])/len(chart_data["values"]) if chart_data["values"] else 0
                
                chart_data['average_monthly_cost'] = 30 * (sum(
                    chart_data["values"])/len(chart_data["values"]) if chart_data["values"] else 0)
        
    return chart_data


# To fetch all regions/services/tags/accounts
@json_view
def filtration_menu_rh_json(request):
    """
    To fetch the filteration menu for filters from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    payload = json.loads(request.body)
    rh = ResourceHandler.objects.get(id=payload['rh_id']).cast()
    rh_file_name = f'filteration_data_{payload["rh_id"]}'
    print(payload)

    should_fetch = check_for_cache(rh_file_name)
    print(f'--------------{rh_file_name}---------------')
    print(should_fetch)

    if should_fetch:
        if isinstance(rh, AWSHandler):
            response = ApiResponse(
                payload, 'filtration_menu'
                ).fetch_response()
            if response:
                response = response.json(
                    )['filteration_menu']["cost_report"]["AWS"]
                if not 'Services' in response:
                    response = {'Services': ''}
            else:
                response = {'Services': ''}

            if response["Services"]:
                set_cache_data(rh_file_name, response)

        elif isinstance(rh, AzureARMHandler):
            response = ApiResponse(
                payload, 
                'azure_filtration_menu').fetch_response()
            if response:
                response = response.json(
                    )['azure_filteration_menu']["azure_cost_report"]["Azure"]
                if not 'Services' in response:
                    response = {'Services': ''}
            else:
                response = {'Services': ''}
                    
            response_resource_group = ApiResponse(
                payload, 'azure_resource_groups',
                request_type="POST").fetch_response()
            if response_resource_group:
                response['ResourceGs'] = response_resource_group.json()
            else:
                response = {'ResourceGs': ''}
                
            response_tag_keys = ApiResponse(
                payload, 'azure_tag_keys'
                ).fetch_response()
            if response_tag_keys:
                response['Tags'] = response_tag_keys.json()
            else:
                response = {'Tags': ''}

            if response["Services"] and response["ResourceGs"] and response["Tags"]:
                set_cache_data(rh_file_name, response)
    else:
        response = get_cache_data(rh_file_name)

    return response


@json_view
def forecast_for_rh_json(request):
    """
    To fetch the forecasting values in case of future dates 
    are selected

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    charts_data = {"labels": [], "values": []}
    payload = json.loads(request.body)
    rh = ResourceHandler.objects.get(id=payload['report']['rh_id']).cast()

    if isinstance(rh, AWSHandler):
        response = ApiResponse(payload, 'get_aws_forecast',
                               request_type="POST").fetch_response()
        if response:
            response = response.json()

    elif isinstance(rh, AzureARMHandler):
        response = ApiResponse(payload, 'get_azure_forecast',
                               request_type="POST").fetch_response()
        if response:
            response = response.json()
            
    print(response)
    # To get the remaining days and hours forecast
    start_date = date.today()
    end_date_string = payload['report']['date_range']['end_date']
    end_date = datetime.strptime(end_date_string, "%d-%m-%Y").date()
    starting_date_string = payload['report']['date_range']['start_date']
    starting_date = datetime.strptime(starting_date_string, "%d-%m-%Y").date()
    
    while start_date <= end_date:
        if start_date >= starting_date:
            charts_data["labels"].append(start_date.strftime("%d %b %Y"))
            if start_date == date.today():
                today = datetime.now()
                remaining_hours_of_day = round(
                    24 - (today.hour + (today.minute/60)), 2)
                value = 24 * response['hour_forecast_value']
                charts_data["values"].append(value)
            else:
                charts_data["values"].append(response['day_forecast_value'])
        start_date += timedelta(days=1)
    
    if payload['report']['monthly']:
        forecast_data = {'labels': [], 'values': []}
        
        for forecast_month in payload['report']['month_labels']:
            total_cost = 0
            
            values_indexes = [index for index, forecast_date in enumerate(
                charts_data['labels']) if forecast_month[0:3] in forecast_date]
            total_cost = sum([charts_data['values'][indexes]
                             for indexes in values_indexes])
            forecast_data['labels'].append(forecast_month)
            forecast_data['values'].append(total_cost)

        return forecast_data

    return charts_data


@json_view
def get_resource_name(request):
    """
    To fetch the Azure tags from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    payload = json.loads(request.body)

    response = ApiResponse(payload, 'azure_resource_names',
                           request_type="POST").fetch_response()
    if response:
        response = response.json()

    return response


@json_view
def get_tag_values(request):
    """
    To fetch the Azure tag values for selected tag from Kumolus

    Args:
        request (http request): request having various params

    Returns:
        dict: Python dictionary having data
    """
    payload = json.loads(request.body)

    response = ApiResponse(
        payload, 
        'azure_tag_values').fetch_response()
    if response:
        response = response.json()

    return response
