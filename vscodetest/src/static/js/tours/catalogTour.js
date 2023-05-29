(function (c2, $, profile_id) {
  'use strict';

  var tour = new Tour({
    orphan: true,
    storage: false,
    onEnd: function () {
      c2.tourUtilities.handleTourEnd(profile_id);
    },
    // Use a template with the btn-fix class added to .popover-navigation for styling correction
    template: `
      <div class='popover tour'>
          <div class='arrow'></div>
          <h3 class='popover-title'></h3>
          <div class='popover-content'></div>
          <div class='popover-navigation btn-fix'></div>
      </div>
    `,
    onShown: c2.tourUtilities.addNavigation,
    steps: [
      {
        element: "",
        title: "Catalog",
        content: "<p>The Catalog displays all the blueprints your user has permission to deploy. You can create blueprints from scratch or import samples from the CloudBolt <strong>Content Library</strong> by clicking <strong>Import</strong> in the upper right corner.</p><p>For detailed documentation about configuring blueprints for use in the Catalog, click <strong>Docs</strong> in the navigation bar.</p>",
        onShown: function () {
          c2.tourUtilities.addNavigation();
          // make the "previous" button activate and redirect even though there is no previous step
          $('[data-role="prev"]').removeAttr('disabled').removeClass('disabled').on('click', function () {
            window.location = '/users/';
          });
        }
      },
      {
        element: "",
        title: "We hope you enjoy CloudBolt!",
        content: "<p>This ends the tour. If you need assistance, please contact <a href='mailto:support@cloudbolt.io'>support@cloudbolt.io</a>.</p>"
      },
    ]
  });

  c2.catalogTour = tour;
  
})(window.c2, window.jQuery, window.profile_id);
