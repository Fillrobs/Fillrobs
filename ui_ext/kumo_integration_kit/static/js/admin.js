import { LoaderClass, DATA_BACKUP_HOURS, numberFormatter } from './common.js';

var loaderObjAdmin = new LoaderClass('admin-tab');
const RESOURCE_HANDLER = {
  handlerId: $('#handler_details').data('handlerid'),
  handlerType: $('#handler_details').data('handler')
}

$(document).ready(function () {

  getCreds(get_rh_list);
  $(".hide-button").hide();
  $(".hide-button-edit").hide();

  $('#myModal').on('shown.bs.modal', function () {
    $('#admin-tab .modal-content').height($('.box-expand').height());
    $('#admin-tab .modal-content').width($('.box-expand').width());
    $('#admin-tab .slides').height($('.box-expand').height() - 180);
  });

  $('#saveCredsForm').submit(function (e) {
    e.preventDefault();
    validateCreds();
  });

  $(document).on('click', '#refresh-page', function (e) {
    window.location.reload();
  });

  $(document).on('click', '.save-creds', function (e) {
    saveCreds();
  });

  $(document).on('click', '.save-kumo-data', function (e) {
    saveKumoData(this);
  });

  $(document).on('click', '#yes-edit', function (e) {
    $('.yes-creds').hide();
    $('.no-creds').show();
    $('.validate').show();
    $('.save-creds').show();
    $('input[name="kumo-domain-url"]').val($('.site-host').val().split("://")[1].split(".")[0]);
    $('input[name="kumo-api-key"]').val($('.api-key').val());
    $('#savingStatus').text('');
    $(".hide-button").show();
    $("#cancel-edit").show();
  });

  $(document).on('click', '#cancel-edit', function (e) {
    $('.yes-creds').show();
    $('.no-creds').hide();
    $('.validate').hide();
    $('.save-creds').hide();
    $('#savingStatus').text('');
    $(".hide-button").hide();
    $("#cancel-edit").hide();
  });

  $(document).on('click', '#edit-setting', function (e) {
    $('.enabling').prop("disabled", false);
    $('#update-configuration').text('');
    $(".hide-button-edit").show();
  });

  $(document).on('click', '#cancel-edit-config', function (e) {
    $('.enabling').prop("disabled", true);
    $('#update-configuration').text('');
    $(".hide-button-edit").hide();
  });

  $(document).on('click', '.collapse-menu', function (e) {
    $("i", this).toggleClass("fa fa-chevron-right fa fa-chevron-down");
  });

  $(document).on('click', '#update-config', function (e) {
    updateConfig();
  });
  
})

function validateCreds() {
  loaderObjAdmin.display();
  $.ajax({
    url: "/xui/kumo/api/validate_credentials/",
    type: 'POST',
    dataType: 'json',
    data: {
      body: JSON.stringify({
        web_host: $('.site-start').text() +
            $('input[name="kumo-domain-url"]').val() + $('.site-end').text(),
        api_key: $('input[name="kumo-api-key"]').val(),
      })
    },
    success: function (response) {
      if (response.result) {
        $('#validationStatus').text('Credentials validate successfully!');
        $('.save-creds').prop('disabled', false);
        $('.save-creds').removeClass('disabled');
      }
      else {
        $('#validationStatus').text('Credentials not valid!');
        $('.save-creds').prop('disabled', true);
        $('.save-creds').addClass('disabled');
      }

      loaderObjAdmin.hide();
    },
    error: function (xhr) {
      alert("An error occured: " + xhr.status + " " + xhr.statusText);
      loaderObjAdmin.hide();
    }
  });
}

function saveCreds() {
  loaderObjAdmin.display();
  $.ajax({
    url: "/xui/kumo/api/save_credentials/",
    type: 'POST',
    dataType: 'json',
    data: {
      body: JSON.stringify({
        web_host: $('.site-start').text() +
          $('input[name="kumo-domain-url"]').val() + $('.site-end').text(),
        api_key: $('input[name="kumo-api-key"]').val(),
      })
    },
    success: function (response) {
      if (response.result) {
        if (response.exists) {
          $('#savingStatus').text('No changes in credentials!');
        } 
        else if (response.changed) {
          $('#savingStatus').text('Credentials updated exists!');
        } 
        else {
          $('#savingStatus').text('Credentials stored successfully!');
        }
        $('.validate, .save-creds').prop('disabled', true);
        $('.validate, .save-creds').addClass('disabled');
        $('#validationStatus').text('');

        getCreds(get_rh_list);
      }
      else {
        $('#savingStatus').text('Credentials not stored!');
      }

      loaderObjAdmin.hide();
    },
    error: function (xhr) {
      alert("An error occured: " + xhr.status + " " + xhr.statusText);
      loaderObjAdmin.hide();
    }
  });
}

