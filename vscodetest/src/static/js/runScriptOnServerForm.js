/*
 * Front end behaviors for RunScriptOnServerForm and BulkRunScriptOnServerForm
 */
$(function() {
  var $elements = $('.js-set-width');
  $elements.removeClass('large-width');
  $elements.parent().css({
    "width": "30em"
  });
});
