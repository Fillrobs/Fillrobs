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
        title: "Welcome to CloudBolt!",
        content: "<p>This is CloudBolt's dashboard, which shows a quick summary of your IT estate across various groups, environments, and technologies. The default starting page can be changed in <strong>Admin > Misc Settings</strong>.</p><p>You can return to this page at any time by clicking the logo in the navigation bar.</p>",
      },
      {
        element: 'li[data-topnav="admin"]',
        content: "Click Next or go to <strong>Admin > Resource Handlers</strong> to begin connecting to your public and private clouds.",
        placement: "left",
        // passing in template with classes 'max-width-400' and 'arrow-fix' in order to change style for this popup only
        template: `
            <div class='popover tour max-width-400'>
                <div class='arrow arrow-fix'></div>
                <h3 class='popover-title'></h3>
                <div class='popover-content'></div>
                <div class='popover-navigation'></div>
            </div>
        `
      },
      {
        path: '/admin/resourcehandlers/'
      }
    ]
  });

  c2.dashboardTour = tour;
  
})(window.c2, window.jQuery, window.profile_id);
