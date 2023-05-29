import {
  LoaderClass, DATA_BACKUP_HOURS, numberFormatter,
  AWS_SERVICE_TYPE_MATCH, AWS_SERVICE_TAG_MAP,
  AZURE_SERVICE_TYPE_MATCH, AZURE_SERVICE_TAG_MAP,
  SERVICE_WISE_METRICS, AWS_COLUMN_TO_SHOW,
  AWS_COLUMN_TO_SHOW_1,
  AZURE_COLUMN_TO_SHOW, PROP_MAPPING
} from './common.js';
import { AWS_GRAPH, AZURE_GRAPH } from './_graph.js'

var loaderObjEffi = new LoaderClass('efficiency-tab');

var tagLists = [];
var suppressed = [];
var unUsedServices = [];
var unOptimizedServices = [];
var data = [];
var selectedTagList = [];
var serviceDetailList = [];
var igonredServiceList = [];
var columns = [];
var tagLists = {};
var amisColumnCount = 0;
var providers_object = {};
var allServiceData = {};
var dataForGraphParams = {};
var metricNames = [];
var startTime = 168;
var period = 1440;
var noOfGraphs = 0;
var sortBy = '';
var service = "";
var selectedServiceName = "";
var graphParameters = "";
var adapterNameMaster = "";
var whichData = "average";
var apiData;
var zeroModalRows;
var mainTagSelectedList;
var mainTable;
var all_services;
var listServicesDatatable;
var regionSelect = dropdownValue('regions');
var serviceSelect = dropdownValue('services');
var lifecycleSelect = dropdownValue('lifecycle');
var tagKeySelect = dropdownValue('tags');
var tagValueSelect = dropdownValue('values');

const KUMO_WEB_HOST_EFFI = $('#tab-efficiency #host_details').data('host');
const RESOURCE_HANDLER = {
  handlerId: $('#handler_details').data('handlerid'),
  handlerType: $('#handler_details').data('handler'),
  handlerCurrency: $('#handler_details').data('acurrency'),
  handlerNormalId : $('#handler_details').data('normalid'),
  normalAdapterId: $('#handler_details').data('normaladapter'),
}
console.log(RESOURCE_HANDLER);

const SERVICE_TYPE_MAP = RESOURCE_HANDLER.handlerType === 'AWS' ? AWS_SERVICE_TYPE_MATCH : AZURE_SERVICE_TYPE_MATCH
const SERVICE_TYPE_TAG_MAP = RESOURCE_HANDLER.handlerType === 'AWS' ? AWS_SERVICE_TAG_MAP : AZURE_SERVICE_TAG_MAP

var validationStatus = validateCred();

$(document).ready(function () {

  if ((KUMO_WEB_HOST_EFFI != "") && (validationStatus)) {
    if ((RESOURCE_HANDLER.handlerNormalId != "") && (RESOURCE_HANDLER.normalAdapterId != "")) {
      $('#efficiency-tab .errorMessageModal').modal('hide');
      $('#form-cost').css('filter', 'none');
      $("#tag-btn").addClass("hidden")
      getRegions();
      getServicesList();

      for (const SER in SERVICE_TYPE_MAP) {
        $("#cost-services, #select-services").append(`<option value="${SERVICE_TYPE_MAP[SER]['id']}">${SERVICE_TYPE_MAP[SER]['name']}</option>`);
      }

      applySelectize('#cost-services, #select-services, #cost-lifecycle, #select-lifecycle', false);

      $(document).on('click', '.clickable-call', function (e) {
        $('#listServicesModal').modal('show');
        regionSelect = $('#cost-regions').val();
        serviceSelect = $('#cost-services').val();
        lifecycleSelect = $('#cost-lifecycle').val();
        mainTagSelectedList = selectedTagList.map(a => ({...a}));
        $('#modal-service').empty();
    
        for(var item=0; item<$('.clickable-call').length; item++) {
          let elementItems = $($('.clickable-call')[item]).data();
          $('#modal-service').append(`<option class="cost-service-detail" data-type= "${elementItems['type']}" value="${elementItems['type']}">${SERVICE_TYPE_MAP[elementItems['type']]['name']} | ${elementItems['count']} | $${numberFormatter(parseFloat(elementItems['amount']))}</option>`);
        }
        getServiceDetail($(this)[0], 'panel');
      });

      $("#listServicesModal").on("hidden.bs.modal", function () {
        selectedTagList = mainTagSelectedList.map(a => ({...a}));
      });

      $(document).on('click', '#kumo-csv-download, #modal-csv-download', function (e) {
        getCSV($(this).data('type'));
      });

      $(document).on('click', '.testRemove', function (e) {
        removeTags($(this).data('value'));
      });

      $(document).on('click', '.closeModal', function (e) {
        $('#efficiency-tab .errorMessageModal').modal('hide');
        $('#form-cost').css('filter', 'none');
        document.body.style.position = 'absolute';
      });

      $(document).on('change', '#modal-service', function (e) {
        getServiceDetail($('#modal-service').find(":selected")[0], 'modal-service');
      });

      $(document).on('change', '#modal-category', function (e) {
        changeServiceType($('#modal-category').find(":selected")[0]);
      });

      $(document).on('click', '.apply-modal-filters', function (e) {
        applyModalFilters();
      });

      $(document).on('click', '.close', function (e) {
        if (($('#select-regions').val() == $('#cost-regions').val()) &&
          ($('#select-services').val() == $('#cost-services').val()) &&
          ($('#select-tags').val() == $('#cost-tags').val()) &&
          ($('#select-lifecycle').val() == $('#cost-lifecycle').val()) &&
          ($('#select-values').val() == $('#cost-values').val())) {
          clearAndResetSelectize()
        }
        else if (($('#select-regions').val() != "") || ($('#select-services').val() != "") ||
          ($('#select-tags').val() != "") || ($('#select-lifecycle').val() != "") ||
          ($('#select-values').val() != "")) {
          clearAndResetSelectize()
          $(`li[data-target='#${$('#modal-category').val()}'] a`).trigger("click");
        }
      });

      // Add event listener for opening and closing details
      $(document).on('click', 'td.details-control', function () {
        showServiceDetailGraph(this);
      });

      $(document).on("change", "#graph_time", function () {
        period = $("#graph_time").val();
        getModalGraphData();
      });

      $(document).on("change", "#graph_duration", function () {
        startTime = $("#graph_duration").val();
        getModalGraphData();
      });

      $(document).on("change", "#graph_type", function () {
        whichData = $("#graph_type").val();
        getModalGraphData();
      });
    } else {
      $('#efficiency-tab .errorMessageModal').modal('show');
      $('#form-cost').css('filter', 'blur(10px)');
      $('#efficiency-tab .go-to-admin').addClass('hidden');
      $('#efficiency-tab .go-to-rh').removeClass('hidden');
      $('#efficiency-tab .no-data').addClass('hidden');
    }
  }
  else {
    $('#efficiency-tab .errorMessageModal').modal('show');
    $('#form-cost').css('filter', 'blur(10px)');
    $('#efficiency-tab .go-to-admin').removeClass('hidden');
    $('#efficiency-tab .go-to-rh').addClass('hidden');
    $('#efficiency-tab .no-data').addClass('hidden');
  }

});