function saveKumoData(event) {
  if (($(`input[name="billing-adapter-${event.id}"]`).val() == "") 
      && ($(`input[name="normal-adapter-${event.id}"]`).val() == "")) {
          $(`#savingKumoData-${event.id}`).text('Please enter data to save!');
  }
  else {
    $(`#savingKumoData-${event.id}`).text('');
    loaderObjAdmin.display();
    
    $.ajax({
      url: "/xui/kumo/api/save_kumo_data/",
      type: 'POST',
      dataType: 'json',
      data: {
        body: JSON.stringify({
          rhid: event.id,
          billing_account: $(`input[name="billing-adapter-${event.id}"]`).val(),
          normal_account: $(`input[name="normal-adapter-${event.id}"]`).val(),
        })
      },
      success: function (response) {
        if (response.result) {
          $(`#savingKumoData-${event.id}`).text('Data Stored!');
        }
        else {
          $(`#savingKumoData-${event.id}`).text('Data not stored!');
        }

        loaderObjAdmin.hide();
      },
      error: function (xhr) {
        alert("An error occured: " + xhr.status + " " + xhr.statusText);
        loaderObjAdmin.hide();
      }
    });
  }
}

function getCreds(func1) {
  loaderObjAdmin.display();
  $.ajax({
    url: "/xui/kumo/api/get_credentials/",
    type: 'POST',
    dataType: 'json',
    data: {},
    success: function (response) {
      $(".show-refresh").hide();
      $(".hide-refresh").show();
      $("a[href='#resource-handlers']").show();
      $("#cancel-edit").hide();
      $("hr").show();
      if ((response.result) && (response.creds.length != 0)) {
        $('.yes-creds').show();
        $('.no-creds').hide();
        $('.validate').hide();
        $('.save-creds').hide();
        $('.site-host').val(`https://${response.creds['web_host']}`);
        $('.api-key').val(response.creds['api_key']);
        $(".hide-button").hide();
        $("#yes-edit").show();
        func1(get_config);
      }
      else {
        $('.yes-creds').hide();
        $('.no-creds').show();
        $('.validate').show();
        $('.save-creds').show();
        $(".hide-button").show();
        $("#yes-edit").hide();
        $('.rh-list-group').empty();
        $('#no-rh-list').text('No resource handlers found!');
        $('#no-rh-list').removeClass('hidden');
        loaderObjAdmin.hide();
      }
    },
    error: function (xhr) {
      $('.yes-creds').hide();
      $('.no-creds').show();
      $('.validate').show();
      $('.save-creds').show();
      $(".hide-button").show();
      $("#cancel-edit").hide();
      $("#yes-edit").hide();
      if(xhr.status == 404) {
        $(".show-refresh").show();
        $(".hide-refresh").hide();
        $("hr").hide();
      }
      $("a[href='#resource-handlers']").hide();
      loaderObjAdmin.hide();
    },
    timeout: 60000
  });
}

function get_rh_list(func2) {
  $.ajax({
    url: "/xui/kumo/api/get_rh_list/",
    type: 'POST',
    dataType: 'json',
    data: {
        body: JSON.stringify({
            show_all: 'true',
            not_configured: 'true',
        })
    },
    success: function (response) {
      $(".show-refresh").hide();
      $(".hide-refresh").show();
      $("a[href='#resource-handlers']").show();
      $('.rh-list-group').empty();
      $('#no-rh-list').addClass('hidden');

      if (response.result.length != 0) {
        response.result.forEach(rh => {
          let iconName = (rh.ip.split(".")[0] == "aws") ? "icon-handler-aws" : "icon-handler-azure_arm";
          let placeHolder = (rh.ip.split(".")[0] == "aws") ? "Account ID" : "Subscription ID";
          let handlerName = (rh.ip.split(".")[0] == "aws") ? "AWS" : "Azure";
          let inputPattern = (rh.ip.split(".")[0] == "aws") ? "^[0-9]{12}$" : "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$";
          $('.rh-list-group').append(`
              <div class="panel panel-default">
                  <div class="panel-heading">
                      <h4 class="panel-title">
                          <a class="collapse-menu" data-toggle="collapse" href="#collapse-${rh.id}" style="float: left; margin-right:15px; margin-top: 7px; padding: 0 0 0 0;">
                              <i class="fa fa-chevron-right"></i>
                          </a>
                          <div style="float: left; margin-top: 5px;">
                              <a> 
                                  <span class="icon icon-30 ${iconName}"></span>
                                  ${rh.name}
                              </a>
                              <!-- <div style="display: inline-flex;">
                                  <form style="display: inline-flex;">
                                      <input class="form-control " type="text" name="billing-adapter-${rh.id}" placeholder="Enter Kumolus Billing ${placeHolder}" style="width: 270px; margin-left: 2%;" pattern="${inputPattern}"> 
                                      <input class="form-control " type="text" name="normal-adapter-${rh.id}" placeholder="Enter Kumolus Normal ${placeHolder}" style="width: 270px; margin-left: 2%;" pattern="${inputPattern}"> 
                                      <button class="btn btn-success save-kumo-data" id="${rh.id}" type="button" style="margin-left: 2%;">Save</button>
                                      <label class="control-label" id="savingKumoData-${rh.id}" style="width: 270px; margin-left: 2%;"></label>
                                  </form>
                              </div> --!>
                          </div>
                          <div style="float: right;">
                              <button class="btn btn-primary" 
                                      onclick="location.href='/admin/resourcehandlers/${rh.id}/#tab-spend';" 
                                      type="button">Spend Tab</button>
                              <button class="btn btn-primary" 
                                      onclick="location.href='/admin/resourcehandlers/${rh.id}/#tab-efficiency';" 
                                      type="button">Efficiency Tab</button>
                          </div>
                      </h4>
                  </div>
                  <div id="collapse-${rh.id}" class="panel-collapse collapse">
                      <table class="table">
                          <thead>
                              <tr>
                                  <th>Resource handler ID</th>
                                  <th>Description</th>
                                  <th>Provider</th>
                                  <th>ID</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr>
                                  <td>${rh.id}</td>
                                  <td>${rh.description}</td>
                                  <td>${rh.ip}</td>
                                  <td>${rh.serviceaccount}</td>
                              </tr>
                          </tbody>
                      </table>
                  </div>
              </div>
          `);

          $(`input[name="billing-adapter-${rh.id}"]`).val(rh.billing_account);
          $(`input[name="normal-adapter-${rh.id}"]`).val(rh.normal_account);
        });
      }
      else {
        $('.rh-list-group').empty();
        $('#no-rh-list').text('No resource handlers found!');
        $('#no-rh-list').removeClass('hidden');
      }
      func2();
    },
    error: function (xhr) {
      if(xhr.status == 404) {
        $(".show-refresh").show();
        $(".hide-refresh").hide();
      }
      $("a[href='#resource-handlers']").hide();
      loaderObjAdmin.hide();
    },
    timeout: 60000
  });
}

