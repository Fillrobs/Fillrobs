(function (c2, $, profile_id) {
  'use strict';
  
  function getStep (tour, stepDescriptor) {
    if (stepDescriptor === 'prev') {
      return tour.getCurrentStep() - 1;
    }
    if (stepDescriptor === 'next') {
      return tour.getCurrentStep() + 1;
    }
  }

  // Only used in endTourThenRestart function
  function waitThenRestart (tour, stepToShow, waitTime) {
    setTimeout(function () {
      tour.restart().goTo(stepToShow);
    }, waitTime);
  }
  
  function endTourThenRestart (tour, options) {
    if (c2.tourUtilities.isTourDisabled()) {
      return;
    }

    tour.end();
    if (options.openDialog) {
      $.ajax({
        method: 'GET',
        url: '/admin/resourcehandlers/add/',
        dataType: 'html',
        success: function (response, textStatus, jqXHR) {
          c2.dialogs.displayJqXHR(jqXHR);
  
          waitThenRestart(tour, options.stepToShow, options.waitTime || 200);
        },
        error: function () {
          c2.alerts.addGlobalAlert('An error occurred with the tour.', 'error', true);
        }
      });
    } else {
      waitThenRestart(tour, options.stepToShow, options.waitTime || 200);
    }
  }
  
  var tour = new Tour({
    orphan: true,
    storage: false,
    onEnd: function () {
      c2.tourUtilities.handleTourEnd(profile_id);
    },
    template: c2.tourUtilities.tourTemplate,
    onShown: c2.tourUtilities.addNavigation,
    steps: [
      {
        element: '',
        title: 'Resource Handlers',
        // HTML is allowed
        content: "<p><strong>Resource Handlers</strong> connect CloudBolt to virtualization systems and public cloud accounts to provision and manage resources.</p><p>Having all this information in one place makes it easier to manage complex infrastructure provisioning workflows.</p>",
        // By default, the "Prev" button of a tour's first step is disabled. This is changed immediately after the popover is shown.
        onShown: function (tour) {
          // add navigation buttons
          c2.tourUtilities.addNavigation();
          $('.popover-navigation button[data-role="prev"]').removeAttr('disabled').removeClass('disabled').on('click', function () {
            window.location = '/dashboard/';
          });
        }
      },
      {
        element: '#docs-link',
        content: "<p>CloudBolt administration pages like this one include a short description and a <em>Learn more</em> link to the documentation at the top of the page.</p><p>Alternatively, you can click <strong>Docs</strong> in the navigation bar to jump to a relevant section of the documentation at any time.</p>",
        placement: 'bottom',
        onShow: function (tour) {
          // This fixes some weird behavior where the title attribute of the target element (#docs-link) was being displayed as the title in the tour popover
          $('#docs-link').removeAttr('data-original-title');
        },
        onNext: function (tour) {
          endTourThenRestart(tour, {
            openDialog: true,
            stepToShow: getStep(tour, 'next')
          });
        }
      },
      {
        element: '#choose_technology',
        content: "<p>Choose from this list of private and public cloud technologies to connect to enable provisioning and management using CloudBolt.</p><p><strong>Note &mdash;</strong> CloudBolt integrates with many other configuration and orchestration tools from other Admin pages.</p>",
        placement: 'right',
        // Use a template with the arrow div removed
        template: `
            <div class='popover tour'>
                <h3 class='popover-title'></h3>
                <div class='popover-content'></div>
                <div class='popover-navigation'></div>
            </div>
        `,
        onShown: function (tour) {
          // add navigation buttons
          c2.tourUtilities.addNavigation();

          var $dialog = $('#dialog-modal');
          
          // Attach an event handler that gets removed after firing once.
          // The 'hide.bs.modal' event gets triggered as soon as $dialog.modal('hide') is called
          $dialog.one('hide.bs.modal', function (e) {
            if ($(this).data('prevButtonClicked')) {
              endTourThenRestart(tour, {
                stepToShow: getStep(tour, 'prev'),
                // Because this event is triggered before the dialog is fully hidden, waitTime is increased
                waitTime: 400
              });
            } else {
              endTourThenRestart(tour, {
                stepToShow: getStep(tour, 'next'),
                waitTime: 400
              });
            }
          });
          
          // When user clicks anywhere in the technology list, end the tour. When dialog is closed, tour will restart per the previous handler
          $('#choose_technology').one('click', function (e) {
            tour.end();
          });
        },
        onPrev: function (tour) {
          var $dialog = $('#dialog-modal');
          $dialog.data('prevButtonClicked', true);
          $dialog.modal('hide');
        },
        onNext: function (tour) {
          $('#dialog-modal').modal('hide');
        }
      },
      {
        element: '#sync_vms_btn',
        content: "<p>After you connect to one or more private or public clouds, CloudBolt will automatically begin discovering VMs for reporting and management.</p><p>You can also initiate the discovery process by clicking <strong>Sync VMs from all resource handlers</strong>.</p><p style='margin-bottom: 0'>Click Next or go to <strong>Admin > Environments</strong> in the navigation bar to continue the tour.</p>",
        placement: 'bottom',
        onPrev: function (tour) {
          endTourThenRestart(tour, {
            openDialog: true,
            stepToShow: getStep(tour, 'prev')
          });
        },
      },
      {
        // This step simply redirects to the environments page
        path: '/environments/'
      }
    ]
  });
  
  // When "Add a resource handler" button is clicked, restart tour at the relevant step
  $('#add_handler').on('click', function () {
    endTourThenRestart(tour, {
      stepToShow: 2
    });
  });

  c2.resourceHandlersTour = tour;
  
})(window.c2, window.jQuery, window.profile_id);