async function validateCred() {
  const URL = "/xui/kumo/api/validate_api_token/";
  let payload = {};
  
  await $.post(URL, JSON.stringify(payload), (response) => {
    console.log(response.result)
    if (Object.keys(response.result).length != 0) {
      if (response.result.message == "success") { return true; }
      else { return false; }
    }
  })
}

function showServiceDetailGraph(event) {
  let tr = $(event).closest('tr');
  let row = listServicesDatatable.row(tr);
  let rowData = row.data();
  let columnName = listServicesDatatable.settings().init().columns;
  let rowObject = {};

  columnName.forEach((element, index) => {
    rowObject[element.title] = rowData[index]
  });

  if (RESOURCE_HANDLER.handlerType == "AWS") {
    providers_object.adapter_id = allServiceData[rowObject.Name].adapter_id;
    providers_object.provider_id = allServiceData[rowObject.Name].provider_id;
    providers_object.region_id = allServiceData[rowObject.Name].region_id;
    providers_object.id = allServiceData[rowObject.Name].id;
  }
  else if (RESOURCE_HANDLER.handlerType == "Azure") {
    providers_object.id = allServiceData[rowObject["Service Name(ID)"]].id;
    providers_object.service_type = allServiceData[rowObject["Service Name(ID)"]].service_type;
  }

  selectedServiceName = rowObject.Name;

  if (row.child.isShown()) {
    // event row is already open - close it
    row.child.hide();
    tr.removeClass('shown');
    $(event).html('<i class="fas fa-angle-down fa-2x"></i>');
  } else {
    collapseAll();
    $(event).html('<i class="fas fa-angle-up fa-2x"></i>');
    // Open event row
    row.child(format(row.data())).show();
    row.child().css('background-color', '#eaeaeaba');
    getModalGraphData();
    tr.addClass('shown');
    applySelectize('#graph_time, #graph_duration, #graph_type', false);
  }
}

function clearAndResetSelectize() {
  resetSelectizeValue(`#select-regions`);
  resetSelectizeValue(`#select-services`);
  resetSelectizeValue(`#select-tags`);
  resetSelectizeValue(`#select-lifecycle`);
  resetSelectizeValue(`#select-values`);
  regionSelect = dropdownValue('regions');
  serviceSelect = dropdownValue('services');
  lifecycleSelect = dropdownValue('lifecycle');
}

function applySelectize(dropdownId, optionArray) {
  let emptyOption = true;
  if ((dropdownId == "#cost-tags") || (dropdownId == "#select-tags") ||
    (dropdownId == "#cost-values") || (dropdownId == "#select-values")) {
    emptyOption = false
  }

  if (optionArray) {
    $(`${dropdownId}`).selectize({
      allowEmptyOption: emptyOption,
      create: true,
      valueField: 'id',
      labelField: 'title',
      searchField: 'title',
      options: optionArray,
    });
  } else {
    $(`${dropdownId}`).selectize({
      allowEmptyOption: emptyOption,
      create: true,
    });
  }
}

function getParsedListServiceData(response, type) {
  let dataSet = [];
  if (RESOURCE_HANDLER.handlerType === 'AWS') {
    switch (type) {
      case 'amis':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(`${response[i].name}` || 'N/A')
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].access || 'N/A')
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].provider_id,
            "region_id": response[i].region_id,
            "id": response[i].id,
          }
          adapterNameMaster = "";
        }
        break;
      case 'idle_stopped_rds':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(`${response[i].name}` || 'N/A')
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].lifecycle || 'N/A')
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].provider_id,
            "region_id": response[i].region_id,
            "id": response[i].id,
          }
          adapterNameMaster = response[i].adapter_name;
        }
        break;
      case 'idle_stopped_ec2':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(`${response[i].name}` || 'N/A')
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].lifecycle || 'N/A')
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].provider_id,
            "region_id": response[i].region_id,
            "id": response[i].id,
          }
          adapterNameMaster = response[i].adapter_name;
          dataForGraphParams[`${response[i].name}`] = {
            "max_cpu": response[i].max_cpu_utilization,
            "nw_in": response[i].max_network_in_utilization,
            "nw_out": response[i].max_network_out_utilization,
          }
        }
        break;
      case 'idle_ec2':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(`${response[i].name}` || 'N/A')
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].lifecycle || 'N/A')
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].provider_id,
            "region_id": response[i].region_id,
            "id": response[i].id,
          }
          adapterNameMaster = response[i].adapter_name;
          dataForGraphParams[`${response[i].name}`] = {
            "max_cpu": response[i].max_cpu_utilization,
            "nw_in": response[i].max_network_in_utilization,
            "nw_out": response[i].max_network_out_utilization,
          }
        }
        break;
      case 'idle_rds':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(`${response[i].name}` || 'N/A')
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].lifecycle || 'N/A')
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].provider_id,
            "region_id": response[i].region_id,
            "id": response[i].id,
          }
          adapterNameMaster = response[i].adapter_name;
        }
        break;
      case 'ec2_right_sizings':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          data.push(`${response[i].instance_name}` || 'N/A');
          data.push(response[i].region || 'N/A');
          data.push(response[i].additional_information.lifecycle || 'N/A');
          data.push(response[i].instancetype || 'N/A');
          data.push(response[i].resizetype || 'N/A');
          data.push(getServiceTags(response[i].instancetags));
          data.push(`$${response[i].costsavedpermonth || 0}`);
          dataSet.push(data);
          allServiceData[`${response[i].instance_name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].instanceid,
            "region_id": response[i].region_id,
          }
          adapterNameMaster = response[i].account_id.name;
          dataForGraphParams[`${response[i].instance_name}`] = {
            "max_cpu": response[i].maxcpu,
            "max_nw": response[i].maxnetwork,
            "max_iops": response[i].maxiops,
          }
        }
        break;
      default:
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(`${response[i].name}` || 'N/A')
          data.push(response[i].region_name || 'N/A');
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "adapter_id": response[i].adapter_id,
            "provider_id": response[i].provider_id,
            "region_id": response[i].region_id,
            "id": response[i].id,
          }
          adapterNameMaster = response[i].adapter_name;
        }
        break;
    }
  } else {
    switch (type) {
      case 'idle_databases':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(response[i].name || 'N/A');
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].service_type || 'N/A');
          data.push(response[i].state || 'N/A')
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "id": response[i].id,
            "service_type": response[i].service_type
          }
          adapterNameMaster = response[i].adapter_name;
        }
        break;
      case 'unassociated_public_ips':
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(response[i].name || 'N/A');
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].service_type || 'N/A');
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "id": response[i].id,
            "service_type": response[i].service_type
          }
          adapterNameMaster = response[i].adapter_name;
        }
        break;
      default:
        for (var i = 0; i < response.length; i++) {
          let data = [];
          let additionalInfo = getAdditionalInfo(response[i])
          data.push(response[i].name || 'N/A');
          data.push(response[i].region_name || 'N/A');
          data.push(response[i].state || 'N/A');
          data.push(additionalInfo);
          data.push(getServiceTags(response[i].service_tags));
          data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
          data.push(response[i].days_old || 0)
          dataSet.push(data);
          allServiceData[`${response[i].name}`] = {
            "id": response[i].id,
            "service_type": response[i].service_type
          }
          adapterNameMaster = response[i].adapter_name;
        }
        break;
    }
  }
  return dataSet;
}

async function getRegions() {
  loaderObjEffi.display();

  var payload = {
    adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
    check_permission: 'false',
    service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
    handler_type: RESOURCE_HANDLER.handlerType,
    provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
  }
  const URL = "/xui/kumo/api/region_list_for_rh_json/"
  await $.post(URL, JSON.stringify(payload), (response) => {
    response.regions_list.forEach(reg => {
      $("#cost-regions, #select-regions").append(`<option value="${reg['region_id']}">${reg['region_name']}</option>`);
    })
    tagLists = response.tags_list;
    appendTagKeys("")
    applySelectize('#cost-regions, #select-regions', false);
  })
}

function appendTagKeys(serviceName) {
  var nestedTagList = []

  if (serviceName === "") {
    for (Object.key in tagLists) {
      nestedTagList = $.merge(Object.keys(tagLists[Object.key]), nestedTagList)
    }
  } else {
    if (jQuery.inArray(serviceName, Object.keys(tagLists)) > -1) {
      nestedTagList = Object.keys(tagLists[serviceName])
    }
  }
  nestedTagList = unique(nestedTagList)

  let tempTagListArray = [];
  nestedTagList.forEach(tag => {
    tempTagListArray.push({ id: tag, title: tag })
  })

  destroySelectize('#cost-tags');
  destroySelectize('#select-tags');
  applySelectize('#cost-tags', tempTagListArray);
  applySelectize('#select-tags', tempTagListArray);
}

function appendTagValues() {
  $("#cost-values, #select-values").empty()
  $("#cost-values, #select-values").append(`<option value="">Select Value</option>`);
  var serviceName = serviceSelect === "" ? "" : SERVICE_TYPE_TAG_MAP[serviceSelect]
  var tagKeyName = dropdownValue('tags');

  var nestedValuesList = []
  if (serviceName === "") {
    for (Object.key in tagLists) {
      if (tagLists[Object.key][tagKeyName]) {
        nestedValuesList = nestedValuesList.concat(tagLists[Object.key][tagKeyName])
      }
    }
  } else {
    nestedValuesList = tagLists[serviceName][tagKeyName]
  }

  let tempTagListArray = [];
  nestedValuesList = unique(nestedValuesList)
  nestedValuesList.forEach(value => {
    tempTagListArray.push({ id: value, title: value })
  })
  destroySelectize('#cost-values');
  destroySelectize('#select-values');
  applySelectize('#cost-values', tempTagListArray);
  applySelectize('#select-values', tempTagListArray);
}

function unique(array) {
  return array.filter(function (el, index, arr) {
    return index === arr.indexOf(el);
  });
}

function dropdownValue(dropdownType) {
  if ($(`#cost-${dropdownType}`).val() == "") {
    if ($(`#select-${dropdownType}`).val() == "") {
      return "";
    } else {
      return $(`#select-${dropdownType}`).val();
    }
  } else {
    return $(`#cost-${dropdownType}`).val();
  }
}