function get_config() {
  $.ajax({
    url: "/xui/kumo/api/get_config/",
    type: 'GET',
    dataType: 'json',
    data: {},
    success: function (response) {
      $(".show-refresh").hide();
      $(".hide-refresh").show();
      $("a[href='#resource-handlers']").show();

      if(response.hasOwnProperty('error')) {
        loaderObjAdmin.hide();
        $("#edit-setting").hide();
      }
      else {
        $("#edit-setting").show();
        let adviser_config = response.result.service_adviser_config;
        (adviser_config.rds_snapshot_config_check) ? $("#rds_snapshot_no").prop("checked", true) : $("#rds_snapshot_no").prop("checked", false);
        (adviser_config.running_rightsizing_config_check) ? $("#idle_running_rs").prop("checked", true) : $("#idle_running_rs").prop("checked", false);
        (adviser_config.stopped_rightsizing_config_check) ? $("#idle_stopped_rs").prop("checked", true) : $("#idle_stopped_rs").prop("checked", false);
        (adviser_config.volume_snapshot_config_check) ? $("#volume_snapshot_no").prop("checked", true) : $("#volume_snapshot_no").prop("checked", false);
        $("#rds_snapshot_after").val(adviser_config.rds_snapshot_retention_period);
        $("#volume_snapshot_after").val(adviser_config.volume_snapshot_retention_period);
        $("#idle_running_after").val(adviser_config.running_rightsizing_retention_period);
        $("#idle_stopped_after").val(adviser_config.stopped_rightsizing_retention_period);
        loaderObjAdmin.hide();
      }
    },
    error: function (xhr) {
      if(xhr.status == 404) {
        $(".show-refresh").show();
        $(".hide-refresh").hide();
        $("a[href='#resource-handlers']").hide(); 
      }
      $("#edit-setting").hide();
      loaderObjAdmin.hide();
    },
    timeout: 60000
  });
}

function updateConfig() {
  loaderObjAdmin.display();
  $.ajax({
    url: "/xui/kumo/api/set_config/",
    type: 'POST',
    dataType: 'json',
    data: 
    {
      body: JSON.stringify({
        right_size_config: {
            rds_snapshot_config_check: $("#rds_snapshot_no").prop("checked"),
            rds_snapshot_retention_period: $("#rds_snapshot_after").val(),
            running_rightsizing_config_check: $("#idle_running_rs").prop("checked"),
            running_rightsizing_retention_period: $("#idle_running_after").val(),
            stopped_rightsizing_config_check: $("#idle_stopped_rs").prop("checked"),
            stopped_rightsizing_retention_period: $("#idle_stopped_after").val(),
            volume_snapshot_config_check: $("#volume_snapshot_no").prop("checked"),
            volume_snapshot_retention_period: $("#volume_snapshot_after").val()
          }
        })
    },
    success: function (response) {
      console.log(response.result);
      $('#update-configuration').text("Updated Successfully!");
      loaderObjAdmin.hide();
    },
    error: function (xhr) {
      alert("An error occured: " + xhr.status + " " + xhr.statusText);
      loaderObjAdmin.hide();
    }
  });
}