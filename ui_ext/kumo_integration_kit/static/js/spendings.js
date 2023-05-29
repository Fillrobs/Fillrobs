import { LoaderClass, DATA_BACKUP_HOURS, numberFormatter,
         DIMENSION_DATA, AWS_SERVICE_MAP, MONTH_NAMES } from './common.js';

const imageData = require('../images/kumolus.png');

var loaderObjSpend = new LoaderClass('spendings-tab');
var riService;
var startDate;
var dateCheck;
var endDate;
var chartData = {};
var legend = {}
var costAdviserData = {};
var riRecommendations = [];
var filtrationData = {};
var selectedTags = {};
var apiData = {};
var forecastData = {};
var dateRange = {};
var resourceGroup = [];
var serviceName = [];
var serviceTier = [];
var location = [];
var subscriptionList = [];
var tab = "";
var subscriptions = [];
var subscription = [];
var consumedService = [];
var subscriptionJson = [];
var resourceName = [];
var monthLabels = [];
var totalSpendService = 0;
var csvStr;
var forecastCost = 0;
var totalCost = 0;
var pdfData = [];
var pageGap = 0;
var colName = "";

let daily = true;
let monthly = false;
let isUpfrontReservationCharges = true;
let isSupportCharges = true;
let isOtherSubscriptionCharges = true;
let multiSeries = false;
let region = [];
let account = [];
let service = [];
let usageType = [];
let dimensions = ["date"];
let productFamily = [];

const SPEND_FORM_DATA = new FormData(document.querySelector("#spendDetailsForm"));
const KUMO_WEB_HOST_SPEND = $('#tab-spend #host_details').data('host');
const RESOURCE_HANDLER = {
  handlerId: $('#handler_details').data('handlerid'),
  handlerType: $('#handler_details').data('handler'),
  handlerCurrency: $('#handler_details').data('acurrency'),
  handlerNormalId : String($('#handler_details').data('normalid')),
  normalAdapterId: $('#handler_details').data('normaladapter'),
}

var validationStatus = validateCred();

console.log(RESOURCE_HANDLER);