function getServicesList() {
  loaderObjEffi.display();
  if ($('#listServicesModal').hasClass('in')) {
    $("efficiency-tab .loader.fade.in").css({
      "position": 'fixed',
      "width": '100%',
      "height": '100%',
      "top": '0px',
      "left": '0px',
    });
  }
  const URL = "/xui/kumo/api/cost_efficiency_for_rh/"
  let payload = {
    adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
    adapter_ids: String(RESOURCE_HANDLER.handlerNormalId),
    region_id: regionSelect,
    service_type: serviceSelect,
    lifecycle: lifecycleSelect,
    count: 'true',
    tags: JSON.stringify(selectedTagList),
    tag_operator: 'OR',
    vcenter_id: '',
    public_snapshot: 'false',
    sort_by: 'days_old',
    sort: 'ASC',
    service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
    rh_id: RESOURCE_HANDLER.handlerId,
    provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
  }

  $.post(URL, JSON.stringify(payload), (response) => {
    
    let noNormal = (response.hasOwnProperty('message')) ? true : false;

    if (noNormal) {
      $('#efficiency-tab .generalError p').text(`
        No normal adapter found in Kumolus. Please create one 
        in Kumolus account and try again later!
      `);
      $('#efficiency-tab .errorMessageModal').modal('show');
      lockModal();
      $('#form-cost').css('filter', 'blur(10px)');
      $('#efficiency-tab .go-to-admin').addClass('hidden');
      $('#efficiency-tab .go-to-rh').addClass('hidden');
      $('#efficiency-tab .no-data').removeClass('hidden');
      $('#efficiency-tab .overviewButton').addClass('hidden');

      loaderObjEffi.hide();
    }
    else {
      if (Object.keys(response.service_type_summary).length != 0) {
        var data = response.service_type_summary
        let potentialBenefit = 0;
        let noOfServices = 0;
        let noOfAdapters = 1;
        all_services = [];

        $('#modal-csv-download').show();
  
        response.service_type_summary.forEach(service => {
          potentialBenefit = potentialBenefit + parseFloat(service.cost_sum);
          noOfServices = noOfServices + parseFloat(service.count);
        });
        
        unUsedServices = [];
        unOptimizedServices = [];
        suppressed = [];
        if (RESOURCE_HANDLER.handlerType === "AWS") {
          data.map(function (val) {
            if (val['type'] == 'Services::Compute::ECS::Cluster') {
              "";
            }
            else if ((val['type'] == 'Services::Compute::Server') || (val['type'] == 'Services::Database::Rds') || (val['type'] == 'ec2_right_sizings')) {
              val.category = "unoptimized";
              unOptimizedServices.push(val);
            } 
            else if (val['type'] == "ignore_services") {
              val.category = "suppressed";
              suppressed.push(val);
            }
            else {
              val.category = "unused";
              unUsedServices.push(val);
            }
          })

          all_services = unUsedServices.concat(unOptimizedServices.concat(suppressed)) ;
        } else {
          data.map(function (val) {
            val.category = "unused";
            unUsedServices.push(val)
          })

          all_services = unUsedServices.map(a => ({...a}));
        }

        if ($('#listServicesModal').hasClass('in')) {
          loadServices(all_services, 'modal');
        } else {
          loadServices(all_services, 'no-modal');
        }
  
        appendTagFilters();
  
        if ($('#listServicesModal').hasClass('in')) {
          if (zeroModalRows) {
            $('#listServicesModal .modal-body').html('<div><h4>We did not find any data for those filters.</h4></div>');
            $('#modal-csv-download').hide();
            loaderObjEffi.hide();
          }
          else {
            $('#modal-csv-download').show();
            $('#listServicesModal .modal-body').html('<div class="table-datatable table-responsive"><table id="list-service-detail" class="display"></table></div>')
            
            let selectedService = $('#modal-service').val();
            let modelServiceValues = [...$('#modal-service')[0].options].map(o => o.value);
            if (modelServiceValues.includes(selectedService)) {
              $('#modal-service').val(selectedService);
            } else {
              $("#modal-service").val($("#modal-service option:first").val());
            }
            $("#modal-service").change()            
          }  
        }
        else {
          $('#potential-cost').text(`$${numberFormatter(potentialBenefit) || 0}`);
          $('#no-of-services').text(`${numberFormatter(noOfServices) || 0}`);
          $('#no-of-adapters').text(noOfAdapters);
          loaderObjEffi.hide();
        }
      } 
      else {
        // $('#cost-accordion').html(`
        //   <div class="panel panel-default">
        //     <div class="panel-heading" style="padding: 12px;">
        //       <h4 class="panel-title">No Data Found</h4>
        //     </div>
        //   </div>
        // </div>
        // `)
        $('#modal-csv-download').hide();
        
        if ($('#listServicesModal').hasClass('in')) {
          $('#listServicesModal .modal-body').html('<div><h4>We did not find any data for those filters.</h4></div>');
          $('#efficiency-tab .errorMessageModal').modal('hide');
          $('#form-cost').css('filter', 'none');
          $('.closeModal').addClass('hidden');
        } else {
          // $('#efficiency-tab .generalError p').text(`
          //   Data is not available or is in sync if added new adapter in Kumolus account. 
          //   Please check Kumolus account or try after sometime!
          // `);
          // $('.closeModal').removeClass('hidden');
          // $('#efficiency-tab .errorMessageModal').modal('show');
          // lockModal();
          // $('#form-cost').css('filter', 'blur(10px)');
          // $('#efficiency-tab .go-to-admin').addClass('hidden');
          // $('#efficiency-tab .go-to-rh').addClass('hidden');
          // $('#efficiency-tab .no-data').removeClass('hidden');
          // $('#efficiency-tab .overviewButton').addClass('hidden');
          loadServices([], 'no-modal');
        }
        loaderObjEffi.hide();
      }
    }
  })
}

