(function (c2, $, profile_id) {
  'use strict';

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
        element: "",
        title: "Environments",
        content: "<strong>Environments</strong> provide powerful organizational structure and can be thought of as logical clouds.",
        onShown: function (tour) {
          // add navigation buttons
          c2.tourUtilities.addNavigation();
          // make the "previous" button activate and redirect even though there is no previous step
          $('[data-role="prev"]').removeAttr('disabled').removeClass('disabled').on('click', function () {
            window.location = '/admin/resourcehandlers/';
          });
        }
      },
      {
        element: '#docs-link',
        content: "Take a moment to read the description on this page and then click <em>Learn more</em> to find out about how to use <strong>Environments</strong> and <strong>Groups</strong> together to tailor controlled access to resources for end users in CloudBolt.",
        placement: 'bottom',
        onShow: function (tour) {
          // This fixes some weird behavior where the title attribute of the target element (#docs-link) was being displayed as the title in the tour popover
          $('#docs-link').removeAttr('data-original-title');
        }
      },
      {
        element: 'li[data-topnav="groups"]',
        // Use template with class 'arrow-fix' for styling correction
        template: `
            <div class='popover tour'>
                <div class='arrow arrow-fix'></div>
                <h3 class='popover-title'></h3>
                <div class='popover-content'></div>
                <div class='popover-navigation'></div>
            </div>
        `,
        content: "Click Next or go to <strong>Groups > All Groups</strong> to begin managing user permissions.",
        placement: "right"
      },
      {
        path: '/groups/'
      }
    ]
  });

  c2.environmentsTour = tour;
  
})(window.c2, window.jQuery, window.profile_id);
