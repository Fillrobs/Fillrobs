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
        element: '',
        title: 'Groups',
        // HTML is allowed
        content: "<p><strong>Groups</strong> associate <strong>Users</strong> with <strong>Environments</strong> and help you to manage permissions, approval processes, and quotas.</p><p>Groups can represent a business unit, department, team, project, or any other set of users. Permissions for Groups of Users can also be used for access and approval workflows in CloudBolt.</p><p>Each group has the same set of roles to which users can belong, and which grant permissions within that group. For example, a user could be a requester within one group and an approver in another.</p>",
        // By default, the "Prev" button of a tour's first step is disabled. This is changed immediately after the popover is shown.
        onShown: function (tour) {
          // add navigation buttons
          c2.tourUtilities.addNavigation();
          $('.popover-navigation button[data-role="prev"]').removeAttr('disabled').removeClass('disabled').on('click', function () {
            window.location = '/environments/';
          });
        }
      },
      {
        element: 'li[data-topnav="admin"]',
        content: "Click Next or go to <strong>Admin > Users</strong> to continue the tour.",
        placement: 'left',
        // Use template with classes 'max-width-400' and 'arrow-fix' for styling corrections
        template: `
            <div class="popover tour max-width-400">
                <div class="arrow arrow-fix"></div>
                <h3 class="popover-title"></h3>
                <div class="popover-content"></div>
                <div class="popover-navigation"></div>
            </div>
        `
      },
      {
        // This step simply redirects to the users page
        path: '/users/'
      }
    ]
  });
  
  c2.groupsTour = tour;
  
})(window.c2, window.jQuery, window.profile_id);