function lockModal() {
  // When the modal is shown, we want a fixed body
  document.body.style.position = 'fixed';
  document.body.style.top = `-${window.scrollY}px`;
}

function unlockModal() {
  // When the modal is hidden, we want a absolute body
  document.body.style.position = 'absolute';
  document.body.style.top = ``;
}

function appendTagFilters() {
  var serviceName = serviceSelect === "" ? "" : SERVICE_TYPE_TAG_MAP[serviceSelect]
  appendTagKeys(serviceName)
}

function applyModalFilters() {
  regionSelect = $('#select-regions').val();
  serviceSelect = $('#select-services').val();
  lifecycleSelect = $('#select-lifecycle').val();
  // regionSelect = $("#select-regions").val();
  // serviceSelect = SERVICE_TYPE_MAP[$("#modal-service").val()]['id']
  // lifecycleSelect = $("#select-lifecycle").val();
  var tagService = SERVICE_TYPE_TAG_MAP[serviceSelect]
  // $("#select-tags").empty()
  // $("#select-tags").append(`<option value="">Select Tag</option>`);
  resetSelectizeValue("#select-tags");
  getServicesList();
  appendTagKeys(tagService);
}

function removeTags(i) {
  selectedTagList.splice(i, 1)
  appendTagListBox();
  var serviceName = serviceSelect === "" ? "" : SERVICE_TYPE_TAG_MAP[serviceSelect]
  $("#cost-tags, #select-tags, #cost-values, #select-values").empty()
  $("#cost-tags, #select-tags").append(`<option value="">All Tags</option>`);
  $("#cost-values, #select-values").append(`<option value="">Select Value</option>`);
  if ($('#listServicesModal').hasClass('in')) {
    resetSelectizeValue("#select-values");
  } else {
    resetSelectizeValue("#cost-values");
  }
  appendTagKeys(serviceName)
}

function resetSelectizeValue(dropdownTag) {
  var $select = $(`${dropdownTag}`).selectize();
  var selectize = $select[0].selectize;
  selectize.clear();
}

function destroySelectize(dropdownTag) {
  var $select = $(`${dropdownTag}`).selectize();
  var selectize = $select[0].selectize;
  selectize.destroy();
}

function appendTagListBox() {
  // resetSelectizeValue('#cost-values');
  // resetSelectizeValue('#select-values');
  if ($('#listServicesModal').hasClass('in')) {
    $("#tagSelectListBox").empty();
    selectedTagList.forEach(function (elm, i) {
      $("#tagSelectListBox").append(`
        <div class="btn btn-success tagList">
        ${elm.tag_key} : ${elm.tag_value}
        <span class="fa fa-times remove-tag-icon testRemove" data-value=${i}></span>
        </div>`
      )
    })
  } else {
    selectedTagList.length > 0 ? $("#tag-btn").removeClass("hidden") : $("#tag-btn").addClass("hidden")
    $("#tagListBox").empty();
    if (selectedTagList.length == 0) {
      $('#costTagvalue').addClass('hidden');
      resetSelectizeValue("#cost-tags");
      getServicesList();
    } else {
      $('#costTagvalue').removeClass('hidden');
    }
    selectedTagList.forEach(function (elm, i) {
      $("#tagListBox").append(`
        <div class="btn btn-success tagList">
        ${elm.tag_key} : ${elm.tag_value}
        <span class="fa fa-times remove-tag-icon testRemove" data-value=${i}></span>
        </div>`
      )
    })
  }
}

function changeServiceType(e) {
  let service = $(e).val();
  let serviceCategory = ''

  switch (service) {
    case 'unused':
      serviceCategory = unUsedServices;
      break;
    case 'unoptimized':
      serviceCategory = unOptimizedServices;
      break;
    default:
      serviceCategory = suppressed;
      break;
  }

  if (serviceCategory.length > 0) {
    $('#modal-csv-download').show();
    $('#modal-service').empty();
    $('#listServicesModal .modal-body').html('<div class="table-datatable table-responsive"><table id="list-service-detail" class="display"></table></div>')
    serviceCategory.forEach(function (ser, i) {
      if (ser['count'] > 0) {
        let serTypeName = (service == 'suppressed') ? 'Ignored Services' : SERVICE_TYPE_MAP[ser['type']]['name'];
        let typeOfClass = (service != 'suppressed') ? "cost-service-detail" : "ignored-service";
        $('#modal-service').append(`<option class="${typeOfClass}" data-type= "${ser['type']}" value="${ser['type']}">${serTypeName} | ${ser['count']} | $${numberFormatter(parseInt(ser['cost_sum']))}</option>`);
      }
    })
    if ($('#modal-service').val() == null) {
      $('#listServicesModal .modal-body').html('<div><h4>We did not find any data for those filters.</h4></div>');
      $('#modal-csv-download').hide();
    } else {
      $('#listServicesModal .modal-body').html('<div class="table-datatable table-responsive"><table id="list-service-detail" class="display"></table></div>')
      $('#modal-csv-download').show();
      getServiceDetail($("#modal-service option:first")[0], 'first');
    }
  } else {
    $('#modal-service').empty();
    $('#listServicesModal .modal-body').html('<div><h4>We did not find any data for those filters.</h4></div>');
    $('#modal-csv-download').hide();
  }
}

