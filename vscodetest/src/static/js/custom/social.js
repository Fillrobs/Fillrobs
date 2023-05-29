/* This script cooperates with the one in $REPODIR/social/social.js, which runs
 * in the social buttons iframe. It receives messages reporting a successful
 * share and gives the appropriave feedback
 */

(function (window) {
  'use strict';

  var onMessage = function (e) {
    // only process the message if it comes from our expected source and
    // if it was sent by the ~/cloudbolt/social/sites.js tellParent function,
    // which attaches the .sender attribute that equals 'cloudbolt.social'
    if (e.origin === 'https://s3.amazonaws.com') {
      if (e.data.sender === 'cloudbolt.social') {
        console.log(e.data.payload);
        window.c2.alerts.addGlobalAlert(e.data.payload, 'info');
      } else {
        console.log('Ignoring message from expected origin but with unexpected format:', e.data);
      }
    } else {
      console.log('Ignoring message from unexpected origin ('+e.origin+').');
    }
  };

  window.addEventListener('message', onMessage);
})(window);
