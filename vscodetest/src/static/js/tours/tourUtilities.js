(function (c2, $) {
  'use strict';
  
  var tourDisabled = false;
  
  function isTourDisabled () {
    return tourDisabled;
  }
  
  function handleTourEnd (profile_id) {
    var disable_tours = $('#disable-tours').prop('checked');
    if (disable_tours) {
      $.ajax({
        url: `/users/${profile_id}/tutorial_off/`,
        type: 'POST',
        success: function (response) {
          tourDisabled = true;
          // Add a success message popup (response is sent from server, 'success' makes it green, true means it's dismissible)
          c2.alerts.addGlobalAlert(response, 'success', true);
        },
        error: function (jqXHR) {
          c2.alerts.addGlobalAlert(jqXHR.responseText, 'error', true);
        }
      });
    }
  }

  //  Adds the navigation buttons back after the page loads to prevent them being sanitized out
  function addNavigation () {
      $(".popover.tour .popover-navigation").html(`
          <div class='btn-group'> 
              <button class='btn btn-default' data-role='prev'>« Prev</button>
              <button class='btn btn-default' data-role='next'>Next »</button>
          </div>
          <div style='display: inline; float: right;'>
              <div style='display: flex; align-items: flex-end;'>
                  <div style='display: inline; vertical-align: bottom; margin-right: 2em;'>
                      <input id='disable-tours' type='checkbox'>
                      <label for='disable-tours'>Disable Tour</label>
                  </div>
                  <button class='btn btn-default' data-role='end'>Dismiss</button>
              </div>
          </div>`
      );
  }

  var tourTemplate = `
      <div class='popover tour'>
          <div class='arrow'></div>
          <h3 class='popover-title'></h3>
          <div class='popover-content'></div>
          <div class='popover-navigation'></div>
      </div>
  `;
  
  c2.tourUtilities = {
    isTourDisabled: isTourDisabled,
    handleTourEnd: handleTourEnd,
    addNavigation: addNavigation,
    tourTemplate: tourTemplate
  };
  
})(window.c2, window.jQuery);