function setSelectizeValue() {
  $(`#select-services`).data('selectize').setValue(serviceSelect, true);
  $(`#select-regions`).data('selectize').setValue(regionSelect, true);
  $(`#select-tags`).data('selectize').setValue(tagKeySelect, true);
  $(`#select-lifecycle`).data('selectize').setValue(lifecycleSelect, true);
  if (($('#cost-values').val() != "") && ($('#cost-values').val() != null)) {
    $(`#select-values`).data('selectize').setValue(tagValueSelect, true);
  }
}

function getServiceDetail(e, selectState) {
  var serviceStatus;

  if ((selectState == "modal-service") || (selectState == "first")) {
    serviceStatus = $(e).attr('class');
  }
  else {
    if ($(e).attr('data-type') == "ignore_services") {
      serviceStatus = "ignored-service";
    } else {
      serviceStatus = "cost-service-detail";
    }
  }
  
  let columnsIgnoreService = [];
  let payload = {};

  loaderObjEffi.display();
  $("efficiency-tab .loader.fade.in").css({
    "position": 'fixed',
    "width": '100%',
    "height": '100%',
    "top": '0px',
    "left": '0px',
  });

  if (serviceStatus == "cost-service-detail") {
    service = SERVICE_TYPE_MAP[$(e).data('type')].id;
    let serviceName = SERVICE_TYPE_MAP[$(e).data('type')].name;
    payload = {
      noloader: '',
      adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
      service_type: service,
      service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
      rh_id: RESOURCE_HANDLER.handlerId,
      sort_by: sortBy,
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
    }
  } else {
    payload = {
      count: 'false',
      sort_by: 'ASC',
      adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
      service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
    }
  }

  const URL = (serviceStatus == "cost-service-detail") ? "/xui/kumo/api/service_details_for_rh_json/" : "/xui/kumo/api/ignored_services_list_for_rh_json/";
  payload.region_id = regionSelect
  payload.lifecycle = lifecycleSelect
  payload.sort = 'ASC'
  payload.public_snapshot = 'false'
  payload.tags = JSON.stringify(selectedTagList)
  payload.per_page = 1000
  payload.page = 1

  $.post(URL, JSON.stringify(payload), (response) => {
    if (serviceStatus === "cost-service-detail") {
      serviceDetailList = response.services;
      data = getParsedListServiceData(serviceDetailList, service);
      // (service == "amis") ? amisColumnCount = data[0].length : "";
      appendHeaders(service)
      columnsIgnoreService = columns;
    } else {
      igonredServiceList = response.services;
      data = igonredServices(igonredServiceList);
      columnsIgnoreService = [{ title: "Name" }, { title: "Region" }, { title: "Service Type" },
      { title: "State" }, { title: "Additional Properties" }, { title: "Service Tags" },
      { title: "MEC" }, { title: "Days Old" }];
    }

    $(`.table-datatable`).html('<table id="list-service-detail" class="display"></table>');

    listServicesDatatable = $(`#list-service-detail`).DataTable({
      destroy: true,
      data: data,
      columns: columnsIgnoreService,
      fixedHeader: {
        header: true,
      },
      "bLengthChange": false,
      "pagingType": "full_numbers",
      "autoWidth": false,
    });

    $('#modal-service').val($(e).data('type'));

    let typeOfService = ''
    if (unUsedServices.flatMap(x => Object.values(x)).includes($(e).data('type'))) {
      typeOfService = "unused"
    }
    else if (unOptimizedServices.flatMap(x => Object.values(x)).includes($(e).data('type'))) {
      typeOfService = "unoptimized"
    } else {
      typeOfService = "suppressed"
    }

    if (serviceStatus === "cost-service-detail") {
      $('#modal-csv-download').show();
      $('#modal-csv-download').data('type', service);
    } else {
      $('#modal-csv-download').hide();
    }

    $('#modal-category').val(typeOfService);
    setSelectizeValue();
    appendTagListBox();
    if (adapterNameMaster) {
      $('#adapterNameMaster').text(adapterNameMaster);
    } else {
      $('#adapterNameMaster').text('');
    }

    $("efficiency-tab .loader.fade.in").css({
      "position": 'absolute',
      "width": '100%',
      "height": '100%',
      "top": '0px !important',
      "left": '0px !important',
    });
    loaderObjEffi.hide();

  })
}

function showIgnoreServiceTypes(serviceType) {
  var newServiceType;
  switch (serviceType) {
    case 'Services::Network::AutoScalingConfiguration::AWS':
    case 'Services::Network::Generic::AutoScalingConfiguration::AWS':
      newServiceType = 'Launch Configuration';
      break;

    case 'Services::Network::ApplicationLoadBalancer::AWS':
    case 'Services::Network::LoadBalancer::AWS':
    case 'Services::Network::Generic::LoadBalancer::AWS':
    case 'Services::Network::NetworkLoadBalancer::AWS':
    case 'Services::Network::LoadBalancer':
      newServiceType = 'Load Balancer';
      break;

    case 'Services::Compute::Server':
    case 'Services::Compute::Server::AWS':
    case 'Services::Compute::Generic::Server::AWS':
      newServiceType = 'EC2';
      break;

    case 'Services::Compute::Server::Volume':
    case 'Services::Compute::Server::Volume::AWS':
    case 'Services::Compute::Generic::Server::Volume::AWS':
      newServiceType = 'Volume';
      break;

    case 'Services::Database::Rds':
    case 'Services::Database::Rds::AWS':
    case 'Services::Database::Generic::Rds::AWS':
      newServiceType = 'RDS';
      break;

    case 'Services::Network::ElasticIP::AWS':
    case 'Services::Network::ElasticIP':
    case 'Services::Network::Generic::ElasticIP::AWS':
      newServiceType = 'Elastic IP';
      break;

    case 'volume':
      newServiceType = 'Volume Snapshots';
      break;

    case 'rds':
      newServiceType = 'RDS Snapshots';
      break;
  }
  return newServiceType;
}

function igonredServices(response) {
  var dataSet = []
  for (var i = 0; i < response.length; i++) {
    let data = [];
    let additionalInfo = getAdditionalInfo(response[i])
    data.push(response[i].name || 'N/A');
    data.push(response[i].region_name || 'N/A');
    data.push(showIgnoreServiceTypes(response[i].service_type))
    data.push(response[i].state || 'N/A')
    data.push(additionalInfo);
    data.push(getServiceTags(response[i].service_tags));
    data.push(`$${response[i].monthly_estimated_cost.toFixed(2) || 0}`);
    data.push(response[i].days_old || 0)
    dataSet.push(data);
    adapterNameMaster = response[i].account_name;
  }
  return dataSet
}

