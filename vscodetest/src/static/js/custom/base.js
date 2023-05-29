/* Avoid 'console is not defined' errors in browsers that lack`console`.
 *
 * In IE8 for example,`console` doesn't exist until the dev tools are opened.
 *
 * This code was taken from the html5-boilerplate project:
 * https://github.com/h5bp/html5-boilerplate/blob/5bc2a985c74a1f854f7fc1ee8f8ce4639fe7cd67/js/plugins.js
 */
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());


function blockActionDialog(msg, selector) {
    var id = selector || '#action-dialog';
    c2.block.block($(id).parent('.ui-dialog'));
}
function unblockActionDialog(dialogId) {
    var id = dialogId || '#action-dialog';
    c2.block.unblock($(id).parent('.ui-dialog'));
}


function loadIframeDialogView(event) {
    /* Generic click handler for an action link/button.  Defines a dialog and
     * loads its contents from the action link's href URL.
     * Options to the jQuery UI Dialog, such as height, title, etc, may be
     * specified as data on the action link, keyed on by attaching them to the
     * clicked
     */
    'use strict';

    event.preventDefault();

    var $this = $(this);

    var options = {
        modal: true,
        // Resize the dialog to fit the iframe:
        height: "auto",
        width: "auto",
        // Unset the iframe's src attribute before closing to prevent the IE
        // bug referenced to below; this is needed in addition to those
        // measures. Using beforeClose to catch all possible ways a dialog is
        // closed (ESC, x, and cancel button).
        beforeClose: function (event, ui) {
          $dialog.find('iframe').attr('src', '');
        }
    };

    // data on the action button can specify extra options
    var extra_options = $this.data('dialog_options');
    if (extra_options) {
        options = $.extend(options, extra_options);
    }

    // clear the content of any previous dialogs
    var dialogId = '#action-dialog';
    $(dialogId).remove();
    var $dialog = $('<div id="' + dialogId.substring(1) +'"></div>');

    // The container div fixes an issue with the horizontal scroll bar
    // appearing unnecessarily.
    var $iframeContainer = $('<div class="iframe-container" width="100%"></div>');
    var $iframe = $('<iframe width="100%" height="100%" iframeborder="0" class="seamless" scrolling="no" />');

    $iframeContainer.append($iframe);
    $dialog.append($iframeContainer);
    $('body').append($dialog);

    $dialog.dialog(options);

    // We set the iframe's ``src`` *after* the iframe is in it's final position
    // in the DOM to avoid triggering an issue with IE9+ where the frame does
    // not have access to the DOM api. If ``src`` was set before the frame was
    // in the DOM, scripts inside that frame would fail. Sources:
    // StackOverflow question: http://stackoverflow.com/questions/8389261/ie9-throws-exceptions-when-loading-scripts-in-iframe-why
    // MSDN article describing iframe behavior: http://msdn.microsoft.com/en-us/library/gg622929%28v=VS.85%29.aspx?ppud=4
    // Note there is another fix for this very same bug in the beforeClose event handler.
    var href = $this.attr('href');
    $iframe[0].src = href;

    if (typeof options.wait_msg != 'undefined') {
        blockActionDialog(options.wait_msg);
    } else {
        blockActionDialog();
    }

    $iframe.load(function () {
        unblockActionDialog(dialogId);

        var $iframeBody = $('iframe').contents().find('body');
        $dialog.dialog("option", "width", $iframeBody.width() + 70);
        $dialog.dialog("option", "height", $iframeBody.height() + 70);
        $dialog.dialog("option", "position", "center");
        // NOTE: this is the initial size of the iframe and dialog. If the
        // user resizes the dialog, the iframe will be resized with it.

        // Make the iframe as tall as its contents, so that the scroll bars
        // show up properly in the dialog:
        $('.iframe-container').height($iframeBody.height());
    });

    $dialog.on("dialogresize", function () {
        // Make the iframe as tall as its contents, so that the scroll bars
        // show up properly in the dialog:
        var $iframeBody = $('iframe').contents().find('body');
        $('.iframe-container').height($iframeBody.height());
    });
}

/* Called by the iframe dialog view's JavaScript: */
close_dialog = function() {
    var $dialog = $('#action-dialog');
    // trigger the beforeClose handler defined above
    $dialog.dialog('close');
    $dialog.dialog('destroy');
};


function ignore_enter_key(event) {
    var enterkeys = new Array(13, 14);
    if ($.inArray(event.which, enterkeys) > -1) {
        event.preventDefault();
        return false;
    }
}


// Extract all selected rows from a dataTable and return val() of
// their input.selector element.
function convertSelectedRowsToCSVInputField(dataTableId, inputName) {
    var values = $(dataTableId).$("tr.selected")
        .find("input.selector")
        .map(function(index) {
            return $(this).val();
        }).toArray();
    return values;
}


$(document).ready(function() {

    // Use delegation for these handlers so that dynamic content
    // gets the behavior automatically.
    $('body').on('click', '.open-iframe-dialog', loadIframeDialogView);

});
