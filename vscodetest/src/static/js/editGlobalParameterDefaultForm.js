/*
 * Front end behaviors for EditGlobalParameterForm
 */

var $osFamilyFormGroup = $('#div_id_os_family');
var $globalTargetField = $('#id_global_target');
var $form = $('form#action_form');

function showHideOSFamilyField(selected, $osFamilyFormGroup) {
  'use strict';

  $osFamilyFormGroup.addClass('hidden');

  if (selected === 'resources' || selected === 'all') {
    $osFamilyFormGroup.addClass('hidden');
    // $osFamilyField.hide();
  } else if (selected === 'servers') {
    $osFamilyFormGroup.removeClass('hidden');
  }
}

// First load; show/hide the OS Family field based on initial value
var initialGlobalTarget = $globalTargetField.children("option:selected").val();
showHideOSFamilyField(initialGlobalTarget, $osFamilyFormGroup);

$globalTargetField.on('change', function (e) {
  'use strict';
  var selected = $(this).children("option:selected").val();
  showHideOSFamilyField(selected, $osFamilyFormGroup);
});