function appendHeaders(service) {
  if (RESOURCE_HANDLER.handlerType == "AWS") {
    switch (service) {
      case 'amis':
        columns = [{ title: "Name" }, { title: "Region" }, { title: "Access" }, { title: "Additional Properties" }, { title: "Service Tags" }, { title: "MEC" }, { title: "Days Old" }]
        break;
      case 'idle_rds':
        columns = AWS_COLUMN_TO_SHOW_1
        break;
      case 'ec2_right_sizings':
        columns = [{ title: "Name" }, { title: "Region" }, { title: "Lifecycle" }, { title: "Instance Size" }, { title: "Recommended Size" }, { title: "Service Tags" }, { title: "MES" }, { title: "", 'className': 'details-control', 'orderable': false, 'data': '', 'defaultContent': '<i class="fas fa-angle-down fa-2x"></i>' }]
        break;
      case 'idle_stopped_rds':
        columns = AWS_COLUMN_TO_SHOW_1
        break;
      case 'idle_stopped_ec2':
        columns = AWS_COLUMN_TO_SHOW_1;
        break;
      case 'idle_ec2':
        columns = AWS_COLUMN_TO_SHOW_1;
        break;
      case 'idle_volume':
        columns = AWS_COLUMN_TO_SHOW;
        break;
      case 'idle_load_balancer':
        columns = AWS_COLUMN_TO_SHOW;
        break;
      case 'unused_provisioned_iops_rds':
        columns = AWS_COLUMN_TO_SHOW;
        break;
      case 'unused_provisioned_iops_volumes':
        columns = AWS_COLUMN_TO_SHOW;
        break;
      default:
        columns = [{ title: "Name" }, { title: "Region" }, { title: "Additional Properties" }, { title: "Service Tags" }, { title: "MEC" }, { title: "Days Old" }]
        break;
    }
  } else {
    switch (service) {
      case 'idle_databases':
        columns = [{ title: "Service Name(ID)" }, { title: "Region" }, { title: "Type" }, { title: "State" }, { title: "Additional Properties" }, { title: "Service Tags" }, { title: "MEC" }, { title: "Days Old" }, { title: "", 'className': 'details-control', 'orderable': false, 'data': '', 'defaultContent': '<i class="fas fa-angle-down fa-2x"></i>' }]
        break;
      case 'unassociated_public_ips':
        columns = [{ title: "Service Name(ID)" }, { title: "Region" }, { title: "Type" }, { title: "Additional Properties" }, { title: "Service Tags" }, { title: "MEC" }, { title: "Days Old" }]
        break;
      case 'idle_lbs':
        columns = AZURE_COLUMN_TO_SHOW;
        break;
      case 'idle_vm':
        columns = AZURE_COLUMN_TO_SHOW;
        break;
      case 'idle_stopped_vm':
        columns = AZURE_COLUMN_TO_SHOW;
        break;
      case 'idle_disks':
        columns = AZURE_COLUMN_TO_SHOW;
        break;
      case 'vm_right_sizings':
        columns = AZURE_COLUMN_TO_SHOW;
        break;
      default:
        columns = [{ title: "Service Name(ID)" }, { title: "Region" }, { title: "State" }, { title: "Additional Properties" }, { title: "Service Tags" }, { title: "MEC" }, { title: "Days Old" }]
        break;
    }

    return columns;

  }
}

function getAdditionalInfo(s) {
  var information = [];

  if (s.additional_information) {
    $.each(s.additional_information, function (p, k) {
      if (p != null) {
        if (typeof p === 'object' && p[0]) {
          information.push(PROP_MAPPING[k] + " : " + p[0]['DeviceName']);
        } else {
          var unit = getUnit(k);
          if (p == 'non-windows')
            p = 'linux';
          information.push(PROP_MAPPING[p] + " : " + k + unit);
        }
      }
    });
    return information.join(', ');
  }
  return 'N/A';
}

function getUnit(key) {
  var unitMapping = {
    'volume_size': ' GiB',
    'allocated_storage': ' GiB',
    'VolumeSize': ' GiB'
  };
  return unitMapping[key] || '';
}

function getServiceTags(tags) {
  var tagArr = []
  if (tags) {
    tags.map(function (tag) {
      if (RESOURCE_HANDLER.handlerType == "AWS") {
        if ((tag['tag_key']) && (tag['tag_value'])) {
          tagArr.push(`${tag['tag_key']} : ${tag['tag_value']}`);
        }
      }
      else if (RESOURCE_HANDLER.handlerType == "Azure") {
        if ((tag['key']) && (tag['value'])) {
          tagArr.push(`${tag['key']} : ${tag['value']}`);
        }
      }
    })
  }
  return tagArr.join(', ')
}

function getCSV(service) {
  var payload;

  if (service == "ec2_right_sizings") {
    payload = {
      adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
      service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
      ec2_status: true
    }
  }
  else {
    payload = {
      noloader: '',
      adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
      region_id: regionSelect,
      service_type: service,
      lifecycle: lifecycleSelect,
      service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
      rh_id: RESOURCE_HANDLER.handlerId,
      sort_by: sortBy,
      sort: 'ASC',
      count: 'true',
      public_snapshot: 'false',
      tags: JSON.stringify(selectedTagList),
      per_page: 10,
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
      ec2_status: false
    }
  }

  const URL = '/xui/kumo/api/csv_download_for_rh_json?' + $.param(payload);
  window.open(URL, '_blank').focus();
}

function loadServices(listServices, serviceCategory) {
  let currentCount = 0;
  $('#modal-service').empty();
  if (serviceCategory == "no-modal") {
    $('#cost-accordion-div').empty();
    $('#cost-accordion-div').html(`
      <table id="cost-accordion-table" class="table table-striped" style="width:100%">
        <thead>
            <tr>
                <th>Type of Efficiency</th>
                <th>Service</th>
                <th>Count</th>
                <th>Estimated Savings</th>
                <th>Download CSV</th>
            </tr>
        </thead>
        <tbody>
            
        </tbody>
      </table>
    `);
    // if ((serviceCategory === 'unused') || (serviceCategory === 'unoptimized') || (serviceCategory === 'azure')) {
    if (listServices.length > 0) {
      listServices.forEach(function (ser, i) {
        if (ser['count'] > 0) {          
          if (ser['type'] == "ignore_services") {
            $('#cost-accordion-table tbody').append(
              `<tr>
                  <td>${ser['category'].charAt(0).toUpperCase() + ser['category'].slice(1)}</td>
                  <td><span><a id = ${i + 1} class="clickable-call" data-type= "${ser['type']}" data-count= "${ser['count']}" data-amount= "${numberFormatter(parseFloat(ser['cost_sum']))}"><span>${SERVICE_TYPE_MAP[ser['type']]['name']}</span></a></span></td>
                  <td>${ser['count']}</td>
                  <td><span class="acc-currency">$</span>${numberFormatter(parseFloat(ser['cost_sum']))}</td>
                  <td><span class="csv" title="Export to CSV" id="kumo-csv-download" data-type="${SERVICE_TYPE_MAP[ser['type']].id}" style="pointer-events: none;"><i class="fa fa-file-excel fa-xl" style="color: lightgray;font-size: x-large;" aria-hidden="true"></i></span></td>
              </tr>`)
            $('#modal-service').append(`<option class="ignored-service" data-type= "${ser['type']}" value="${ser['type']}">${SERVICE_TYPE_MAP[ser['type']]['name']} | ${ser['count']} | $${numberFormatter(parseFloat(ser['cost_sum']))}</option>`);
          } 
          else {
            $('#cost-accordion-table tbody').append(
              `<tr>
                  <td>${ser['category'].charAt(0).toUpperCase() + ser['category'].slice(1)}</td>
                  <td><span><a id = ${i + 1} class="clickable-call" data-type= "${ser['type']}" data-count= "${ser['count']}" data-amount= "${numberFormatter(parseFloat(ser['cost_sum']))}"><span>${SERVICE_TYPE_MAP[ser['type']]['name']}</span></a></span></td>
                  <td>${ser['count']}</td>
                  <td><span class="acc-currency">$</span>${numberFormatter(parseFloat(ser['cost_sum']))}</td>
                  <td><span class="csv" title="Export to CSV" id="kumo-csv-download" data-type="${SERVICE_TYPE_MAP[ser['type']].id}"><i class="fa fa-file-excel fa-xl" style="color: #2aa522;font-size: x-large;" aria-hidden="true"></i></span></td>
              </tr>`)
            $('#modal-service').append(`<option class="cost-service-detail" data-type= "${ser['type']}" value="${ser['type']}">${SERVICE_TYPE_MAP[ser['type']]['name']} | ${ser['count']} | $${numberFormatter(parseFloat(ser['cost_sum']))}</option>`);
          }
          currentCount++;
        }
      });

      if (currentCount > 0) {
        zeroModalRows = false;
      } else {
        zeroModalRows = true;
      }
    }
    else {
      zeroModalRows = true;
    }
  } else {
    if (listServices.length > 0) {
      listServices.forEach(function (ser, i) {
        if (ser['count'] > 0) {
          $('#modal-service').append(`<option class="cost-service-detail" data-type= "${ser['type']}" value="${ser['type']}">${SERVICE_TYPE_MAP[ser['type']]['name']} | ${ser['count']} | $${numberFormatter(parseFloat(ser['cost_sum']))}</option>`);
          currentCount++;
        }
      });

      if (currentCount > 0) {
        zeroModalRows = false;
      } else {
        zeroModalRows = true;
      }
    }
    else {
      zeroModalRows = true;
    }
  }  
  mainTable = $('#cost-accordion-table').dataTable({responsive: true, searching: false, paging: true, info: false, "bDestroy": true});
}