$(document).ready(function () {

  if ((KUMO_WEB_HOST_SPEND != "") && (validationStatus)) {
    if ((RESOURCE_HANDLER.handlerNormalId != "") && (RESOURCE_HANDLER.normalAdapterId != "")) {
      $('#spendings-tab .errorMessageModal').modal('hide');
      $('#spendDetailsForm').css('filter', 'none');
      appendDefaultValues();
      fetchOverviewData();
      getServicesList();
      getFiltrationMenu();
      
      $(document).on('click', '.removeTags', function (e) {
        removeTags($(this).data('value'));
      });

      $(document).on('click', '.closeModal', function (e) {
        $('#spendings-tab .errorMessageModal').modal('hide');
        $('#spendDetailsForm').css('filter', 'none');
        document.body.style.position = 'absolute';
      });
      
      $(document).on('click', '#exportToCSV', function (e) {
        downloadCSV(csvStr);
      });

      $(document).on('click', '#exportToPDF', function (e) {
        downloadPDF(csvStr);
      });

      $(document).on('click', '.overviewButton', function (e) {
        $('#spendings-tab .errorMessageModal').modal('hide');
        $('#spendDetailsForm').css('filter', 'none');
        $('#spendings-tab .go-to-admin').addClass('hidden');
        $('#spendings-tab .go-to-rh').addClass('hidden');
        $('#spendings-tab .no-data').addClass('hidden');
        $('#spendings-tab .overviewButton').addClass('hidden');
        $("li[data-target='#overview']").tab('show').click();
        unlockModal();
      });

    } else {
      $('#spendings-tab .errorMessageModal').modal('show');
      lockModal();
      $('#spendDetailsForm').css('filter', 'blur(10px)');
      $('#spendings-tab .go-to-admin').addClass('hidden');
      $('#spendings-tab .go-to-rh').removeClass('hidden');
      $('#spendings-tab .no-data').addClass('hidden');
    }
  } else {
    $('#spendings-tab .errorMessageModal').modal('show');
    lockModal();
    $('#spendDetailsForm').css('filter', 'blur(10px)');
    $('#spendings-tab .go-to-admin').removeClass('hidden');
    $('#spendings-tab .go-to-rh').addClass('hidden');
    $('#spendings-tab .no-data').addClass('hidden');
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

function lockModal() {
  // When the modal is shown, we want a fixed body
  document.body.style.position = 'fixed';
  document.body.style.top = `0`;
}

function unlockModal() {
  // When the modal is hidden, we want a absolute body
  document.body.style.position = 'absolute';
  document.body.style.top = ``;
}

function appendDefaultValues() {
  loaderObjSpend.display();

  appendRIService();
  $('#ri-percentage-saving').text(`${0}%`);
  $('#ri-on-demand').text(`$${0}`);
  $('#total-ri').text(`${0}`);
  $('#ri-potensials_savings').text(`$${0}`);
  $('#cost-adviser').text(`$${0}`);
  $('#unused').text(`$${0} (${0})`);
  $('#unoptimized').text(`$${0} (${0})`);
  $('#ignored').text(`$${0} (${0})`);
}

function appendRIService() {
  if (RESOURCE_HANDLER.handlerType === "AWS") {
    $('#header-used-ris').removeClass('hidden')
    $('#header-unsed-ris').removeClass('hidden')
    riService = 'Amazon Elastic Compute Cloud - Compute'
    $('#res-service').append(`
      <option value="Amazon Elastic Compute Cloud - Compute" selected="selected">EC2</option>
      <option value="Amazon ElastiCache">ElastiCache</option>
      <option value="Amazon Elasticsearch Service">Elasticsearch</option>
      <option value="Amazon Relational Database Service">RDS</option>
      <option value="Amazon Redshift">Redshift</option>
    `)
  }
  else {
    $('#header-used-ris').addClass('hidden')
    $('#header-unsed-ris').addClass('hidden')
    riService = 'VirtualMachines'
    $('#res-service').append(`
      <option value="VirtualMachines">Virtual Machines</option>
      <option value="SQLDatabases">SQL Databases</option>
      <option value="PostgreSQL">PostgreSQL</option>
      <option value="ManagedDisk">Managed Disk</option>
      <option value="MySQL">MySQL</option>
      <option value="RedHat">Red Hat</option>
      <option value="MariaDB">Maria DB</option>
      <option value="RedisCache">Redis Cache</option>
      <option value="CosmosDB">Cosmos DB</option>
      <option value="SqlDataWarehouse">Sql DataWarehouse</option>
      <option value="SUSELinux">SUSE Linux</option>
      <option value="AppService">App Service</option>
      <option value="BlockBlob">Block Blob</option>
      <option value="AzureDataExplorer">Azure Data Explorer</option>
      <option value="VMwareCloudSimple">VMware CloudSimple</option>
    `)
  }
}

async function fetchOverviewData() {
  
  const URL = "/xui/kumo/api/charts_data_rh_json/";
  let payload = { 
    rh_id: RESOURCE_HANDLER.handlerId,
    provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
  }

  await $.post(URL, JSON.stringify(payload), (response) => {

    let noBilling = (response.hasOwnProperty('message')) ? true : false;

    let validateData = ((Object.keys(response.cost_by_service_chart_data).length == 0) &&
                        (Object.keys(response.cost_by_day_chart_data).length == 0) &&
                        (Object.keys(response.cost_by_year_chart_data).length == 0) &&
                        (response.yesterday_spend == 0) && (response.total_spend == 0) && 
                        (response.month_to_date == 0) && (response.year_to_date == 0) &&
                        (response.year_forecast == 0) && (response.day_cost_diff == 0) &&
                        (response.month_cost_diff == 0))
                                           
    console.log(validateData);
    
    if ((response.hasOwnProperty('error')) || (validateData)) {
      if (noBilling) {
        $('#spendings-tab .generalError p').text(`
          No billing adapter found for this normal adapter in Kumolus. 
          Please create one and try again later!
        `);
        $('.closeModal').addClass('hidden');
      } else {
        $('#spendings-tab .generalError p').text(`
          Data is not available or is in sync if added new adapter in Kumolus account. 
          Please check Kumolus account or try after sometime!
        `);
        $('.closeModal').removeClass('hidden');
      }
      
      $('#spendings-tab .errorMessageModal').modal('show');
      lockModal();
      $('#spendDetailsForm').css('filter', 'blur(10px)');
      $('#spendings-tab .go-to-admin').addClass('hidden');
      $('#spendings-tab .go-to-rh').addClass('hidden');
      $('#spendings-tab .no-data').removeClass('hidden');
      $('#spendings-tab .overviewButton').addClass('hidden');
    } else {
      $('#spendings-tab .errorMessageModal').modal('hide');
      $('#spendDetailsForm').css('filter', 'none');
      chartData = response;
      
      if (Object.keys(chartData['cost_by_service_chart_data']).length != 0) {
        totalSpendService = eval(chartData['cost_by_service_chart_data'].values.join("+"))
      }
      
      drawServiceChart();
      drawCostByDayChart();
      drawCostByYearChart();      
      appendCostData(chartData);
      unlockModal();
    }
  })
}

function appendCostData(chartData) {
  $('#yesterday-spend').text(`$${numberFormatter(chartData['yesterday_spend']) || 0}`);
  $('#total-spend').text(`$${numberFormatter(chartData['total_spend']) || 0}`);
  $('#month-to-date').text(`$${numberFormatter(chartData['month_to_date']) || 0}`);
  $('#year-to-date').text(`$${numberFormatter(chartData['year_to_date']) || 0}`);
  $('#year-forecast').text(`$${numberFormatter(chartData['year_forecast']) || 0}`);
  if (RESOURCE_HANDLER.handlerType == "AWS") {
    $('#used-reservations').text(`${numberFormatter(chartData['used_reservations']) || 0}`);
    $('#unused-reservations').text(`${numberFormatter(chartData['unused_reservations']) || 0}`);
  }

  if (chartData['day_cost_diff'] < 0) {
    $('#day-on-day-span').html(
      `<i class="fa fa-long-arrow-down fa-md pull-left" style="color: red; margin-top:5px" aria-hidden="true"></i>&nbsp
        <span class="form-label">${-(numberFormatter(chartData['day_cost_diff'])) || 0}% day on day</span>
      `)
  } else {
    $('#day-on-day-span').html(
      `<i class="fa fa-long-arrow-up fa-md pull-left" style="color: green; margin-top:5px" aria-hidden="true"></i>&nbsp
        <span class="form-label">${numberFormatter(chartData['day_cost_diff']) || 0}% day on day</span>
      `)
  }

  if (chartData['month_cost_diff'] < 0) {
    $('#month-on-month-span').html(`
        <i class="fa fa-long-arrow-down fa-md pull-left" style="color: red; margin-top:5px" aria-hidden="true"></i>&nbsp
        <span class="form-label">${-(numberFormatter(chartData['month_cost_diff'])) || 0}% vs last month</span>
      `)
  } else {
    $('#month-on-month-span').html(`
      <i class="fa fa-long-arrow-up fa-md pull-left" style="color: green; margin-top:5px" aria-hidden="true"></i>&nbsp
      <span class="form-label">${numberFormatter(chartData['month_cost_diff']) || 0}% vs last month</span>
    `)
  }

  $('#total-spend-service').text(`$${numberFormatter(totalSpendService) || 0}`);
  $('#yesterday-spend-cost-day').text(`$${numberFormatter(chartData['yesterday_spend']) || 0}`);
  $('#month-to-date-day').text(`$${numberFormatter(chartData['month_to_date']) || 0}`);
  $('#year-to-date-cost-by-year').text(`$${numberFormatter(chartData['year_to_date']) || 0}`);
  $('#year-forecast-cost-by-year').text(`$${numberFormatter(chartData['year_forecast']) || 0}`);
}

function drawServiceChart() {
  legend = {
    enabled: false,
    align: 'left',
    itemMarginTop: 3,
    itemMarginBottom: 3,
    labelFormatter: function () {
      return `$ ${numberFormatter(parseFloat(this.y))} ➜ ${this.name}`;
    }
  };
  
  let series = [];

  if (Object.keys(chartData['cost_by_service_chart_data']).length != 0) {
    let data = {
      values: chartData['cost_by_service_chart_data'].labels.map((name, i) =>
        ({ name, y: chartData['cost_by_service_chart_data'].values[i] })
      )
    }
    series = [{ data: data.values, animation: false }];
  } else {
    series = [{ data: [], animation: false }];
  }
  
  DrawHighChart('div-service-chart', legend, '$ (USD)', 'pie', "", [], series, '295', 5)
}

function drawCostByDayChart() {
  let series = [];
  let dataLabels = [];

  if (Object.keys(chartData['cost_by_day_chart_data']).length != 0) {
    let data = chartData['cost_by_day_chart_data']
    series = [{ data: data.values, animation: false }];
    dataLabels = data.labels;
  } else {
    series = [{ data: [], animation: false }];
  }

  DrawHighChart('div-cost-by-day-chart', '', '$ (USD)', 'column', "", dataLabels, series, '295', 5)
}

function drawCostByYearChart() {
  let series = [];
  let dataLabels = [];
  
  if (Object.keys(chartData['cost_by_year_chart_data']).length != 0) {
    let data = chartData['cost_by_year_chart_data']
    series = [{ data: data.values, animation: false }];
    dataLabels = data.labels;
  } else {
    series = [{ data: [], animation: false }];
  }

  DrawHighChart('div-cost-by-year-chart', '', '$ (USD)', 'column', "", dataLabels, series, '295', 5)
}

async function getServicesList() {
  loaderObjSpend.display();
  const URL = "/xui/kumo/api/cost_adviser_overview_for_rh/"
  var payload = {
    adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
    adapter_ids: String(RESOURCE_HANDLER.handlerNormalId),
    count: 'true',
    sort_by: 'ASC',
    sort: 'ASC',
    public_snapshot: 'false',
    tags: "[]",
    service_adviser_klass: `ServiceAdviser::${RESOURCE_HANDLER.handlerType}`,
    rh_id: RESOURCE_HANDLER.handlerId,
    provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
  }
  await $.post(URL, JSON.stringify(payload), (response) => {
    costAdviserData = response['data'];
    if (costAdviserData == undefined) {
      costAdviserData = {
        potential_benefit: 0,
        unused_cost_sum: 0,
        unoptimized_cost_sum: 0,
        ignored_cost_sum: 0,
        unused_count: 0,
        unoptimized_count: 0,
        ignored_count: 0,
      }
    }
    $('#cost-adviser').text(`$${numberFormatter(costAdviserData['potential_benefit']) || 0}`);
    $('#unused').text(`$${numberFormatter(costAdviserData['unused_cost_sum']) || 0} (${costAdviserData['unused_count'] || 0})`);
    $('#unoptimized').text(`$${numberFormatter(costAdviserData['unoptimized_cost_sum']) || 0} (${costAdviserData['unoptimized_count'] || 0})`);
    $('#ignored').text(`$${numberFormatter(costAdviserData['ignored_cost_sum']) || 0} (${costAdviserData['ignored_count'] || 0})`);
    loaderObjSpend.hide();
  })
  getRIRecommendations();
}

async function getRIRecommendations() {
  loaderObjSpend.display();
  if (RESOURCE_HANDLER.handlerType === "AWS") {
    var URL = "/xui/kumo/api/aws_ri_recommendations_for_rh_json/"
    var payload = {
      provider: "AWS",
      term_in_years: "ONE_YEAR",
      payment_option: "ALL_UPFRONT",
      service: riService,
      lookback_period_in_days: "SEVEN_DAYS",
      account_scope: "PAYER",
      service_specification: {
        ec2_specification: {
          offering_class: "STANDARD"
        }
      },
      is_overview: true,
      rh_id: RESOURCE_HANDLER.handlerId,
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
    }
  }
  else {
    var URL = "/xui/kumo/api/azure_ri_recommendations_for_rh_json/"
    var payload = {
      provider: 'Azure',
      term: 'P1Y',
      scope: 'Single',
      resource_type: riService,
      look_back_period: 'Last7Days',
      next_page_token: null,
      adapter_id: String(RESOURCE_HANDLER.handlerNormalId),
      rh_id: RESOURCE_HANDLER.handlerId,
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
    }
  }
  await $.post(URL, JSON.stringify(payload), (response) => {
    riRecommendations = response
    if (riRecommendations.length != 0) {
      if (RESOURCE_HANDLER.handlerType === "AWS") {
        $('#ri-percentage-saving').text(`${numberFormatter(riRecommendations['percentage_saving']) || 0}%`);
        $('#ri-on-demand').text(`$${numberFormatter(riRecommendations['total_on_demand_cost']) || 0}`);
        $('#total-ri').text(`$${numberFormatter(riRecommendations['total_ri_cost']) || 0}`);
        $('#ri-potensials_savings').text(`$${numberFormatter(riRecommendations['total_potential_benefit']) || 0}`);
      }
      else {
        let percentageSaving = 0;
        let totalOnDemandCost = 0;
        let totalRICost = 0;
        let potentialSaving = 0;

        if ((riRecommendations != "no_data_found") && !((Object.keys(riRecommendations).includes("page-stats")) && (Object.keys(riRecommendations).length == 1))) {
          riRecommendations.forEach(item => {
            totalRICost = totalRICost + item.total_cost_with_reserved_instances;
            totalOnDemandCost = totalOnDemandCost + item.cost_with_no_reserved_instances;
            potentialSaving = potentialSaving + item.net_savings;
          });

          percentageSaving = (potentialSaving / totalOnDemandCost) * 100;
        }

        $('#ri-percentage-saving').text(`${numberFormatter(percentageSaving) || 0}%`);
        $('#ri-on-demand').text(`$${numberFormatter(totalOnDemandCost) || 0}`);
        $('#total-ri').text(`$${numberFormatter(totalRICost) || 0}`);
        $('#ri-potensials_savings').text(`$${numberFormatter(potentialSaving) || 0}`);

      }
    }
    loaderObjSpend.hide();
  })
}

function setDateRange() {
  let start = moment().subtract(30, 'days');
  let end = moment().subtract(1, 'days')

  function formatDate(start, end) {
    startDate = start.format('MMMM D, YYYY');
    endDate = end.format('MMMM D, YYYY');
    $('div[name="daterange"] span').val(start.format('MM/DD/YYYY') + '-' + end.format('MM/DD/YYYY'));
    $('div[name="daterange"] span').html(start.format('MM/DD/YYYY') + '-' + end.format('MM/DD/YYYY'));

    if ((formateDate(startDate) === dateRange.start_date) && (formateDate(endDate) === dateRange.end_date)) {
      changeButtonState(false);
      dateCheck = false;
    } else {
      changeButtonState(true);
      dateCheck = true;
    }
  }
  $('div[name="daterange"]').daterangepicker({
    startDate: start,
    endDate: end,
    ranges: {
      'Today': [moment(), moment()],
      'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
      'Last 7 Days': [moment().subtract(6, 'days'), moment()],
      'Last 30 Days': [moment().subtract(30, 'days'), moment()],
      'Current Month': [moment().startOf('month'), moment().endOf('month')],
      'Previous Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
      'Current Quarter': [getQuarter("current").quarteStart, getQuarter("current").quarterEnd],
      'Previous Quarter': [getQuarter("previous").quarteStart, getQuarter("previous").quarterEnd],
    }
  }, formatDate)
  formatDate(start, end)
}

function getQuarter(id) {
  let d = new Date();
  let quarter = Math.floor((d.getMonth() / 3));
  let firstDate = "";
  let endDate = "";

  switch (id) {
    case "current":
      firstDate = new Date(d.getFullYear(), quarter * 3, 1);
      endDate = new Date(firstDate.getFullYear(), firstDate.getMonth() + 3, 0);
      break;
    case "previous":
      firstDate = new Date(d.getFullYear(), quarter * 3 - 3, 1);
      endDate = new Date(firstDate.getFullYear(), firstDate.getMonth() + 3, 0);
      break;
  }

  return {
    quarteStart: firstDate,
    quarterEnd: endDate
  };
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

async function getFiltrationMenu() {
  loaderObjSpend.display();
  setDateRange()
  dateRange.start_date = formateDate(startDate);
  dateRange.end_date = formateDate(endDate);
  
  const URL = "/xui/kumo/api/filtration_menu_rh_json/";
  let payload = {
    rh_id: RESOURCE_HANDLER.handlerId,
    provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
  }
  
  if (RESOURCE_HANDLER.handlerType == "Azure") {
    payload.date_range = dateRange;
  }

  await $.post(URL, JSON.stringify(payload), (response) => {

    filtrationData = response;
  })

  if (RESOURCE_HANDLER.handlerType == "AWS") {

    // for (const reg in filtrationData.Regions) {
    //   $("#region").append(`<option value="${filtrationData.Regions[reg]}">${reg}</option>`);
    // }

    for (const SER in filtrationData.Services) {
      $("#service").append(`<option value="${SER}">${SER} ${AWS_SERVICE_MAP[SER]}</option>`);
    }

    for (const TAG in filtrationData.Tags) {
      $("#tagsList").append(`<option value=${TAG}>${TAG}</option>`);
    }

    $('#service').selectize({
      placeholder: 'All Services',
      plugins: ['remove_button', 'select_remove_all_options']
    })

    $('#tagsList').selectize({
      placeholder: 'All Tags',
      plugins: ['remove_button', 'select_remove_all_options']
    })

    $('#region').selectize({
      placeholder: 'All Regions',
      plugins: ['remove_button', 'select_remove_all_options']
    })
  }
  else if (RESOURCE_HANDLER.handlerType == "Azure") {

    for (const LOC in filtrationData.Locations) {
      $("#location").append(`<option value="${filtrationData.Locations[LOC]}">${filtrationData.Locations[LOC]}</option>`);
    }

    for (const SER in filtrationData.Services) {
      $("#serviceName").append(`<option value="${SER}">${SER}</option>`);
    }

    for (const GROUP in filtrationData.ResourceGs) {
      $("#resourceGroup").append(`<option value="${filtrationData.ResourceGs[GROUP]}">${filtrationData.ResourceGs[GROUP]}</option>`);
    }

    for (const TAG in filtrationData.Tags) {
      $("#tagsList").append(`<option value=${filtrationData.Tags[TAG]}>${filtrationData.Tags[TAG]}</option>`);
    }

    $('#resourceGroup').selectize({
      placeholder: 'All Resource Groups',
      plugins: ['remove_button', 'select_remove_all_options']
    })

    $('#tagsList').selectize({
      placeholder: 'All Tags',
      plugins: ['remove_button', 'select_remove_all_options']
    })

    $('#serviceName').selectize({
      placeholder: 'All Services',
      plugins: ['remove_button', 'select_remove_all_options']
    })

    $('#location').selectize({
      placeholder: 'All Locations',
      plugins: ['remove_button', 'select_remove_all_options']
    })
  }

  $("#tagsList").on("change", (e) => {
    const SELECTED = $("#tagsList").val();

    if (SELECTED.length === 0) {
      $("#tagsListNestedParent").addClass("hidden");
      selectedTags = {};
    }
    else {
      $("#tagsListNestedParent").removeClass("hidden");

      let tempTagListArray = []

      if (RESOURCE_HANDLER.handlerType == "AWS") {
        for (const TITLE in filtrationData.Tags[SELECTED]) {
          tempTagListArray.push({ id: TITLE, title: TITLE })
        };
        $('#tagsListNested').selectize()[0].selectize.destroy();
        $('#tagsListNested').selectize({
          valueField: 'id',
          labelField: 'title',
          searchField: 'title',
          options: tempTagListArray,
          create: false,
          placeholder: 'Select Tag Values'
        });
      }

      else if (RESOURCE_HANDLER.handlerType == "Azure") {
        loaderObjSpend.display();
        let payload = {
          rh_id: RESOURCE_HANDLER.handlerId,
          tag_key: $('#tagsList').val(),
          provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
        }

        const URL = "/xui/kumo/api/get_tag_values/"
        $.post(URL, JSON.stringify(payload), (response) => {
          let azureTagValues = response;

          azureTagValues.forEach(tagValues => {
            if ((tagValues != " ") && (tagValues != "")) {
              tempTagListArray.push({
                id: tagValues,
                title: tagValues,
              })
            }
          })
          $('#tagsListNested').selectize()[0].selectize.destroy();
          $('#tagsListNested').selectize({
            valueField: 'id',
            labelField: 'title',
            searchField: 'title',
            options: tempTagListArray,
            create: false,
            placeholder: 'Select Tag Values'
          });

          loaderObjSpend.hide();
        });
      }
    }
  })  
}

function changeButtonState(clicked) {
  if (clicked) {
    $("#submit").removeClass("border-btn btn btn-default");
    $("#submit").addClass("border-btn btn btn-primary");
  } else {
    $("#submit").removeClass("border-btn btn btn-primary");
    $("#submit").addClass("border-btn btn btn-default");
  }
}

function commonOperations(callback) {
  $('#spendDetailsForm')[0].reset();

  if (Object.keys(filtrationData.Services).length != 0) {
    setDateRange();
    multiSeries = false;
    dateRange.start_date = formateDate(startDate);
    dateRange.end_date = formateDate(endDate);
    callback();
    loadChartData();
  }
  else {
    $('#spendings-tab .errorMessageModal').modal('show');
    lockModal();
    $('#spendDetailsForm').css('filter', 'blur(10px)');
    $('#spendings-tab .go-to-admin').addClass('hidden');
    $('#spendings-tab .go-to-rh').addClass('hidden');
    $('#spendings-tab .no-data').removeClass('hidden');
    $('#spendings-tab .overviewButton').removeClass('hidden');
  }
}

function setSelectizeValue(dropdownTag, dropdownValue) {
  var $select = $(`#${dropdownTag}`).selectize();
  var selectize = $select[0].selectize;
  selectize.setValue(selectize.search(dropdownValue).items[0].id);
}

function listOfDates(startDate, endDate) {
  var start      = startDate.split('-');
  var end        = endDate.split('-');
  var startYear  = parseInt(start[2]);
  var endYear    = parseInt(end[2]);
  var dates      = [];

  for(var i = startYear; i <= endYear; i++) {
    var endMonth = i != endYear ? 11 : parseInt(end[1]) - 1;
    var startMon = i === startYear ? parseInt(start[1])-1 : 0;
    for(var j = startMon; j <= endMonth; j = j > 12 ? j % 12 || 11 : j+1) {
      var month = j+1;
      var displayMonth = month < 10 ? '0'+month : month;
      dates.push([displayMonth, '01', i].join('-'));
    }
  }
  return dates;
}

function resetDropdowns() {
  if (RESOURCE_HANDLER.handlerType == "AWS") {
    resetSelectizeValue('region');
    resetSelectizeValue('service');
    resetSelectizeValue('usage_type');
  }
  else if (RESOURCE_HANDLER.handlerType == "Azure") {
    resetSelectizeValue('serviceName');
    resetSelectizeValue('serviceTier');
    resetSelectizeValue('resourceName');
    resetSelectizeValue('location');
    resetSelectizeValue('resourceGroup');
  }

  resetSelectizeValue('tagsList');
  resetSelectizeValue('tagsListNested');
  $('#tagListBox').empty();
  $('#tagListBoxAzure').empty();
}

function resetSelectizeValue(dropdownTag) {
  var $select = $(`#${dropdownTag}`).selectize();
  var selectize = $select[0].selectize;
  selectize.clear();
}

async function loadChartData() {
  loaderObjSpend.display();
  const URL = "/xui/kumo/api/spend_details_for_rh_json/";
  if (RESOURCE_HANDLER.handlerType == "AWS") {
    var payload = {
      report: {
        daily: daily,
        date_range: dateRange,
        tags: selectedTags,
        type: "cost_report",
        // account: [RESOURCE_HANDLER.handlerNormalId],
        account: [],
        service: service,
        region: region,
        usage_type: usageType,
        operation: [],
        monthly: monthly,
        multi_series: multiSeries,
        select_metric: "unblended",
        product_family: productFamily,
        is_upfront_reservation_charges: isUpfrontReservationCharges,
        is_support_charges: isSupportCharges,
        is_other_subscription_charges: isOtherSubscriptionCharges,
        rh_id: RESOURCE_HANDLER.handlerId,
        dimensions: dimensions,
        metrics: ["unblended"],
        provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
      }
    }
  }
  else if (RESOURCE_HANDLER.handlerType == "Azure") {
    var payload = {
      report: {
        daily: daily,
        monthly: monthly,
        group_by: "date_range",
        resource_group: resourceGroup,
        date_range: dateRange,
        consumed_service: consumedService,
        service_name: serviceName,
        service_tier: serviceTier,
        resource_name: resourceName,
        tags: selectedTags,
        location: location,
        type: "azure_cost_report",
        provider: RESOURCE_HANDLER.handlerType,
        multi_series: multiSeries,
        tab: tab,
        subscription: [],
        dimensions: dimensions,
        metrics: ["cost"],
        select_metric: "cost",
        rh_id: RESOURCE_HANDLER.handlerId,
        provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
      }
    }
  }  

  await $.post(URL, JSON.stringify(payload), (response) => {
    apiData = response;
    totalCost = apiData.total_cost
  })

  var endDate = payload["report"]["date_range"]["end_date"].split('-').reverse().join('-')
  endDate = new Date(endDate)
  if (endDate >= new Date) {
    const URL = "/xui/kumo/api/forecast_for_rh_json/";
    if (RESOURCE_HANDLER.handlerType == "AWS") {
      payload.report.dimensions = dimensions
      payload.report.metrics = ["unblended"]
    }

    payload.report.month_labels = (monthly) ? monthLabels : [];
    payload.report.custom_filters = true;

    await $.post(URL, JSON.stringify(payload), (response) => {
      forecastData = response;
    })
  }
  // Calculating Total Cost = Actual Cost + Forecast Cost
  if (endDate >= new Date) {
    forecastCost = forecastData.values.reduce((a, b) => a + b, 0);
  } else {
    forecastData = {};
  }
  
  totalCost = apiData.total_cost + forecastCost
  $('#total-cost').text(`$${numberFormatter(totalCost) || 0}`);
  $('#average-daily-cost').text(`$${numberFormatter(apiData.average_daily_cost) || 0}`);
  $('#average-monthly-cost').text(`$${numberFormatter(apiData.average_monthly_cost) || 0}`);
  if (monthly) {
    $('.hidePreviousCost').hide();
    $('.adjustWidth').removeClass('col-sm-3');
    $('.adjustWidth').addClass('col-sm-4');
  } else {
    $('.hidePreviousCost').show();
    $('.adjustWidth').removeClass('col-sm-4');
    $('.adjustWidth').addClass('col-sm-3');
    $('#yesterday-cost').text(`$${numberFormatter(apiData.previous_spend) || 0}`);
  }
  
  var series;
  if (payload["report"]["multi_series"]) {
    series = apiData.values
  } else {
    series = [{ data: apiData.values }]
    if (endDate >= new Date) {
      var colorChangedForecastValues = [];
      forecastData.values.forEach(val => {
        colorChangedForecastValues.push({y: val, color: '#a6c96a'})
      });

      let seriesData = {};

      seriesData.forecast = {
        name: 'Forecast',
        stack: '',
        data: [],
        color: '#a6c96a',
      }

      seriesData.actual = {
        name: 'Actual',
        stack: '',
        data: [],
        color: '#7cb5ec',
      }

      if (monthly) {
        let loopCounter = Math.max(apiData.labels.length, forecastData.labels.length);
        let uniqueArray = new Set(apiData.labels.concat(forecastData.labels));
        apiData.labels = Array.from(uniqueArray);
        
        let i = 0;
        let apiD = 0;
        let foreD = 0;

        for (i = 0; i < loopCounter; i++) {
          apiD = (series[0].data[i]) ? series[0].data[i] : 0;
          foreD = (forecastData.values[i]) ? forecastData.values[i] : 0;
          seriesData.forecast.stack = String(i);
          seriesData.forecast.data.push(foreD);
          seriesData.actual.stack = String(i);
          seriesData.actual.data.push(apiD);
        }

        series = [];

        Object.keys(seriesData).forEach(function(key) {
          series.push(seriesData[key])
        })
      } else {
        apiData.labels = apiData.labels.concat(forecastData.labels);
        let valCounter = 0;
        apiData.values.forEach(val => {
          seriesData.forecast.stack = String(valCounter);
          seriesData.forecast.data.push(0);
          seriesData.actual.stack = String(valCounter);
          seriesData.actual.data.push(val);
          valCounter++;
        });
        forecastData.values.forEach(val => {
          seriesData.forecast.stack = String(valCounter);
          seriesData.forecast.data.push(val);
          seriesData.actual.stack = String(valCounter);
          seriesData.actual.data.push(0);
          valCounter++;
        });

        series = [];

        Object.keys(seriesData).forEach(function(key) {
          series.push(seriesData[key])
        })
      }
    }
  }

  legend = { 
    align: 'left',
    maxHeight: 95,
  }

  let chartType = ((multiSeries) && (daily)) ? 'line' : 'column';
  series = (multiSeries) ? series.filter(d => d.name != null) : series;
  DrawHighChart('div-chart', legend, '$ (USD)', chartType, "", apiData.labels, series, null, 0);
  changeButtonState(false);
  loaderObjSpend.hide();
}

function DrawHighChart(divId, legend, yAxisName, type, text, labels, series, height, minPoint) {
  if (multiSeries === "account") {
    series.forEach(ser => {
      filtrationData.Accounts.forEach(acc => {
        if (acc['account_id'] === ser['name']) {
          ser['name'] = acc['account_name']
        }
      })
    })
  }
  $(`#${divId}`).highcharts({
    chart: { 
      type:type, 
      shadow: false, 
      height: height,
      events: {
        load: function() {
          this.series.forEach(function(s) {
            if (s.name.includes("Series")) {
              s.update({
                showInLegend: false,
              });
            }
          });
        }
    }},
    legend: legend || { enabled: false },
    title: { text: text },
    xAxis: {
      categories: labels,
      title: { text: 'Date' },
      labels: {
        enabled: true,
        overflow: "allow",
        rotation: -90,
        y: 10,
        formatter: function () {
          return this.value.slice(0, -4) + this.value.slice(-2);
        }
      }
    },
    yAxis: { title: { text: yAxisName } },
    tooltip: {
      formatter: function() {
        if (this.series.name.includes("Series")) {
          return '<b>Cost: $' + numberFormatter(this.y) + '</b><br/>';
        }
        else {
          return this.series.name + '<br/><b>Cost: $' + numberFormatter(this.y) + '</b><br/>';
        }
        
      },
      shared: false,
    },
    series: series,
    credits: { enabled: false },
    plotOptions: {
      series: {
        stacking:true,
        minPointLength: minPoint,
        marker: {
          radius: 2
      }
      },
      pie: {
        dataLabels: { enabled: false },
        showInLegend: true,
      },
    },
  }, function (chart) {
    if ((divId == "div-service-chart") && (chart.series.length != 0)) {
      let legend = $('#customLegend');

      $.each(chart.series[0].data, function (j, data) {
        legend.append('<div class="item"><span class="serieName"><span class="symbol" style="background-color:' + data.color + '"></span>' + `$ ${numberFormatter(parseFloat(data.y))} ➜ ${data.name}` + '</span></div>');
      });

      $('#customLegend .item').click(function () {
        var inx = $(this).index(),
          point = chart.series[0].data[inx];

        if (point.visible)
          point.setVisible(false);
        else
          point.setVisible(true);
      });
    }
    else if (divId == "div-chart") { 
      let dataJson = [];
      colName = dimensions[0].toUpperCase();
      pdfData = [];

      if (Object.keys(forecastData).length > 0) {
        let finalArray = sumArray(chart.series[0].data, chart.series[1].data)
        
        chart.series[0].data.forEach((item, index) => {
          dataJson.push({
            "Date": item.category,
            "Costs": finalArray[index]
          });

          pdfData.push([item.category, finalArray[index]]);
        });
      }
      else if (multiSeries) {        
        chart.series.forEach((data, index) => {
          dataJson.push({
            "Date": data.userOptions.name,
            "Costs": data.userOptions.data.reduce((a, b) => a + b)
          });

          pdfData.push([data.userOptions.name, data.userOptions.data.reduce((a, b) => a + b)]);
        });
      }
      else {
        chart.series[0].data.forEach(item => {
          dataJson.push({
            "Date": item.category,
            "Costs": item.options.y
          });

          pdfData.push([item.category, item.options.y]);
        });
      }

      csvStr = JsonToCSV(dataJson);
    }
  });
};

function sumArray(a, b) {
  var c = [];
  for (var i = 0; i < Math.max(a.length, b.length); i++) {
    c.push((a[i].options.y || 0) + (b[i].options.y || 0));
  }
  return c;
}

function JsonToCSV(jsonArray){
  csvStr = '';
  let jsonFields = [colName, 'Costs (unblended)'];
  let filterFields = {
    "FILTERS": "",
    "Provider": RESOURCE_HANDLER.handlerType,
    "Date Range": dateRange.start_date + ' to ' + dateRange.end_date,
    "Historical Total": apiData.total_cost,
    "Forecast Total": forecastCost,
    "Total Cost": totalCost,
    "Report Type": (daily) ? "Daily" : "Monthly",
  };

  let csv_tags = Object.keys(selectedTags).map(function (key) { 
    return "" + key + " => " + selectedTags[key]; 
  }).join(", ");

  // console.log(String(service).replace(/,/g, '\,'));
  if (RESOURCE_HANDLER.handlerType == "AWS") {
    (Object.keys(selectedTags).length>0) ? filterFields.Tags = `\"${String(csv_tags)}\"` : "";
    (service.length>0) ? filterFields.Service = `\"${String(service)}\"` : "";
    (region.length>0) ? filterFields.Region = `\"${String(region)}\"` : "";
    (usage_type.length>0) ? filterFields["Usage Type"] = `\"${String(usage_type)}\"` : "";
    (is_upfront_reservation_charges) ? filterFields["Upfront Reservation Charges"] = "Yes" : "";
    (is_support_charges) ? filterFields["Support Charges"] = "Yes" : "";
    (is_other_subscription_charges) ? filterFields["Other Subscription Charges"] = "Yes" : "";
  } 
  else if (RESOURCE_HANDLER.handlerType == "Azure") {
    (Object.keys(selectedTags).length>0) ? filterFields.Tags = `\"${String(csv_tags)}\"` : "";
    (consumedService.length>0) ? filterFields.Service = `\"${String(consumedService)}\"` : "";
    (resourceGroup.length>0) ? filterFields["Resource Group"] = `\"${String(resourceGroup)}\"` : "";
    (resourceName.length>0) ? filterFields["Resource Name"] = `\"${String(resourceName)}\"` : "";
    (serviceName.length>0) ? filterFields["Service Name"] = `\"${String(serviceName)}\"` : "";
    (serviceTier.length>0) ? filterFields["Service Tier"] = `\"${String(serviceTier)}\"` : "";
    (location.length>0) ? filterFields.Location = `\"${String(location)}\"` : "";
  }
  
  Object.entries(filterFields).forEach(([key, value]) => {
    csvStr += key + ',' + value + "\n";
  });
  
  csvStr += '' + ',' + '' + "\n";
  csvStr += jsonFields.join(",") + "\n";

  jsonArray.forEach(element => {
    csvStr += element.Date + ',' + element.Costs + "\n";
  })

  return csvStr;
}

function downloadCSV(csvStr) {

  var hiddenElement = document.createElement('a');
  hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csvStr);
  hiddenElement.target = '_blank';  
	let report_name = "Cost Usage Report".split(' ').join('_') + moment().format('_DDMMYYYYhhmmss');
  hiddenElement.download = report_name + '.csv';
  hiddenElement.click();
}

function downloadPDF(csvStr) {
  //Get svg markup as string
  let svg = $('#div-chart').highcharts().container.innerHTML;
  let canvas = document.createElement('canvas');
  let doc = new jsPDF();
  pageGap = 10;
  var continueFurther = 0;
  let daiMon = (daily) ? "Daily" : "Monthly";

  canvg(canvas, svg);
  let dataUrl = canvas.toDataURL('image/png');
  
  doc.setFont('helvetica');
  doc.setFontType('bold');
  createHeader(doc);
  doc.text(pageGap, pageGap+25, 'Filters:');
  doc.setFontSize(10);
  doc.text(pageGap+10, pageGap+30, `Provider: ${RESOURCE_HANDLER.handlerType}`)
  doc.text(pageGap+10, pageGap+35, `Date Range: ${dateRange.start_date} to ${dateRange.end_date}`)
  doc.text(pageGap+10, pageGap+40, `Report Type: ${daiMon}`)

  if (RESOURCE_HANDLER.handlerType == "AWS") {
    let lineGap = pageGap+40;
    (Object.keys(selectedTags).length>0) ? doc.text(pageGap+10, lineGap+5, `Tags: ${String(csv_tags)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (service.length>0) ? doc.text(pageGap+10, lineGap+5, `Service: ${String(service)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (region.length>0) ? doc.text(pageGap+10, lineGap+5, `Region: ${String(region)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (usage_type.length>0) ? doc.text(pageGap+10, lineGap+5, `Usage Type: ${String(usage_type)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (is_upfront_reservation_charges) ? doc.text(pageGap+10, lineGap+5, "Upfront Reservation Charges: Yes") : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (is_support_charges) ? doc.text(pageGap+10, lineGap+5, "Support Charges: Yes") : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (is_other_subscription_charges) ? doc.text(pageGap+10, lineGap+5, "Other Subscription Charges: Yes") : lineGap = lineGap-5;
    continueFurther = lineGap+5;
  }
  else if (RESOURCE_HANDLER.handlerType == "Azure") {
    let lineGap = pageGap+40;
    (Object.keys(selectedTags).length>0) ? doc.text(pageGap+10, lineGap+5, `Tags: ${String(csv_tags)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (consumedService.length>0) ? doc.text(pageGap+10, lineGap+5, `Service: ${String(consumedService)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (resourceGroup.length>0) ? doc.text(pageGap+10, lineGap+5, `Resource Group: ${String(resourceGroup)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (resourceName.length>0) ? doc.text(pageGap+10, lineGap+5, `Resource Name: ${String(resourceName)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (serviceName.length>0) ? doc.text(pageGap+10, lineGap+5, `Service Name: ${String(serviceName)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (serviceTier.length>0) ? doc.text(pageGap+10, lineGap+5, `Service Tier: ${String(serviceTier)}`) : lineGap = lineGap-5;
    lineGap = lineGap+5;
    (location.length>0) ? doc.text(pageGap+10, lineGap+5, `Location: ${String(location)}`) : lineGap = lineGap-5;
    continueFurther = lineGap+5;
  }

  doc.setFontSize(12);
  doc.text(pageGap, continueFurther+10, "Costing:");
  doc.setFontSize(10);
  doc.text(pageGap+10, continueFurther+15, `Historical: ${apiData.total_cost}`);
  doc.text(pageGap+10, continueFurther+20, `Forecast: ${forecastCost}`);
  doc.text(pageGap+10, continueFurther+25, `Total: ${totalCost}`);
  doc.addImage(dataUrl, 'PNG', 10, continueFurther+35, 190, 100);
  
  doc.addPage();
  createHeader(doc);
  doc.text(pageGap, pageGap+25, 'Costing data:');
  doc.setFontSize(10);

  // Or use javascript directly:
  doc.autoTable({
    head: [[colName, 'Costs (unblended)']],
    body: pdfData,
    startY: 40,
    margin: {right: 10, left: 10},
    pageBreak: 'auto',
  })

  let report_name = "Cost Usage Report".split(' ').join('_') + moment().format('_DDMMYYYYhhmmss');
  createFooter(doc);
  doc.save(report_name + '.pdf');
}

function createHeader(doc) {
  let imgData = 'data:image/png;base64,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';

  doc.setFontSize(14);
  doc.text(pageGap, pageGap+12, "Cost Usage Report");
  doc.addImage(imgData, 'PNG', 150, pageGap+5, 10, 10);
  doc.text(162, pageGap+12, 'Kumolus');
  doc.setFontSize(12);
  doc.line(pageGap, pageGap+18, 200, pageGap+18); // horizontal line.
  doc.setLineWidth(0.5);
}

function createFooter(doc) {
  let pageCount = doc.internal.getNumberOfPages();
  doc.setFont("courier");
  doc.setFontType("normal");
  doc.setFontSize(9)
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.text(83, 294, "Powered by Kumolus.com");
  }
}

function getSelectedValues(selector) {
  let options = []
  $(`#${selector} option:selected`).each((id, opt) => {
    options.push($(opt).text())
  })
  return options
}

function setFilters(tab) {
  if (RESOURCE_HANDLER.handlerType == "Azure") {
    if (tab == "compute") {
      serviceName = ["Virtual Machines", "Virtual Machines Licenses",
        "Storage", "Bandwidth", "Virtual Network"]
      consumedService = ["Microsoft.Compute"]
    }
    else if (tab == "database") {
      serviceName = ["SQL Database", "Azure Database for MySQL",
        "Azure Database for PostgreSQL",
        "Advanced Data Security", "Azure Cosmos DB",
        "SQL Managed Instance"]
      consumedService = []
    }
    else if (tab == "storage") {
      serviceName = ["Storage", "Bandwidth", "Event Grid",
        "Advanced Threat Protection"]
      consumedService = ["Microsoft.Storage"]
    }
    else {
      serviceName = [];
      consumedService = [];
    }

    $(`#serviceName`).data('selectize').setValue(serviceName, true);
  }
}

$("li[data-target='#overview']").on("click", (e) => {
  $("#spend-details").addClass("hidden");
  $("#overview").removeClass("hidden");
})

$("a[href='#tab-spend']").on("click", (e) => {
  if (!$('#spendings-tab .errorMessageModal').hasClass('in')) {
        unlockModal();  
      }
  else {
    lockModal();
  }
})

$("li[data-target='#custom']").on("click", (e) => {
  tab = "custom";
  $('.charge-type').show();
  commonOperations(() => {
    resetDropdowns();
    $("#spend-details, #custom_tab").removeClass("hidden");
    $("#overview, #compute_tab, #other_tab, #database_tab, #storage_tab, #data_transfer_tab").addClass("hidden");
    productFamily = [];
    service = [];
    selectedTags = {};
    consumedService = [];
    changeButtonState(false);
    (RESOURCE_HANDLER.handlerType == "AWS") ? $(`#service`).data('selectize').setValue(service, true) : "";
  })
})

$("li[data-target='#compute']").on("click", (e) => {
  tab = "compute";
  $('.charge-type').hide();
  commonOperations(() => {
    resetDropdowns();
    $("#spend-details, #compute_tab, #other_tab").removeClass("hidden");
    $("#overview, #custom_tab, #database_tab, #storage_tab, #data_transfer_tab").addClass("hidden");
    productFamily = [];
    service = [$("li[data-target='#compute']").data("value")];
    changeButtonState(false);
    (RESOURCE_HANDLER.handlerType == "AWS") ? setSelectizeValue('service', service[0]) : "";
    setFilters("compute");
  })
})

$("li[data-target='#database']").on("click", (e) => {
  tab = "database";
  $('.charge-type').hide();
  commonOperations(() => {
    resetDropdowns();
    $("#spend-details, #database_tab, #other_tab").removeClass("hidden");
    $("#overview, #custom_tab, #compute_tab, #storage_tab, #data_transfer_tab").addClass("hidden");
    productFamily = [];
    service = [$("li[data-target='#database']").data("value")];
    changeButtonState(false);
    (RESOURCE_HANDLER.handlerType == "AWS") ? setSelectizeValue('service', service[0]) : "";
    setFilters("database");
  })
})

$("li[data-target='#storage']").on("click", (e) => {
  tab = "storage";
  $('.charge-type').hide();
  commonOperations(() => {
    resetDropdowns();
    $("#spend-details, #storage_tab, #other_tab").removeClass("hidden");
    $("#overview, #custom_tab, #compute_tab, #database_tab, #data_transfer_tab").addClass("hidden");
    productFamily = [];
    service = [$("li[data-target='#storage']").data("value")];
    changeButtonState(false);
    (RESOURCE_HANDLER.handlerType == "AWS") ? setSelectizeValue('service', service[0]) : "";
    setFilters("storage");
  })
})

$("li[data-target='#data_transfer']").on("click", (e) => {
  $('.charge-type').hide();
  commonOperations(() => {
    resetDropdowns();
    $("#spend-details, #data_transfer_tab, #other_tab").removeClass("hidden");
    $("#overview, #custom_tab, #compute_tab, #database_tab, #storage_tab").addClass("hidden");
    service = [];
    productFamily = [$("li[data-target='#data_transfer']").data("value")];
    changeButtonState(false);
  })
});

$('#serviceName').on('change', (e) => {
  loaderObjSpend.display();
  const SERVICES = $("#serviceName").val();
  if (SERVICES.length === 0) {
    $("#serviceTier, #resourceName").html("");
    $("#serviceTierParent, #resourceNameParent").addClass("hidden");
    loaderObjSpend.hide();
  }
  else {
    $("#serviceTier, #resourceName").html("");
    $("#serviceTierParent, #resourceNameParent").removeClass("hidden");

    let tempUsageTypeArray = []

    SERVICES.forEach(ser => {
      for (const TIERS in filtrationData.Services[ser]) {
        tempUsageTypeArray.push({
          id: filtrationData.Services[ser][TIERS],
          title: filtrationData.Services[ser][TIERS]
        })
      }
    })

    $('#serviceTier').selectize()[0].selectize.destroy();
    $('#serviceTier').selectize({
      maxItems: null,
      valueField: 'id',
      labelField: 'title',
      searchField: 'title',
      options: tempUsageTypeArray,
      create: false,
      placeholder: 'Select Service Tier',
      plugins: ['remove_button', 'select_remove_all_options'],
    });

    let payload = {
      rh_id: RESOURCE_HANDLER.handlerId,
      resource_group: resourceGroup,
      service_name: $("#serviceName").val(),
      subscription_name: subscriptions,
      provider_account_id: String(RESOURCE_HANDLER.handlerNormalId),
    }

    const URL = "/xui/kumo/api/get_resource_name/"
    $.post(URL, JSON.stringify(payload), (response) => {
      let resourceNameList = response;
      let tempUsageTypeArray = []
      $('#resourceName').selectize()[0].selectize.destroy();
      
      if ((!(Object.keys(resourceNameList).includes("page-stats")) 
        && !(Object.keys(resourceNameList).length == 1) 
        && !(resourceNameList == "no_data_found"))) {
        resourceNameList.forEach(resource => {
          tempUsageTypeArray.push({
            id: resource,
            title: resource,
          })
        })
        
        $('#resourceName').selectize({
          maxItems: null,
          valueField: 'id',
          labelField: 'title',
          searchField: 'title',
          options: tempUsageTypeArray,
          create: false,
          placeholder: 'Select Resource Name',
          plugins: ['remove_button', 'select_remove_all_options'],
        });
        loaderObjSpend.hide();
      }
      else {
        $('#resourceName').selectize({
          maxItems: null,
          options: tempUsageTypeArray,
          create: false,
          placeholder: 'No Resources',
        });
        loaderObjSpend.hide();
      }
    })
  }

  serviceName = $("#serviceName").val();
});

$('#tagsListNested').on('change', (e) => {
  
  if (($("#tagsList").val() != "") && ($('#tagsListNested').val() != "")) {
    var tagKey = $('#tagsList').val();
    var tagValue = $('#tagsListNested').val();
    if (selectedTags.hasOwnProperty(tagKey)) {
      selectedTags[tagKey].push(tagValue)
      selectedTags[tagKey] = [...new Set(selectedTags[tagKey])];
    } else {
      selectedTags[tagKey] = [tagValue]
    }

    appendTagListBox();
  }
});

function destroySelectize(dropdownTag) {
  var $select = $(`${dropdownTag}`).selectize();
  var selectize = $select[0].selectize;
  selectize.destroy();
}

function removeTags(i) {
  let tempString = $(`span[data-value="${i}"]`).parent().text();
  let removedItem = $.trim(tempString).split('=')
  let removedTagKey = $.trim(removedItem[0]);
  let removedTagValue = $.trim(removedItem[1]);
  selectedTags[removedTagKey].splice(removedTagValue, 1);
  (selectedTags[removedTagKey].length == 0) ? delete selectedTags[removedTagKey] : '';
  appendTagListBox();
}

function appendTagListBox() {
  $("#tagListBoxAzure").empty();
  if (Object.keys(selectedTags).length == 0) {
    $('#tagsListNestedParent').addClass('hidden');
    $("#tagListBoxAzure").empty();
    resetSelectizeValue("tagsList");
    resetSelectizeValue("tagsListNested");
  } else {
    $('#tagsListNestedParent').removeClass('hidden');
  }

  Object.entries(selectedTags).forEach(([key, value], i) => {
    value.forEach((elm, j) => {
      $("#tagListBoxAzure").append(`
        <div class="btn btn-success tagList">${key} = ${elm}<span class="fa fa-times remove-tag-icon removeTags" data-value=${i}${j} style="margin-left: 7px;"></span></div>`
      )
    })
  });
}

$('#res-service').on('change', function () {
  riService = $("#res-service").val();
  getRIRecommendations();
});

$("#submit").on("click", () => {
  dateRange.start_date = formateDate(startDate);
  dateRange.end_date = formateDate(endDate);
  
  if (monthly) {
    let DateArray = listOfDates(formateDate(startDate), formateDate(endDate));
    monthLabels = [];

    DateArray.forEach(dated => {
      monthLabels.push(MONTH_NAMES[(new Date(dated)).getMonth()] + " " + String((new Date(dated)).getFullYear()))
    });
  }

  loadChartData();
})

$("#spendDetailsForm").on("change", () => {
  const SPEND_FORM_DATA = new FormData(document.querySelector("#spendDetailsForm"))
  daily = SPEND_FORM_DATA.get("dailyMonthly") === "daily" ? true : false;
  monthly = SPEND_FORM_DATA.get("dailyMonthly") === "monthly" ? true : false;
  isUpfrontReservationCharges = $("#is_upfront_reservation_charges").is(':checked');
  isSupportCharges = $("#is_support_charges").is(':checked');
  isOtherSubscriptionCharges = $("#is_other_subscription_charges").is(':checked');

  if ((multiSeries) || (dateCheck) || (region.length > 0) || (service.length > 0) || (!$.isEmptyObject(selectedTags)) || (monthly)) {
    changeButtonState(true);
  } else {
    changeButtonState(false);
  }
})

$("#custom_type, #compute_type, #storage_type, #database_type, #data_transfer_type, #other_type").on("change", function () {
  multiSeries = ($(this).val() != "overview") ? $(this).val() : false;
  dimensions = [DIMENSION_DATA[RESOURCE_HANDLER.handlerType][$(this).attr('id')][$(this).val()]];
  var multiSeriesBy = (multiSeries == "tags") ? "tags" : "";
  changeButtonState(false);
});

$('#region, #account').on('change', function () {
  if (this.id === 'region') {
    region = $(this).val();
  } else {
    account = $(this).val();
  }
});

$("#service").on("change", () => {
  const SERVICES = $("#service").val();
  if (SERVICES.length === 0) {
    $("#usage_type").html("");
    $("#usage_typeParent").addClass("hidden");
  }
  else {
    $("#usage_type").html("");
    $("#usage_typeParent").removeClass("hidden");

    let tempUsageTypeArray = []

    SERVICES.forEach(ser => {
      for (Object.key in filtrationData['Services'][ser].usageTypes) {
        tempUsageTypeArray.push({
          id: Object.key,
          title: Object.key
        })
      }
    })

    $('#usage_type').selectize()[0].selectize.destroy();
    $('#usage_type').selectize({
      maxItems: null,
      valueField: 'id',
      labelField: 'title',
      searchField: 'title',
      options: tempUsageTypeArray,
      create: false,
      placeholder: 'Select Usage Type',
      plugins: ['remove_button', 'select_remove_all_options'],
    });
  }

  service = $("#service").val();
})

$("#usage_type").on("change", () => {
  usageType = $("#usage_type").val();
})

$("#serviceTier").on("change", () => {
  serviceTier = $("#serviceTier").val();
})

$("#location").on("change", () => {
  location = $("#location").val();
})

$("#resourceGroup").on("change", () => {
  resourceGroup = $("#resourceGroup").val();
})

$("#resourceName").on("change", () => {
  resourceName = $("#resourceName").val();
})

// $("#subscription").on("change", () => {
//   subscription = $("#subscription").val();
//   subscription.forEach(sub => {
//     subscriptions.push(subscriptionJson[sub]);
//     subscriptionList.push({
//       id: sub,
//       name: subscriptionJson[sub]
//     })
//   });
// })

Selectize.define('select_remove_all_options', function (options) {
  if (this.settings.mode === 'single') return;

  var self = this;

  self.setup = (function () {
    var original = self.setup;
    return function () {
      original.apply(this, arguments);

      var allBtn = $('<button type="button" class="select-all-options btn btn-default btn-xs" data-toggle="tooltip" title="" data-original-title="Select all items"><i class="fas fa-asterisk"></i></button>');
      var clearBtn = $('<button type="button" class="select-no-options btn btn-default btn-xs" data-toggle="tooltip" title="" data-original-title="Clear selection"><i class="fas fa-times"></i></button>');
      var btnGrp = $('<div class="selectize-toolbar btn-group"></div>');
      btnGrp.append(allBtn, clearBtn);

      allBtn.on('click', function () {
        self.setValue($.map(self.options, function (v, k) {
          return k
        }));
      });
      clearBtn.on('click', function () {
        self.setValue([]);
      });

      this.$wrapper.append(btnGrp)
    };
  })();
});
