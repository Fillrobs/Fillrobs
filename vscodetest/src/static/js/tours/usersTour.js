(function (c2, $, profile_id) {
  'use strict';

  var tour = new Tour({
    orphan: true,
    storage: false,
    onEnd: function () {
      c2.tourUtilities.handleTourEnd(profile_id);
    },
    template: c2.tourUtilities.tourTemplate,
    steps: [
      {
        element: "",
        title: "Users",
        content: "<p>Create <strong>Users</strong> manually or use an enterprise user management system such as Active Directory to synchronize and manage them in CloudBolt.</p><p>Click <strong>Docs</strong> in the navigation bar and scroll down to see the default roles for Users. As an example, the \"Devops admin\" role provides access to manage all servers without needing per-group permissions.</p><p>Click Next or go to <strong>Catalog</strong> in the navigation bar to continue the tour.</p>",
        onShown: function (tour) {
          // add navigation buttons
          c2.tourUtilities.addNavigation();
          // make the "previous" button activate and redirect even though there is no previous step
          $('[data-role="prev"]').removeAttr('disabled').removeClass('disabled').on('click', function () {
            window.location = '/groups/';
          });
        }
      },
      {
        path: '/catalog/'
      },
    ]
  });

  c2.usersTour = tour;
  
})(window.c2, window.jQuery, window.profile_id);