if (RESOURCE_HANDLER.handlerType === 'Azure') {
  $("li[data-target='#unoptimized'], li[data-target='#suppressed']").addClass('disabled-li');
  $('#cost-lifecycle').parent().hide();
  sortBy = 'cost_by_hour';
} else {
  $("li[data-target='#unoptimized'], li[data-target='#suppressed']").removeClass('disabled-li');
  $('#cost-lifecycle').parent().show();
  sortBy = 'provider_created_at';
}

$("#cost-services, #cost-regions, #cost-lifecycle").on("change", function () {
  regionSelect = dropdownValue('regions');
  serviceSelect = dropdownValue('services');
  lifecycleSelect = dropdownValue('lifecycle');
  var tagService = SERVICE_TYPE_TAG_MAP[serviceSelect]
  $("#cost-tags").empty()
  $("#cost-tags").append(`<option value="">All Tags</option>`);
  $("#cost-values").empty()
  $("#cost-values").append(`<option value="">Select Value</option>`);
  if (this.id === 'cost-services') {
    getServicesList();
    appendTagKeys(tagService)
  } else {
    getServicesList();
  }
})

$(window).on('resize', function () {
  $($.fn.dataTable.tables(true)).DataTable().columns.adjust();
});

$("#cost-tags, #select-tags").on("change", function () {
  appendTagValues()
  $("#cost-tags").val() == "" ? $('#costTagvalue').addClass('hidden') : $('#costTagvalue').removeClass('hidden')
})

$("#cost-values, #select-values").on("change", () => {
  if (($("#cost-tags").val() != "") || ($("#select-tags").val() != "")) {
    if ($('#listServicesModal').hasClass('in')) {
      var tagKey = $('#select-tags').val();
      var tagValue = $('#select-values').val();
    } else {
      var tagKey = $('#cost-tags').val();
      var tagValue = $('#cost-values').val();
      tagValue.length > 0 ? $("#tag-btn").removeClass("hidden") : $("#tag-btn").addClass("hidden")
    }
    selectedTagList.push({ "tag_key": tagKey, "tag_value": tagValue, "tag_sign": "=" })
    appendTagListBox();
  }
})

$("#submit-tag").on("click", () => {
  resetSelectizeValue("#cost-tags");
  getServicesList();
})

$("a[href='#tab-efficiency']").on("click", (e) => {
  if (!$('#efficiency-tab .errorMessageModal').hasClass('in')) {
        unlockModal();
      }
  else {
    lockModal();
  }
})

/* Formatting function for row details - modify as you need */
function format(d) {
  return (RESOURCE_HANDLER.handlerType == "AWS") ? AWS_GRAPH : AZURE_GRAPH;
}

function formateDate(date) {
  let formatted = new Date(date);
  var dd = formatted.getDate();

  var mm = formatted.getMonth() + 1;
  var yyyy = formatted.getFullYear();
  if (dd < 10) {
    dd = '0' + dd;
  }

  if (mm < 10) {
    mm = '0' + mm;
  }
  formatted = dd + '-' + mm + '-' + yyyy;
  return formatted;
}

function getModalGraphData() {
  let payload = {};
  loaderObjEffi.display();

  $("efficiency-tab .loader.fade.in").css({
    "position": 'fixed',
    "width": '100%',
    "height": '100%',
    "top": '0px',
    "left": '0px',
  });

  const URL = "/xui/kumo/api/get_graph_data/"
  if (RESOURCE_HANDLER.handlerType == "AWS") {
    metricNames = SERVICE_WISE_METRICS[service];
    payload.service_params = {};
    payload.service_params[`${providers_object.provider_id}`] = {
      adpater_id: providers_object.adapter_id,
      region_id: providers_object.region_id,
      metric_names: metricNames,
      start_time: startTime,
      period: period,
    }
    payload.noloader = null;
  }
  else if (RESOURCE_HANDLER.handlerType == "Azure") {

    metricNames = (service == "idle_databases") ? SERVICE_WISE_METRICS[service][providers_object.service_type] : SERVICE_WISE_METRICS[service];

    payload.service_params = {};
    payload.service_params[`${providers_object.id}`] = {
      metric_names: metricNames,
      duration: startTime,
      interval: period,
    }
    payload.provider = RESOURCE_HANDLER.handlerType
  }

  payload.provider_account_id = String(RESOURCE_HANDLER.handlerNormalId);

  $.post(URL, JSON.stringify(payload), (response) => {
    apiData = response[Object.keys(response)[0]];
    plotingTheGraphs();
  });
}

