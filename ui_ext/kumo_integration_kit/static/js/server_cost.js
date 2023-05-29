import { LoaderClass, DATA_BACKUP_HOURS, numberFormatter,
  DIMENSION_DATA, AWS_SERVICE_MAP, MONTH_NAMES, SERVER_PARTS,
  POTENTIAL_SAVINGS } from './common.js';

var startDate;
var endDate;
var datesArray;
var csvStr;
var totalCost = 0;
var pdfData = [];
var pageGap = 0;
var costBreakdown;
var operationalCost;
var totalCostBreakdown;
var seriesData = [];
var totalGraphCost = 0;
var loaderObjServer = new LoaderClass('server-tab');
const SERVER_DATA = $('#server_details').data('server');

$(document).ready(function () {
  setDateRange();
  getCostSummary();
  getPotentialSavings();
  
  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    $(window).resize();
  });

  $(document).on('click', '#exportToCSV', function (e) {
    downloadCSV(csvStr);
  });

  $(document).on('click', '#exportToPDF', function (e) {
    downloadPDF(csvStr);
  });

  var jQueryScript = document.createElement('script');  
  jQueryScript.setAttribute('src','https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.2.5/jspdf.plugin.autotable.js');
  document.head.appendChild(jQueryScript);
});

function setDateRange() {
  let start = moment().subtract(30, 'days');
  let end = moment().subtract(1, 'days')

  function formatDate(start, end) {
    startDate = start.format('MMMM D, YYYY');
    endDate = end.format('MMMM D, YYYY');
    $('div[name="daterange"] span').val(start.format('MM/DD/YYYY') + '-' + end.format('MM/DD/YYYY'));
    $('div[name="daterange"] span').html(start.format('MM/DD/YYYY') + '-' + end.format('MM/DD/YYYY'));
    getCostBreakdown();
  }
  $('div[name="daterange"]').daterangepicker({
    startDate: start,
    endDate: end,
    ranges: {
      'Today': [moment(), moment()],
      'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
      'Last 7 Days': [moment().subtract(7, 'days'), moment().subtract(1, 'days')],
      'Last 30 Days': [moment().subtract(30, 'days'), moment().subtract(1, 'days')],
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

function plotChart(labels, seriesData) {
  $('#graph-div').highcharts({
    chart: {
      type: "line", 
      height: "250",
    },

    title: { text: "" },

    xAxis: {
      categories: labels,
      title: { text: 'Date' },
      labels: {
        enabled: true,
        overflow: "allow",
        rotation: -90,
        y: 10,
        formatter: function () {
          return this.value.slice(-2) + this.value.slice(4,7) 
            + '-' + this.value.slice(2,4)
        }
      }
    },

    yAxis: {
      title: { text: 'Cost' },
      labels: {
        enabled: true,
        formatter: function () {
          return '$' + this.value;
        }
      }
    },

    tooltip: {
      formatter: function () {
          return `${this.x}<br />${this.series.name}: <b>$${numberFormatter(this.y)}</b>`;
        }
    },

    legend: { enabled: false },

    series: seriesData,

    responsive: {
        rules: [{
          condition: {
              minWidth: ($('#tab-content').width()*0.84)*0.62
          },
        }]
    },

    credits: {
      enabled: false
    },
  }, function (chart) {

    if (totalGraphCost == 0) {
      chart.renderer.text('No data to display', ((chart.chartWidth/2) - (chart.chartWidth/10)), 125)
        .css({
            color: '#CCC',
            fontSize: '16px',
            fontWeight: '700'
        })
        .add();
    }
    else {
      if (chart.series.length != 0) {
        $('#graph-legend').empty();
        let legend = $('#graph-legend');
        let count_legend = 0;
        let legend_str = ``;
        let counter_loop = 0;
        
        $.each(chart.series, function (j, data) {
          if (chart.series.length == 1) {
            legend_str = legend_str + `<div class="legend-group col-sm-12">`;
            legend_str = legend_str + `<div class="item col-sm-6"><span class="serieName"><span class="symbol" style="background-color: ${data.color}"></span><div style="display: inline-block;"><div style="float: left;">${data.name}</div><div class="legend-value">$${numberFormatter(data.yData.reduce((a, b) => a + b, 0))}</div></div></span></div>`;
            legend_str = legend_str + `</div>`;
            legend.append(legend_str);
          }
          else {
            if (count_legend == 0) {
              legend_str = legend_str + `<div class="legend-group col-sm-12">`;
            }
    
            legend_str = legend_str + `<div class="item col-sm-6"><span class="serieName"><span class="symbol" style="background-color: ${data.color}"></span><div style="display: inline-block;"><div style="float: left;">${data.name}</div><div class="legend-value">$${numberFormatter(data.yData.reduce((a, b) => a + b, 0))}</div></div></span></div>`;
    
            if (count_legend == 1) {
              legend_str = legend_str + `</div>`;
            }
    
            count_legend++;
            counter_loop++;

            if ((chart.series.length%2 == 1) && (chart.series.length == counter_loop)) {
              count_legend = 0;
              legend.append(legend_str);
              legend_str = ``;
            }
            
            if (count_legend == 2) {
              count_legend = 0;
              legend.append(legend_str);
              legend_str = ``;
            }        
          }
        });
  
        $('#graph-legend .item').click(function () {
  
          let selectedSerieName = $(this)[0].children[0].children[1].children[0].textContent
  
          let filteredSerie = chart.series.filter(function(value) {
            return value.name == selectedSerieName;
          });
          
          if (filteredSerie[0].visible == true) {
              filteredSerie[0].hide();
              $($(this)[0]).addClass("unselected");
          }
          else {
              filteredSerie[0].show();
              $($(this)[0]).removeClass("unselected");
          }
        });
  
        let dataJson = [];
        pdfData = [];
  
        chart.series.forEach((data, index) => {
          if (data.userOptions.data.length != 0) {
            dataJson.push({
              "Date": data.userOptions.name,
              "Costs": numberFormatter(data.userOptions.data.reduce((a, b) => a + b))
            });
    
            pdfData.push([data.userOptions.name, numberFormatter(data.userOptions.data.reduce((a, b) => a + b))]);
          }
        });
  
        csvStr = JsonToCSV(dataJson);
  
      }
    }
  });
}

function getCostSummary() {
  loaderObjServer.display();
  $.ajax({
    url: "/xui/kumo/api/get_cost_summary/",
    type: 'GET',
    dataType: 'json',
    data: {
      body: JSON.stringify({ 
        server_id: SERVER_DATA.id,
        instance_id: SERVER_DATA.resource_handler_svr_id,
        server_provider_type: SERVER_DATA.type_slug,
      })
    },
    success: function (response) {
      if (response.result == "NO RH") {
        $('#server-tab .errorMessageModal').modal('show');
        $('#server-container').css('filter', 'blur(10px)');
        $('#server-tab .go-to-admin').addClass('hidden');
        $('#server-tab .go-to-rh').addClass('hidden');
        $('#server-tab .no-data').addClass('hidden');
        $('#server-tab .no-server-rh').removeClass('hidden');
        loaderObjServer.hide();
      }
      else {
        if (response.result == "NO RH") {
          $('#server-tab .errorMessageModal').modal('show');
          $('#server-container').css('filter', 'blur(10px)');
          $('#server-tab .go-to-admin').addClass('hidden');
          $('#server-tab .go-to-rh').addClass('hidden');
          $('#server-tab .no-data').addClass('hidden');
          $('#server-tab .no-server-rh').removeClass('hidden');
          loaderObjServer.hide();
        }
        else {
          $('#lsd-cost').html(`<span class="acc-currency">$</span>${response.result.last_7_days_cost}`);

          if (response.result.percentage > 0) {
            $('#day-on-day-span').html(`<i class="fa fa-long-arrow-up fa-md pull-left" aria-hidden="true"></i>&nbsp;${numberFormatter(response.result.percentage)}% in last 24 hours`);
          }
          else if (response.result.percentage == 0) {
            $('#day-on-day-span').html(`${numberFormatter(response.result.percentage)}% in last 24 hours`);
          }
          else {
            $('#day-on-day-span').html(`<i class="fa fa-long-arrow-down fa-md pull-left" aria-hidden="true"></i>&nbsp;${numberFormatter(response.result.percentage)}% in last 24 hours`);
          }

          if (response.result.last_updated_at != "N/A") {
            let updateTime = response.result.last_updated_at.split('T')[1].substring(0,5);
            let updateDate = response.result.last_updated_at.split('T')[0];

            $('#update-timing-utc').html(`<p style="margin-bottom: 0px;">(Last updated at ${updateTime} UTC</p><p>on ${updateDate})</p>`);
          }

          if (response.result.previous_month_cost != 0) {
            $('#previous-month-cost').show();
            $('#pm-cost').html(`<span class="acc-currency">$</span>${response.result.previous_month_cost}`);
          }
          else {
            $('#previous-month-cost').hide();
          }

          $('#cm-cost').html(`<span class="acc-currency">$</span>${numberFormatter(response.result.current_month_estimated_cost)}`);
          $('#t-cost').html(`<span class="acc-currency">$</span>${numberFormatter(response.result.total_cost.total_cost)}`);
          $('#server-date-range').html(`(${response.result.total_cost.date_range})`);
          // loaderObjServer.hide();
        }
      }
    },
    error: function (xhr) {
      // alert("An error occured: " + xhr.status + " " + xhr.statusText);
      loaderObjServer.hide();
    },
    timeout: 600000
  });
}

function getCostBreakdown() {
  loaderObjServer.display();
  datesArray = getDatesBetweenDates(new Date(startDate), new Date(endDate));
  $.ajax({
    url: "/xui/kumo/api/get_cost_breakdown/",
    type: 'GET',
    dataType: 'json',
    data: {
      body: JSON.stringify({ 
        server_id: SERVER_DATA.id,
        instance_id: SERVER_DATA.resource_handler_svr_id,
        start_date: startDate,
        end_date: endDate,
        server_provider_type: SERVER_DATA.type_slug,
      })
    },
    success: function (response) {
      if (response.result == "NO RH") {
        $('#server-tab .errorMessageModal').modal('show');
        $('#server-container').css('filter', 'blur(10px)');
        $('#server-tab .go-to-admin').addClass('hidden');
        $('#server-tab .go-to-rh').addClass('hidden');
        $('#server-tab .no-data').addClass('hidden');
        $('#server-tab .no-server-rh').removeClass('hidden');
        loaderObjServer.hide();
      }
      else {
        costBreakdown = response.result;
        getOperationalCostBreakdown();
      }
    },
    error: function (xhr) {
      // alert("An error occured: " + xhr.status + " " + xhr.statusText);
      getOperationalCostBreakdown();
      loaderObjServer.hide();
    },
    timeout: 600000
  });
}

function getOperationalCostBreakdown() {
  loaderObjServer.display();
  if(SERVER_DATA.type_slug == 'aws'){
    $.ajax({
      url: "/xui/kumo/api/get_operational_cost_breakdown/",
      type: 'GET',
      dataType: 'json',
      data: {
        body: JSON.stringify({ 
          server_id: SERVER_DATA.id,
          instance_id: SERVER_DATA.resource_handler_svr_id,
          start_date: startDate,
          end_date: endDate,
          server_provider_type: SERVER_DATA.type_slug,
        })
      },
      success: function (response) {
        operationalCost = response.result;
        totalCostBreakdown = $.extend({}, costBreakdown, operationalCost);
        var dateJson = {};
        var mappingData = {};
        seriesData = [];
        totalGraphCost = 0;
        
        Object.keys(totalCostBreakdown).forEach(parts => {
          var existingDates = {};
  
          // console.log(totalCostBreakdown[parts]);
          mappingData[parts] = {};
          
          datesArray.forEach(dates => dateJson[dates] = 0)
          totalCostBreakdown[parts].chart_data.forEach(date => existingDates[date.label] = date.cost);
          
          datesArray.forEach(element => {
            if (Object.keys(existingDates).includes(element)) {
              mappingData[parts][element] = existingDates[element];
            }
            else {
              mappingData[parts][element] = 0;
            }
          });
          
          totalGraphCost = totalGraphCost + Object.values(mappingData[parts]).reduce((a, b) => a + b, 0);
  
          var totalSumParts = Object.values(mappingData[parts]).reduce((a, b) => a + b, 0)
          if (totalSumParts != 0) {
            seriesData.push({
              name: SERVER_PARTS[parts],
              data: Object.values(mappingData[parts])
            });
          }
        });
  
        if ((totalGraphCost == 0) || (seriesData.length == 0)) {
          seriesData = [{
            name: "amis",
            data: []
          },
          {
            name: "backup",
            data: []
          },
          {
            name: "data_transfer",
            data: []
          },
          {
            name: "storage",
            data: []
          },
          {
            name: "ips",
            data: []
          },
          {
            name: "instance_type",
            data: []
          }]
          $('#graph-legend').hide();
          $('#graph-div').removeClass('col-sm-8');
          $('#graph-div').addClass('col-sm-12');
        }
        else {
          $('#graph-legend').show();
          $('#graph-div').removeClass('col-sm-12');
          $('#graph-div').addClass('col-sm-8');
        }
  
        $('#total-graph-cost').html(`<span class="acc-currency">$</span>${numberFormatter(totalGraphCost)}`);
        plotChart(datesArray, seriesData);
        loaderObjServer.hide();
      },
      error: function (xhr) {
        // alert("An error occured: " + xhr.status + " " + xhr.statusText);
        seriesData = [{
          name: "amis",
          data: []
        },
        {
          name: "backup",
          data: []
        },
        {
          name: "data_transfer",
          data: []
        },
        {
          name: "storage",
          data: []
        },
        {
          name: "ips",
          data: []
        },
        {
          name: "instance_type",
          data: []
        }]
        $('#graph-legend').hide();
        $('#graph-div').removeClass('col-sm-8');
        $('#graph-div').addClass('col-sm-12');
        plotChart(datesArray, seriesData);
        loaderObjServer.hide();
      },
      timeout: 600000
    });
  }
  else{
    totalCostBreakdown = $.extend({}, costBreakdown);
    var dateJson = {};
    var mappingData = {};
    seriesData = [];
    totalGraphCost = 0;
    
    Object.keys(totalCostBreakdown).forEach(parts => {
      var existingDates = {};

      // console.log(totalCostBreakdown[parts]);
      mappingData[parts] = {};
      
      datesArray.forEach(dates => dateJson[dates] = 0)
      totalCostBreakdown[parts].chart_data.forEach(date => existingDates[date.label] = date.cost);
      
      datesArray.forEach(element => {
        if (Object.keys(existingDates).includes(element)) {
          mappingData[parts][element] = existingDates[element];
        }
        else {
          mappingData[parts][element] = 0;
        }
      });
      
      totalGraphCost = totalGraphCost + Object.values(mappingData[parts]).reduce((a, b) => a + b, 0);

      var totalSumParts = Object.values(mappingData[parts]).reduce((a, b) => a + b, 0)
      if (totalSumParts != 0) {
        seriesData.push({
          name: SERVER_PARTS[parts],
          data: Object.values(mappingData[parts])
        });
      }
    });

    if ((totalGraphCost == 0) || (seriesData.length == 0)) {
      seriesData = [{
        name: "amis",
        data: []
      },
      {
        name: "backup",
        data: []
      },
      {
        name: "data_transfer",
        data: []
      },
      {
        name: "storage",
        data: []
      },
      {
        name: "ips",
        data: []
      },
      {
        name: "instance_type",
        data: []
      }]
      $('#graph-legend').hide();
      $('#graph-div').removeClass('col-sm-8');
      $('#graph-div').addClass('col-sm-12');
    }
    else {
      $('#graph-legend').show();
      $('#graph-div').removeClass('col-sm-12');
      $('#graph-div').addClass('col-sm-8');
    }

    $('#total-graph-cost').html(`<span class="acc-currency">$</span>${numberFormatter(totalGraphCost)}`);
    plotChart(datesArray, seriesData);
    loaderObjServer.hide();
  }
}

function getPotentialSavings() {
  loaderObjServer.display();
  $.ajax({
    url: "/xui/kumo/api/get_potential_savings/",
    type: 'GET',
    dataType: 'json',
    data: {
      body: JSON.stringify({ 
        server_id: SERVER_DATA.id,
        instance_id: SERVER_DATA.resource_handler_svr_id,
        server_provider_type: SERVER_DATA.type_slug,
      })
    },
    success: function (response) {      
      if (response.result == "NO RH") {
        $('#server-tab .errorMessageModal').modal('show');
        $('#server-container').css('filter', 'blur(10px)');
        $('#server-tab .go-to-admin').addClass('hidden');
        $('#server-tab .go-to-rh').addClass('hidden');
        $('#server-tab .no-data').addClass('hidden');
        $('#server-tab .no-server-rh').removeClass('hidden');
        loaderObjServer.hide();
      }
      else {
        let totalSavings = 0; 
        response.result.forEach(element => {
          if (element.count != 0) {
            $('#example tbody').append(`<tr>
                                        <td>${element.type.charAt(0).toUpperCase() + element.type.slice(1)}</td>
                                        <td>${POTENTIAL_SAVINGS[element.service]}</td>
                                        <td>${element.count}</td>
                                        <td><strong><span class="acc-currency">$</span>${numberFormatter(parseFloat(element.cost_sum))}</strong></td>
                                    </tr>`)
            totalSavings = totalSavings + parseFloat(element.cost_sum);
          }
        });

        $('#total-savings').html(`<span class="acc-currency">$</span>${numberFormatter(totalSavings)}`);
        $('#example').dataTable({searching: false, paging: false, info: false, "bDestroy": true});
      }
    },
    error: function (xhr) {
      // alert("An error occured: " + xhr.status + " " + xhr.statusText);
      $('#example').dataTable({searching: false, paging: false, info: false, "bDestroy": true});
      loaderObjServer.hide();
    },
    timeout: 600000
  });
}

function GetFormattedDate(givenD) {
  var month = givenD.getMonth() + 1;
  
  if (month < 10) {
    month = '0' + month;
  }

  var day = givenD.getDate();
  
  if (day < 10) {
    day = '0' + day;
  }

  var year = givenD.getFullYear();
  return year + "-" + month + "-" + day;
}

const getDatesBetweenDates = (startDate, endDate) => {
  let dates = []
  //to avoid modifying the original date
  const theDate = new Date(startDate)
  while (theDate <= endDate) {
    dates = [...dates, GetFormattedDate(theDate)]
    theDate.setDate(theDate.getDate() + 1)
  }
  return dates
}

function JsonToCSV(jsonArray){
  csvStr = '';
  let jsonFields = ['Elements', 'Costs (unblended)'];
  let filterFields = {
    "FILTERS": "",
    "Server ID": SERVER_DATA.resource_handler_svr_id,
    "Date Range": `\"${startDate} to ${endDate}\"`,
    "Total Cost": numberFormatter(totalGraphCost),
  };
  
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
	let report_name = "Server Cost Usage Report".split(' ').join('_') + moment().format('_DDMMYYYYhhmmss');
  hiddenElement.download = report_name + '.csv';
  hiddenElement.click();
}

function downloadPDF(csvStr) {
  //Get svg markup as string
  let svg = $('#graph-div').highcharts().container.innerHTML;
  let canvas = document.createElement('canvas');
  let doc = new jsPDF();
  pageGap = 10;
  var continueFurther = 0;

  canvg(canvas, svg);
  let dataUrl = canvas.toDataURL('image/png');
  
  doc.setFont('helvetica');
  doc.setFontType('bold');
  createHeader(doc);
  doc.text(pageGap, pageGap+25, 'Filters:');
  doc.setFontSize(10);
  doc.text(pageGap+10, pageGap+30, `Provider: ${SERVER_DATA.resource_handler_svr_id}`)
  doc.text(pageGap+10, pageGap+35, `Date Range: ${startDate} to ${endDate}`)
  doc.text(pageGap+10, pageGap+40, `Total: ${numberFormatter(totalGraphCost)}`);
  doc.addImage(dataUrl, 'PNG', 10, pageGap+50, 190, 100);
  
  doc.addPage();
  createHeader(doc);
  doc.text(pageGap, pageGap+25, 'Costing data:');
  doc.setFontSize(10);

  // Or use javascript directly:
  doc.autoTable({
    head: [['Elements', 'Costs (unblended)']],
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
