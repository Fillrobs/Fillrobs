/* wizards.js */

//
// available at window.wizards namespace
//

(function (window) {
  'use strict';

  /* Enable or disable a specific pagination link. Also changes Prev or Next
   * links when appropriate.
   *
   * Args:
   *   index (0 based) of wizard step to affect
   *   enable (bool)
   */
  function enableStep (index, enable) {
    var $step = $('ul.wizard-pagination a[data-step="'+ index +'"]');
    var $next = $('ul.wizard-pagination .wizard-pagination-next');
    var $prev = $('ul.wizard-pagination .wizard-pagination-prev');
    var toggleDisabled;

    if (enable) {
      toggleDisabled = function ($el) {
        $el.removeClass('disabled');
      };
    } else {
      toggleDisabled = function ($el) {
        $el.addClass('disabled');
      };
    }

    toggleDisabled($step.closest('li'));
    if (index == $next.data('step')) {
      // Also its container for consistent behavior (Bootstrap styles cursor)
      toggleDisabled($next.closest('li'));
    } else if (index == $prev.data('step')) {
      toggleDisabled($prev.closest('li'));
    }
  }

  function disableStep(index) {
    enableStep(index, false);
  }

  window.wizards = {
    enableStep: enableStep,
    disableStep: disableStep
  };
})(window);