function plotingTheGraphs() {
  $('#graph_container').html('');
  let tempList = [];

  if (RESOURCE_HANDLER.handlerType == "AWS") {
    if ((service == "idle_stopped_ec2") || (service == "idle_ec2")) {
      tempList = ["CPUUtilization"];
      extractDataForGraph(tempList, whichData, "CPU Utilization", "(In percent)", "timestamp");

      tempList = ["NetworkIn", "NetworkOut", "NetworkPacketsIn", "NetworkPacketsOut"];
      extractDataForGraph(tempList, whichData, "Network", "(Bytes)", "timestamp");

      noOfGraphs = 2;
    }

    else if (service == "idle_load_balancer") {
      tempList = ["RequestCount"];
      extractDataForGraph(tempList, whichData, "Request Count", "", "timestamp");

      noOfGraphs = 1;
    }

    else if ((service == "idle_volume") || (service == "unused_provisioned_iops_volumes")) {
      tempList = ["VolumeReadOps", "VolumeWriteOps"];
      extractDataForGraph(tempList, whichData, "Throughput", "(Ops/s)", "timestamp");

      noOfGraphs = 1;
    }

    else if (service == "ec2_right_sizings") {
      tempList = ["CPUUtilization"];
      extractDataForGraph(tempList, whichData, "CPU Utilization", "(In percent)", "timestamp");

      tempList = ["DiskReadBytes", "DiskReadOps", "DiskWriteBytes", "DiskWriteOps"];
      extractDataForGraph(tempList, whichData, "Network", "(Bytes)", "timestamp");

      tempList = ["NetworkIn", "NetworkOut"];
      extractDataForGraph(tempList, whichData, "Disk", "(Operations)", "timestamp");

      noOfGraphs = 3;
    }

    else if ((service == "idle_stopped_rds") || (service == "idle_rds") ||
      (service == "unused_provisioned_iops_rds")) {
      tempList = ["DatabaseConnections"];
      extractDataForGraph(tempList, whichData, "DB Connections", "", "timestamp");

      tempList = ["WriteIOPS", "ReadIOPS"],
        extractDataForGraph(tempList, whichData, "Operations", "", "timestamp");

      noOfGraphs = 2;
    }
  }

  else if (RESOURCE_HANDLER.handlerType == "Azure") {
    if ((service == "idle_vm") || (service == "idle_stopped_vm")) {
      tempList = ["PercentageCpu"];
      extractDataForGraph(tempList, whichData, "CPU Utilization", "(In percent)", "time_stamp");

      tempList = ["NetworkInTotal", "NetworkOutTotal"];
      extractDataForGraph(tempList, whichData, "Network", "(Bytes)", "time_stamp");

      tempList = ["OSDiskReadOperationsSec", "OSDiskWriteOperationsSec", "VMCachedIOPSConsumedPercentage"];
      extractDataForGraph(tempList, whichData, "Disk", "(Operations)", "time_stamp");

      noOfGraphs = 3;
    }

    else if (service == "idle_disks") {
      tempList = ["CompositeDiskReadBytessec", "CompositeDiskReadOperationssec",
        "CompositeDiskWriteBytessec", "CompositeDiskWriteOperationssec"];
      extractDataForGraph(tempList, whichData, "Disk", "(Operations)", "time_stamp");

      noOfGraphs = 1;
    }

    else if (service == "idle_lbs") {
      tempList = ["ByteCount"];
      extractDataForGraph(tempList, whichData, "Byte Count", "(Bytes)", "time_stamp");

      noOfGraphs = 1;
    }

    else if (service == "idle_databases") {
      if (providers_object.service_type == "SQL") {
        tempList = ["dtu_consumption_percent"];
        extractDataForGraph(tempList, whichData, "DTU Consumption", "(In percent)", "time_stamp");

        noOfGraphs = 1;
      }
      else {
        tempList = ["io_consumption_percent"];
        extractDataForGraph(tempList, whichData, "IO Consumption", "(In percent)", "time_stamp");

        tempList = ["network_bytes_ingress", "network_bytes_egress"];
        extractDataForGraph(tempList, whichData, "Network", "(Bytes)", "time_stamp");

        noOfGraphs = 2;
      }
    }
  }

  $("efficiency-tab .loader.fade.in").css({
    "position": 'absolute',
    "width": '100%',
    "height": '100%',
    "top": '0px !important',
    "left": '0px !important',
  });

  loaderObjEffi.hide();
}

function extractDataForGraph(tempList, whichData, title, subtitle, timestamp) {
  let xAxis = [];
  let graphData = [];
  let series = [];
  let i = 0;

  tempList = tempList;

  for (i = 0; i < tempList.length; i++) {
    graphData = [];
    apiData[tempList[i]].forEach(element => {
      xAxis.push(formateDate(element[`${timestamp}`]));
      graphData.push(element[`${whichData}`]);
    });
    series.push({ name: tempList[i], data: graphData })
  }

  if ((service == "idle_stopped_ec2") || (service == "idle_ec2")) {
    switch (tempList[0]) {
      case "CPUUtilization":
        graphParameters = `
            <span><strong>Max-CPU-Uti :</strong>${dataForGraphParams[selectedServiceName].max_cpu}</span>`;
        break;

      case "NetworkIn":
        graphParameters = `
            <div style="display: flex;justify-content: space-between;">
              <span><strong>Max-N/W In :</strong>${dataForGraphParams[selectedServiceName].nw_in}</span>
              <span><strong>Max-N/W Out :</strong>${dataForGraphParams[selectedServiceName].nw_out}</span>
            </div>`;
        break;

      default:
        graphParameters = "";
        break;
    }
  }

  else if (service == "ec2_right_sizings") {
    switch (tempList[0]) {
      case "CPUUtilization":
        graphParameters = `
          <span><strong>Max-CPU-Uti :</strong>${dataForGraphParams[selectedServiceName].max_cpu}</span>`;
        break;

      case "NetworkIn":
        graphParameters = `
        <span><strong>Max-Network :</strong>${dataForGraphParams[selectedServiceName].max_nw}</span>`;
        break;

      case "DiskReadBytes":
        graphParameters = `
        <span><strong> Max-IOPS :</strong>${dataForGraphParams[selectedServiceName].max_iops}</span>`;
        break;

      default:
        graphParameters = "";
        break;
    }
  }

  else {
    graphParameters = "";
  }

  if (graphParameters) {
    $('#graph_container').append(`
      <div class="form-group" style="margin-inline:7px;">
        ${graphParameters}
        <div id="${tempList[0]}">
        </div>
      </div>
    `);
  } else {
    $('#graph_container').append(`
        <div class="form-group" style="margin-inline:7px;">
          <div id="${tempList[0]}">
          </div>
        </div>
      `);
  }


  DrawHighChart(title, subtitle, xAxis, series, tempList[0]);
}

function DrawHighChart(title, subtitle, xAxis, series, div_id) {
  $(function () {
    $(`#${div_id}`).highcharts({
      chart: {
        height: 250,
        width: ($('#graph_container').parent().width() / noOfGraphs) - 14,
        events: {
          load: function (event) {
            event.target.reflow();
          }
        }
      },
      title: {
        text: title
      },
      subtitle: {
        text: subtitle
      },
      xAxis: {
        categories: xAxis,
        labels: {
          enabled: true,
          overflow: "allow",
          rotation: -90,
          y: 10,
          formatter: function () {
            return this.value.slice(0, -5);
          }
        },
      },
      yAxis: {},
      tooltip: {},
      legend: {
        layout: 'horizontal',
        align: 'center',
        verticalAlign: 'bottom',
        borderWidth: 0,
        showInLegend: false
      },
      series: series,
    });
  });
}

function collapseAll() {
  // Enumerate all rows
  listServicesDatatable.rows().every(function () {
    // If row has details expanded
    if (this.child.isShown()) {
      // Collapse row details
      this.child.hide();
      $(this.node()).removeClass('shown');
    }
  });
}