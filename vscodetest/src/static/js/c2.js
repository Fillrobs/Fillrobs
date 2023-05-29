/* Global initialization functions
 *
 * This is the entry point for our app and is the first module concatenated into c2.js and
 * c2.min.js. Thus, any global configuration that other c2 modules depend on should be added
 * here at the module level so it can be executed immediately.
 */


/*
 * Global c2 object contains settings and will have all modules registered as members
 * once all c2.js code has executed.
 */
window.c2 = {

  /*
  * Global c2.settings
  */
  settings: {

    /*
     * Logging settings.
     * See c2.logging for more details.
     */
    logging: {
      // To enable console logging for a c2 module, add it to this list.  All c2 modules reside in
      // static_src/js/c2/.  Use the exported module name (which sometimes differs from the file
      // name), e.g.  'server'
      enabledModules: ['accessibility'],

      // Log level determines the importance of messages that are logged:
      //   debug: show debug, info, warning and error messages.
      //   info: show info, warning, and error messages.
      //   warn: show warnings and errors.
      //   errors are always logged when the module is enabled
      level: 'info'
    },
    urls: {}

  }

};


/*
 * This function is the entry point for our JavaScript.  It must be called from a Django template
 * that has the ability to inject these values.
 */
c2.go = function(
    CBLicenseID,
    mixpanelToken,
    CSRFToken,
    staticURL,
    loginURL,
    logoutURL,
    activityURL,
    detectTimeZone,
    timeoutMin) {

  c2.settings.CBLicenseID = CBLicenseID;
  c2.settings.mixpanelToken = mixpanelToken;
  c2.settings.CSRFToken = CSRFToken;
  c2.settings.urls.static = staticURL;
  c2.settings.urls.login = loginURL;
  c2.settings.urls.logout = logoutURL;
  c2.settings.urls.activity = activityURL;

  // Send a Django encrpytion token with every AJAX request
  $.ajaxPrefilter(function(options, originalOptions, jqXHR) {
    if (!options.crossDomain) {
      // only set token on same-domain requests to avoid leaking it to 3rd parties
      jqXHR.setRequestHeader('X-CSRFToken', CSRFToken);
    }
  });

  /*
   * Set up global handler for when any AJAX call using $.get, $.post, $getJSON, etc. gets a
   * response that indicates Maintenance Mode is on.
   *
   * Trouble is knowing what's the best thing to do for each situation:
   * - fail silently?
   * - show an error in the page?
   * - redirect the entire page, forcing the user to find their way back later?
   */
  /*  Stashed for now...

  $(document).ajaxComplete(function(e, xhr, settings) {
    if (xhr.responseText.indexOf('Maintenance Mode') != -1) {
      console.error('Maintenance Mode is on.');

      // While redirecting the entire page does result in the maintenance mode page being
      // displayed, it's too unkind to users.
      // window.location.replace(window.location);

      // Gently informing them of it's temporal nature is probably best.
      c2.alerts.addGlobalAlert('Looks like CB is in maintenance mode. Try again in a few minutes.', 'warning');
    }
  });

  */

  $.ajaxSetup({
    // Global error handler that redirects the whole page to the login page if the session is expired:
    // See https://cloudbolt.atlassian.net/browse/DEV-194
    //
    // NOTE: If the .ajax() calls contain another error handler, then BOTH that
    // handler and this global handler will be called.
    //
    // Unfortunately, this does not apply to $.get or $.post calls, which
    // bypass use of jqXHR; we may want to move to using $.ajax everywhere.
    error: function(data) {
      console.log('    Ajax error occurred:', data);

      if( data.status == 401 ) {
        console.log('    401: session expired. Redirect to log in page.');
        window.location.replace(
          loginURL + "?next=" + encodeURI(window.location.pathname)
        );
      }
    }
  });

  function handleInactivity() {
      window.location.href = logoutURL + '?inactivity-timeout-minutes=' + timeoutMin;
  }

  if (timeoutMin) {
    c2.inactivity.init(timeoutMin, handleInactivity, activityURL);
  }

  if (detectTimeZone) {
    var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    // All modern browsers support the new Internationalization API; ignore otherwise.
    if (tz !== undefined) {
      $.post('/detect_time_zone', {tz: tz});
    }
  }
};


/*
 * Global initializations that run on document load.
 */
$(function () {
  'use strict';

  c2.accessibility.init();
  c2.include.loadAll();
  c2.navbar.init();
  c2.dataTables.init();
  c2.dialogs.init();
  c2.toggles.enablePostOnChange();
  c2.commonEventHandlers.enablePostOnClick();
  c2.commonEventHandlers.aceOnPanelOpen();
  c2.commonEventHandlers.popovers();
  c2.search.init();
  c2.sparklines.init();
  c2.tabs.init();
  c2.tooltip.init();
  c2.clipboard.init();

  // Customers may completely disable mixpanel by assigning settings.MIXPANEL_TOKEN = ''
  if (c2.settings.mixpanelToken !== '') {
    c2.mixpanel.init();
  }

  // Call this after other modules have initialized to give them a chance to
  // register event handlers
  c2.commonEventHandlers.bindGlobalKeyHandlers();

  // Dialogs are initialized in ./dialogs.js

  // Bootstrap datepicker
  $.fn.datepicker.defaults.autoclose = true;
  $.fn.datepicker.defaults.format = "yyyy-mm-dd";
  $.fn.datepicker.defaults.todayBtn = true;
  $.fn.datepicker.defaults.todayHighlight = true;
});

/*
 * Client side logging framework
 *
 * Conditionally logs messages to the console depending on c2.settings.  Lets
 * us write useful permanent log messages into our front end modules that only
 * actually log when configured to do so.
 *
 * Add logging statements to your c2 modules:
 *
 *   var logger = c2.logging.getLogger('server');
 *   logger.debug('this is logged for log level "debug" only');
 *   logger.info('this is logged for log levels "info" and "debug"');
 *   logger.warn('this is logged for log levels "warn" and lower');
 *   logger.error('this should be logged no matter what the log level');
 *
 * Logging for a particular module is enabled by registering it on the c2.settings object in
 * c2.init. For example, to enable the 'c2.include' module:
 *
 *   c2.settings.logging.enabledModules.push('include');
 *
 */

(function (__module__, c2, $) {
  'use strict';

  /*
   * Convert an arguments object into a true array
   */
  function toArray(origArguments) {
    return Array.prototype.slice.call(origArguments, 0);
  }


  /*
   * Returns an object that has various logging methods that log based on logLevel.
   *
   * All messages using this logger include the name of the module that emitted the message, like
   * 'c2.server: '.
   */
  function loggerEnabled(moduleName) {
    var logLevel = c2.settings.logging.level;
    var prefix = moduleName + ': ';

    return {
      // These functions use `apply` to pass arbitrary number of args on to console.log, like
      // unpacking an array in Python via *args.

      // Log messages if the log level is debug
      debug: function () {
        if (logLevel == 'debug') {
          console.log.apply(console, [prefix].concat(toArray(arguments)));
        }
      },

      // Log messages if the log level is info or lower
      info: function () {
        if (logLevel == 'info' || logLevel == 'debug') {
          console.info.apply(console, [prefix].concat(toArray(arguments)));
        }
      },

      // Log warnings if the log level is warn or lower
      warn: function () {
        if (logLevel == 'warn' || logLevel == 'info' || logLevel == 'debug') {
          console.warn.apply(console, [prefix].concat(toArray(arguments)));
        }
      },

      // Always log errors and use console.error() instead
      error: function () {
        console.error.apply(console, [prefix].concat(toArray(arguments)));
      }
    };
  }


  /*
   * Returns an object that has various logging methods that do nothing.
   */
  function loggerDisabled() {
    return {
      debug: function () {},
      info: function () {},
      // Should warnings be logged even when a module isn't enabled?
      warn: function () {},
      // Should errors be logged even when a module isn't enabled?
      error: function () {}
    };
  }


  /*
   * Return a logger object that only logs to console when this module is configured for it.
   * Otherwise, returns a no-op function.
   *
   * Modules are enabled to log messages in c2.init, where the c2.settings.logging object is
   * defined. If enabledModules list contains 'all', logging is enabled for all modules.
   */
  function getLogger(moduleName) {
    if (c2.settings.logging.enabledModules) {
      if (c2.settings.logging.enabledModules.indexOf('all') != -1 ||
          c2.settings.logging.enabledModules.indexOf(moduleName) != -1) {
        return loggerEnabled(moduleName);
      }
    }

    return loggerDisabled();
  }


  c2[__module__] = {
    getLogger: getLogger
  };
})('logging', window.c2, window.jQuery);

/*
 * jquery.clearable.js
 *
 * jQuery plugin adds a clickable widget to a text input for easy clearing of
 * its value. To clear the input, the user may hit Escape while the input is
 * focused, or click on the clearable trigger icon/span.
 *
 * Options:
 *   inputClass: CSS class applied to the input field.
 *               Default 'clearable'.
 *   triggerHtml: Markup of trigger icon or control.
 *               Default '<span class="icon-delete"></span>'
 *
 * Usage:
 *
 *     <input name="thing" type="text"/>
 *     <script>
 *       $('input[name=thing]').clearable();
 *     </script>
 *
 * Result:
 *
 *     <input class="clearable" name="thing" type="text"/>
 *     <span class="clearable-trigger"><span class="icon-delete"></span></span>
 */

(function ($) {
  'use strict';

  $.fn.clearable = function (userOptions) {
    var options = $.extend({}, defaults, userOptions);

    /* Insert the clickable trigger next to the input and hide or show it as
     * needed.
     */
    function addTrigger($input) {
      var $trigger;
      var $parent = $input.parent();
      $input.addClass(options.inputClass);

      // Need input and trigger to be inside a .clearable-wrapper for
      // correct positioning of the trigger. However, Bootstrap input-group
      // layout breaks if the input is not its child. For that special case,
      // wrap the parent of the input instead.
      if ($parent.hasClass('input-group')) {
        $parent.wrap('<span class="clearable-wrapper"></span>');
      } else {
        $input.wrap('<span class="clearable-wrapper"></span>');
      }

      $trigger = $('<span class="clearable-trigger">'+ options.triggerHtml +'</span>');
      // place the trigger immediately after the input
      $input.after($trigger);

      hideOrShowTrigger($input);

      // Clear input value and ensure its event handlers fire
      $trigger.click(function (e) {
        clear($input);
      });
    }

    /* Event handler for input element changes */
    function hideOrShowTrigger($input) {
      var $trigger = $input.next();
      if ($input.val()) {
        $trigger.show();
      } else {
        $trigger.hide();
      }
    }

    function clear($input) {
      $input
        .trigger('keydown')
        .val('')
        .trigger('keyup')
        .trigger('change')
        .focus();
    }

    return this.each(function () {
      var $input = $(this);
      if ($input.hasClass(options.inputClass)) {
        // this input is already clearable
        return;
      }

      addTrigger($input);

      $input.keyup(function (e) {
        hideOrShowTrigger($input);

        // Clear the input value when user hits Escape key on the input
        if (e.key == 'Escape') {
          clear($input);
          e.stopPropagation();
        }
      });
    });
  };

  var defaults = {
    inputClass: 'clearable',
    triggerHtml: '<span class="icon-delete"></span>'
  };

})(jQuery);

/*
 * jQuery clickable plugin 
 *
 * Author: Thomas Hamlin, Chris Mitchell
 *
 * Makes checkboxes in lists or tables clickable toggled by clicks on their
 * containing list elements or table rows: 
 *     - clicks on <li> or <tr> elements toggles any checkboxes in that element.
 *     - can be given a strategy to make other things 'clickable'
 *     - allows for selecting multiple items with click, shift-click.
 */

(function ($) {
    'use strict';

    $.fn.clickable = function (userOptions) {
        var options = $.extend({}, defaults, userOptions);

        return this.each(function () {
            var $container = $(this).addClass(options.containerClass);
            var strategy;
            var $item, $items; // the clickable elements
            var $checkboxes; // all checkboxes; used for shift-select
            var $control, $target;

            // the last non shift-clicked box
            $container.data('prevBox', null);

            // choose strategy
            if (options.strategy) {
                strategy = options.strategy;
            } else {
                for (var strategyName in strategies) {
                    var candidate = strategies[strategyName];
                    if (candidate.isAppropriate($container)) {
                        strategy = candidate;
                        break;
                    }
                }
            }
            strategy = $.extend({}, strategies['default'], strategy);

            // find clickable items (rows in table or items in lists)
            $items = strategy.findItems($container);

            // clickable assumes each item has no more than one checkbox or
            // radio button. Let's check that assumption here so that we can
            // warn developers who breach this assumption
            $items.each(function () {
                $item = $(this);
                $control = $item.find('input:checkbox, input:radio');

                if ($control.length > 1) {
                    console.log("Warning: the clickable plugin's behavior is not well defined for items with more than one checkbox or radio button");
                    return;
                }

                // Highlight items whose input was checked before .clickable was called
                if ($control.prop('checked')) {
                    $item.addClass(options.selectedClass);
                }

            });

            // Allow this plugin to be idempotent (invoked multiple times on a
            // container without ill effects).  Avoids attaching event handlers
            // multiple times.
            $items.off('click.clickable');
            $items.on('click.clickable', function (e, data) {
                // Target is the item that the user clicked (e.g. a label for a checkbox, a TD)
                $target = $(e.target);

                // Ignore Alt-clicks and CMD-clicks completely
                if (e.altKey || e.metaKey || options.ignoreThisTarget($target)) {
                    return;
                }

                // Shift-clicking will often make text-selections. This removes
                // those selections. IE 8 doesn't support this.
                if (document.getSelection) {
                    document.getSelection().removeAllRanges();
                }

                if (strategy.isClickable($target)) {
                    handleClick(e, $items, $container, options);
                }
            });
        });
    };


    function handleClick(e, $allItems, $container, options) {
        // Item is the TR or LI to be highlighted when selected
        var $item = $(e.delegateTarget);
        // Find the checkbox/radio button that is in the clicked item:
        var $control = $item.find('input:radio, input:checkbox').first();
        var $target = $(e.target);
        var highlightClass = options.selectedClass;

        // a click in a radio set removes other selections
        if ($control.is(':radio')) {
            $allItems.removeClass(highlightClass);
        }

        // activate the input if the user didn't click on it
        if (! $target.is($control)) {
            $control.prop('checked', !$control.prop('checked'));
            $control.trigger('change');
        }

        var highlight = $control.prop('checked');
        $item.toggleClass(highlightClass, highlight);

        // shift-select behavior!
        var $prevBox = $container.data('prevBox');
        if ($control.is(':checkbox') && $prevBox && e.shiftKey) {
            // for shift-select
            var $checkboxes = $allItems.find('input[type=checkbox]:first');
            var idxA = $checkboxes.index($prevBox);
            var idxB = $checkboxes.index($control);
            var $controls = $checkboxes.slice(Math.min(idxA, idxB), Math.max(idxA, idxB));
            $controls.prop('checked', highlight);

            var $prevItem = $prevBox.closest($item[0].tagName);
            var start = $allItems.index($prevItem);
            var end = $allItems.index($item);
            var $affectedItems = $allItems.slice(Math.min(start, end), Math.max(start, end));
            $affectedItems.toggleClass(highlightClass, highlight);
        }
        $container.data('prevBox', $control);

        // fire callback
        options.onSelect(e, $container, $item);

        if ($target.is('label')) {
            // Fix an issue where if the user clicks on a label, it will
            // toggle back the checkbox:
            e.preventDefault();
        }
    }

    // Enables caller to reset shift-click behavior if needed.
    $.fn.clickable.forgetPrevClick = function ($container) {
        $container.data('prevBox', null);
    };

    var defaults = {
        containerClass: 'clickable',
        selectedClass: 'selected', // CSS class assigned to selected items (i.e. rows)

        // callback fires when an item is considered selected. This typically
        // happens when an item's checkbox is changed or other non-input
        // elements in the item are clicked. (eg. when a td in a tr item is
        // clicked)
        onSelect: function(e, $container, $item) {
        },

        // Users may specify a callback to determine if clicks on certain
        // targets should *not* cause the row to be selected.
        ignoreThisTarget: function ($target) {
          return false;
        },

        strategy: null
    };

    // Because the main clickable logic is the same (find clickable elements,
    // attach event handlers) but the details are different depending on the
    // type of container (eg. which items are considered clickable, which
    // aren't), we pull the details out into these strategies.
    var strategies = {
        // when another strategy doesn't define some behavior, the behavior in
        // this default strategy is used
        'default': {
            // Return true if this strategy is a good fit for the container.
            isAppropriate: function ($container) {
                return false; // default is a last-resort
            },

            // Return the items the user should be able to click on.
            findItems: function ($container) {
                return $container.children();
            },

            isClickable: function ($target) {
                // By default, checkboxes and everything else except for other
                // input-like elements trigger a selection change.

                // ':input' is a jQuery selector that matches input-related
                // elements: http://api.jquery.com/input-selector/
                return (
                    $target.is(':checkbox, :radio') ||
                    (!$target.is(':input, a') &&
                     !$target.parents('a').length &&
                     !$target.parents('label').length)
                );
            }
        },

        table: {
            isAppropriate: function ($container) {
                var tagName = $container.get(0).tagName;
                return tagName === 'TABLE';
            },
            findItems: function ($container) {
                return $container.find('tbody tr');
            }
        },

        list: {
            isAppropriate: function ($container) {
                var tagName = $container.get(0).tagName;
                return tagName === 'UL' || tagName === 'OL';
            },
            findItems: function ($container) {
                return $container.children('li');
            }
        }
    };
})(jQuery);

// Lightweight highlight effect without requiring jQuery UI
// Derived from http://stackoverflow.com/a/13106698
jQuery.fn.highlight = function(bgColor) {
  $(this).each(function() {
    var el = $(this);
    var offset = el.offset();
    $('<div/>')
      .width(el.outerWidth())
      .height(el.outerHeight())
      .css({
          "position": "absolute",
          "left": offset.left,
          "top": offset.top,
          "background-color": bgColor || "#ffff99",
          "opacity": ".5",
          "z-index": "9999999"
      }).appendTo('body').fadeOut(700).queue(function () {
        $(this).remove();
      });
  });
};

/* jQuery plugin to select an element's text.
  *
  * Based on code from a couple of SO's including this one:
  * http://codereview.stackexchange.com/questions/38089/select-text-with-just-one-click
  */
$.fn.selectText = function () {
  var range, selection;

  return $(this).each(function (index, el) {
    if (window.getSelection) {
      selection = window.getSelection();
      range = document.createRange();
      range.selectNodeContents(el);
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(range);
    } else if (document.selection) {
      range = document.body.createTextRange();
      range.moveToElementText(el);
      range.select();
    }
  });
};

/* AWSReservedInstances.js
 *
 * For scripts executed on the AWS Billing Tab to show and summarize reserved instance recommendations
 */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);

  function init(url, tableSelector, $container, $submitButton, $form) {

    function addSumTableFooter(tfoot, data, start, end, display, sum_col) {
        // Remove the formatting to get integer data for summation
        var intVal = function (i) {
            return typeof i === 'string' ?
                i.replace(/[\$,]/g, '')*1 :
                typeof i === 'number' ?
                    i : 0;
        };

        var total_savings = 0;
        for (var i=0; i<data.length; i++) {
          total_savings += intVal(data[i][sum_col]);
        }

        $(tfoot).find('th').eq(0).html("Total Estimated Savings: $" + total_savings.toFixed(2));
    }

    // Initial load of the recommendations summary + table
    // Add a loading icon and disable the submit button
    c2.block.block($container);
    $submitButton.prop('disabled', 'disabled');
    // Get the html for recommendations
    $.ajax({
        url: url,
        dataType: 'html',
        type: "GET",
        success: function (response) {
          $container.html(response);
          // Keep re-selecting the table - it's necessary because we've replaced the HTML and it is a new element.
          $(tableSelector).dataTable({
              "aaSorting": [[6, "desc"]],
              "footerCallback": function(tfoot, data, start, end, display) {
                  addSumTableFooter(tfoot, data, start, end, display, 6);
              }
          });
          c2.block.unblock($container);  // remove loading icon
          $submitButton.prop('disabled', '');
        },
        error: function (xhr, errmsg, err) {
          logger.debug('Error handling GET request: ' + xhr + '  ' + errmsg + '  ' + err);
          c2.block.unblock($container);  // remove loading icon
          $submitButton.prop('disabled', '');
        }
      });

    // When a user wants to get recommendations from new parameters using the form
    $submitButton.on('click', function(event) {
      event.preventDefault();

      c2.block.block($container, false);  // add a loading icon to the table to indicate it will change
      $submitButton.prop('disabled', 'disabled');

      var formData = $form.serializeArray();

      $.ajax({
          url: url,
          dataType: 'html',
          type: "POST",
          data: formData,
          success: function (response) {
            $(tableSelector).DataTable().clear().destroy();
            $container.html(response);
            // Keep re-selecting the table - it's necessary because we've replaced the HTML and it is a new element.
            $(tableSelector).dataTable({
                "aaSorting": [[6, "desc"]],
                "footerCallback": function(tfoot, data, start, end, display) {
                    addSumTableFooter(tfoot, data, start, end, display, 6);
                }
            });
            c2.block.unblock($container);  // remove loading icon
            $submitButton.prop('disabled', '');
          },
          error: function (xhr, errmsg, err) {
            logger.debug('Error handling POST request: ' + xhr + '  ' + errmsg + '  ' + err);
            c2.block.unblock($container);  // remove loading icon
            $submitButton.prop('disabled', '');
          }
        });

    });

  }

  c2[__module__] = {
    init: init
  };

})('AWSReservedInstances');




(function(__module__) {

  var logger = c2.logging.getLogger(__module__);

  /*
   * Initialize features that enhance accessibility of the UI.
   */
  function init() {
    var keyHandlers = {
      '?': openHelpDialog,
      h: openHelpDialog
    };
    keyHandlers = addDocsKeyHandler(keyHandlers);

    c2.commonEventHandlers.registerGlobalKeyHandlers('accessibility', keyHandlers);

    focusPageLinkTargetsManually();

    setTimeout(function() {
      alertAll();
    }, 1000);
  }


  /**
   * Find all elements on the page that want to be announced by a screen reader. Each should have a
   * `data-alert=true` attribute. This works regardless of where keyboard focus is. For an ideal
   * user experience, there is only one such element.
   *
   * Once an element has been announced, its data-alert is set to false so it won't be announced
   * again by subsequent calls.
   */
  function alertAll() {
    $('[data-alert=true]').each(function() {
      var $visible = $(this);
      alert($visible.text());
      $visible.attr('data-alert', false);
    });
  }


  /*
   * Create a screen reader alert by inserting a hidden message into the DOM with special ARIA
   * attributes.
   */
  function alert(message) {
    var $alert = $('<div class="sr-only" role="alert" aria-live="assertive"></div>');
    $alert.text(message).appendTo('body');
  }


  /*
   * Add a global key shortcut for opening docs, but only if the link is currently visible.  Some
   * customers hide this link completely in customer.css for whitelabeling or other reasons.
   *
   * The global help dialog hides this shortcut key using the same logic: if the help link is
   * not visible, that shortcut is simply not shown.
   */
  function addDocsKeyHandler(keyHandlers) {
    var link = '[data-topnav="help"] a.help-link';
    if ($(link).is(':visible')) {
      keyHandlers.d = function(e) {
        // Unsure why, but to actually click this we must access the DOM element
        $(link).first()[0].click();
        e.preventDefault();
      };
    }
    return keyHandlers;
  }


  /*
    * For links targeting content on the page, use JavaScript to focus the target element on
    * click. This fixes the limitation of some browsers which do not shift the tabindex position
    * to the target (so the next Tab key would visit the next element after the link). By focusing
    * the element explicitly, the Tab key will navigate from the target onward as intended.
    *
    * https://www.bignerdranch.com/blog/web-accessibility-skip-navigation-links/
    */
  function focusPageLinkTargetsManually() {
    $('a[href^="#"]').on('click', function(e) {
      var targetId = this.href.split('#')[1];
      if (!targetId) {
        // This link's target is just '#' so nothing to do
        return;
      }

      // Before some elements (div, span, etc) can be programmatically focused, they must have a
      // tabindex attribute set.  Here we give the target a temporary 'no-op' tabindex.
      $('#' + targetId).attr('tabindex', -1).on('blur focusout', function() {
        // Remove the temporary tabindex as soon as user leaves it
        $(this).removeAttr('tabindex');
      })
      // Now focus the element which moves the tabbing position
      .focus()
      // No need to keep focus. Calling this removes the blue outline around the content div.
      .blur();
    });
  }


  function openHelpDialog(e) {
    // This link is always present in the footer, just not visible except to screen readers
    $('#global-help-dialog').trigger('click');
    e.preventDefault();
  }


  c2[__module__] = {
    alert: alert,
    alertAll: alertAll,
    init: init
  };
})('accessibility');

// Ace code editor

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);
  var langTools = ace.require("ace/ext/language_tools");
  var newline = String.fromCharCode(10);
  var powershellHeader = "# PowerShell doesn't need a shebang since CB'll append a .ps1 file extension.";
  var defaultLangs = [
    {caption: 'SH', name: 'sh'},
    {caption: 'Go', name: 'golang'},
    {caption: 'Perl', name: 'perl'},
    {caption: 'Powershell', name: 'powershell'},
    {caption: 'Python', name: 'python'},
    {caption: 'Ruby', name: 'ruby'}
  ];


    /**
     * Ajax call to send code edited inside an ace editor as POST. Takes the id for the hook, the id for the editor,
     * and the edited code.
     */
    function saveUpdatedCode(hook_id, editor_id, edited_code) {
        $.ajax({
            url: '/actions/' + hook_id + '/edit_code/',
            type: 'POST',
            data: {"file_content": edited_code},
            success: function (response) {
                //  Disable the "save code" button since code has already been saved
                $('#' + editor_id + '-save_button').attr("disabled", true);
                $('#' + editor_id + '-save_button').text("Saved!");
                //  Enable the "show out-out-of-box code" and "revert changes" buttons without refreshing page
                $('#' + editor_id + '-revert-code').removeClass("hidden");
                $('#' + editor_id + '-show_ootb_link').removeClass('disabled');
                $('#' + editor_id + '-show_ootb_link').css('cursor', 'pointer');
                $('#' + editor_id + '-show_ootb_link').off("click");
                $('#' + editor_id + '-show_ootb_link').click(function () {
                    c2.ace.toggleOotbCode('#action-source-code-' + editor_id)
                });
                $('#' + editor_id + '-show_ootb_link').attr('data-original-title', 'yourText');
                //  Confirm success
                c2.alerts.addGlobalAlert(response, 'success', true);
            },
            error: function (jqXHR) {
                c2.alerts.addGlobalAlert(jqXHR.responseText, 'error', true);
            }
        });
    }


  /**
   * If a panel contains a textarea with class "ace-lg", an Ace editor will be
   * instantiated (but only once).
   */
  function initializeAceInPanel($panelBody) {
    var $textarea;

    $panelBody.find('textarea.ace-lg').each(function() {
      $textarea = $(this);

      // Only initialize Ace once
      if ($textarea.data('aceInitialized')) {
        return;
      }
      $textarea.data('aceInitialized', true);

      var editor_id = $textarea.attr('id');
      var hook_id = $textarea.attr('hook_id');
      var edited_code = null;


      //   * if there is a save button (which only happens if permissions are appropriate),
      //   * set up the event listeners to make the Ace editor options
        if ($('#' + editor_id + '-save_button').length > 0) {
            var editor = c2.ace.init(editor_id, {
                aceOptions: {
                    readOnly: false
                }
            });
          // * if code is editable, i.e. not the out-of-the-box comparison code,
          // *set up the ace dropdown language preferences and snippets
            if (editor_id.indexOf('ootb') == -1) {
                setupLanguages(editor)
                setupSnippets(editor)
            }
            // set up event listener that enables save button and updates edited_code if code is changed
            editor.on("change", function (e) {
                edited_code = editor.getValue();
                $('#' + editor_id + '-save_button').attr("disabled", false)
                $('#' + editor_id + '-save_button').text('Save Code')
            });
            //  "Save Code" button sends all necessary info the the saveUpdatedCode function
            $('#' + editor_id + '-save_button').click(function () {
                saveUpdatedCode(hook_id, editor_id, edited_code)
            })
        } else {
            c2.ace.init(editor_id, {
                aceOptions: {
                    readOnly: true
                }
            });
        }
    });
  }

  /* Initialize an editor
     editorID: required ID
     options:
         aceOptions: passed directly to Ace
           theme: string for the theme to use (default 'ace/theme/chrome')
           language: initial language (default 'ace/mode/python')
         compact: if true, remove line numbers, gutter, etc.
         oneLine: constrain editor to one line; prevent newlines.
         cursorAtStart: bool, place cursor at start (default) or end of content
     initialContent: optional content. If not specified, contents of the editor
         element will be used.
  */
  function init(editorID, options, initialContent) {
    var baseId = editorID || 'editor';
    var $editor = $('#' + baseId);
    // If $editor is a textarea or input field:
    var value_by_val = $editor.val && $editor.val();
    // If $editor is a non-form-field such as a div:
    var value_by_html = $editor.html && $editor.html();
    initialContent = (initialContent || value_by_val || value_by_html || "").trim();

    options = options || {};
    var compactMode = options.compact || false;
    var oneLineMode = options.oneLine || false;

    // Bool option defaults to true
    var cursorAtStart = (options.curstorAtStart === undefined) ? true : options.cursorAtStart;
    var cursorLoc = cursorAtStart ? 1 : -1;
    var aceOptions = _.defaults(options.aceOptions || {}, {
      enableBasicAutocompletion: true,
      mode: 'ace/mode/python',
      theme: 'ace/theme/chrome'
    });

    if (compactMode) {
      aceOptions.showPrintMargin = false;
      aceOptions.showGutter = false;
    }

    if (oneLineMode) {
      aceOptions.highlightActiveLine = false;
      // Remove new lines from initial content
      initialContent = initialContent.replace(/[\r\n]/g, '');
    }

    logger.debug('Initializing editor #'+baseId+' with aceOptions ', aceOptions);
    var editor = ace.edit(baseId);

    // Annotate the Ace editor object so other functions have access to these
    editor.id = baseId;
    editor.oneLineMode = oneLineMode;

    editor.setOptions(aceOptions);

    // Prevent deprecation warning message in console
    editor.$blockScrolling = Infinity;

    editor.setWrapBehavioursEnabled(false);

    if (oneLineMode) {
      // Set up a change handler that strips newlines as they're inserted
      // (by typing or pasting).  This must be set up before the `setValue`
      // call below which may introduce newlines too.
      editor.getSession().on('change', replaceNewlines(editor));
    }

    editor.setValue(initialContent, cursorLoc);

    return editor;
  }


  /* Return an event handler that essentially ignores newline characters typed
   * by the user.  The cursor goes to the end of the line if a newline is typed
   * anywhere.
   */
  function replaceNewlines(editor) {
    return function (e) {
      if (e.action == 'insert') {
        var val = editor.getValue();
        // Use plain js string search to look for newlines, as `find` always
        // returns a range and is harder to work with
        if (val.search(newline) != -1) {
          // Set needle so it can be replaced
          editor.find(newline);
          editor.replaceAll('');
        }
      }
    };
  }


  /* Set up two dropdowns that aid user in inserting snippets for CB objects
   * and attributes, such as "{{ server.hostname }}".
   */
  function setupSnippets(editor) {
    var selId1 = '#' + editor.id + '-objects';
    var selId2 = '#' + editor.id + '-attrs';
    var $objects = $(selId1);
    var $attrs = $(selId2);

    c2.combobox.chain(
      selId1, selId2,
      // URL to fetch options for 2nd select
      '/context_attrs_for_object/<%=value%>/',
      // Selectize 1 options
      {
        allowEmptyOption: false,
        // By default, plugins includes selectable placeholder but we don't
        // want that here
        plugins: {}
      },
      // Selectize 2 options
      {
        valueField: 'value',
        labelField: 'label'
      }
    );

    $attrs.on('change', function() {
      if (editor.oneLineMode) {
        // Prevent infinite loop from change handler
        editor.getSession().off('change');
      }

      // The 2nd dropdown actually contains the full snippet
      editor.insertSnippet($attrs.val());

      if (editor.oneLineMode) {
        // Restore change handler
        editor.getSession().on('change', replaceNewlines);
      }

      // Reset both dropdowns to empty values and remove options from the 2nd
      $objects[0].selectize.setValue('');
      var attrSelectize = $attrs[0].selectize;
      attrSelectize.setValue('');
      attrSelectize.disable();
      attrSelectize.clearOptions();

      // Take focus off dropdown and back where cursor is
      editor.focus();
      // Let user type; without this the text is selected and cursor won't move
      editor.setReadOnly(false);
    });
  }


  function setupLanguages(editor, language, defaultToPowershell) {
    language = language || 'ace/mode/python';
    defaultToPowershell = defaultToPowershell || false;
    editor.getSession().setMode(language);

    var otherLangs = document.getElementById(editor.id + '-other-langs');
    var langSelect = document.getElementById(editor.id + '-language');

    otherLangs.addEventListener('change', function() { buildLangSelect(editor, langSelect, otherLangs); });
    langSelect.addEventListener('change', function() { updateSelects(editor, langSelect); }, true);

    setLangs(langSelect, defaultLangs);

    // Make Powershell the default selection if requested (AKA if Windows)
    if (editor.getValue() === "") {
      // Set "shebang" and move cursor to end of it (2nd arg to setValue)
      if (defaultToPowershell) {
        setSelectOption(langSelect, 'powershell');
        editor.setValue(powershellHeader, 1);
      } else {
        // Provide a default for the user's shebang for new scripts.
        editor.setValue("#!/usr/bin/env bash\n", 1);
      }
    }
  }


  function updateSelects(editor, select) {
    var language = "ace/mode/" + select.value;
    var cursorPos, firstLine;

    // Do nothing with shebang if the editor already had code in it.
    if (editor.getValue() !== '') {
      var header = "";
      if (header) {
        cursorPos = editor.getCursorPosition();
        firstLine = editor.getValue().split("\n")[0];
        var first_line_header = firstLine.startsWith("#!") || firstLine.startsWith(powershellHeader);
        if (first_line_header) {
          editor.moveCursorToPosition({row: 0, column: 0});
          editor.removeToLineEnd();
          editor.moveCursorToPosition({row: 0, column: 0});
          editor.insert(header);
        } else {
          editor.moveCursorToPosition({row: 0, column: 0});
          editor.insert(header + "\n");
        }
        editor.moveCursorToPosition(cursorPos);
      }

    }
    editor.getSession().setMode(language);
    logger.debug("Set editor " + editor.id + " mode to: "+language);
  }

  function removeSelectOptions(elem) {
    var i;
    for(i=elem.options.length-1;i>=0;i--) {
      elem.remove(i);
    }
  }

  function setSelectOption(elem, val) {
    var opts = elem.options;
    for(var opt, j = 0; opt = opts[j]; j++) {
      if(opt.value == val) {
        elem.selectedIndex = j;
        break;
      }
    }
  }

  function setLangs(elem, langs) {
    var oldLen = elem.length;
    var lang, lastSelected;

    if (oldLen) {
      lastSelected = elem.value;
      removeSelectOptions(elem);
    }
    for (lang in langs) {
      var option = document.createElement("option");
      option.text = langs[lang].caption;
      option.value = langs[lang].name;
      elem.add(option);
    }
    if (oldLen) {
      setSelectOption(elem, lastSelected);
    }
  }

  function buildLangSelect(editor, select, checkbox) {
    if (checkbox.checked === true) {
      var modelist = ace.require("ace/ext/modelist");
      setLangs(select, modelist.modes);
    } else {
      setLangs(select, defaultLangs);
    }
    updateSelects(editor, select);
  }

  function toggleOotbCode(container_id) {
    var $container = $(container_id);
    var $label = $container.find('.show-or-hide');
    var $row = $container.find('.source-code-row');
    var $cols = $row.children('div');

    // Change the link wording, then make the OOTB code show/hide and be pretty
    if ($label.text() === 'Show') {
      $label.text('Hide');

      $row.addClass('row');
      $cols.addClass('col-sm-6');
      // The label on the current code (1st div) also needs to be shown
      $cols.first().children('h5').first().show();
      // The actual OOTB code part is the last div
      $cols.last().show();
    } else {
      $label.text('Show');

      $row.removeClass('row');
      $cols.removeClass('col-sm-6');
      $cols.first().children('h5').first().hide();
      $cols.last().hide();
    }
  }

  function autoHeightAceInModal(modalId) {
    var modalId = '#'+ (modalId || 'dialog-modal')

    // For when a modal is already opened and transitions to a page
    // with the ace editor
    calcAndSetHeight();

    // For when a modal is just being opened to trigger after opening
    $(modalId).on('shown.bs.modal', function() {
      calcAndSetHeight();
    });

    function calcAndSetHeight() {
      var $modalDialog = $(".modal-dialog");
      var $aceEditor = $modalDialog.find(".ace_editor");
      if (!$aceEditor.length) {
        return;
      }
      var newHeight = $modalDialog.height() - $aceEditor.height();
      $aceEditor.css({
        "height": "calc(100vh - " + newHeight + "px - 4rem)",
        "min-height": "12rem",
      });
    }
  }

  c2[__module__] = {
    init: init,
    initializeAceInPanel: initializeAceInPanel,
    autoHeightAceInModal: autoHeightAceInModal,
    saveUpdatedCode: saveUpdatedCode,
    addCompleter: langTools.addCompleter,
    setupLanguages: setupLanguages,
    setupSnippets: setupSnippets,
    toggleOotbCode: toggleOotbCode
  };

})('ace');

/* alerts.js
 *
 * Tools for creating and working with user notifications.
 */

(function (__module__) {
  'use strict';

  // Array of messages to prevent duplicates from being shown
  var alreadyAddedMessages = [];
  var logger = c2.logging.getLogger(__module__);

  /* Private methods */

  // Convert Django's messages framework tags to Bootstrap's alert classes.
  // Need to determine if tags may have multiple statuses.
  function toAlertClass(tags) {
    if (tags === 'error') {
      return 'alert-danger';
    }
    // success, info, and warning need no translation
    return 'alert-'+ tags;
  }

  /* Public methods */

  /* Adds message as a Django messages notification, but
   * prevents duplicate messages (having exactly same string content).
   */
  function addGlobalAlert(msg, tags, dismissable, dismissMilliseconds) {
    var alertClasses = "alert ",
        dismiss = "",
        $message;
    var $box = $('#alert-box');

    if (dismissable === true) {
      alertClasses += "alert-dismissable";

      // TODO: dismiss button does not remove the msg from alreadyAddedMessages, preventing it
      // from being shown again on the same page.
      dismiss = '<button type="button" class="close" data-dismiss="alert" ' +
        ' title="Dismiss this notification"><i class="fas fa-times"></i></button>';
    }

    if (alreadyAddedMessages.indexOf(msg) == -1) {
      logger.debug('Alert msg: ' + msg);
      alreadyAddedMessages.push(msg);

      $message = $('<div class="'+ alertClasses +' '+ toAlertClass(tags) +'">'+ dismiss + msg +'</div>');
      $message.hide();
      // Add messages in reverse-chronological order to #alert-box.
      $box.prepend($message);

      // Simultaneously fade in and slide down
      $message
        .css('opacity', 0)
        .slideDown(400)
        .animate(
          { opacity: 1 },
          { queue: false, duration: 400 }
        );

      // Because these messages are faded in, screen readers don't recognize them even with the
      // aria-live and role attributes. Instead, call a function that creates a new invisible DOM
      // element to be read aloud. Didn't work without a slight delay.
      setTimeout(function() {
        c2.accessibility.alert(msg);
      }, 100);
    }

    if (dismissMilliseconds) {
      setTimeout(clearGlobalAlerts, dismissMilliseconds);
    }
  }


  function clearGlobalAlerts() {
    var $box = $('#alert-box');
    var $msg;

    alreadyAddedMessages = [];
    $box.find('div.alert').each(function () {
      $msg = $(this);

      $msg.fadeOut(1000, function () {
        // remove content once fade animation ends
        $msg.remove();
      });
    });
  }


  c2[__module__] = {
    addGlobalAlert: addGlobalAlert,
    clearGlobalAlerts: clearGlobalAlerts
  };
})('alerts');

(function (c2) {
  'use strict';

  function isSupported() {
    var supported = false;
    var testElement = document.getElementsByTagName('body')[0];
    var domPrefixes = 'Webkit Moz O ms Khtml'.split(' ');

    if (testElement.style.animationName !== undefined) {
      supported = true;
    }

    if (supported === false) {
      for (var i = 0; i < domPrefixes.length; i++) {
        if (testElement.style[domPrefixes[i] + 'AnimationName'] !== undefined) {
          supported = true;
          break;
        }
      }
    }

    return supported;
  }

  c2.animation = {
    isSupported: isSupported
  };
})(window.c2);

// Block and unblock UI elements with a spinner. Useful to prevent user interaction while loading content.

(function (c2) {
  'use strict';

  // Generic wrapper for spinner blocks
  var blockerHtml = '' +
    '<div class="blocker fade">' +
    '  <div class="dead-center-container">' +
    '    <div class="dead-center-content">' +
    '    </div>' +
    '  </div>' +
    '</div>';

  function block (el, useInlineCss) {
    var blockingPage = el === undefined;

    var $el = $(blockingPage ? 'body' : el);

    // get or create the blocker element
    var $blocker = $el.find('> .blocker');
    if ($blocker.length === 0) {
      $blocker = $(blockerHtml).appendTo($el);
    }

    var $blockContainer =  $blocker.find('.dead-center-content');
    var innerHtml;
    if (!useInlineCss) {
      // default to spinner image, more at spinners.less
      innerHtml = '<div class="spinner"></div>';
    } else {
      // Use inline css based blocker, each div is a dot.  More in portals.css.
      // It needs to be in portals,css 'cause the bg-color is dynamic based on menu hover color
      innerHtml = '' +
          '<div class="spinner-inline">' +
          '  <div></div>' +
          '  <div></div>' +
          '  <div></div>' +
          '  <div></div>' +
          '  <div></div>' +
          '</div>';
    }

    $blockContainer.html(innerHtml);

    if (blockingPage) {
      $blocker.css({position: "fixed"});
    } else {
      // give element styles required by .blocker
      $el.css({
        position: "relative",
        overflow: "hidden"
      });
    }

    reflow();
    $blocker.addClass('in');
  }

  function unblock(el) {
    var $el = $(el || 'body');
    var $blocker = $el.find('> .blocker');
    $blocker.removeClass('in');
  }

  /**
   * Force the browser to reflow.
   *
   * Useful for showing a CSS transition from state A to state B (think of a
   * state as some set of applied classes in the DOM). Apply state A, reflow,
   * then apply state B to see the transition. Without reflowing, state A never
   * participates in CSS transitions because it was replaced by state B before
   * the CPU is given to the browser to render.
   */
  function reflow() {
    return document.body.offsetWidth;
  }

  c2.block = {
    block: block,
    unblock: unblock
  };
})(window.c2);

/* Catalog filters and related behaviors
 */

(function (__module__) {
  'use strict';

  var $blueprintCards;
  var blueprintDataByID = {};
  var groupSelectize;
  var envSelectize;
  var labelSelectize;
  var searchField;
  var $byOSFamily;
  var groupNamesByID;
  var envNamesByID;
  var labelNamesByID;
  var shuffle;
  var logger = c2.logging.getLogger(__module__);


  /**
   * Initialize Catalog page behaviors.
   */
  function initCatalog(filterData) {
    var $blueprints = $('#blueprint-list');
    var $cards = $('.blueprint-card');

    c2.buttonTabs.init();
    c2.blueprints.initFilters($cards, filterData);
    $('#catalog-filters').fadeIn();
    c2.blueprints.handleCardClicks($blueprints);
  }


  /**
   * Set up widgets and behaviors of list filters.
   *
   * Add an empty choice to each filter if there's more than one choice; each
   * selectize widget defines a placeholder like "Any group". This also allows
   * user to unfilter the view.
   */
  function initFilters($items, filterData) {
    // Save these for later
    $blueprintCards = $items;
    envNamesByID = filterData.env_names_by_id;
    groupNamesByID = filterData.group_names_by_id;
    labelNamesByID = filterData.label_names_by_id;

    groupSelectize = c2.selectize('select[name=filter_by_group]', {
      onChange: function(value) {
        filter();

        if (value) {
          updateEnvFilter();
          updateLabelFilter();
        }
      },
      options: filterData.group_options,
      placeholder: gettext('Any group')
    });

    envSelectize = c2.selectize('select[name=filter_by_env]', {
      onChange: function(value) {
        filter();

        if (value) {
          updateGroupFilter();
          updateLabelFilter();
        }
      },
      options: filterData.env_options,
      placeholder: gettext('Any environment')
    });

    labelSelectize = c2.selectizeMultiple('select[name=filter_by_label]', {
      onChange: function(value) {
        filter();

        if (value) {
          updateGroupFilter();
          updateEnvFilter();
        }
      },
      options: filterData.label_options,
      placeholder: gettext('Any label'),
      plugins: ['remove_button']
    });

    // If there are no labels in use by any blueprints, hide the filter but
    // keep it in the DOM so logic below doesn't need to be complicated needlessly.
    if (Object.keys(filterData.label_names_by_id).length === 0) {
      labelSelectize.$wrapper.hide();
    }

    searchField = $('input[name="text_search"]')
      .clearable()
      .on('keyup', filterDebounced);

    $byOSFamily = $('input[name=filter_by_os_family]').on('change', function(e) {
      var $button = $(this);

      // When user clicks an OS family button a second time, the filter is
      // removed but Bootstrap does not deactivate the button state. Do it
      // manually here.
      var $label = $button.closest('label');
      if ($label.hasClass('active')) {
        // Bootstrap always applies 'active' on click and that happens after
        // this click handler; so the class must be removed in a new execution
        // context to take effect just after Bootstrap's click handler.
        setTimeout(function () {
          $label.removeClass('active');
        }, 0);
      }

      filter();

      updateGroupFilter();
      updateEnvFilter();
      updateLabelFilter();
    });

    $('#showing-msg').on('click', '#clear-filters', clearFilters);


    // Set up Shuffle. Actual filtering logic lives in our filter function below.
    shuffle = new Shuffle(document.querySelector('#blueprint-list'), {
      filterMode: Shuffle.FilterMode.ALL,  // AND query (default is OR)
      itemSelector: '.blueprint-card'
    });

    setupSortControls();
    buildFilterData($items);
    restoreFiltersFromLocalStorage();
    filter();
  }


  function setupSortControls() {
    var sortFunctions = {
      'sequence': function (element) { return element.getAttribute('data-sequence'); },
      'name': function (element) { return element.getAttribute('data-name'); }
    };
    var initialSortBy = localStorage.getItem('catalog-sort-by') || 'sequence';
    var initialSortRev = localStorage.getItem('catalog-sort-reverse') || false;
    if (initialSortRev) {
      initialSortRev = JSON.parse(initialSortRev);
    }

    // Initialize page based on last state persisted in localStorage
    shuffle.sort({by: sortFunctions[initialSortBy], reverse: initialSortRev});
    updateSortButtons(initialSortBy, initialSortRev);

    // Set up click handler for sort buttons
    $('#sortButtons label').on('click', function(e) {
      var $label = $(this);
      var wasAsc = ($label.find('i[data-asc]:visible').length !== 0);
      var reverse = $label.hasClass('active') && wasAsc;
      var sortBy = $label.find('input').val();
      shuffle.sort({by: sortFunctions[sortBy], reverse: reverse});
      updateSortButtons(sortBy, reverse);
      localStorage.setItem('catalog-sort-by', sortBy);
      localStorage.setItem('catalog-sort-reverse', reverse);
    });
  }


  /*
   * Update the state of all sort buttons to correspond to the `sortBy` ('name' or 'sequence') and
   * a boolean `reverse`.
   */
  function updateSortButtons(sortBy, reverse) {
    var $buttons = $('#sortButtons');
    // Mark the selected button
    var $labels = $buttons.find('label').removeClass('active');
    var $activeButton = $buttons.find('input[value="' + sortBy + '"]');
    var $activeLabel = $activeButton.closest('label');
    $activeLabel.addClass('active');

    // Find the 2 icons for this button and show the one corresponding to the value of `reverse`
    var $iconDesc = $activeLabel.find('i[data-desc]');
    var $iconAsc = $activeLabel.find('i[data-asc]');
    if (reverse) {
      $iconAsc.hide();
      $iconDesc.show();
    } else {
      $iconAsc.show();
      $iconDesc.hide();
    }
  }


  var filterDebounced = $.debounce(100, filter);


  function getCurrentFilterFamilyID() {
    var val = $byOSFamily.filter(':checked').val();
    return val ? parseInt(val) : null;
  }


  /*
   * For all visible blueprint cards, return an object with a list of distinct items (IDs
   * actually) made by combining all cached data-`attrName` values.  This is used to
   * get all group, label and environment IDs that are relevant for a set of visible
   * blueprints. Options of filter dropdowns that have not been set will be modified to show only
   * those that are visible in the current view.
   */
  function getCombinedDataForVisibleCards() {
    var blueprintData,
        combinedData = {
          groups: [],
          environments: [],
          labels: []
        };

    $blueprintCards.filter(".shuffle-item--visible").each(function(index) {
      blueprintData = blueprintDataByID[$(this).data('id')];
      combinedData.groups = _.union(combinedData.groups, blueprintData.groups);
      combinedData.environments = _.union(combinedData.environments, blueprintData.environments);
      combinedData.labels = _.union(combinedData.labels, blueprintData.labels);
    });
    logger.debug('combinedData:', combinedData);

    return combinedData;
  }


  /**
   * Set the options for the selectize object.
   * `values` is a list of values
   * `labelsByValue` is a mapping of value to user-visible label
   */
  function setSelectizeOptions(selectize, values, labelsByValue) {
    selectize.clearOptions();

    // loop over item names to add options to the filter in alphabetical order
    _.forEach(_.keys(labelsByValue), function (value) {
      value = parseInt(value);
      if (_.contains(values, value)) {
        selectize.addOption({value: value, text: labelsByValue[value]});
      }
    });

    // update the selectize dropdown
    selectize.refreshOptions(false);
  }


  /**
   * Update the given selectize's options to those that are represented by the
   * visible blueprints. Hides options that would lead to an empty catalog view.
   */
  function updateDropdownChoices(selectize, metadataField, labelsByValue) {
    var value = selectize.getValue();
    if (!(value === "" || value.length === 0)) {
      logger.debug('  Skipping; user already chose something');
      return;
    }
    var combinedData = getCombinedDataForVisibleCards();
    logger.debug('updateDropdownChoices new ' + metadataField + ' values:', combinedData[metadataField]);
    setSelectizeOptions(selectize, combinedData[metadataField], labelsByValue);
  }

  function updateGroupFilter() {
    updateDropdownChoices(groupSelectize, 'groups', groupNamesByID);
  }

  function updateEnvFilter() {
    updateDropdownChoices(envSelectize, 'environments', envNamesByID);
  }

  function updateLabelFilter() {
    updateDropdownChoices(labelSelectize, 'labels', labelNamesByID);
  }


  /*
   * Build a mapping of BP IDs to objects representing attributes that can be
   * filtered by. By doing the DOM manipulations now instead of as filter
   * events are handled, performance is nicely increased.
   */
  function buildFilterData($cards) {
    $cards.each(function(index) {
      var $card = $(this);

      blueprintDataByID[$card.data('id')] = {
        id: $card.attr('id'),
        name: ($card.data('name') || '').toLowerCase(),
        desc: ($card.data('description') || '').toLowerCase(),
        groups: $card.data('groups'),
        labels: $card.data('labels'),
        environments: $card.data('environments'),
        familyIDs: $card.data('os-family-ids')
      };
    });
  }


  function getFilterValues() {
    return {
      group: parseInt(groupSelectize.getValue()),
      env: parseInt(envSelectize.getValue()),
      // Handle the list returned by the SelectizeMultiple widget.
      labels: _.filter(labelSelectize.getValue(), function(strVal) {
        return parseInt(strVal);
      }),
      osFamily: getCurrentFilterFamilyID(),
      searchTerm: searchField.val().toLowerCase()
    };
  }


  // Hide items that are filtered out
  function filter() {
    var filterValues = getFilterValues();
    var showing = '';
    var matchingBlueprintsCount = 0;

    // Now use Shuffle to redraw the collection
    shuffle.filter(function(card, shuffle) {
      var $card = $(card);
      var blueprintData = blueprintDataByID[$card.data('id')];
      var groupMatches = filterValues.group && _.contains(blueprintData.groups, filterValues.group);
      var envMatches = filterValues.env && _.contains(blueprintData.environments, filterValues.env);
      var osMatches = filterValues.osFamily && _.contains(blueprintData.familyIDs, filterValues.osFamily);
      var labelMatches = false;
      var termMatches = false;

      if (filterValues.labels.length) {
        labelMatches = _.every(filterValues.labels, function(filterLabel, index, collection) {
          return _.contains(blueprintData.labels, parseInt(filterLabel));
        });
      }

      if (filterValues.searchTerm) {
        termMatches = (
          blueprintData.name.indexOf(filterValues.searchTerm) !== -1 ||
          blueprintData.desc.indexOf(filterValues.searchTerm) !== -1);
      }

      if ((filterValues.group && !groupMatches) ||
          (filterValues.env && !envMatches) ||
          (filterValues.osFamily && !osMatches) ||
          (filterValues.labels.length && !labelMatches) ||
          (filterValues.searchTerm && !termMatches)) {
        return false; // This tells Shuffle to hide the card
      } else {
        matchingBlueprintsCount += 1;
        return true; // This tells Shuffle to show the card
      }
    });

    // Remove any open tooltips (especially the one on the "Clear filters"
    // button, which otherwise hangs around forever)
    $('#tooltip-container').html('');

    var totalBlueprints = Object.keys(blueprintDataByID).length;
    updateNumberOfBlueprintsMessage(matchingBlueprintsCount, totalBlueprints);

    saveFilterState();
  }


  function updateNumberOfBlueprintsMessage(matchingBlueprintsCount, totalBlueprints) {
    var msg;

    if (matchingBlueprintsCount != totalBlueprints) {
      msg = gettext('Showing %(matchingCount)s of %(totalCount)s blueprints available to you.');
      msg = interpolate(msg, {
        "matchingCount": matchingBlueprintsCount,
        "totalCount": totalBlueprints
      }, true);
      msg += ' &nbsp;&nbsp; ' +
        '<button id="clear-filters" class="btn btn-default btn-sm">' +
        gettext("Clear filters") + '<span class="icon-delete"></span>' +
        '</button>';
    } else {
      msg = ngettext('Showing the %(count)s blueprint available to you.',
                     'Showing all %(count)s blueprints available to you', totalBlueprints);
      msg = interpolate(msg, {"count": totalBlueprints}, true);
    }
    $('#showing-msg').html(msg);
  }


  function clearFilters() {
    // Reset localStorage
    localStorage.removeItem('catalogFilterGroup');
    localStorage.removeItem('catalogFilterEnv');
    localStorage.removeItem('catalogFilterOSFamily');
    localStorage.removeItem('catalogFilterLabels');
    localStorage.removeItem('catalogFilterTextSearch');

    // Reset the controls
    groupSelectize.setValue('');
    envSelectize.setValue('');
    labelSelectize.setValue('');
    searchField.val('');

    // Bootstrap Button plugin only updates 'active' state on click so we undo
    // it manually here.
    $byOSFamily.filter('input').prop('checked', false).closest('label').removeClass('active');

    filter();

    // Ensure all dropdowns are returned to showing all options for the visible cards
    updateGroupFilter();
    updateEnvFilter();
    updateLabelFilter();
  }


  // Save filter values in localStorage
  function saveFilterState() {
    var filterValues = getFilterValues();
    localStorage.setItem('catalogFilterGroup', filterValues.group);
    localStorage.setItem('catalogFilterEnv', filterValues.env);
    localStorage.setItem('catalogFilterLabels', filterValues.labels);
    localStorage.setItem('catalogFilterOSFamily', filterValues.osFamily);
    localStorage.setItem('catalogFilterSearchTerm', filterValues.searchTerm);
  }


  // Restore filter values from localStorage if they're set
  function restoreFiltersFromLocalStorage() {
    var filterGroup = localStorage.getItem('catalogFilterGroup');
    var filterEnv = localStorage.getItem('catalogFilterEnv');
    var filterLabels = localStorage.getItem('catalogFilterLabels');
    var filterOSFamily = localStorage.getItem('catalogFilterOSFamily');
    var filterSearchTerm = localStorage.getItem('catalogFilterSearchTerm');

    if (filterGroup) {
      groupSelectize.setValue(filterGroup);
    }

    if (filterEnv) {
      envSelectize.setValue(filterEnv);
    }

    if (filterLabels) {
      logger.debug('restore labels filter to:', filterLabels);
      _.forEach(filterLabels.split(','), function(labelID) {
        labelSelectize.addItem(parseInt(labelID.trim()));
      });
    }

    if (filterOSFamily) {
      var $input = $byOSFamily.filter('[value='+ filterOSFamily +']');
      $input.prop('checked', true);
      $input.closest('label').addClass('active');
    }

    if (filterSearchTerm) {
      $('input[name=text_search]').val(filterSearchTerm);
    }
  }


  /**
   * Open blueprint card links.
   *
   * Args: a BP card jQuery object, a click/mousedown event object, and a boolean for whether to
   * open this in a new tab.
   */
  function followBlueprintLink($card, e, newTab) {
    var url = $card.data('href');
    logger.debug('url:', url);
    logger.debug('newTab:', newTab);

    // add group and environment filter values to the URL
    var groupId = $('[name=filter_by_group]').val();
    var envId = $('[name=filter_by_env]').val();
    if (groupId || envId) {
      url += '?';
      url += groupId ? 'group=' + groupId + '&' : '';
      url += envId ? 'env=' + envId : '';
    }

    // Manage link clicks target the child (span.glyphicon)
    var $manageLink = $(e.target).parent('a.manage-link');
    if ($manageLink.length) {
      url = $manageLink.attr('href');
    }

    // Only open the link if the BP is orderable or the user clicked on the management link
    // for the BP. Ie. do not follow the URL if they clicked on the card of a non-orderable BP.
    if ($card.hasClass("orderable") || $manageLink.length) {
      // Cmd, Ctrl, or middle-click opens in a new tab
      if (newTab) {
        window.open(url, '_blank');
      } else {
        window.location.href = url;
      }
    }
  }


  function handleCardClicks($container) {
    // Allow `handleCardClicks` to be idempotent; that is, called multiple
    // times but result in only one event handler.
    $container.off('mousedown', '.blueprint-card, .resource-card');
    $container.off('click', '.blueprint-card, .resource-card');

    // Mousedown fires during drag too (if user is scrolling overflowed card contents). Only respond
    // to middle-click mousedown events to honor the native behavior of opening links in a new tab.
    $container.on('mousedown', '.blueprint-card, .resource-card', function(e) {
      var $card = $(this);
      var newTab = (e.which == 2); // Middle-click

      if (newTab) {
        e.preventDefault();
        followBlueprintLink($card, e, newTab);
      }
    });

    /**
    * Handle left-clicks on blueprint and resource cards. Support targeting a new browser tab via
    * Cmd-click (Mac) or ctrl-click.
    */
    $container.on('click', '.blueprint-card, .resource-card', function(e) {
      e.preventDefault();
      var $card = $(this);
      var newTab = (e.metaKey || e.ctrlKey); // Cmd-click (Mac) or Ctrl-click

      followBlueprintLink($card, e, newTab);
    });
  }

  // For each panel that has input toggle set to 'immediately', find the
  // following panel (if any) and decrement its sequence number.
  function renumberParallelItems($serviceItemList) {
      var $panel, $followingSibling;
      var $panels = $serviceItemList.find('.panel');
      var seq;
      var $nextSeq;
      var $nextPanel;
      var isParallel;

      $panels.each(function() {
          $panel = $(this);
          $nextPanel = $panel.closest('li').next().find('.panel');
          if ($nextPanel) {
              seq = parseInt($panel.find('.sort-seq').text(), 10);

              $nextSeq = $nextPanel.find('.sort-seq');
              if (!$nextSeq.length) {
                  return;
              }

              isParallel = $panel.find('input[name=execute_in_parallel]').prop('checked');
              if (isParallel) {
                  $nextSeq.text(seq);
              } else {
                  $nextSeq.text(seq + 1);
              }
          }
      });
  }


  c2[__module__] = {
    initCatalog: initCatalog,
    initFilters: initFilters,
    handleCardClicks: handleCardClicks,
    renumberParallelItems: renumberParallelItems
  };

})('blueprints');

// Bookmarks

(function (__module__) {
  'use strict';

  var $topMenuItem;
  var $bookmarks;
  var logger = c2.logging.getLogger(__module__);


  function bookmarkThisPage() {
    var relativeUrlWithHashAndQueryArgs = window.location.href.split(window.location.host)[1];

    $.post(
      $topMenuItem.find('[data-add-bookmark]').attr('href'),
      {
        title: document.title,
        url: relativeUrlWithHashAndQueryArgs
      },
      function (response) {
        if (response && response.success) {
          // Fix stuck bookmark menu tooltip bug by closing any open tt
          $('#tooltip-container').html('');

          c2.include.reload($bookmarks);
          init($topMenuItem);

          $topMenuItem.highlight('#d0e9c6'); // Success green
        } else {
          // Highlight the menu even if the entry was a duplicate, or some
          // error occurred, to acknowledge the keypress.
          $topMenuItem.highlight('#faf2cc'); // Warning yellow
        }
      }
    );
  }


  function goToBookmark(num) {
    var a = $('#bookmarks-submenu a.bookmark')[num - 1];
    if (a && a.href) {
      c2.block.block();
      window.location = a.href;
    } else {
      // Bookmark with this number does not exist
      c2.navbar.closeSubMenu($topMenuItem);
    }
  }


  function init($topMenuItemArg) {
    // Hang on to a jQuery object for the top menu LI
    $topMenuItem = $topMenuItemArg;
    $bookmarks = $topMenuItem.find('#bookmarks-submenu');

    // If submenu content came from memcache, the bookmarks menu never
    // got the data-include attribute.  Set it now to enable reloading.
    $bookmarks.data('include', $bookmarks.data('reload-url'));

    c2.navbar.closeSubMenu($topMenuItem);

    // Remove all event handlers in 'bookmarks' namespace. This allows `init`
    // to be idempotent.  It is called after the submenu is reloaded.
    $topMenuItem.off('.bookmarks');

    c2.commonEventHandlers.registerGlobalKeyHandlers('bookmarks', {
      '.': function(e) {
        bookmarkThisPage();
        e.preventDefault();
      },
      'g': function(e) { // toggle bookmark menu
        if (c2.navbar.isSubMenuOpen($topMenuItem)) {
          c2.navbar.closeSubMenu($topMenuItem);
        } else {
          c2.navbar.openSubMenu($topMenuItem);

          // Scroll menu into view
          window.scroll(0, 0);
        }
        e.preventDefault();
      }
    });

    // Click handlers
    $topMenuItem.on('click.bookmarks', '[data-add-bookmark]', function(e) {
      e.preventDefault();
      bookmarkThisPage();
    });

    $topMenuItem.on('click.bookmarks', '[data-delete-bookmark]', function(e) {
      e.preventDefault();
      $.post($(this).attr('href'), {}, function(response) {
        c2.include.reload($bookmarks);
        init($topMenuItem);
      });
    });

    $topMenuItem.on('keydown.bookmarks', function(e) {
      if (c2.navbar.isSubMenuOpen($topMenuItem)) {
        var code = e.which || e.keyCode;

        if ((code >= 48 && code <= 57) || (code >= 96 && code <= 105)) {
          // This is a number (1-9 on keyboard or keypad)
          c2.navbar.closeSubMenu($topMenuItem);
          goToBookmark(String.fromCharCode(code));

          // Stop any further global key handlers from running
          e.preventDefault();
        } else if (e.key == 'Escape') {
          c2.navbar.closeSubMenu($topMenuItem);
          e.preventDefault();
        }
      }
    });
  }


  c2[__module__] = {
    init: init
  };
})('bookmarks');

/* Tabs that are presented as button groups.  This module implements the
 * tabbing behavior as well as persistence and deep linking.
 *
 * Usage:
 *    <div class="btn-group" data-toggle="button-tabs">
 *      <a href="#view-1" class="btn btn-default active"> View 1 </a>
 *      <a href="#view-2" class="btn btn-default"> View 2 </a>
 *    </div>
 *
 *    <div class="tab-content">
 *      <div id="view-1" class="tab-pane active"> {{ content1 }} </div>
 *      <div id="view-2" class="tab-pane"> {{ content2 }} </div>
 *    </div>
 */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);
  var persist = true;


  // Return the key to use when saving/restoring the active tab from
  // localStorage. Returns a key based on the URL's pathname.
  var localStorageKey = function () {
    return 'c2.button-tabs.active.' + window.location.pathname;
  };

  // Try to activate the tab with ID `tabID`, returning `true` if successful,
  // `false` if not.
  function activateTab(tabId) {
    if (tabId === '') {
      return false;
    }
    var $pane = $('#' + tabId);
    var $button = $('[data-toggle=button-tabs] a[href="#'+ tabId +'"]');
    var $buttons = $('[data-toggle=button-tabs] a');

    // Highlight only the active tab button
    $buttons.removeClass('active');
    $button.addClass('active');

    // Show the active tab pane
    $pane.closest('.tab-content').find('.tab-pane').removeClass('active');
    $pane.addClass('active');

    return !! $button.length;
  }

  // Save `tabID` as the active tab to localStorage.
  function persistToLocalStorage(tabId) {
    var key = localStorageKey();
    localStorage.setItem(key, tabId);
  }

  // Show the tab that has been remembered by localStorage. Return true if a
  // tab is restored, false otherwise.
  function restoreFromLocalStorage() {
    var key = localStorageKey();
    var tabId = localStorage.getItem(key);
    return activateTab(tabId);
  }

  // Save `tabID` as the active tab to the current URL's hash.
  function persistToHash(tabId) {
    if (history.replaceState) {
      history.replaceState({}, '', '#' + tabId);
    }
  }

  // Show the tab indicated by the page's URL hash. Return true if a tab is
  // restored, false otherwise.
  function restoreFromHash() {
    var tabId = location.hash.slice(1);
    return activateTab(tabId);
  }


  /*
   * Initialize button tabs on the page. There should only be one set.
   *
   * The tabs element may disable localStorage persistence by setting data attr
   * 'buttontabs-persist' to 'off'.
   */
  function init() {
    // Only one set of buttonTabs is supported
    var $tabs = $('[data-toggle=button-tabs]').first();

    if ($tabs.data('buttontabs-persist') === 'off') {
      // Set this for the entire page
      logger.debug('persistence to localStorage disabled for all buttonTabs on page');
      persist = false;
    }

    $tabs.on('click', '.btn', function(e) {
        e.preventDefault();

        var $button = $(this);
        var $target = $($button.attr('href'));
        var tabId = $target.attr('id');

        activateTab(tabId);
        persistToHash(tabId);

        if (persist) {
          persistToLocalStorage(tabId);
        }
    });


    // Only restore from localStorage if we don't restore from the URL hash
    // because URLs have the most authority.
    if (! restoreFromHash()) {
      if (persist) {
        restoreFromLocalStorage();
      }
    }
  }

  // expose public functions
  c2[__module__] = {
    init: init
  };

})('buttonTabs');

/*
 * Functions for history tables used by various CB objects.
 */
(function(c2, $) {
  "use strict";
  function init(initialViewMode,viewingMode) {
    viewingMode(initialViewMode);
    $(function() {
      function getQuerystring() {
        var querydict = {};

        var current_search_term = $("#catalog-search").val();
        if (
          typeof current_search_term !== "undefined" &&
          current_search_term !== ""
        ) {
          querydict["q"] = current_search_term;
        }
        var current_sort = $("#options--grid-sort").val();
        if (typeof current_sort !== "undefined") {
          querydict["sort"] = current_sort;
        }
        var current_filters = $("aside.catalog-filters input:checked")
          .map(function() {
            return this.id.replace("filter-", "");
          })
          .toArray()
          .join(",");
        if (typeof current_filters !== "undefined" && current_filters !== "") {
          querydict["filters"] = current_filters;
        }
        var viewMode = $("#viewing-modes-group").val();
        if ((viewMode !== "undefined") & (viewMode !== "")) {
          querydict["viewing_mode"] = viewMode;
          if (viewMode === "table") {
            // clear all filters
            querydict["filters"] = "";
          }
        } else {
          // Persist the current viewing mode.
          querydict["view_mode"] = initialViewMode;
        }

        if (initialViewMode === "categories") {
          var selectedCategoryID = $(".category__item.selected").attr("id");
          if (!selectedCategoryID || selectedCategoryID === "undefined") {
            // If a user just switched to this category, make sure we
            // remove all filters to start.
            querydict["filters"] = "";
          } else {
            // Add the category this user just clicked on to the querystring.
            querydict["filters"] = selectedCategoryID;
          }
        }

        var querystring = Object.keys(querydict)
          .map(function(key) {
            return [key, querydict[key]].join("=");
          })
          .join("&");
        return querystring;
      }

      var latestReloadRequested = undefined;
      function reloadPage(delay, url) {
        // Reload the page with the currently selected options, but with a 1 second delay
        // so the page doesn't load as someone is checking several options.
        delay = delay === undefined ? 1000 : delay;

        c2.block.block("ol.tile-list");
        var reloadRequested = new Date();
        latestReloadRequested = reloadRequested;
        // Wait a second, and only reload the page if another request hasn't come in since this one.
        if (typeof url === "undefined") {
          url = window.location.origin + window.location.pathname + "?";
        } else {
          url += "&";
        }
        setTimeout(function() {
          if (latestReloadRequested.getTime() === reloadRequested.getTime()) {
            window.location.href = url + getQuerystring();
          }
        }, delay);
      }

      $(".category__item").click(function() {
        event.preventDefault();
        // reload
        $(this).addClass("selected");
        reloadPage();
      });

      // Hook up the remove buttons on the active filters
      $("#filters-active--list li a.catalog-icon-close").on(
        "click",
        function() {
          event.preventDefault();
          var currentFilterID = $(this).attr("filterid");
          $(this)
            .parent("li")
            .remove();
          $("aside.catalog-filters input#filter-" + currentFilterID).prop(
            "checked",
            false
          );
          reloadPage();
          return false;
        }
      );
      // The close all button on the active filters
      $(".filter--head a.catalog-icon-close-dark").on("click", function() {
        event.preventDefault();
        $("#filters-active--list li").remove();
        $("aside.catalog-filters input").prop("checked", false);
        var delay;
        reloadPage((delay = 0));
        return false;
      });
      // The checkboxes on all available filters
      $("aside.catalog-filters input").on("click", function() {
        reloadPage();
      });
      // The sort choices
      $("select#options--grid-sort").change(function() {
        if ($(this).val() != "{{sort}}") {
          var delay;
          reloadPage((delay = 0));
        }
      });
      // The pagination links
      $("a.nav-link").on("click", function() {
        event.preventDefault();
        var delay;
        var url;
        reloadPage((delay = 0), (url = this.href));
        return false;
      });
      // The search field, while typing
      $("#catalog-search").on("keyup", function() {
        reloadPage();
      });
      // The search field, on hitting enter
      $("form.form--grid-search").on("submit", function() {
        var delay;
        reloadPage((delay = 0));
        return false;
      });

      // The viewing modes
      $("button.view-mode").on("click", function() {
        // set the value of this button to the parent, which will get then get added to the
        // querystring in the request on reloadPage() -> getQuerystring()
        this.parentElement.value = this.value;
        reloadPage();
      });
    });
  }

  c2.catalogList = {
    init: init
  };
})(window.c2, window.jQuery);

/* Chart utilities */

// site-wide default for bar width. If series don't specify maxPointWidth, this
// will be used.
var globalMaxPointWidth = 40;

(function (c2, $, _, Highcharts) {
  'use strict';

  // Provide a maxPointWidth setting to Hichcharts to enable max bar widths in
  // pixels. Extends the Highcharts.drawPoints function.
  // When initializing a chart, set it on any series like this:
  //    series: [{maxPointWidth: 25, data: seriesData}]
  (function(H) { 
    var each = H.each;
    H.wrap(H.seriesTypes.column.prototype, 'drawPoints', function(proceed) {
      var series = this;
      var maxPointWidth = (typeof(series.options.maxPointWidth) === undefined) ?
          globalMaxPointWidth : series.options.maxPointWidth;
      if(series.data.length > 0 ){
        var width = series.barW > maxPointWidth ? maxPointWidth : series.barW;
        each(this.data, function(point) {
          point.shapeArgs.x += (point.shapeArgs.width - width) / 2;
          point.shapeArgs.width = width;
        });
      }
      proceed.call(this);
    });
  })(Highcharts);


  // Sum an array of numbers after filtering out `null` values. 
  function sum(values) {
    var filtered_values, n, i, s = 0;

    filtered_values = _.without(values, null);
    n = filtered_values.length;
    
    if (n == 0) {
      return 0;
    }

    for (i = 0; i < n; i++) {
      s += filtered_values[i];
    }
    return s;
  }


  // Given an array of numbers, calculate their average
  function avg(values) {
    var filtered_values,
        total_value,
        n = values.length;
    if (n === 0) {
      return 0;
    }
    
    // The `.without` function will remove the `null`'s that we used to replace
    // empty values with in our `values` array, allowing us to correctly
    // calculate the average.
    filtered_values = _.without(values, null);
    total_value = sum(filtered_values);
    if (total_value == 0 || filtered_values.length == 0) {
      return 0;
    }
    return total_value / filtered_values.length;
  }

  function getCategoriesAsDates(categories) {
    var dates = Array();
    var n = categories.length;
    var i;
    for (i = 0; i < n; i++) {
      dates[i] = new Date(categories[i]);
    }
    return dates;
  }

  // Returns null for missing float values, allowing us to plot empty data on
  // the chart. If the value can be converted to a float, treat it as such and
  // divide by the denominator.
  function parseFloatNull(value, denominator) {
    var nan_values = ['', 'null'];
    if (nan_values.includes(value)) {
      return null;
    }

    return parseFloat(value) / denominator;
  }

  /**
   * This method gets the SVG of the chart and uses canvg to draw it on a
   * HTML5 canvas. The canvas is then streamed to the browser window as a
   * download. Replaces a server-side solution for chart export.
   * http://www.highcharts.com/docs/export-module/export-module-overview
   */
  function exportChartAsPNG(chart) {
    var svg = chart.getSVG(),
        width = parseInt(svg.match(/width="([0-9]+)"/)[1]),
        height = parseInt(svg.match(/height="([0-9]+)"/)[1]),
        canvas = document.createElement('canvas');

    canvas.setAttribute('width', width);
    canvas.setAttribute('height', height);

    if (canvas.getContext && canvas.getContext('2d')) {
      canvg(canvas, svg);
      c2.downloads.startDownload(
        canvas.toDataURL("image/png"),
        chart.options.exporting.filename + '.png'
      );
    } else {
      alert ("Your browser doesn't support this feature. Please use a " +
             "modern browser that supports the canvas element.");
    }
  }


  function bar($elem, options) {
    var barDefaults = serverBarChartDefaults;

    $elem.highcharts(_.merge(barDefaults, options));
  }


  function pie($elem, options) {
    var pieDefaults = {
      plotOptions: {
        chart: {type: 'pie'},
        pie: {
          allowPointSelect: true,
          cursor: 'pointer',
          dataLabels: {
            enabled: true,
            color: '#000000',
            connectorColor: '#000000',
            formatter: function() {
              return '<b>'+ this.point.name +'</b>: '+ this.point.y;
            }
          },
          shadow: false
        }
      },
      tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.1f} %</b>'
      },
      yAxis: { title: {text: 'Total percent'} },
      legend: {enabled: false},
      credits: {enabled: false},
      exporting: exportingOptions
    };

    $elem.highcharts(_.merge(pieDefaults, options));
  }


  // default export menu items
  var exportingOptions = {
    buttons: {
      contextButton: {
        menuItems: [
          {
            text: gettext('Print'),
            onclick: function() {
              this.print();
            }
          },
          { separator: true },
          {
            text: gettext('Export as PNG Image'),
            onclick: function() {
              exportChartAsPNG(this, this.options.exporting.filename + '.png');
            }
          },
          {
            text: gettext('Export as CSV'),
            onclick: function() {
              // The report configuration defines toCSV, a non-standard
              // Highcharts option, so that this handler remains generic.
              c2.downloads.startDownloadFromContent(
                this.options.exporting.toCSV(),
                this.options.exporting.filename + '.csv');
            }
          }
        ]
      }
    }
  };

  var serverBarChartDefaults = {
    subtitle: {
      text: gettext('Includes all servers in groups you have permission to view.')
    },
    yAxis: {
      title: { text: gettext('Number of Servers') }
    },
    series: [
      {
        name: gettext('Servers'),
        maxPointWidth: 40,
      }
    ],
    chart: {
      type: 'bar'
    },
    plotOptions: {
      bar: {
        dataLabels: {
          enabled: true
        }
      }
    },
    tooltip: {
      pointFormat: '{series.name}: <b>{point.y}</b>'
    },
    legend: {
      enabled: false
    },
    credits: {
      enabled: false
    },
    exporting: exportingOptions
  };

  var serverPieChartDefaults = {
    plotOptions: {
      pie: {
        allowPointSelect: true,
        cursor: 'pointer',
        dataLabels: {
          enabled: true,
          color: '#000000',
          connectorColor: '#000000',
          formatter: function() {
            return '<b>'+ this.point.name +'</b>: '+ this.point.y + gettext(' servers');
          }
        }
      }
    },
    subtitle: {
      text: gettext('Includes all servers in groups you have permission to view.')
    },
    tooltip: {
      pointFormat: '{series.name}: <b>{point.percentage:.1f} %</b>'
    },
    legend: {
      enabled: false
    },
    credits: {
      enabled: false
    },
    exporting: exportingOptions
  };

  var billingSeriesDefaults = {
    title: {
      text: ""
    },
    yAxis: {
      labels: {
        format: '${value:.2f}',
      },
      title: {
        text: "Cost (USD)"
      }
    },
    xAxis: {
      type: 'datetime',
      tickInterval: 5,
      labels: {
        format: '{value:%e %b %Y}'
      },
    },
    tooltip: {
      headerFormat: '<b>{point.x:%e %b %Y}</b> <br>',
      pointFormat: '{series.name}: <b>${point.y:.2f}</b>',
    },
    series: {
      type: 'spline'
    },
    credits: {
      enabled: false
    },
    exporting: exportingOptions,
    chart: {
      zoomType: 'xy'
    },
  };

  var commonStatChartOpts = {
    chart: {
      zoomType: 'xy'
    },
    title: {
      text: ''
    },
    xAxis: {
      type: 'datetime',
      tickPixelInterval: 150
    },
    yAxis: { // Primary yAxis
      labels: {
        format: '{value} %',
        style: {
          color: '#335b83'
        }
      },
      title: {
        text: gettext('Percentage'),
        style: {
          color: '#335b83'
        }
      }
    },
    credits: {
      enabled: false
    },
    exporting: {
      enabled: false
    }
  };

  var diskStatChartOpts = {
    chart: {
      zoomType: 'xy'
    },
    title: {
      text: ''
    },
    xAxis: {
      type: 'datetime',
      tickPixelInterval: 150
    },
    yAxis: { // Primary yAxis
      labels: {
        format: '{value} kB/s',
        style: {
          color: '#335b83'
        }
      },
      title: {
        text: 'Disk I/O (in kB/s)',
        style: {
          color: '#335b83'
        }
      }
    },
    credits: {
      enabled: false
    },
    exporting: {
      enabled: false
    }
  };

  var netStatChartOpts = {
    chart: {
      zoomType: 'xy'
    },
    title: {
      text: ''
    },
    xAxis: {
      type: 'datetime',
      tickPixelInterval: 150
    },
    yAxis: { // Primary yAxis
      labels: {
        format: '{value} kB/s',
        style: {
          color: '#335b83'
        }
      },
      title: {
        text: 'Throughput (in kB/s)',
        style: {
          color: '#335b83'
        }
      }
    },
    credits: {
      enabled: false
    },
    exporting: {
      enabled: false
    }
  };

  /* Creates series data array of objects, with markers added where
   * server events occur.
   *
   * Returns object:
   * {
   *   data: the series data points
   *   average: average value of numbers in data array
   *   eventAtTime: a dict of events by time used to generate tooltips
   * }
   *
   * Markers are drawn on the series wherever event times correspond with
   * series times. Since exact matches between event millisecond times and
   * series times are unlikely, markers are added to the next x value
   * after the time they happened.
   * Args:
   *   pointValues: array of numbers
   *   serverEventsSorted: array of event objects in chronological order
   *   interval: distance in seconds between each point
   *   isPercentage: boolean indicating whether the provided pointValues are percentage 
        values or not (CPU and Memory data points are, whereas disk and network data points are not)
   */
  function seriesData(startTime, interval, pointValues, serverEventsSorted, isPercentage) {
    var data = [];
    var intervalInMS = interval * 1000;
    var x, i, k, point, event;
    // dict of server history events on a particular x value (time), used
    // by tooltips
    var eventAtTime = {};

    if (isPercentage) {
      var denominator = 100.0;
    }
    else {
      var denominator = 1.0;
    }
    for (i = 0; i < pointValues.length; i++) {
      x = startTime + (i * intervalInMS);
      point = {
        x: x,
        y: parseFloatNull(pointValues[i], denominator),
        marker: {
          enabled: false
        }
      };

      // go through the events that haven't been processed yet and
      // add them to the series if they happened before this point.
      for (k = 0; k < serverEventsSorted.length; k++) {
        event = serverEventsSorted[k];
        if (point.x > event.epoch_ms) {
          //point.color = '#393';
          point.marker = {
            enabled: true,
            fillColor: '#393',
            lineColor: '#060',
            radius: 10,
            symbol: 'diamond'
          //symbol: url('event-type-icon.png')
          };

          // data used by tooltip
          eventAtTime[point.x] = event;

          // remove it from the list of events
          serverEventsSorted.splice(k, 1);
        }
      }

      data.push(point);
    }

    return {
      data: data,
      eventAtTime: eventAtTime,
      average: avg(_.map(data, 'y'))
    };
  }

  /* Given a data series, return the Highcharts tooltip option object.
   * Series object should include the eventAtTime dict that is needed
   * to look up event information.
   *
   * The percentage arg is a boolean to indicate whether to present
   * each point as percentages or as real numbers.
   */
  function getServerStatTooltip(series, percentage) {
    return {
      formatter: function() {
        var s = '<b>'+ Highcharts.dateFormat('%b %e %Y at %H:%M:%S', this.x) +'</b>';

        _.forEach(this.points, function(point) {
          if (percentage) {
            s += '<br/>'+ point.series.name +': <b>'+ point.y +'% </b>';
          }
          else {
            s += '<br/>'+ point.series.name +': <b>'+ point.y +'</b>';
          }

        });

        if (series.eventAtTime[this.x] !== undefined) {
          var e = series.eventAtTime[this.x];
          // add server event info
          s += '<div class="chart-tip event-tip">';
          s += 'Event: <b>'+ e.type +'</b><br/>';
          s += 'Owner: <b>'+ e.owner_html +'</b><br/>';
          s += 'Job: <b>'+ e.job_html +'</b><br/>';
          s += '<p>'+ e.message +'</p>';
          s += '</div>';
        }

        return s;
      },
      useHTML: true,
      shared: true
    };
  }


  /* Draw chart of CPU stats with server history events added as markers
   * on the line.
   * Args:
   *     startTime: epoch seconds
   *     interval: seconds between each x value
   *     cpuUsageValues: array of float numbers representing % values
   *     serverEvents: array of event objects
   *     options: Highchart options object
   */
  function drawServerCPUStatsChart(
      startTime, interval, cpuUsageValues, serverEvents, options) {
    if (cpuUsageValues === undefined) {
        cpuUsageValues = [];
    }

    // array of event objects sorted chronologically
    var serverEventsSorted = _.sortBy(serverEvents, 'epoch_ms');
    var series = seriesData(startTime, interval, cpuUsageValues, serverEventsSorted, true);

    $('#cpu-container').highcharts(_.merge({
      subtitle: {
        text: gettext('CPU Stats')
      },
      series: [
        {
          name: 'Usage',
          color: '#335b83',
          type: 'line',
          data: series.data
        }, {
          name: 'Average',
          color: '#4a9de4',
          type: 'spline',
          marker: { enabled: false },
          data: (function() {
            var i,
                points = [],
                n = series.data.length;
            for (i = 0; i < n; i++) {
              points.push({
                x: series.data[i].x,
                y: Math.round(series.average * 100) / 100
              });
            }
            return points;
        }())
      }],
      tooltip: getServerStatTooltip(series, true)
    }, options));
  }


  /* Draw chart of memory stats with server history events added as markers
   * on the line.
   * Args:
   *     startTime: epoch seconds
   *     interval: seconds between each x value
   *     memUsageValues: array of float numbers representing % values
   *     serverEvents: array of event objects
   *     options: Highchart options object
   */
  function drawServerMemStatsChart(
      startTime, interval, memUsageValues, serverEvents, options) {
    if (memUsageValues === undefined) {
        memUsageValues = [];
    }

    // array of event objects sorted chronologically
    var serverEventsSorted = _.sortBy(serverEvents, 'epoch_ms');
    var series = seriesData(startTime, interval, memUsageValues, serverEventsSorted, true);

    $('#mem-container').highcharts(_.merge({
      subtitle: {
        text: gettext('Memory Stats')
      },
      series: [
        {
          name: 'Usage',
          color: '#335b83',
          type: 'line',
          data: series.data
        }, {
          name: 'Average',
          color: '#4a9de4',
          type: 'spline',
          marker: { enabled: false },
          data: (function() {
            var i,
                points = [],
                n = series.data.length;
            for (i = 0; i < n; i++) {
              points.push({
                x: series.data[i].x,
                y: Math.round(series.average * 100) / 100
              });
            }
            return points;
        }())
      }],
      tooltip: getServerStatTooltip(series, true)
    }, options));
  }


  /* Draw chart of disk usage stats with server history events added as markers
   * on the line.
   * Args:
   *     startTime: epoch seconds
   *     interval: seconds between each x value
   *     diskUsageValues: array of float numbers representing disk usage values
   *     serverEvents: array of event objects
   *     options: Highchart options object
   */
  function drawServerDiskStatsChart(
      startTime, interval, diskUsageValues, serverEvents, options) {
    if (diskUsageValues === undefined) {
        diskUsageValues = [];
    }

    // array of event objects sorted chronologically
    var serverEventsSorted = _.sortBy(serverEvents, 'epoch_ms');
    var series = seriesData(startTime, interval, diskUsageValues, serverEventsSorted, false);

    $('#disk-container').highcharts(_.merge({
      subtitle: {
        text: gettext('Disk Stats')
      },
      series: [
        {
          name: 'Rate',
          color: '#335b83',
          type: 'line',
          data: series.data
        }, {
          name: 'Average',
          color: '#4a9de4',
          type: 'spline',
          marker: { enabled: false },
          data: (function() {
            var i,
                points = [],
                n = series.data.length;
            for (i = 0; i < n; i++) {
              points.push({
                x: series.data[i].x,
                y: series.average
              });
            }
            return points;
        }())
      }],
      tooltip: getServerStatTooltip(series, false)
    }, options));
  }


  /* Draw chart of network stats with server history events added as markers
   * on the line.
   * Args:
   *     startTime: epoch seconds
   *     interval: seconds between each x value
   *     netUsageValues: array of float numbers representing network usage
   *     serverEvents: array of event objects
   *     options: Highchart options object
   */
  function drawServerNetStatsChart(
      startTime, interval, netUsageValues, serverEvents, options) {
    if (netUsageValues === undefined) {
        netUsageValues = [];
    }

    // array of event objects sorted chronologically
    var serverEventsSorted = _.sortBy(serverEvents, 'epoch_ms');
    var series = seriesData(startTime, interval, netUsageValues, serverEventsSorted, false);

    $('#net-container').highcharts(_.merge({
      subtitle: {
        text: gettext('Network Stats')
      },
      series: [
        {
          name: 'Throughput',
          color: '#335b83',
          type: 'line',
          data: series.data
        }, {
          name: 'Average',
          color: '#4a9de4',
          type: 'spline',
          marker: { enabled: false },
          data: (function() {
            var i,
                points = [],
                n = series.data.length;
            for (i = 0; i < n; i++) {
              points.push({
                x: series.data[i].x,
                y: series.average
              });
            }
            return points;
        }())
      }],
      tooltip: getServerStatTooltip(series, false)
    }, options));
  }


  /* Make monochrome colors and set them as default for all pies
   *
   * Start with slightly darker than base, end with much brighter.
   */
  function distributeMonochromePieColors(categoryCount) {
    Highcharts.getOptions().plotOptions.pie.colors = (function () {
      var colors = [],
          base = Highcharts.getOptions().colors[0],
          i, b,
          start = -0.2,
          end = 0.4,
          step = categoryCount ? ((end - start) / categoryCount) : 1;

      for (i = 0, b = start; i < categoryCount; i += 1, b += step) {
        //console.log('b: ', b);
        colors.push(Highcharts.Color(base).brighten(b).get());
      }
      return colors;
    }());

    // Return colors in case the caller wants these
    return Highcharts.getOptions().plotOptions.pie.colors;
  }


  /**
    * Bar chart on the Storage Report.
    * Given an array of arrays representing the visible datatable contents,
    * draw a bar chart of each server's storage. This data is taken directly
    * from the datatable.
    */
  function drawStorageChart(rows) {
      console.log(rows);

      var hostnameColumn = 1;
      var storageColumn = 2;

      var categories = [],
          storageSizes = [],
          hostname;

      _.forEach(rows, function(row){
          // Hostname column contains hidden hostname and other HTML; extract
          // the actual hostname
          hostname = $(row[hostnameColumn]).find('.hostname').text();
          categories.push(hostname);
          storageSizes.push(row[storageColumn]);
      });

      var heightPx = 400;
      if (categories.length > 25) {
          heightPx = 600;
      }

      $('#chart_div')
          .highcharts(_.merge(c2.charts.serverBarChartDefaults, {
              chart: {
                  height: heightPx
              },
              plotOptions: {
                series: {
                  animation: false
                }
              },
              title: {
                  text: gettext('Servers by storage')
              },
              xAxis: {
                  categories: categories
              },
              yAxis: {
                  title: { text: gettext('Storage in GB') }
              },
              series: [
                  {
                      name: gettext('Storage in GB'),
                      data: storageSizes
                  }
              ],
              exporting: {
                  enabled: false
              }
          }));
  }

  function buildServerBillingSeries(values) {
    var series = [
            {
              showInLegend: false,
              name: 'Daily Total',
              type: 'spline',
              marker: {enabled: false},
              data: (function () {
                var i, points = [], n = values.length;
                for (i = 0; i < n; i++) {
                  points.push({
                    x: i,
                    y: values[i]
                  });
                }
                return points;
              }()),
            }
          ];
    return series;
  }

  function buildSeriesFromObject(valuesBySeriesName, type) {
    // Build an array of series objects from a dictionary/Obj of values by series name.
    var series = [];
    var n = 0;

    for (var name in valuesBySeriesName) {
      var values = valuesBySeriesName[name];
      var series_x = {
        name: name,
        type: type,
        marker: {enabled: false},
        data: (function () {
          var i, points = [], n = values.length;
          for (i = 0; i < n; i++) {
            points.push({
              x: i,
              y: values[i]
            });
          }
          return points;
        }())
      };

      series[n] = series_x;
      n++;
    }
    return series;
  }

  function buildGroupBillingBarSeries(valuesBySeriesName) {
    // Build an array of series objects from a dictionary/Obj of values by series name.
    var series = [];
    var n = 0;

    for (var name in valuesBySeriesName) {
      var values = valuesBySeriesName[name];
      var series_x = {
        name: name,
        data: (function () {
          var i, points = [], n = values.length;
          for (i = 0; i < n; i++) {
            points.push(values[i]);
          }
          return points;
        }())
      };

      series[n] = series_x;
      n++;
    }
    return series;
  }

  // Vary chart container height based on number of categories.
  // Intended for charts with horizontal bars.
  function containerHeight(numCategories) {
    var pxPerCategory;

    // Slightly more dense layout as the number of categories increases.
    if (numCategories < 40) {
      pxPerCategory = 30; // Nice and spacious, max 1200px high
    } else {
      if (numCategories < 80) {
        pxPerCategory = 20; // More compact and max 1600px high
      } else {
        pxPerCategory = 15; // Very compact and no max height
      }
    }

    var minContainerHeight = 400;
    var containerHeight = pxPerCategory * numCategories;
    if (containerHeight < minContainerHeight) {
      containerHeight = minContainerHeight;
    }

    return containerHeight;
  }




  // expose public functions
  c2.charts = {
    exportChartAsPNG: exportChartAsPNG,
    serverBarChartDefaults: serverBarChartDefaults,
    serverPieChartDefaults: serverPieChartDefaults,
    billingSeriesDefaults: billingSeriesDefaults,
    // Server stat charts with history events
    commonStatChartOpts: commonStatChartOpts,
    diskStatChartOpts: diskStatChartOpts,
    netStatChartOpts: netStatChartOpts,
    getCategoriesAsDates: getCategoriesAsDates,
    containerHeight: containerHeight,
    buildSeriesFromObject: buildSeriesFromObject,
    buildGroupBillingBarSeries: buildGroupBillingBarSeries,
    buildServerBillingSeries: buildServerBillingSeries,
    distributeMonochromePieColors: distributeMonochromePieColors,
    drawServerCPUStatsChart: drawServerCPUStatsChart,
    drawServerMemStatsChart: drawServerMemStatsChart,
    drawServerDiskStatsChart: drawServerDiskStatsChart,
    drawServerNetStatsChart: drawServerNetStatsChart,
    drawStorageChart: drawStorageChart,
    bar: bar,
    pie: pie,
    // There's at least 1 case where we only want to use the exporting
    // options, not all of the defaults
    exportingOptions: exportingOptions
  };

})(window.c2, window.$, window._, window.Highcharts);

/* A module that enables our ZeroClipboard buttons and returns an object with
 * an `activateClipboardButtons` method.
 *
 * Automatically activates the buttons on page load. If you need to activate
 * the buttons again because you added more markup to the page, call
 * `c2.clipboard.activateClipboardButtons()`.
 *
 * The clipboard button must have class '.clipboard-button' and an attribute
 * 'data-clipboard-target' whose value is the id of a target element that
 * contains the text to be copied.
 */
(function(c2, $) {
  "use strict";

  /*
   * Initialize. Called by c2.init after c2.settings has been defined.
   */
  function init() {
    activateClipboardButtons();
  }

  /* Indicate to user that text was copied.
   */
  $(".clipboard-button").tooltip({
    trigger: "click",
    placement: "bottom"
  });

  function setTooltip(btn, message) {
    $(btn)
      .tooltip("hide")
      .attr("data-original-title", message)
      .tooltip("show");
  }

  function hideTooltip(btn) {
    setTimeout(function() {
      $(btn).tooltip("hide");
    }, 1000);
  }

  // activate clipboard buttons
  function activateClipboardButtons() {

    const clipButtons = document.getElementsByClassName("clipboard-button");
    const clipboard = new ClipboardJS(clipButtons);

    clipboard.on("success", function(e) {
      setTooltip(e.trigger, "Copied!");
      hideTooltip(e.trigger);
    });

    clipboard.on("error", function(e) {
      setTooltip(e.trigger, "Did not copy.");
      hideTooltip(e.trigger);
    });

    return clipboard;
  }

  // return an object that contains our public functions
  c2.clipboard = {
    activateClipboardButtons: activateClipboardButtons,
    init: init
  };
})(window.c2, $);

/* Collapsible panel state persistence. */

(function (c2) {
  'use strict';

  /**
   * Persist state of collapsible panels in localStorage.
   *
   * All [data-toggle=collapse] elements within `container`, a selector or
   * jQuery object, will have their state immediately restored and persisted on
   * change.
   */
  function init(container) {
    var cacheKey = key();
    var $container = $(container);

    // Build a list of IDs for collapsible elements
    var collapsibleIDs = $container.find('[data-toggle="collapse"]').map(function() {
      return $(this).data('target');
    }).get();

    // Restore state before hooking up shown/hidden event handler
    restoreCollapsedStateOfItems(cacheKey, $container);
    // Add collapsed to panel if not opened.
    _.forEach(collapsibleIDs, function (id) {
      if(!$(id).hasClass('in')) {
        $('[data-target="' + id + '"]').addClass("collapsed");
      }
    });
    $container.on('shown.bs.collapse hidden.bs.collapse', function () {
      cacheCollapsedStateOfItems(cacheKey, collapsibleIDs);
    });
  }

  // Generate a unique cache key for this page
  function key() {
    return 'c2.collapsible' + window.location.pathname;
  }

  function getOpenCollapsibles(itemIDs) {
    return _.filter(itemIDs, function(item) {
      return $(item).hasClass('in');
    });
  }

  function cacheCollapsedStateOfItems(cacheKey, itemIDs) {
    var openItems = getOpenCollapsibles(itemIDs);

    localStorage.setItem(cacheKey, JSON.stringify(openItems));
  }

  function restoreCollapsedStateOfItems(cacheKey, container) {
    var openItems = localStorage.getItem(cacheKey);
    // If initial load open all panels
    if (openItems === undefined || openItems === null) {
      if(container.attr('class') === 'admin'){
        $('.panel-body').addClass('in');
      }
      return;
    }
    var panelIDs = JSON.parse(openItems);
    var $panelBody;

    if (panelIDs && panelIDs.length) {
      _.forEach(panelIDs, function(panelID) {
        $panelBody = $(panelID);

        if ($panelBody.length) {
          $panelBody.addClass("in");
          // Trigger the show event so any global handlers can do their thing
          $panelBody.trigger("show.bs.collapse");

          // Update the collapse trigger so the indicator is correct
          $('[data-target="' + panelID + '"]').removeClass("collapsed");
        } else {
          // Silently ignore panels with persisted state that do not currently
          // exist in the DOM. This can happen when a panel was on a different page
          // of a DataTable, for example.
        }
      });
    }
  }


  // Expose public functions
  c2.collapsible = {
    init: init
  };

})(window.c2);

/*
 * Combobox: widgets that combine dropdown functionality with auto-complete,
 * using selectize.js and whatever else is useful.
 */

(function (c2, _) {
  'use strict';

  /*
   * Chain two selectized controls together.
   *
   * Usage:
   *   c2.combobox.chain('#select1', '#select2', '/s2-data/<%=value%>/',
   *                     {valueField: 'id', labelField: 'name'})
   *
   * Args:
   *   select1 & select2: selectors for the 2 select elements
   *   dataUrl: string for URL from which the 2nd combobox will be loaded,
   *            in lodash.template format and with optional 'value' placeholder,
   *            which will be the value of the first combobox.
   *            GETing the URL should return a JSON list of option objects like:
   *                [{'field-name-1': 'value-1', 'field-name-2': 'value-2'}, ...]
   *   s2options: options object for the select2 selectize.
   *       Specify at least the valueField name, probably also the labelField.
   *       If not specified, the sort and search fields default to using the user-visible
   *       field.
   *       sortField: object or list of objects to control option sorting.
   *           (see https://github.com/brianreavis/sifter.js#sifterjs)
   *       searchField: name or list of field names to search as user types.
   */
  function chain(select1, select2, dataUrl, s1options, s2options) {
      var $select1 = $(select1);
      var $select2 = $(select2);
      var selectize2;
      var urlTemplate = _.template(dataUrl);

      // Set defaults for sorting and searching by what the user sees
      // (labelField or valueField).
      var defaultLabelField = s2options.labelField || s2options.valueField || undefined;
      var selectize2DefaultOptions = {
        labelField: defaultLabelField,
        sortField: {
          field: defaultLabelField,
          direction: 'asc'
        },
        searchField: [defaultLabelField]
      };
      _.defaults(s2options, selectize2DefaultOptions);

      c2.selectize(select2, s2options);
      selectize2 = $select2[0].selectize;

      /* This is from the selectize docs
       * (https://github.com/brianreavis/selectize.js/blob/master/examples/cities.html),
       * but with the addition of rendering the microtemplate for the URL given
       * the value of the first select.
       */
      var xhr;
      function loadS2(value, callback, options) {
          options = _.defaults(options || {}, {
              focusOnLoad: true
          });

          xhr && xhr.abort();
          var url = urlTemplate({value: value});
          xhr = $.ajax({
              url: url,
              success: function(results) {
                  selectize2.enable();
                  callback(results);
                  if (options.focusOnLoad) {
                      selectize2.focus();
                  }
              },
              error: function() {
                  callback();
              }
          });
      }

      /*
       * Hook up the change handler to reload s2 when s1 changes.
       */

      // A Selectize onChange callback for triggering the loading of values for
      // the second select when the first select is changed.
      // https://github.com/brianreavis/selectize.js/blob/master/docs/usage.md#callbacks
      function onSelectize1Change(value, options) {
          if (!value.length) return;
          selectize2.disable();
          selectize2.clearOptions();
          selectize2.load(function(callback) {
              loadS2(value, callback, options);
          });
      }

      c2.selectize(select1, _.defaults(s1options, {
          onChange: onSelectize1Change
      }));


      /*
       * Initialize s2 if s1 has an initial value; otherwise disable.
       */
      selectize2.disable();
      var select1Val = $select1.val();
      if (select1Val) {
          onSelectize1Change(select1Val, {focusOnLoad: false});
      }
  }

  c2.combobox = {
    chain: chain
  };

})(window.c2, window._);

// Common behaviors

(function (__module__, c2) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);
  var globalKeyHandlerMapping = {};


  /**
   * Set up general purpose click handler for controls that want to POST on
   * click. This provides a lightweight AJAX interaction.
   *
   * The server side view should respond with a JSON object having one of
   *   redirectURL: URL to load next (not technically a redirect)
   *   success: message to be displayed as a 'success' alert
   *   error: message to be displayed as a 'danger' alert
   *
   * By default, calling this applies to all elements with data-post="click".
   * An optional selector may be specified intead.  Click handler is attached
   * at the document level and triggered via delegation.
   *
   * Required attrs on target element, one of:
   *   data-post-url: where to POST to
   *   href (for anchors)
   *
   * Optional:
   *   data-post-data: object/dict to post
   *   data-post-callback: a function to be called after the request completes
   *     Args:
   *        response: the response object
   *        $target: the click target. This is useful for making DOM changes
   *   data-silence-alerts: if truthy, alerts for server-side 'success' and
   *        'error' messages will not be shown
   */
  function enablePostOnClick(selector) {
    $(document).on('click', selector || '[data-post=click]', function (e) {
        e.preventDefault();

        var $target = $(this);
        var callback = $target.data('post-callback');

        $.post(
          $target.data('post-url') || $target.attr('href'),
          $target.data('post-data') || {},
          function (response) {

            if (callback) {
              // Provide the callback with an indication of whether the request
              // succeeded or not, and pass the target element.
              callback(response, $target);
            }

            if (response.redirectURL) {
              window.location.href = response.redirectURL;
            }
            if ($target.data('silence-alerts')) {
              return;
            }
            if (response.success) {
              c2.alerts.addGlobalAlert(response.success, 'success', true);
            }
            if (response.error) {
              c2.alerts.addGlobalAlert(response.error, 'error', true);
            }
        });
    });
  }


  /**
   * Set up a document-wide event handler on panel expansion to instantiate Ace editor.
   */
  function aceOnPanelOpen() {
    var $panelBody;

    $(document).on('show.bs.collapse', function(e) {
      $panelBody = $(e.target);
      c2.ace.initializeAceInPanel($panelBody);
    });
  }


  // Initialize Bootstrap popovers.
  // http://getbootstrap.com/javascript/#popovers
  //
  // We extend behavior to allow declaring popover content by referencing
  // the content of another element with the `data-content-selector` attribute.
  function popovers() {
    $('body').popover({
      selector: '[data-toggle=popover]',

      /* When no `data-content` attribute is specified, Bootstrap will use this
      * function to find popover content, which returns the content of an
      * element that matches the selector set by a `data-content-selector`
      * attribute. Example:
      *
      *      <button
      *          data-toggle="popover"
      *          data-html="true"
      *          data-content-selector="#rocking-content">
      *              A Popover Button
      *      </button>
      *      <div class="popover-content-el" id="rocking-content">
      *          This popover content <strong>rocks</strong>!
      *      </div>
      *
      * Adding the `popover-content-el` class to the popover content element
      * will cause it to be hidden from view.
      */
      content: function () {
        console.debug("Finding popover content for this target: ", this);
        var contentSelector = $(this).data('contentSelector');
        if (! contentSelector) {
          console.error(
            'Cannot find content because neither a `data-content` ' +
            'nor a `data-content-selector` attribute was specified.'
          );
          return;
        }

        var contentEl = document.querySelector(contentSelector);
        if (! contentEl) {
          console.error(
            'Cannot find content because a content element matching selector `' +
            contentSelector + '` cannot be found'
          );
          return;
        }

        return contentEl.innerHTML;
      },
    });
  }


  /*
   * Lets c2 modules register their own global key handlers (keyup events bound
   * to the document rather than a specific element).
   *
   * Args:
   *   namespace: string must be provided to facilitate management of bound handlers.
   *   keyHandlerMapping: an object whose keys are event.key values (or
   *     event.keyCode for compatibility with some browsers) and whose values
   *     are handler functions.
   *
   * E.g.
   *    registerGlobalKeyHandlers('activityCenter', {'a': toggleActivityCenterSidebar});
   *    registerGlobalKeyHandlers('bookmarks', {
   *      '.': bookmarkThisPage,
   *      'g': toggleBookmarksMenu,
   *      'Escape': closeBookmarksMenuIfOpen,
   *      default: goToBookmarkIfNumeric
   *    });
   *
   * Handlers will only be called if the user is not typing in a form field.
   *
   * A module may register a "default" handler for any keyup events that do not
   * match any of its specific keys. This is context dependent: e.g. bookmarks
   * relies on a default handler to see if a user has typed a number 1-9 and
   * handles that, **but only** if the bookmarks menu is open. Default handlers
   * receive a lot of events, so should always be careful to check the context
   * of the event.
   *
   * Each event handler function gets a single parameter - the event object. If
   * it decides to handle the event, it MUST call event.preventDefault() to
   * prevent any further global keyup handlers from running.
   *
   * E.g.
   * - bookmarks registers a handler for 'Escape' that only fires if the bookmarks menu is open.
   * - search also registers a handler for 'Escape' that only fires if the search menu is open.
   *
   * All handlers should call event.preventDefault() to prevent further global
   * keyup handlers for this key from running.
   */
  function registerGlobalKeyHandlers(namespace, keyHandlerMapping) {
    if (globalKeyHandlerMapping[namespace] === undefined) {
      // First time handlers for this namespace are registered
      globalKeyHandlerMapping[namespace] = keyHandlerMapping;

    } else {
      // Not the first time handlers have been registered for this namespace;
      // add new handlers but only allow one per key.
      for (var key in keyHandlerMapping) {
        globalKeyHandlerMapping[namespace][key] = keyHandlerMapping[key];
      }
    }

    // Need to re-bind using new generated handlerForNamespace function;
    // otherwise the handler for this namespace or another has gone out of
    // scope due to the above changes.
    bindGlobalKeyHandlers();
  }


  /*
   * Unbind and rebind all global registered document-wide keyup event handlers.
   */
  function bindGlobalKeyHandlers() {
    for (var namespace in globalKeyHandlerMapping) {
      var handlerForNamespace = getKeyHandler(namespace);

      // Binding to keyup because it does not repeat like keydown can, triggering excessive events.
      // Prefix with .global namespace to enable adding other keyup handlers on these namespaces.
      $(document).off('keyup.global.' + namespace);
      $(document).on('keyup.global.' + namespace, handlerForNamespace);
    }
  }


  /*
   * Return keyup handler that handles keys for this namespace.
   */
  function getKeyHandler(namespace) {
    return function(e) {
      if (isUserTypingInField(e) || c2.dialogs.isOpen()) {
        return;
      }

      var keyHandlers = globalKeyHandlerMapping[namespace];
      // Use the newer `key` if available, otherwise `keyCode` which is deprecated
      var typed = e.key || e.keyCode;
      var foundHandlerForKey = false;

      logger.debug('Look for "'+ typed +'" keyup.global.'+ namespace +' handler');

      // Just because a handler is listening for some key does not mean
      // it'll actually handle it.  E.g. A bookmarks handler may only
      // handle 'Escape' if the bookmarks submenu is open, while search
      // handler may do the same for the search submenu.
      //
      // If a prior handler (in this or another namespace) prevented the
      // default event for this key, using e.preventDefault(), that means
      // it handled it so do not call any further handlers.
      if (e.isDefaultPrevented()) {
        logger.debug('  Event default was already prevented so skipping handlers in this namespace');
        return;
      }
      logger.debug('  active element:', document.activeElement);

      // Loop over list of key-to-handler mappings for this namespace
      for (var key in keyHandlers) {
        if (typed == key) {
          logger.debug('  Found a handler and calling it');
          keyHandlers[key](e);
          foundHandlerForKey = true;

          // Only one handler per key in a namespace
          break;
        }
      }

      // No handlers matched; call the default handler if one is defined.
      if (!e.isDefaultPrevented() && !foundHandlerForKey && keyHandlers.default !== undefined) {
        logger.debug('  Calling default handler in namespace "'+ namespace +'"');
        keyHandlers.default(e);
      }
    };
  }


  /*
   * Given a keyup event, return true if the user is typing in certain fields, meaning
   * keystrokes should be ignored by global key event handlers.
   */
  function isUserTypingInField(e) {
    var _focused = document.activeElement;
    var _focusedTagName = _focused.tagName.toLowerCase();

    // Select and selectize dropdowns capture key events before this one, so
    // don't need to be included.
    if (_focusedTagName==="textarea" || _focusedTagName==="input") {
      return true;
    }

    // Other logic?
    return false;
  }


  c2[__module__] = {
    aceOnPanelOpen: aceOnPanelOpen,
    enablePostOnClick: enablePostOnClick,
    popovers: popovers,
    bindGlobalKeyHandlers: bindGlobalKeyHandlers,
    isUserTypingInField: isUserTypingInField,
    registerGlobalKeyHandlers: registerGlobalKeyHandlers
    // TODO: move c2.toggles.enablePostOnChange here
  };
})('commonEventHandlers', window.c2);

/*
 * Functions for setting up the Custom Resource Report filters.
 */

(function (c2, $) {
  'use strict';

  function init(formsetPrefix) {
    // For more info, see the BestPractice marker in
    // 'templates/reports/internal/custom_server_report_filters.html'
    //
    $('#filters tbody tr').formset({
      addLabel: '<span class="icon-add"></span> ' + gettext('Add a Filter'),
      addClass: 'btn btn-default',
      added: filterAdded,

      hideRemovedRows: true,
      showDeleteAllLink: false,

      // These 2 options allow multiple formsets on the same page.
      formCssClass: 'server-filter-form',
      // Django formset must be instantiated with same prefix value.
      prefix: formsetPrefix
    });
  }


  function filterAdded(row) {
      var $row = $(row);

      setupFieldStylesAndBehaviors($row);
  }


  function setupFieldStylesAndBehaviors($row) {
    // Enable any dynamic behaviors on those new fields now
    $row.find('.render_as_datepicker').datepicker({dateFormat: 'yy-mm-dd'});

    // Style plain input field with Bootstrap styles
    $row.find('input').addClass('form-control');

    // Selectize dropdowns
    $row.find('td select').each(function() {
      c2.selectize($(this));
    });
  }


  function reloadFormOnAttrChange(formURL) {
    $('#filters').on('change', 'td.attr select', function(e) {
      // Load this filter form again; this time `attr` has a value so
      // the form's __init__ will determine the widget and choices for
      // `values` field, if any.
      var attr = $(this).val();
      if (attr === undefined) {
        return;
      }

      var $row = $(this).closest('tr');
      c2.block.block($row);

      $.get(formURL, {'attr': attr}, function(result) {

        replaceField($row, 'td.operator', result.operator);
        replaceField($row, 'td.values', result.values);

        setupFieldStylesAndBehaviors($row);

        c2.block.unblock($row);

      }).fail(function(response) {
        $row.html('<td colspan=4 class=error>' + gettext('Something went wrong. Please try again.') + '</td>');
        c2.block.unblock($row);
      });
    });
  }


  function replaceField($row, cellSelector, newFieldHtml) {
    var $cell = $row.find(cellSelector);
    var $old = $cell.find('input,select');
    var $new = $(newFieldHtml);
    $new.attr('id', $old.attr('id'));
    $new.attr('name', $old.attr('name'));
    $cell.html($new);
  }


  /**
   * Run the Report by posting all form data. If format is not specified, requests 'json' which
   * causes the report view to return JSON data as table HTML. If 'csv' format is specified,
   * the report view returns CSV data and a file download is triggered.
   */
  function runReport(url, format) {
    var $form = $('form#custom-resource-report-form');
    var data = $form.serializeArray();
    data.push({name: 'format', value: format || 'json'});

    c2.block.block($('#report-container'));

    $.post(url, data, function(response) {

      if (response.table) {
        var $table = $(response.table);
        $('#report-container').html($table);

      } else if (response.export) {
        c2.downloads.startDownloadFromContent(response.export, response.filename);

      } else if (response.errors) {
        _.forEach(response.errors, function(errors, index) {
          console.log('index: ', index);
          console.log('errors: ', errors);
        });
      }

      c2.block.unblock($('#report-container'));
    });
  }


  window.c2.customResourceReport = {
    init: init,
    reloadFormOnAttrChange: reloadFormOnAttrChange,
    runReport: runReport,
    setupFieldStylesAndBehaviors:setupFieldStylesAndBehaviors
  };

})(window.c2, window.jQuery);

/*
 * Functions for setting up the Custom Server Report filters.
 */

(function (c2, $) {
  'use strict';

  function init(formsetPrefix) {
    // For more info, see the BestPractice marker in
    // 'templates/reports/internal/custom_server_report_filters.html'
    //
    $('#filters tbody tr').formset({
      addLabel: '<span class="icon-add"></span> ' + gettext('Add a Filter'),
      addClass: 'btn btn-default',
      added: filterAdded,

      hideRemovedRows: true,
      showDeleteAllLink: false,

      // These 2 options allow multiple formsets on the same page.
      formCssClass: 'server-filter-form',
      // Django formset must be instantiated with same prefix value.
      prefix: formsetPrefix
    });
  }


  function filterAdded(row) {
      var $row = $(row);

      setupFieldStylesAndBehaviors($row);
  }


  function setupFieldStylesAndBehaviors($row) {
    // Enable any dynamic behaviors on those new fields now
    $row.find('.render_as_datepicker').datepicker({dateFormat: 'yy-mm-dd'});

    // Style plain input field with Bootstrap styles
    $row.find('input').addClass('form-control');

    // Selectize dropdowns
    $row.find('td select').each(function() {
      c2.selectize($(this));
    });
  }


  function reloadFormOnAttrChange(formURL) {
    $('#filters').on('change', 'td.attr select', function(e) {
      // Load this filter form again; this time `attr` has a value so
      // the form's __init__ will determine the widget and choices for
      // `values` field, if any.
      var attr = $(this).val();
      if (attr === undefined) {
        return;
      }

      var $row = $(this).closest('tr');
      c2.block.block($row);

      $.get(formURL, {'attr': attr}, function(result) {

        replaceField($row, 'td.operator', result.operator);
        replaceField($row, 'td.values', result.values);

        setupFieldStylesAndBehaviors($row);

        c2.block.unblock($row);

      }).fail(function(response) {
        $row.html('<td colspan=4 class=error>' + gettext('Something went wrong. Please try again.') + '</td>');
        c2.block.unblock($row);
      });
    });
  }


  function replaceField($row, cellSelector, newFieldHtml) {
    var $cell = $row.find(cellSelector);
    var $old = $cell.find('input,select');
    var $new = $(newFieldHtml);
    $new.attr('id', $old.attr('id'));
    $new.attr('name', $old.attr('name'));
    $cell.html($new);
  }


  /**
   * Run the CSR by posting all form data. If format is not specified, requests 'json' which
   * causes the report view to return JSON data as table HTML. If 'csv' format is specified,
   * the report view returns CSV data and a file download is triggered.
   */
  function runReport(url, format) {
    var $form = $('form#custom-server-report-form');
    var data = $form.serializeArray();
    data.push({name: 'format', value: format || 'json'});

    c2.block.block($('#report-container'));

    $.post(url, data, function(response) {

      if (response.table) {
        var $table = $(response.table);
        $('#report-container').html($table);

      } else if (response.export) {
        c2.downloads.startDownloadFromContent(response.export, response.filename);

      } else if (response.errors) {
        _.forEach(response.errors, function(errors, index) {
          console.log('index: ', index);
          console.log('errors: ', errors);
        });
      }

      c2.block.unblock($('#report-container'));
    });
  }


  window.c2.customServerReport = {
    init: init,
    reloadFormOnAttrChange: reloadFormOnAttrChange,
    runReport: runReport,
    setupFieldStylesAndBehaviors:setupFieldStylesAndBehaviors
  };

})(window.c2, window.jQuery);

/* DataTables plugins */

// 4-button pagination control with Bootstrap style glyphicons
$.extend($.fn.dataTableExt.oPagination, {
  "bootstrap_four_button": {

    "fnInit": function(oSettings, nPaging, fnDraw) {
      var oLang = oSettings.oLanguage.oPaginate;
      var pageButton = _.template(
        '<a class="<%= action %> btn btn-default" data-action="<%= action %>"' +
        '  title="<%= title %>"' +
        '  data-toggle="tooltip" ' +
        '  data-html="true" ' +
        '  tabindex="0">' +
        '  <span class="glyphicon glyphicon-<%= icon %>"></span>' +
        '</a>'
      );
      var iconButtonGroup =
        '<span class="btn-group">' +
        pageButton({action: 'first', icon: 'step-backward', title: gettext('First page')}) +
        pageButton({action: 'previous', icon: 'play mirror-horizontally', title: gettext('Previous page')}) +
        pageButton({action: 'next', icon: 'play', title: gettext('Next page')}) +
        pageButton({action: 'last', icon: 'step-forward', title: gettext('Last page')}) +
        '</span>';

      $(nPaging).append(iconButtonGroup);

      // Support keyboard control of pagination links
      $('a', nPaging).on('keydown.DT', function(e) {
        if (e.isDefaultPrevented()) {
          return;
        }

        switch (e.key) {
          case 'Enter':
          case ' ':
            $(this).click();
            break;
        }
      });

      // Pass the anchor's data-action attr to _fnPageChange
      $('a', nPaging).on('click.DT', function (e) {
        e.preventDefault();
        if (oSettings.oApi._fnPageChange(oSettings, $(this).data('action'))) {
          fnDraw(oSettings);
        }
      });
    },

    "fnUpdate": function (oSettings, fnDraw) {
      var oPaging = oSettings.oInstance.fnPagingInfo();
      var onFirstPage = oPaging.iPage === 0;
      var onLastPage = (oPaging.iTotalPages === 0 || oPaging.iPage === oPaging.iTotalPages - 1);
      // There may be more than one set of paging controls per table
      var pagers = oSettings.aanFeatures.p;

      for (var i = 0; i < pagers.length; i++) {
        // Enable/disable pager buttons based on current page
        $('.first, .previous', pagers[i]).toggleClass('disabled', onFirstPage);
        $('.next, .last', pagers[i]).toggleClass('disabled', onLastPage);
      }
    }

  }
});


/*
API plugins from http://datatables.net/plug-ins/api
*/

jQuery.fn.dataTableExt.oApi.fnProcessingIndicator = function ( oSettings, onoff ) {
    if( typeof(onoff) == 'undefined' ) {
      onoff=true;
    }
    this.oApi._fnProcessingDisplay( oSettings, onoff );
};


jQuery.fn.dataTableExt.oApi.fnPagingInfo = function ( oSettings ) {
  return {
    "iStart":         oSettings._iDisplayStart,
    "iEnd":           oSettings.fnDisplayEnd(),
    "iLength":        oSettings._iDisplayLength,
    "iTotal":         oSettings.fnRecordsTotal(),
    "iFilteredTotal": oSettings.fnRecordsDisplay(),
    "iPage":          Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
    "iTotalPages":    Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
  };
};

/* Example usage */
/*
$(document).ready(function() {
    $('#example').dataTable( {
        "fnDrawCallback": function () {
        alert( 'Now on page'+ this.fnPagingInfo().iPage );
      }
    } );
} );
*/


/* Change number of rows being displayed by pagination plugin */
jQuery.fn.dataTableExt.oApi.fnLengthChange = function ( oSettings, iDisplay ) {
    oSettings._iDisplayLength = iDisplay;
    oSettings.oApi._fnCalculateEnd( oSettings );

    /* If we have space to show extra rows (backing up from the end point - then do so */
    if ( oSettings._iDisplayEnd == oSettings.aiDisplay.length ) {
        oSettings._iDisplayStart = oSettings._iDisplayEnd - oSettings._iDisplayLength;
        if ( oSettings._iDisplayStart < 0 ) {
            oSettings._iDisplayStart = 0;
        }
    }

    if ( oSettings._iDisplayLength == -1 ) {
        oSettings._iDisplayStart = 0;
    }

    oSettings.oApi._fnDraw( oSettings );

    if ( oSettings.aanFeatures.l ) {
        $('select', oSettings.aanFeatures.l).val( iDisplay );
    }
};


/* Return a list of input values for all selected table rows.
 *
 * First try using the table data of selected row values, if defined, rather
 * than by CSS class 'selected'. This is the case for Ajax tables where some
 * selected rows may not be in the dataTable object at all.
 */
jQuery.fn.dataTableExt.oApi.getSelectedValues = function (oSettings, onoff) {
  var $table = $(this).dataTable();

  // Are selected rows being tracked as data on the table element?
  var values = $table.data('selectedRows');
  if (values !== undefined) {
    return values;
  }

  // Fall back to using the traditional way of finding all selected rows
  var selectedRows = $table.$('tr.selected');
  // Clickable DataTables have first column cells containing input.selector elements,
  // so find them all and make a list of their values.
  return selectedRows.find("input.selector")
    .map(function(index) {return $(this).val();}).toArray();
};


jQuery.fn.dataTableExt.oApi.countSelectedRows = function ( oSettings, onoff ) {
  var $table = $(this).dataTable(),
      byClass = $table.$('tr.selected'),
      // DataTables using server side processing may have some selected rows on pages not loaded
      // into the dataTable object. That means the above search for selected
      // rows won't work. Instead, our custom clickable datatable behavior
      // saves selected rows as a data property on the table.
      byData = $table.data('selectedRows'),
      numSelected = (byData !== undefined) ? byData.length : byClass.length;
  return numSelected;
};


jQuery.fn.dataTableExt.oApi.isServerSide = function (oSettings) {
  return (oSettings.sAjaxSource !== undefined && oSettings.sAjaxSource !== null);
};


// DataTables plugin to unselect all rows.
jQuery.fn.dataTableExt.oApi.clearSelection = function (oSettings, onoff) {
  var $table = $(this).dataTable();

  // unselect/uncheck all visible rows and clear the cached selection list
  $table.$('td:eq(0) input:checked').prop('checked', false);
  $table.$('tr.selected').removeClass('selected');

  // clear the data structure used to remember row selection in Ajax tables
  $table.isServerSide() && $table.data('selectedRows', []);

  // refresh the badge
  $table.fnUpdateSelectionInfo();

  // ensure the batch checkbox at top of first column is updated
  c2.forms.updateBatchCheckboxes($table);

  // invoke any callbacks registered on the table object via data attr 'on-selection-changes'
  _.forEach($table.data('on-selection-change'), function (callback) {
    callback($table);
  });
};


jQuery.fn.dataTableExt.oApi.isSingleSelect = function (oSettings, onoff) {
  var $table = $(this).dataTable();

  return $table.$('td:eq(0) input:radio').length > 0;
};


/* For tables whose rows may be selected by the user, update the number of
 * selected rows in an informational area. This counts selections across all
 * rows, not just visible rows.
 */
jQuery.fn.dataTableExt.oApi.fnUpdateSelectionInfo = function (oSettings, onoff) {
  var $table = $(this).dataTable();

  // Do not show selection info for single-select tables (i.e. radio buttons)
  if ($table.isSingleSelect()) {
    return;
  }

  var numSelected = $table.countSelectedRows();
  var $wrap = $table.closest('.dataTables_wrapper');
  var $toolbar = $wrap.find('.dataTables_toolbar');

  // Create the badge element if needed; custom selection-info element may
  // provide completely different markup (e.g. dropdown menu)
  var $info = $wrap.find('.selection-info');
  if ($info.length === 0) {
    return;
  }

  // find all controls that are identified to work when there is an active selection
  var $actionButtons = $toolbar.find('.selection-action');

  if (numSelected > 0) {
    $info.addClass('active-selection');
    $actionButtons.removeClass('disabled');
  } else {
    $info.removeClass('active-selection');
    $actionButtons.addClass('disabled');
  }

  var $count = $wrap.find('.selection-info .selection-count');
  $count.html(numSelected);
};


/* Add a delay to the firing of DataTables search box. Gives user a chance to
 * type more letters before requesting results in a server-side table.
 *
 * Taken from http://datatables.net/plug-ins/api/fnSetFilteringDelay
 */
jQuery.fn.dataTableExt.oApi.fnSetFilteringDelay = function (oSettings, iDelay) {
  var _that = this;

  if (iDelay === undefined) {
    iDelay = 250;
  }
  //console.log('delaying '+ String(iDelay) +'ms');

  this.each( function (i) {
    $.fn.dataTableExt.iApiIndex = i;
    var $this = this,
        oTimerId = null,
        sPreviousSearch = null,
        anControl = $('input[type="search"]', _that.fnSettings().aanFeatures.f);

    anControl.unbind('keyup search input').bind('keyup search input', function(e) {
      var $$this = $this;
      var currentSearch = anControl.val();

      // Ignore user tabbing through
      if (e.key == 'Tab') {
        return;
      }

      if (sPreviousSearch === null || sPreviousSearch != currentSearch) {
        window.clearTimeout(oTimerId);
        sPreviousSearch = currentSearch;
        oTimerId = window.setTimeout(function() {
          $.fn.dataTableExt.iApiIndex = i;
          _that.fnFilter(currentSearch);
        }, iDelay);
      }
    });

    return this;
  });
  return this;
};

/* This module sets default options for the jQuery dataTable plugin so that it
 * works well in CB. It also exports more defaults fitting for more specialized
 * cases, such as tables in importation dialogs.
 *
 * One might use specialized defaults like so:
 *
 *    $table.dataTable(_.defaults({
 *        "aoColumnDefs": [
 *            { "bSortable": false, "aTargets": [0] }
 *        ],
 *    }, c2.dataTables.dialogDefaults));
 */

(function (__module__, c2, $, _) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);

  /* Initialize any tables having attribute 'data-table' as dataTables.
   * DataTable options may be specified through the data-table-* API.
   *
   * Args:
   *   selector - optional selector of table(s) to initialize
   *   options - a DataTables options object (optional)
   *
   * The data-table attribute may be empty or specify a predefined "type":
   * - 'dialog': dataTables in dialogs use some common init options, e.g.  that
   *   table state should not be saved.
   * - 'formset': disables some features that don't work well with formsets.
   * - 'checkboxTableDialog': adds options in addition to the default 'dialog'
   *   table type options: fixed height, turns off pagination and info
   *   features, etc. This is used by the common datatable_form_dialog.html
   *   that renders a datatable with a single column.
   *
   * Other data attributes can be used to configure the dataTable:
   *   - data-table-clickable: rows of this table will be highlighted when user clicks anywhere
   *     inside them that is not itself clickable (i.e. a link, input, etc).
   *   - data-clickable-options: override options on the $.clickable plugin, if this table has
   *     data-table-clickable set. Use this to add a customIsClickable function.
   *   - data-table-options: yet another way to specify DataTables options
   *   - data-table-no-auto-init: prevents auto-initialization (when `init` is
   *     called without a specific selector, typically at document load.
   *     Sometimes tables need more involved setup before the init call, to
   *     avoid missing functionality.
   *
   *   - data-table-sort="3,asc": will sort the table by col index 3 in asc order.
   *   - data-table-sort-disabled="9": disables sorting by specific columns.
   *   - data-table-source="/url/to/ajax-data/" will cause table to use server-side
   *     processing and fetch data from that URL.
   */
  function init(selector, options) {
    var $table, type, types = [];
    var selectAllTables = 'table[data-table]';
    options = options || {};

    // By default, initialize all tables with data-table attr
    // TODO: perhaps fail if a selector is given but doesn't match?
    $(selector || selectAllTables).each(function () {
      $table = $(this);

      // Options may be set as a data attribute on the table
      options = _.merge(options, $table.data('table-options'));

      // Avoid re-initializing any dataTables in this collection. Also skip
      // those that do not want to be *auto* initialized, i.e. when init is
      // called without a selector.
      if (isDataTable(this) ||
          ($table.data('table-no-auto-init') !== undefined && !selector)) {
        return;
      }

      type = $table.data('table');
      if (type) {
        types = type.split(' ');
      }

      // Combine various pieces of dataTable option objects into one
      options = _.defaults(options, _.defaults.apply(null, _.filter([
        // Various canned 'types' define a common set of options and can be
        // combined. E.g. data-table="dialog clickable".
        (-1 != types.indexOf('formset')) ? _optionsForFormsetTable($table) : null,
        (-1 != types.indexOf('scrollable')) ? _optionsForScrollableTable($table) : null,
        (-1 != types.indexOf('clickable')) ? _optionsForClickableTable($table) : null,
        (-1 != types.indexOf('dialog')) ? _optionsForDialogTable($table) : null,

        _optionsForSort($table.data('table-sort')),
        _optionsForDataSource($table.data('table-source')),
        _optionsForDataSourceProp($table.data('table-source-prop')),
        _optionsForServerData($table.data('table-fnServerDataCallback')),
        _optionsForServerParams($table.data('table-fnServerParams')),
        c2.dataTables.defaults
        // This isObject test allows these funcs to return null instead of an
        // empty object, significantly simplifying each function.
      ], _.isObject)));

      // Special case for aoColumnDefs because it needs to *extend* existing
      // column defs (e.g. clickable tables disable sorting on the checkbox
      // column).
      options.aoColumnDefs = _optionsForColumnDefs($table.data('table-sort-disabled'), options);

      logger.debug('  table options: ', options);
      $table.dataTable(options);

      // if defined, add a toolbar
      addToolbar($table);

      // Now that the table is initialized, hook up the clickable plugin to
      // reflect any existing selections. This is the case in the Env > Groups
      // > Add dialog, where the table is initialized with related groups
      // selected.
      if (-1 != types.indexOf('clickable')) {
        setupClickableTable($table);
        c2.dialogs.onSubmitSerializeAllSelectedRows($table);
      }
    });
  }


  // Tables that have selectable rows *and* use server-side processing
  // need to keep track of which rows are selected in order to restore
  // those selections on each redraw.

  // Save the value of each selected row in an array, set as data on the
  // dataTable element, so they can be restored. Basically adds all selected
  // rows that are visible to the array, and removes all unselected visible
  // rows.
  function saveSelectedRows($table) {
    var $dt = $table.dataTable(),
        // Get selected rows that are in the DOM. Server-side dataTables may
        // have rows not retrieved by this search that still need to be tracked
        // here as selected.
        $inDomSelectedInputs = $dt.$('td:eq(0) input:checked'),
        $inDomUnselectedInputs = $dt.$('td:eq(0) input:not(:checked)'),
        valuesOld = $table.data('selectedRows') || [],
        values = _.map($inDomSelectedInputs, function(v) { return $(v).val(); }),
        valuesNotSelected = _.map($inDomUnselectedInputs, function(v) { return $(v).val(); });

    values = _.union(values, valuesOld);
    values = _.difference(values, valuesNotSelected);

    $table.data('selectedRows', _.uniq(values));
  }

  // Restore the selected state of all rows that were selected prior to the last
  // server-side request.
  function restoreSelectedRows($table) {
    var $input,
        values = $table.data('selectedRows');

    _.forEach(values, function (val) {
      $input = $table.$('tr').find('input[value='+ val +']');
      if ($input) {
        // Check the input field. This ensures visible rows are shown as
        // selected, and also that they are posted on submit. Ajax tables with
        // remote data will use a different mechanism to actually post those
        // rows on submit, i.e. by sending the stored array in
        // data('selectedRows').
        $input.prop('checked', true);
        $input.closest('tr').addClass('selected');
      }
    });

    $table.fnUpdateSelectionInfo();
  }

  function _optionsForDialogTable($table) {
    return c2.dataTables.dialogDefaults;
  }

  // Formsets currently don't work well with these dataTable features
  function _optionsForFormsetTable($table) {
    return {
      'bFilter': false,
      'bSort': false,
      'bStateSave': false
    };
  }

  // Table presented in a fixed-height container with scrollable content.
  function _optionsForScrollableTable($table) {
    return {
      'bInfo': false,
      'bPaginate': false,
      // Always keep the table height under this value
      'sScrollY': '250px',
      // Make the table shorter if few rows exist
      'bScrollCollapse': false
    };
  }

  // For tables with selectable rows, enables jQuery clickable, adds a tally of
  // selected rows at the top of the table, and persists selected rows in
  // memory. This works even when table data is server-side.
  function setupClickableTable($table) {
    var clickableOptions = {
      onSelect: function(event, $container, $item) {
        // A setTimeout is necessary here to switch to a new event context;
        // without it, saveSelectedRows does not detect checkbox state
        // correctly because onSelect is fired by clickable before its own
        // effects are finished propagating.
        setTimeout(function () {
          $table.isServerSide() && saveSelectedRows($table, $item);
          $table.fnUpdateSelectionInfo();

          // Now call any registered callbacks set as data attrs on the table.
          // The callbacks get two args: the table object and the selected row.
          // This lets tables have additional behavior that fires when
          // selection changes are made.
          _.forEach($table.data('on-selection-change'), function (callback) {
            callback($table, $item);
          });
        }, 0);
      }
    };
    var userOptions = $table.data('clickable-options');

    initializeSelectionInfo($table);
    $table.clickable(_.merge(clickableOptions, userOptions));
    restoreSelectedRows($table);
    $table.fnUpdateSelectionInfo();
  }

  // Tables where first column has checkbox and rows are clickable.
  function _optionsForClickableTable($table) {
    return {
      // checkbox column is not sortable
      'aoColumnDefs': [
        {'bSortable': false, 'aTargets': [0]}
      ],
      // sort by first column after the checkbox
      'aaSorting': [[ 1, 'asc' ]],
      'fnDrawCallback': function (oSettings) {
        var currentSearch = this.fnSettings().oPreviousSearch.sSearch,
            prevSearch = $table.data('prevSearch'),
            searchChanged = (currentSearch != prevSearch);

        // re-setup the row selection behavior
        setupClickableTable($table);

        // When DataTable search is changed, prevent shift-click selection
        // of contiguous rows that may have gotten filtered out.
        if (searchChanged) {
          $table.data('prevSearch', currentSearch);
          $().clickable.forgetPrevClick($table);
        }

        initStandardTableBehaviors($table);

        // Broadcast the 'table:draw' event to any callbacks listenting for it
        // and include the dataTable's settings object.
        $table.trigger('table:draw', this.fnSettings());
        highlightActiveSearch($table);
      }
    };
  }

  /* Return a dataTable options object for initial sorting if sort is
   * defined.
   * - sort="0" -> sort by column 0 in ascending order
   * - sort="0,desc"  -> sort by column 0 in descending order
   * - sort="disabled" -> disable sorting completely
   */
  function _optionsForSort(sort) {
    var column, direction;
    if (sort === undefined) {
      return {
        'order': []
      };
    } else {
      if (sort === 'disabled') {
        return {
          'ordering': false
        };
      }

      sort = String(sort).split(',');
      column = sort[0];
      direction = (sort[1] === undefined) ? "asc" : sort[1];
      return {
        'order': [[ column, direction ]]
      };
    }
  }

  /* Return a dataTable options object for some column definition settings.
   * Adds to any existing aoColumnDefs defined in `options`.
   *
   * Currently these are:
   *
   * - nonSortedCols: single column index or CSV list of indexes that should
   *   *not* be sortable.
   *
   * Support for other column defs may be added later for, e.g. to support
   * column types such as "currency" or "date".
   */
  function _optionsForColumnDefs(nonSortedCols, options) {
    if (nonSortedCols !== undefined) {
      // Create an array of numbers from the string
      var disabledColumns = _.map(String(nonSortedCols).split(','), Number);
      var newDef = {'bSortable': false, 'aTargets': disabledColumns};

      if (options.aoColumnDefs) {
        options.aoColumnDefs.push(newDef);
        return options.aoColumnDefs;
      } else {
        return [newDef];
      }

    }
  }

  /* Return a dataTable options object for data source definition.
   *
   * Server-side JSON source:
   *   data-table-source="/some/url/to/jsondata"
   *
   * JSON string:
   *   data-table-source="[{...}, {...}, ...]"
   *
   * JSON object:
   *   $table.data('table-source', [{...}, {...}, ...]
   */
  function _optionsForDataSource(dataSource) {
    if (dataSource === undefined) {
      return {};
    }

    switch (typeof dataSource) {
      case 'string':
        // it's either a URL or a JSON repr of a collection
        dataSource = dataSource.trim();
        if (dataSource.substr(0, 1) == '[') {
          return {
            'aaData': JSON.parse(dataSource)
          };
        } else {
          return {
            'bServerSide': true,
            'sAjaxSource': dataSource
          };
        }
        break;

      case 'object':
        // it is a local JavaScript collection
        return {
          'aaData': dataSource
        };

      default:
        return {};
    }
  }

  /* Return a dataTable options object for property names to use when reading
   * the server-side ajax source.
   */
  function _optionsForDataSourceProp(props) {
    var columns;
    if (props !== undefined) {
      return {
        'aoColumns': _.map(props.split(','), function(prop) {
          return {'mDataProp': prop};
        })
      };
    }
  }

  /* Set up a custom function to be called after the table's data is returned
   * from server side.  Replaces the default DataTables function that fetches
   * server side data.
   */
  function _optionsForServerData(serverData) {
    if (typeof serverData === 'function') {
      // Use our custom fnServerData function which fetches table data
      // as usual but also makes the response object available to code
      // other than the table object.  Some of our AJAX responses return
      // additional data required by views.  E.g. server list filtersInUse.
      var customServerData = function(sSource, aoData, originalCallback, oSettings) {
        oSettings.jqXHR = $.ajax({
          'dataType': 'json',
          'type': 'GET',
          'url': sSource,
          'data': aoData,
          'success': function(data) {
            serverData(data);
            originalCallback(data);
          }
        });
      };

      return {'fnServerData': customServerData};
    }
  }

  /* Sets up the fnServerParams option for DataTables.
   * Expects either a function as required for the dataTables 'fnServerParams'
   * option, or an array of objects to push on to the aoData array passed to
   * the server side.
   */
  function _optionsForServerParams(serverParams) {
    if (typeof serverParams === 'function') {
      return {'fnServerParams': serverParams};
    } else if (typeof serverParams === 'object') {
      return {'fnServerParams': function (aoData) {
        // serverParams is either an object or an array of objects to be
        // simply concatenated to the aoData array
        aoData.concat(serverParams);
      }};
    }
  }

  /* Uses column indexed by `groupingCol` to group rows.
   *
   * Table should be sorted by the grouping column which will be hidden.
   * Loops over rows; for every new grouping column vale, a new row spanning
   * all columns is displayed.
   *
   * In your fnDrawCallback or 'table:draw' event handler, add this line
   * (`this` is the oTable):
   *
   *     c2.dataTables.drawRowsGroupedByCol(this, oSettings, 0);
   *
   */
  function drawRowsGroupedByCol(oTable, oSettings, groupingCol, headerClass) {
    if (oSettings.aiDisplay.length === 0) {
      return;
    }

    var $rows = oTable.$('tbody tr');
    var colspan = $rows[0].getElementsByTagName('td').length;
    var lastGroup = "";

    for (var i=0; i < $rows.length; i++) {
      var iDisplayIndex = oSettings._iDisplayStart + i;
      // `group` will contain the content of the grouping table cell (which
      // could be plain text or HTML)
      var group = oSettings.aoData[oSettings.aiDisplay[iDisplayIndex]]._aData[groupingCol];

      // Detect a new group by the value of the grouping table cell. For each new
      // group, a new row and cell spanning all columns is created and inserted
      // into the table. The cell's value will be set to the group value.
      if (group != lastGroup) {
        var nGroup = document.createElement('tr');
        var nCell = document.createElement('td');
        nCell.colSpan = colspan;
        nCell.className = (headerClass === undefined) ? "grouped-by" : headerClass;
        nCell.innerHTML = group;
        nGroup.appendChild(nCell);
        $rows[i].parentNode.insertBefore(nGroup, $rows[i]);
        lastGroup = group;
      }
    }

    // Hide the grouping column
    oTable.column(groupingCol).visible(false);
  }

  // Determine whether element is an initialized dataTable.
  // Note: dataTables 1.10 has a built-in function for this.
  function isDataTable(el) {
    var settings = $.fn.dataTableSettings;
    for (var i = 0, iLen = settings.length ; i < iLen ; i++) {
      if (settings[i].nTable == el) {
        return true;
      }
    }
    return false;
  }

  function keyForDataTable(oSettings) {
    var tableId = oSettings.sInstance || '';
    return 'DataTable#' + tableId + window.location.pathname;
  }

  /* Add Bootstrap styles to draw a field "addon" with a glyphicon.
   * This will be a visual indicator for whether the dataTable search is in
   * effect (blue) or not (gray).
   */
  function setupFilterAddon($filter) {
    var $parent, $filterIcon;

    // First remove the default label element's text content.
    // We must do it here dynamically rather than using the oLanguage.sSearch
    // initialization parameter because that is already used by our templates,
    // so setting it as a default doesn't work.
    $parent = $filter.parent('label');
    // replace just the text content of the label
    var textNodes = $parent.contents().filter(function () {
      return this.nodeType == 3;
    });
    if (textNodes.length > 0) {
      textNodes[0].nodeValue = "";
    }

    // Now add Bootstrap markup to render the addon
    var $wrapper = $('<span class="input-group addon-right"></span>');
    // BS icon classes must live in their own span; thus the redundant spans
    $filterIcon = $('<span class="input-group-addon">' +
                    '  <span class="glyphicon glyphicon-search"></span>' +
                    '</span>');
    $filter.wrap($wrapper);
    $filter.addClass('form-control');
    $filter.attr('aria-label', 'Search in this table');
    $filter.after($filterIcon);
  }


  function showMatchingTerm($dt, term) {
    var $matching = getOrSetupMatchingTerm($dt);
    $matching.show().find('b').text(term);
  }


  function hideMatchingTerm($dt) {
    var $matching = getOrSetupMatchingTerm($dt);
    $matching.hide().find('b').text('');
  }


  /* If a search is in effect, let the user know by styling via CSS
   */
  function highlightActiveSearch($dt) {
    var $filter = getSearchField($dt);
    var $parent = $filter.parent();
    var term = $filter.val();
    if (term) {
      $parent.addClass('active-search');
      showMatchingTerm($dt, term);
    } else {
      $parent.removeClass('active-search');
      hideMatchingTerm($dt);
    }
  }

  function getSearchField($dt) {
    var $dtWrapper = $dt.closest('.dataTables_wrapper');
    var $filter = $dtWrapper.find('.dataTables_filter input');
    return $filter;
  }

  /* If table has a toolbar defined in prop 'data-table-toolbar', append it to
   * the .dataTables_toolbar area of this DataTable.
   *
   * The value of the data-table-toolbar attribute should be a selector of a
   * DOM fragment, or the fragment itself, with any behaviors already defined.
   */
  function addToolbar($table) {
    var toolbarSelector = $table.data('table-toolbar');
    if (toolbarSelector === undefined) {
      return;
    }

    var $toolbar = $(toolbarSelector);
    if ($toolbar && $toolbar.length) {
      var $dtWrapper = $table.closest('.dataTables_wrapper');
      var $toolbarContainer = $dtWrapper.find('.dataTables_toolbar');
      $toolbarContainer.append($toolbar);
      $toolbar.show();
    }
  }


  /* If this table needs one, add a selection info badge.
   */
  function initializeSelectionInfo($table) {
    if ($table.isSingleSelect() || $table.data('table-toolbar')) {
      // No selection info required for single-selection tables, nor
      // for tables that define a custom toolbar.
      return;
    }

    var $dtWrapper = $table.closest('.dataTables_wrapper');
    var $toolbarContainer = $dtWrapper.find('.dataTables_toolbar');
    if ($toolbarContainer.find('.selection-info').length === 0) {
      $toolbarContainer.prepend(createDefaultSelectionBadge($table));
    }
  }


  /* Create a widget that shows the number of selected rows and allows the user
   * to clear the selection.
   */
  function createDefaultSelectionBadge($table) {
    var $info = $(
        '<div class="selection-info">' +
        '  <span class="label label-default">' +
        '    <span class="selection-count">0</span> ' + gettext("selected") +
        '  </span>' +
        '</div>');

    // Add selection-clearing link to the selection info label
    var $clearLink = $(
        '<a class="clear-selection no-tooltip-affordance" ' +
        '  data-toggle="tooltip" title="' + gettext("Clear selection") + '">' +
        '  <span class="icon-delete"></span>' +
        '</a>');

    $clearLink.on('click', function(e) {
      e.preventDefault();
      $table.clearSelection();
    });

    $info.find('.label').append($clearLink);
    return $info;
  }


  /* Set up toolbar behaviors. This function is called before the DataTable has
   * been initialized, so $table is the *jQuery* object of the table.  The
   * DataTable is retrieved from it just-in-time during the various event
   * handlers.
   *
   * Clicks on toolbar buttons are handled as follows:
   * - If the toolbar button specifies `data-href`, that URL will be used to load
   *   the dialog. Otherwise, a common URL that handles multiple toolbar
   *   actions can be passed to this function, in `commonUrl`. Each button must
   *   then specify a `data-action` to let the view know which action is being
   *   performed.
   * - HTTP GET parameters are prepared (as an object) to represent selected
   *   rows and action.  The param name is determined by the `name` attribute
   *   of the checkboxes in the first column. E.g. input name="profile_id" will
   *   be available to the dialog view as request.GET.getlist('profile_id[]',
   *   []).
   *
   * A click handler for the selection info area is also set up for selecting
   * no rows and all visible rows.
   */
  function setupToolbarBehavior($table, $toolbar, commonUrl) {
    // Handle toolbar button/dropdown clicks
    $toolbar.on('click',
      '.btn.selection-action:not(.disabled):not(.dropdown-toggle),' +
      '.btn.selection-action:not(.disabled) + .dropdown-menu a',
      function(e) {
        e.preventDefault();

        var data = {};
        var dataTable = $table.dataTable();
        var fieldName = dataTable.$('input.selector')[0].name;
        var values = dataTable.getSelectedValues();
        data[fieldName] = values;

        // The action button may specify data-href and data-action
        var $btn = $(this);
        var url = $btn.data('href') || commonUrl;
        var action = $btn.data('action');
        if (action) {
          data.action = action;
        }

        if ($btn.hasClass('selection-action-new-tab')) {
          // special case: don't open a dialog, just temporarily open a new tab that
          // can be used to do something like get and return a zip file
          var queryString = $.param(data);
          window.open(url + "?" + queryString, "_blank");
        } else {
          // default behavior: open a dialog
          var $dialog = $("#dialog-modal");

          // copy data attributes from the trigger to the dialog element to honor
          // data- API. This is how the conventional js-dialog-link handler
          // works, which we bypass here because we're calling get manually.
          $dialog.data($btn.data());

          // load the confirmation dialog via GET
          c2.dialogs.displayJqXHR(
            $.get(url, data)
          );
        }
      }
    );

    // Handle clicks on the selection info dropdown (select none/all)
    $toolbar.on('click', '.selection-info .dropdown-menu a', function(e) {
        var dataTable = $table.dataTable();
        var action = $(this).data('action');
        var $checkboxes;

        switch (action) {
          case 'select-none':
            dataTable.clearSelection();
            break;
          case 'select-page':
            $checkboxes = dataTable.find('tbody tr:visible td:first-child input');
            $checkboxes.not(':checked').click();
            break;
          case 'select-all':
            console.log('selecting all rows in all pages is not supported yet');
            $checkboxes = dataTable.$('tbody tr:visible td:first-child input');
            $checkboxes.not(':checked').click();
            break;
        }
      }
    );
  }


  // Display whether a search is in effect near the pagination info area
  function getOrSetupMatchingTerm($dt) {
    var tableId = $dt.attr('id');
    var $matching = $dt.find('matching-term');

    if ($matching.length === 0) {
      $matching = $('<span class="matching-term"> ' + gettext('matching the term') + ' <b></b></span>');

      // Append the matching-term span near the page size and row info area
      $dt.closest('.dataTables_wrapper').find('.dataTables_info').append($matching);
    }
    return $matching;
  }


  function customizeSearchBehavior($dt) {
    var $field = getSearchField($dt);
    setupFilterAddon($field);

    $dt.fnSetFilteringDelay(500);

    // Add the x widget for one-click clearing
    $field.clearable();

    $field.on('keyup', function () {
    });
  }


  /*
   * Set up standard behaviors found in many CB tables.  This is called in the
   * draw handler before the custom table:draw event is triggerd.  It avoids
   * developers having to set these up manually all the time.
   *
   * Args:
   *   $table: the DataTable object
   */
  function initStandardTableBehaviors($table) {
    var tableId = '#' + $table.attr('id');

    c2.sparklines.init(tableId + ' .sparkline');
    c2.tooltip.init($table);
    c2.text.enableDoubleClickSelection(tableId);

    // Enable 'select all/none' behavior on checkboxes for batch selection of rows or columns, if
    // any exist in the table.
    c2.forms.enableBatchCheckboxes(tableId);

    // Create toggles and hook up their click behavior
    $table.find('input[data-toggle=toggle]').bootstrapToggle();
    c2.toggles.enablePostOnChange(tableId + ' input[data-toggle=toggle]');
  }


  // Set DataTable defaults for our Bootstrap styling.
  var defaults = _.merge($.fn.dataTable.defaults, {
    aLengthMenu: [10,25,50,100,500],
    bAutoWidth: false,
    bProcessing: true,
    iDisplayLength: 25,
    sPaginationType: 'full_numbers',
    oLanguage: {
        // About these settings: http://legacy.datatables.net/usage/i18n
        sInfo: interpolate(
          gettext("%(range)s of %(total)s items"),
          {'range': '<span class="table-items-shown">_START_ - _END_</span>',
           'total': '<span class="table-items-total">_TOTAL_</span>'},
          true),
        sInfoFiltered: interpolate(gettext(' (%(count)s total)'), {'count': '_MAX_'}, true),
        sInfoEmpty: gettext("No items"),
        sLengthMenu: '_MENU_ &nbsp;',
        sEmptyTable: gettext('No results found'),
        sProcessing: '<div class="blocker fade-in"><div class="dead-center-container"><div class="dead-center-content"><div class="spinner"></div></div></div></div>',
    },
    // place the DataTable inside a panel
    sDom: "<'panel panel-default'" +
          "  <'panel-body dataTables-header'" +
          // search box
          "    f  " +
          // custom element to contain selection info and
          // optionally any controls for working with table items
          "    <'dataTables_toolbar'>" +
          // processing (not sure if we override this)
          "    r  " +
          "  >    " +
          // the actual table
          "  <'scroll-wide-content't> " +
          "  <'panel-body dataTables-footer'" +
          // page length changing
          "    l  " +
          // information on number of rows/total entries
          "    i  " +
          // bottom pagination
          "    p  " +
          ">>",

    fnInitComplete: function () {
      customizeSearchBehavior(this);
      this
        // Remove our legacy class 'stats'
        .removeClass('stats')
        .addClass('table table-hover table-condensed');

      // Enable styling to fix layout if there is no row of column headings
      if (this.find('thead th').text() === "") {
        this.closest('.dataTables_wrapper').addClass('noHeadings');
      }
    },

    fnDrawCallback: function () {
      var $dt = $(this);

      initStandardTableBehaviors($dt);

      // Broadcast the 'table:draw' event to any callbacks listenting for it
      // and include the dataTable's settings object.
      $dt.trigger('table:draw', this.fnSettings());

      highlightActiveSearch($dt);
    },

    // Save the state of most tables in localStorage
    bStateSave: true,
    fnStateSave: function(oSettings, oData) {
      //console.log('<-- saving state for ', keyForDataTable(oSettings));
      // Always restore a table to the first page, avoiding much user confusion.
      oData.iStart = 0;
      oData.iEnd = oData.iLength;
      localStorage.setItem(keyForDataTable(oSettings), JSON.stringify(oData));
    },
    fnStateLoad: function(oSettings) {
      //console.log('--> loading state for ', keyForDataTable(oSettings));
      try {
        return JSON.parse(localStorage.getItem(keyForDataTable(oSettings)));
      } catch (e) {
        console.log(e);
      }
    }
  });


  /*
   * Convenience function to reload DataTables that have a server-side source.
   *
   * This may be used in conjunction with fnServerParams to dynamically modify
   * parameters passed with the GET request.
   */
  function reloadTable(selector) {
    try {
      $(selector).DataTable().ajax.reload();
    } catch (e) {
      console.error('Failed to reload dataTable "'+ selector +'".  Exception: ', e);
    }
  }


  // Add currency sorting to dataTables.  To use, simply assign the 'currency'
  // type to a column to get correct sort behavior.
  // From http://datatables.net/plug-ins/sorting
  $.extend( $.fn.dataTableExt.oSort, {
    "currency-pre": function ( a ) {
      a = (a==="-") ? 0 : a.replace( /[^\d\-\.]/g, "" );
      return parseFloat( a );
    },
    "currency-asc": function ( a, b ) { return a - b; },
    "currency-desc": function ( a, b ) { return b - a; }
  });


  var dialogDefaults = _.defaults({
    bStateSave: false
  }, defaults);

//////////////////////////////////
// Load the list filters panel via AJAX and set up the behavior of the buttons.

// Being used by the Server List Datatable, the admin/history Datatable, and at least one UIX in the cloudbolt-forge.
//////////////////////////////////

function initListFilters(tableID, url) {
  /**
   * Controls the filters panel and initializes filters.
   * Controls the csv button, gets csv data, and initializes download.
   * Controls the hide/show filters panel toggle.
   * The url parameter is optional, but is useful if your filter form view has a different URL than just the
   * relative `/filter_form/`. This is the case for UI Extensions that use filters.
   *
   * **/
  var filtersLoaded = false;
  var $table = $(tableID);
  var $filtersPanel = $('#filters-panel');
  var $filtersPanelToggle = $('.filters-panel-toggle-btn-text');
  var $filterButton = $('#filters-panel-toggle');
  var $csvExportButton = $('#export-to-csv');
  // if the url is not specified, default to the relative "filter_form/" (this is what is used for the pages built into
  // the product such as the server list page and admin>history page)
  url = url || 'filter_form/';

  $filterButton.on('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      $(this).click();
    }
  });
  $filterButton.click(function() {
    if (filtersLoaded) {
      // only load the filters form once per loading of this page.  Ie. if
      // the user expands, collapses, and expands the filters, only load them
      // on the first expand click
      return;
    }
    c2.block.block($filtersPanel);
    $filtersPanel.load(url, function() {
      c2.block.unblock($filtersPanel);
      filtersLoaded = true;

      // register the submit handler and click handler for the reset button
      // only after the server filter form is loaded
      $filtersPanel.find('form').submit(function(e) {
        e.preventDefault();
        $table.dataTable().clearSelection();

        // add a flag so server knows to persist new filter values
        $(this).append('<input type="hidden" name="new_filters" value="1" />');

        $table.DataTable().ajax.reload();
      });

      $('#unfilter').on('click', clearFilters);
    });
  });

  // control the CSV export button on click
  $csvExportButton.click(function() {
    var data = $table.DataTable().ajax.params();
    data.as_csv = 'true';
    var url = $table.attr('data-table-source');

    // get data to export and initialize download of csv file if the response is to export, else log errors
    $.get(url, data, function(response) {
      if (response.export) {
        c2.downloads.startDownloadFromContent(response.export, response.filename);
      } else if (response.errors) {
        _.forEach(response.errors, function(errors, index) {
          console.log('index: ', index);
          console.log('errors: ', errors);
        });
      }
    });

  });

  // toggle the filters button between 'Hide' and 'Show' display
  $filtersPanel.on('shown.bs.collapse', function () {
    $filtersPanelToggle.html(gettext('Hide filters'));
  });
  $filtersPanel.on('hidden.bs.collapse', function () {
    $filtersPanelToggle.html(gettext('Show Filters'));
  });
}

function clearFilters(e) {
  var $clearButton = $(this);
  var $field;

  // Clear all selectize widgets
  $('#filters-panel select').each(function() {
    $field = $(this)[0].selectize;
    $field.clear();
  });

  // uncheck all checkboxes to reset to no filters
  $('#filters-panel input:checkbox').prop("checked", false);

  $('#filters-panel input[type=text]').val('');
  // Save the cleared state server side
  $clearButton.submit();
  // Update Filter Count Message to Zero
  updateFiltersInUseMsg(0);
}


// Serialize the list filter form and include with each dataTable request.
// Also save all selected rows so they can be restored when the page redraws.
function addListFilters(aoData) {
  var filterFields = $('#filters-panel form').serializeArray();
  var payload = {};
  $.each(filterFields, function(index, field) {
    // group form field objects by field name.
    if (!(field.name in payload)) {
        // make new
        payload[field.name] = [field.value];
    } else {
        // add to existing
        payload[field.name].push(field.value);
    }
  });

  aoData.push({name: 'filters_selected', value: JSON.stringify(payload)});
  aoData.push({name: 'with_checkboxes', value: 1});
  aoData.push({name: 'load_filters_from_profile', value: 1});
}


// Callback invoked with server table JSON response which includes
// a count of the number of filters in use.
function updateFiltersInUseFromResponse(serverListResponse) {
  updateFiltersInUseMsg(serverListResponse.filtersInUse);
}


function updateFiltersInUseMsg(qty) {
  // counts the number of filters in use
  // updates message on the Show/Hide Filters toggle button
  if (qty === 0) {
    $('#filtersInUse').html('');
  } else {
    $('#filtersInUse').html('<b>('+ qty + ' ' + gettext('in use') + ')</b>');
  }
}

  // define lookup with module name, i.e. c2.dataTables.init()
  c2[__module__] = {
    init: init,
    isDataTable: isDataTable,
    defaults: defaults,
    dialogDefaults: dialogDefaults,
    drawRowsGroupedByCol: drawRowsGroupedByCol,
    setupToolbarBehavior: setupToolbarBehavior,
    reloadTable: reloadTable,
    // server and history list filters:
    addListFilters: addListFilters,
    initListFilters: initListFilters,
    updateFiltersInUseFromResponse: updateFiltersInUseFromResponse
  };

})('dataTables', window.c2, window.jQuery, window._);

/* Various utilities for server lists, datatables, etc.
 */

(function (c2, $) {
  'use strict';

    ////////////////////////////
    // History Table Datepicker
    ////////////////////////////
  function initDatePicker() {
    /**
     * Initialize, validate, and control the datepicker.
     *
     * Initializes the bootstrap datepicker on the input-daterange class.
     * Selects the input fields for the daterange form and checks if they have both been filled out
     * Validates entered dates with JS Date() objects and checks if they are in linear order
     * Updates UI elements with according style for errors and lack-thereof
     *
     * Bootstrap Datepicker: https://bootstrap-datepicker.readthedocs.io/en/stable/index.html
     * **/

    // set datepicker options
    var options = {
      autoclose: true,       // close on select
      clearBtn: true,
      endDate: "0d",         // today
      format: "mm/dd/yyyy",  // changing this will affect date parsing below and in the serving view.
      todayHighlight: true,
      todayBtn: false        // disables the default today button - ugly & unnecessary
    };

    $('.input-daterange input').datepicker(options).on("changeDate", function(e) {

        // query DOM
        var startDate = $("#start").val();
        var endDate = $("#end").val();
        var applyBtn = $("[value=Apply]");
        var daterangeInput = $(".daterange-group input");
        var errorMessage = $("#daterange-error-message");

        // helper function for styling a valid date range.
        function displayValidDateRange() {
            // Enable 'Apply' button again
            applyBtn.removeAttr("disabled");
            // Remove error text and error css
            errorMessage.empty().removeClass("daterange-error-active");
            daterangeInput.removeClass("daterange-group-error");
        }

        // Only check for a linear date range if both date fields are populated.
        if (startDate !== "" && endDate !== "") {

            // parse dates
            // doc: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/parse
            var startDT = new Date(startDate);
            var endDT = new Date(endDate);

            // Check if the start date comes before the end date. (inclusive)
            var is_valid = (startDT <= endDT);

            if (is_valid === false) {
                // disable 'Apply' button
                applyBtn.attr("disabled", "true");

                // Add error class styles & add text using gettext() for internationalization.
                daterangeInput.addClass("daterange-group-error");
                errorMessage.text(gettext("Start date must come before end date"))
                             .addClass("daterange-error-active");
            } else {
                // user enters a valid date range
                displayValidDateRange();
            }
        } else {
            // user clears the date range
            displayValidDateRange();
        }

        // control the daterange selectize toolbar for adding or clearing dates
        $('#daterange-selectize-toolbar').on('click', function(e) {
            $("#start").val('');
            $("#end").val('');
            displayValidDateRange();
        });
    });
  };

  c2.datepicker = {
    initDatePicker: initDatePicker
  };
})(window.c2, window.jQuery);

/* We build on top of Bootstrap's modals to give us a dialog component */

// Usage
// =====
//
// For a link to trigger a dialog, it must have:
//
//   1. a ``js-dialog-link`` class
//   2. an ``href`` attribute or data property who's value is a URL that will be loaded into the
//     modal dialog. The URL should be an HTML fragment that is a
//     .modal-dialog element. See http://getbootstrap.com/javascript/#modals
//     for markup.
//
// These ``data-`` attributes are supported on the trigger:
//
//   * data-dialog-width -- a CSS length for the width of the dialog
//
// Default form-submission behavior can be overridden by setting a data
// attribute, 'customFormSubmissionHandler', on the dialog modal (wait until
// the dialog is opened)::
//
//   $('#dialog-modal').data('customFormSubmissionHandler', function(e) {
//      alert('Custom form submission process.');
//   }
//
// To trigger the framework's typical form submission behavior, call
// `c2.dialogs.submitForm`.

(function (c2) {
  'use strict';

  var dialogSelector = "#dialog-modal"; // a .modal from templates/base.html

  // unlike $form and $submitButton, the dialog modal always exists so we can
  // get it now.
  var $dialog = null;

  // these will be set and re-set after every time a dialog has new content
  // loaded by updateWithJqXHR.
  var $form = null;
  var $submitButton = null;


  function init() {
    $dialog = $(dialogSelector);

    $(document).on('click', '.open-dialog', dialogTriggerClickHandler);
    // js-dialog-link is deprecated
    $(document).on('click', '.js-dialog-link', dialogTriggerClickHandler);

    $(document).on('shown.bs.modal', handleDialogShown);
    $(document).on('hidden.bs.modal', handleDialogHidden);
  }


  function handleDialogShown(e) {
    focusFirstFormField($(e.target));
  }


  function handleDialogHidden(e) {
    var modalEl = e.target;

    if (modalEl === $dialog[0]) { // ensure we're looking at the dialogs.js dialog
      // `reload_on_close` dialog setting (see dialog template) allows
      // dialog_views to reload the page, useful if backend data has changed.
      var opts = $dialog.data('dialogOptions');

      // prevent settings from a previous dialog from affecting the next dialog
      $dialog.removeData();

      // clear modal contents so we don't see old content when a new dialog is opened
      $dialog.empty();

      if (opts && opts.reloadOnClose) {
        c2.block.block();
        location.reload();
      }
    }
  }


  function submitFormHandler(e) {
    // a hack to let JS in orders/order_item.html take over.
    var customHandler = $dialog.data('customFormSubmissionHandler');
    if (customHandler) {
      // console.log('c2.dialogs.submitFormHandler: Executing ``customSubmitHandler``');
      return customHandler(e);
    }

    e.preventDefault();
    submitForm();
  }


  /**
   * For dialogs, form data is derived in one of three possible ways:
   * 1. From data-altPostData attribute on the form element.
   * 2. By calling HTML FormData on the form element, if it's supported.
   * 3. By calling $.serializeArray and skipping file data.
   */
  function serializeDialogForm($form) {
    // Let altPostData override actual form fields
    var data = $form.data('altPostData');
    if (data) {
      return data;
    }

    // When the form has files, we need to serialize using FormData to send it
    // over AJAX. If browser doesn't support FormData (i.e. IE 9) it's not
    // sent.
    var hasFileInputs = $form.find("input[type='file']").length !== 0;
    var supportsFormData = typeof(FormData) !== 'undefined';
    if (hasFileInputs && supportsFormData) {
      return new FormData($form[0]);
    }

    return $form.serializeArray();
  }


  function submitForm() {
    // prevent submitting the dialog multiple times
    if ($dialog.data('submitInProgress')) {
      // console.log("Preventing duplicate form submission.");
      return;
    } else {
      $dialog.data('submitInProgress', true);
    }

    // place the submit button in the loading state to disable it and indicate
    // pending activity.
    var $submitButton = $dialog.find('.modal-footer .cb-btn-primary');
    $submitButton.button('loading');

    // submit the form
    var opts = $dialog.data('dialogOptions');
    if (opts && opts.useAjax) {
      var settings = {
        data: serializeDialogForm($form),
        type: 'POST',
        url: $form.attr('action')
      };

      if (Object.prototype.toString.call(settings.data) === '[object FormData]') {
        // Prevent jQuery.ajax from automatically transforming data into UTF-8
        settings.processData = false;
        settings.contentType = false;
      }

      var jqXHR = $.ajax(settings);
      updateWithJqXHR(jqXHR);
      jqXHR.always(function () {
        $dialog.data('submitInProgress', false);
      });
    } else {
      var formEl = $form[0];

      if (formEl.target) {
        // Submit is processed in a different window. To avoid the dialog
        // spinning indefinitely, close it.
        $dialog.modal('hide');
      }

      // Call the form /element/'s submit method; calling jQuery's submit
      // method, which triggers a submit event and causes a loop when our
      // custom submit handler is invoked again.
      formEl.submit();
    }
  }

  // Nicely display an error object in a dialog. The error object should have
  // two properties: title, message.
  function displayError(errorObj) {
    var errorHtml =
      '<div class="modal-dialog">' +
      '  <div class="modal-content">' +
      '    <div class="modal-header">' +
      '      <h4 class="modal-title text-danger">' + (errorObj.title || 'An Error Has Occurred') + '</h4>' +
      '      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
      '    </div>' +
      '    <div class="modal-body">' +
      '      <pre class="pre-scrollable">' +
               (errorObj.message || 'The server is not responding. Please contact an administrator.') +
               (errorObj.details || '')+
      '      </pre>' +
      '    </div>' +
      '    <div class="modal-footer">' +
      '      <button class="btn btn-default cb-btn cb-btn-link" data-dismiss="modal">Close</button>' +
      '    </div>' +
      '  </div>' +
      '</div>';
    $dialog.html(errorHtml);
  }

  function updateOnFulfilledAjax(data, textStatus, jqXHR) {
    // the ``dialog_view`` decorator sometimes returns JSON that triggers
    // special behavior. The first two conditionals demonstrate this.
    if (data.redirect_url) {
      // This line is necessary to get rid of the "data unsaved" browser dialog
      window.onbeforeunload = null;
      window.location = data.redirect_url;
    } else if (data.error) {
      displayError(data.error);
    } else if (data.nextURL) {
      // load dialog contents from a new URL
      // console.log('dialog loading next step from data.nextURL: ', data.nextURL);
      var newjqXHR = $.get(data.nextURL);
      displayJqXHR(newjqXHR);
    } else {
      // The data is probably HTML because we haven't been able to
      // understand it as JSON object that the dialog_view decorator
      // returns.
      $dialog.html(data);
    }
  }

  function focusFirstFormField($dialog) {
    // First form field is either the first visible input or a selectized select element
    var $field = $dialog.find('form').find(':input:visible,select.selectized,input.selectized').first();
    var sel;
    var priorOpenOnFocus;

    // If first field is selectized, temporarily prevent its openOnFocus behavior
    if ($field.length && $field[0] && $field[0].selectize) {
      sel = $field[0].selectize;
      priorOpenOnFocus = sel.settings.openOnFocus;
      sel.settings.openOnFocus = false;
    }

    $field.focus();

    // If selectize, restore its openOnFocus behavior
    sel && (sel.settings.openOnFocus = priorOpenOnFocus);
  }

  function updateOnRejectedAjax(jqXHR, textStatus, errorThrown) {
    displayError(textStatus + ': ' + errorThrown);
  }

  function updateWithJqXHR(jqXHR) {
    jqXHR.then(
      updateOnFulfilledAjax,
      updateOnRejectedAjax
    ).always(
      function () {
        // The dialog now has new content; we need to re-find the form and submit button.
        $form = $dialog.find('#action_form');
        if ($form.length !== 1) { // the specific selector failed; 'form' is a generic fallback
          $form = $dialog.find('form');
        }
        $submitButton = $dialog.find('.js-submit-form');

        $form.on('submit', submitFormHandler);
        $submitButton.on('click', submitFormHandler);

        // Submit the form when the user presses enter.
        $form.on('keypress', function(e) {
          // did user hit the enter key?
          var enter = e.keyCode === 13;

          // did user hit ctrl or shift while pressing enter?
          var megaEnter = (enter && (e.ctrlKey || e.shiftKey)) || e.keyCode === 10;

          // did the keypress occur while inside a textarea?
          var textarea = e.target.tagName === 'TEXTAREA';

          // submit on enter, except when typing in a textarea (the user wants
          // to insert a line break) unless the user signals intent to submit
          // by also pressing ctrl or shift at the same time.
          if (enter && !textarea || megaEnter) {
            submitFormHandler(e);
          }
        });

        // if the user requested a width, set it!
        var width = $dialog.data('dialog-width');
        if (width) {
          $dialog.find('.modal-dialog').css('width', width);
        }

        // Custom handler to support double-clicking on the backdrop to close
        // the dialog.
        closeDialogOnBackdropDoubleClick($dialog);
      }
    ).then(
      function () {
        var options = {
          // Prevent the backdrop from closing the dialog on click, which is
          // too easy to do unintentionally (e.g. when trying to raise the
          // browser window after being in another app). However, there is a
          // custom handler to support dialog closing when the backdrop is
          // double-clicked, affording a reasonable alternative.
          'backdrop': 'static'
        };

        var preventEscapeKeyClosing = $dialog.data('prevent-esc-closing');
        if (preventEscapeKeyClosing) {
          options.keyboard = false;
        }

        $dialog.modal(options);
      },
      function () {
        console.log('Could not load the dialog\'s contents.');
      }
    );
  }

  /*
   * When dialog links are clicked, open a dialog and load its content.
   */
  function dialogTriggerClickHandler (e) {
    // If the click originated within an IFRAME, cause the dialog to be opened
    // in the top window instead of the IFRAME. This deprecates the older
    // 'open-parent-dialog' class.
    if (window !== window.top) {
      window.top.c2.dialogs.clickHandler(e);
      return;
    }

    e.preventDefault();

    // Ensure tooltips are closed first. This can happen when one dialog opens
    // another via a.open-dialog (e.g. see flow for adding a hook)
    $('#tooltip-container').html('');

    // ``e.currentTarget`` will be the element matched by the second
    // argument to ``.on`` above --- the link element.
    var $dialogToggle = $(e.currentTarget);

    // Bootstrap's modal data-* API supports setting the ``href`` attribute
    // equal to an ID selector, but we haven't implemented support for that
    // here. We assume a remote resource.
    var remote = $dialogToggle.attr('href') || $dialogToggle.data('href');

    // copy data attributes from the trigger to the dialog element so that
    // other bits of code can access dialog settings without needing to know
    // the trigger element. dialog-width is one of these settings.
    $dialog.data($dialogToggle.data());

    var jqXHR = $.get(remote);
    displayJqXHR(jqXHR);
  }

  /* If user double-clicks on the backdrop, i.e. outside of the dialog content
   * area, close the dialog.  This handler takes the place of the default
   * Bootstrap behavior of closing on single-click, which has serious usability
   * problems.
   */
  function closeDialogOnBackdropDoubleClick($dialog) {
    $dialog.on('dblclick', function (e) {
      // only close the dialog if the click is outside of .modal-content (first
      // and only child of .modal-dialog)
      if (!$(e.target).parents('.modal-dialog').length) {
        $dialog.modal('hide');
      }
    });
  }


  // Show the dialog, with content loaded from the jqXHR response.
  //
  // Automatically blocks and waits for the response to be fulfilled. Useful
  // for showing dialogs that are the result of a complex $.post with
  // custom-generated request bodies (eg. server batch actions dialog).
  function displayJqXHR(jqXHR) {
    c2.block.block();
    updateWithJqXHR(jqXHR);
    jqXHR.always(function () {
      c2.block.unblock();
    });
  }


  // Return True if a dialog is currently open, False otherwise.
  function isOpen() {
    return $('#dialog-modal').is(':visible');
  }


  // Tell the dialog framework to use different submit behavior: serialize all
  // data in the form as well as all data in selected rows of the dataTable.
  //
  // $table: jQuery object of the table.
  // $actionForm: optional form jQuery object; if not specified, the closest
  //    ancestor form of the dataTable will be used.
  //
  function onSubmitSerializeAllSelectedRows($table, $actionForm) {
    var $form = ($actionForm !== undefined) ? $actionForm : $table.closest('form');
    $table = $($table).dataTable();

    $('#dialog-modal').data('customFormSubmissionHandler', function (e) {
      e.preventDefault();

      // Pass the serialized POST data to the dialog framework
      $form.data('altPostData', c2.forms.serializeFormAndTableSelection($form, $table));

      c2.dialogs.submitForm();
    });
  }


  c2.dialogs = {
    init: init,
    displayJqXHR: displayJqXHR,
    isOpen: isOpen,
    submitForm: submitForm,
    onSubmitSerializeAllSelectedRows: onSubmitSerializeAllSelectedRows,
    clickHandler: dialogTriggerClickHandler
  };
})(window.c2);

/* Download utilities */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);


  function startDownload(url, filename) {
    var downloader = document.createElement('a');
    downloader.setAttribute('href', url);
    // this may not work in all browsers
    downloader.setAttribute('download', filename);
    downloader.classList.add('hidden');
    // attach to body for FF click to work
    document.getElementsByTagName('body')[0]
      .insertAdjacentElement('beforeend', downloader);
    downloader.click();
    setTimeout(function() { downloader.remove(); }, 50);
  }


  /**
   * Trigger a file download containing `content`, suggested file name `filename`.
   * If mimeType is not specified, uses default "text/csv".
   */
  function startDownloadFromContent(content, filename, mimeType) {
    if (mimeType === undefined) {
      mimeType = 'text/csv';
    }
    logger.debug('filename:', filename, 'mimeType:', mimeType);

    var blob = new Blob([content], {type: mimeType});
    if (navigator.msSaveBlob) {
      // Special case for IE 11, of course.
      // https://msdn.microsoft.com/library/Hh772331
      navigator.msSaveBlob(blob, filename);
    } else {
      var url = URL.createObjectURL(blob);
      logger.debug('url:', url);
      startDownload(url, filename);
    }
  }

  function quoteValues(values) {
    return _.map(values, function(value) {
      return '"' + value + '"';
    });
  }

  function arrayToCSV(headers, rowsIn) {
    var rows = [quoteValues(headers).join(',')];

    _.forEach(rowsIn, function (row) {
      var cols = quoteValues(row);
      rows.push(cols.join(','));
    });

    return rows.join("\r\n");
  }


  // expose public functions
  c2[__module__] = {
    startDownload: startDownload,
    startDownloadFromContent: startDownloadFromContent,
    quoteValues: quoteValues,
    arrayToCSV: arrayToCSV
  };

})('downloads');

(function (c2, $, _) {
  'use strict';

  /************************** Formset helpers **************************/

  /* Formsets with "Add another" may call this to replace that link when
     the list of objects that can be added is empty.
   */
  function hide_add_link_when_depleted(list, msg) {
    if (list.length === 0) {
      $('a.add-form').replaceWith('<p>' + msg + '</p><br>');
    }
  }

  /* Group formset row delete behavior:

     Click on the delete link (red icon): row turns red and icons becomes
     a cancel link.  Checkboxes are _not_ altered, though, so they can be
     reinstated in case user cancels.

     Unchecking all permissions in a row triggers a click on the delete
     link as well.

     If a row is passed in, apply only to that row. Otherwise, apply to all
     rows.
   */
  function markRowForDeletionOrNot(formsetContainer, $row) {
    var $rows;
    if ($row) {
      $rows = $row;
    } else {
      $rows = $(formsetContainer).find('tbody tr');
    }

    $rows.each(function (index) {
      var row = $(this);
      if (row.find('input:checkbox:checked').length === 0) {
        row.find('a.delete-form').trigger('click');
      } else {
        row.find('a.unremove').trigger('click');
      }
    });

  }


  /***************** Batch checking by column and row *****************/

  /* Check all or none of the subjects in the column of the clicked batch
   * checkbox.
   */
  function toggleAllInColumn(e) {
    var $checkbox = $(this);
    var check = $checkbox.prop('checked');
    var colNum = $checkbox.closest('th').prevAll().length;
    $checkbox.closest('table').find('tbody tr:visible').each(function (i) {
      var $input = $(this).children().eq(colNum).find('input');
      if ($input.prop('checked') != check) {
        $input.trigger('click');
      }
    });
  }

  function toggleAllInRow(e) {
    var $control = $(this);
    var $row = $control.closest('tr');
    var check = $control.prop('checked');
    $row.find('input:not(.check-row)').prop('checked', check);
  }

  /* Check and uncheck the batch checkboxes to reflect the state of
    * their subjects. Only check the batch box if all subjects are checked.
    */
  function updateBatchCheckboxes(formsetContainer) {
    var $control, colNum, $subjects, allChecked, $allColumns, $tdColumns;
    $(formsetContainer).find('.check-column').each(function (i) {
      $control = $(this);
      colNum = $control.closest('th').prevAll().length;
      $subjects = $(formsetContainer).find('tbody tr:visible').find('td:eq(' + colNum + ') input');
      allChecked = ($subjects.length > 0 && $subjects.length == $subjects.filter(':checked').length);
      $control.prop('checked', allChecked);
    });

    $(formsetContainer).find('.check-row').each(function (i) {
      $control = $(this);
      $subjects = $control.closest('tr').find('td input:not(.check-row):visible');
      allChecked = ($subjects.length > 0 && $subjects.length == $subjects.filter(':checked').length);
      $control.prop('checked', allChecked);
    });
  }

  /* This is called by c2.dataTables to set up standard behaviors every time a page is drawn.
   */
  function enableBatchCheckboxes(container) {
    var $container = $(container);
    $container.on('click', '.check-column', toggleAllInColumn);
    $container.on('click', '.check-row', toggleAllInRow);

    // When any subject checkboxes in the table body change, update the row & column batch
    // checkboxes to reflect the new state (i.e. checked if all boxes in a row or column are
    // selected).
    $container.on('change', 'tbody input:checkbox:not(.check-column)', function (e) {
      updateBatchCheckboxes(container);
    });

    updateBatchCheckboxes(container);
  }

  /************************* Widgets and Controls *************************/


  /* To be used with input fields created by the SuggestInputField widget.
   * This adds the dropdown button to the input field, making the widget
   * behave more like a combobox (type or click to pick a selection) that
   * also allows new values to be created (type something that's not in
   * the list already).
   *
   * Derived from the jQuery UI demo of making a combobox widget:
   * http://jqueryui.com/resources/demos/autocomplete/combobox.html
   */
  function appendShowAllButton(selector) {
    var $input = $(selector),
      wasOpen = false;
    if ($input.next().hasClass('custom-combobox-toggle')) {
      return;
    }

    $("<a>")
      .attr("tabIndex", -1)
      .attr("title", "Show All Items")
      .insertAfter($input)
      .button({
        icons: {
          primary: "ui-icon-triangle-1-s"
        },
        text: false
      })
      .removeClass("ui-corner-all")
      .addClass("custom-combobox-toggle ui-corner-right")
      .mousedown(function () {
        wasOpen = $input.autocomplete("widget").is(":visible");
      })
      .click(function () {
        $input.focus();

        // Close if already visible
        if (wasOpen) {
          return;
        }

        // Pass empty string as value to search for, displaying all results
        $input.autocomplete("search", "");
      });

    // Keep dropdown button from wrapping when input is assigned width 100%
    $input.css('width', 'auto');
  }

  /* Click handler for order actions such as duplicate, cancel, approve.
    * Submits the form containing the icon/button and passes the target's
    * data-action attr value in a hidden input with the submitted form.
    */
  function doOrderAction(e) {
    // prevent event bubbling and possible double-submit in IE
    e.preventDefault();

    var $icon = $(e.target);
    // clear button has confirmation step
    if ($icon.hasClass('icon-delete')) {
      var answer = confirm("Remove all items from this order (cannot be undone)? ");
      if (!answer) {
        return false;
      }
    }
    c2.block.block();
    var action = $icon.data('action');
    var theform = $icon.closest('form');
    theform.find('input[name="action"]').val(action);
    theform.submit();
  }

  // Ensure all selected rows from the DataTable are serialized along with the
  // form's data.  Also remove duplicate parameter values, which can happen
  // when some selected rows are visible in the DOM and thus included by the
  // form.  So [{name: 'param', value:1}, {name: 'param', value: 1}, ...]
  // becomes [{name: 'param', value:1}, ...]. Return serialized data in the
  // form of a urlencoded querystring.
  function serializeFormAndTableSelection($form, $table) {
    var serialized = '',
      // Start by serializing the entire form. This may also include some
      // visible dataTable rows if the table is wrapped by the form.
      formData = $form.serializeArray(),
      // Serialize all (visible) selected rows in the DataTable object
      tableData = $table.$('tr.selected').find('input,select').serializeArray(),

      params,
      distinct;

    if ($table.hasClass('clickable')) {
      // Handle clickable paginated tables where selected rows have a checkbox
      // and may not be visible (thus not included in tableData)
      var selectedValues = $table.getSelectedValues();
      var selector = $table.$('input.selector');
      if (selector.length) {
        _.forEach(selectedValues, function (val) {
          tableData.push({ name: selector[0].name, value: val });
        });
      }
    }

    /*
     * Combine all params and remove any duplicate objects from the list

        E.g. this: [ {name: 'a', value: 1},
                    {name: 'a', value: 2},
                    {name: 'b', value: 'bear'},
                    {name: 'b', value: 'bear'} ]
        Returns:
                  [ {name: 'a', value: 1},
                    {name: 'a', value: 2},
                    {name: 'b', value: 'bear'} ]
      */
    params = _.union(tableData, formData);
    distinct = _.uniq(params, false, function (param, i, c) {
      return param.name + '::' + String(param.value);
    });


    // turn the {name: 'n', value: v} objects into {'n': v} objects
    distinct = _.map(distinct, function (param) {
      var obj = {};
      obj[param.name] = param.value;
      return obj;
    });

    // stringify objects, join into one, and URL encode it
    return encodeURI(_.map(distinct, c2.querystring.stringify).join('&'));
  }


  // Password fields should get a show/hide toggle icon
  function initPasswordFields() {
    // Disable existing handlers so we don't end up with multiple
    $(".toggle-password").off("click")
    // Function to show the password and set a timeout to hide it again
    function show($eye, $input) {
      $eye.toggleClass("fa-eye fa-eye-slash");
      $input.attr("type", "text");
      var timeoutId = setTimeout(
        function () { hide($eye, $input); },
        $eye.attr("delay")
      );
      $eye.attr("timeout", timeoutId);
    }
    // Function to hide the password and clear the timeout if it exists
    function hide($eye, $input) {
      $eye.toggleClass("fa-eye fa-eye-slash");
      $input.attr("type", "password");
      var timeoutId = $eye.attr("timeout");
      clearTimeout(timeoutId);
      $eye.removeAttr("timeout");
    }
    $(".toggle-password").click(function () {
      var $eye = $(this);
      var $input = $("#" + $eye.attr("toggle"));
      if ($input.attr("type") == "password") {
        show($eye, $input);
      } else {
        hide($eye, $input);
      }
    });
  }

  // Actions with source code (plugin, remote script) may have a file uploaded
  // or point at a URL.  Form enables/disables fields based on where the code
  // comes from.
  function setupActionFileFields() {
    var $fileLocation = $('input[name=file_location]');
    var $uploadFields = $('.upload-widget').find('#id_module_file, #browse_button, .js-clear, #module_file-current a');
    var $externalUrlFields = $('#id_source_code_url');
    // Terraform specific fields
    var $localPathFields = $('#id_local_path');
    var $externalGitUrlFields = $('#id_git_source_code_url');

    // Improve form layout by putting the sub-fields into the radio labels
    // and moving the File location help text above the choices.
    function moveFileFieldsIntoRadioLabels() {
      var uploadLabel = $('#div_id_file_location [value="upload"]').parent()
      $('#div_id_module_file').appendTo(uploadLabel);

      var urlLabel = $('#div_id_file_location [value="url"]').parent();
      $('#div_id_source_code_url').appendTo(urlLabel);

      // Terraform specific options
      // Terraform also allows users to point to a git repo
      var gitUrlLabel = $('#div_id_file_location [value="git"]').parent()
      $('#div_id_git_source_code_url').appendTo(gitUrlLabel);
      $('#div_id_branch').appendTo('#div_id_git_source_code_url');
      $('#div_id_refresh_on_order').appendTo('#div_id_git_source_code_url');

      // Terraform has the concept of a local path on disk
      var localPathLabel = $('#div_id_file_location [value="local"]').parent()
      $('#div_id_local_path').appendTo(localPathLabel);
    };

    moveFileFieldsIntoRadioLabels();

    function morphFields() {
      var fileLocation = $fileLocation.filter(':checked').val();

      // Define a map of fileLocation values and JQuery objects
      var labels = {
        upload: $('#div_id_module_file'),
        url: $('#div_id_source_code_url'),
        later: null,
        local: $('#div_id_local_path'),
        git: $('#div_id_git_source_code_url'),
      };

      // Define a map of fileLocation values and Fields
      var fields = {
        upload: $uploadFields,
        url: $externalUrlFields,
        later: null,
        local: $localPathFields,
        git: $externalGitUrlFields,
      };

      function showOnly(location) {
        // We have two separate ways of hiding things. I'm not sure why, but that's how it is.
        // Refactors happen in baby steps sometimes. :shrug:
        // Iterate over all fields and hide them.
        $.each(labels, function (_, id) {
          if (id != null) { id.hide(); }
        });
        if (labels[location] != null) {
          // Show only the field we were asked to show.
          labels[location].show();
        }

        // Do the same loop for the `fields` map above
        $.each(fields, function (_, field) {
          if (field != null) { field.prop('disabled', true).addClass('disabled'); }
        });
        if (fields[location] != null) {
          // Leave only the one we want enabled
          fields[location].prop('disabled', false).removeClass('disabled');
        }
      };

      showOnly(fileLocation);
    }

    $fileLocation.on('change', morphFields);
    morphFields();
  }


  // When changing resources on a server with the Change Resources form, the change
  // may be set to happen "immediately"/ASAP or scheduled for a later time. Form
  // enables/disables the datepicker for scheduling based on whether that option is selected
  function setupSchedulingFields() {
    var $runOption = $('input[name=run_option]');
    var $scheduledTimeField = $('#id_scheduled_time');

    // Improve form layout by putting the datepicker sub-field into the radio label
    var moveDatepickerIntoRadioLabel = function () {
      var scheduleLabel = $('#div_id_run_option label:eq(2)');
      $('#div_id_scheduled_time').appendTo(scheduleLabel);
    };

    moveDatepickerIntoRadioLabel();

    // Hide/show and enable/disable based on which option is selected
    function morphFields() {
      var selectedOption = $runOption.filter(':checked').val();

      if (selectedOption == 'now') {
        $('#div_id_scheduled_time').hide();
      } else if (selectedOption == 'later') {
        $('#div_id_scheduled_time').show();
      }
    }

    $runOption.on('change', morphFields);
    morphFields();
  }


  // Web hook action form morphs based on the selected auth type.
  function setupWebHooksForm() {
    var $auth_method = $('select[name=authentication_method]');
    var $basic_fields = $('input[name=http_username], input[name=http_password]');
    var $token_fields = $('input[name=auth_header_name], input[name=auth_header_value]');

    function morphAuthFields() {
      var auth_method = $auth_method.val();
      if (auth_method == 'none') {
        $basic_fields.prop('disabled', true).closest('.form-group').hide();
        $token_fields.prop('disabled', true).closest('.form-group').hide();

      } else if (auth_method == 'basic') {
        $basic_fields.prop('disabled', false).closest('.form-group').show();
        $token_fields.prop('disabled', true).closest('.form-group').hide();

      } else if (auth_method == 'token') {
        $basic_fields.prop('disabled', true).closest('.form-group').hide();
        $token_fields.prop('disabled', false).closest('.form-group').show();
      }
    }

    $auth_method.on('change', morphAuthFields);
    morphAuthFields();
  }


  /**
   * Helper for Bootstrappy forms that do not want checkbox/radio labels in the
   * right column. Moving them into the left column lays them out more
   * consistently with other field's labels.
   */
  function moveOffsetLabelsToLeftCol($form) {
    var $col2, $formGroup, $label, $parent;

    // Each offset element represents a checkbox or radio rendered by crispy
    // forms to be in the right column (aka col2).
    $form.find('.col-lg-offset-3').removeClass('col-lg-offset-3')
      .each(function () {
        $col2 = $(this);
        $formGroup = $col2.closest('.form-group');

        // First remove 'checkbox' or 'radio' classes added by crispy
        // forms because it interferes with help text layout.
        $formGroup.find('div.checkbox').removeClass('checkbox');
        $formGroup.find('div.radio').removeClass('radio');

        $label = $col2.find('label');
        $label.addClass('control-label col-lg-3');
        $label.prependTo($formGroup);
        // Move the control and any help text to col2 again
        $label.children().appendTo($col2);
      });
  }


  /* Dynamically update the preview of an action button with icon
   * based on input field values.  Used by server and resource action edit
   * forms (i.e. ButtonActionMixin).
   */
  function actionButtonPreview() {
    // Create the preview button to show label + icon
    var $preview = $('<button id="preview" class="btn btn-default"></button>');

    // Disable the button since it's just a preview
    $preview.on('click', function (e) { e.preventDefault(); });
    // Insert it
    var $xc = $('#id_extra_classes');
    var $btnpreview = gettext('Button preview')
    $xc.closest('.form-group').after(
      '<div class="form-group">' +
      '  <label class="control-label col-lg-3"> ' + $btnpreview + ' </label>' +
      '  <div id="preview-wrap" class="controls col-lg-9">' +
      '  </div>' +
      '</div>');
    $('#preview-wrap').html($preview);

    var $label = $('#id_label');

    function updatePreview() {
      var classes = $xc.val();
      var $icon = $('<i id="preview-icon"></i>');
      $preview.html($icon);

      // Strip certain chars to avoid XSS attacks
      var badChars = /['";\/><]/g;
      $icon.addClass(classes.replace(badChars, ''));
      $icon.after('&nbsp;&nbsp;' + $label.val().replace(badChars, ''));
    }

    updatePreview();
    $xc.on('keyup', updatePreview);
    $label.on('keyup', updatePreview);
  }


  /* Dynamically update the preview of a resource type's icon based on what the
   * user types in that field in the add/ edit dialogs for ResourceType
   */
  function iconPreview() {
    var $preview = $('<span id="icon-preview"></span>');

    // Insert it
    var $iconField = $('#id_icon');
    $iconField.closest('.form-group').after(
      '<div class="form-group">' +
      '  <label class="control-label col-lg-3">Icon preview</label>' +
      '  <div id="preview-wrap" class="controls col-lg-9">' +
      '  </div>' +
      '</div>');
    var $previewFormGroup = $iconField.closest('.form-group').next();
    $('#preview-wrap').html($preview);

    function updatePreview() {
      var classes = $iconField.val();

      if (classes) {
        // Strip certain chars to avoid XSS attacks
        var badChars = /['";\/><]/g;
        $preview.removeClass();
        $preview.addClass(classes.replace(badChars, ''));
        $previewFormGroup.show();
      } else {
        // Don't show the Icon preview line if they haven't entered anything
        // in the icon field
        $previewFormGroup.hide();
      }
    }

    updatePreview();
    $iconField.on('keyup', updatePreview);
  }


  // Required to avoid "ManagementForm data is missing or has been tampered
  // with" ValidationError on server side.
  function makeFormsetManagementData(formCount) {
    return {
      'form-TOTAL_FORMS': formCount,
      'form-INITIAL_FORMS': 0,
      'form-MAX_NUM_FORMS': 1000
    };
  }


  /*
    * Return jQuery element of DOM fragment for Bootstrap columns containing
    * the elements in collection `$items` split at index `atIndex`.
    *
    * `bootstrapBreakPoint` may be sm, md, or lg.
    */
  function splitElementsIntoColumns($elements, atIndex, bootstrapBreakPoint) {
    var breakpoint = bootstrapBreakPoint || 'lg';

    var $row = $('<div class="row"></div>');
    var $col0 = $('<div class="col-' + breakpoint + '-6"></div>').appendTo($row);
    var $col1 = $('<div class="col-' + breakpoint + '-6"></div>').appendTo($row);

    $col0.append($elements.slice(0, atIndex));
    $col1.append($elements.slice(atIndex));
    return $row;
  }

  function setUpKubernetesSettingsForm() {
    var authTypeSelector = "input[name=auth_type]"
    var $auth_type = $(authTypeSelector);

    var password_field = "input[name=servicepasswd]";
    var token_field = "input[name=bearer_token]";
    var ca_field = "textarea[name=ca_file_contents]";
    var key_field = "textarea[name=key_file_contents]";
    var cert_field = "textarea[name=cert_file_contents]";

    var allFields = [
      password_field,
      token_field,
      ca_field,
      key_field,
      cert_field,
    ];

    var fieldsByAuthType = {
      "PASSWORD": [password_field],
      "TOKEN": [token_field],
      "CERTIFICATE": [ca_field, key_field, cert_field],
    };

    function disableFields(fieldsToEnable) {
      for (var i = 0; i < allFields.length; i++) {
        var field = allFields[i];

        // Only disable and hide fields that are not being enabled.
        if (!fieldsToEnable.includes(field)) {
          var $field = $(field);
          $field.prop("disabled", true).closest(".form-group").hide();
        }
      }
    }

    function showAndEnableField(field) {
      var $field = $(field);
      $field.prop("disabled", false).closest(".form-group").show();
    }

    function morphAuthType() {
      var $auth_type = $(authTypeSelector);
      var auth_type = $auth_type.filter(":checked").val();

      // Enable and show fields for the auth_type selection.
      var fieldsToEnable = fieldsByAuthType[auth_type];
      for (var i = 0; i < fieldsToEnable.length; i++) {
        showAndEnableField(fieldsToEnable[i]);
      }

      // Disable fields not in this auth_type selection.
      disableFields(fieldsToEnable);
    }

    function moveFieldsIntoRadioLabel() {
      // Move form fields into their the appropriate radio label elements.
      // Note, that when indexing these radio labels, we rely on the order in which the
      // three auth_type options are defined inside the 'Kubernetes' model as 'AUTH_TYPE_CHOICES'.

      // Append all 3 certificate-specific form fields to the 'Certificate' Radio Label.
      var certLabelSelector = "#div_id_auth_type label:eq(3)";
      $("#div_id_ca_file_contents").appendTo($(certLabelSelector));
      $("#div_id_cert_file_contents").appendTo($(certLabelSelector));
      $("#div_id_key_file_contents").appendTo($(certLabelSelector));

      // Append the 'bearer_token' form field to the 'Token' Radio Label.
      var tokenLabel = $("#div_id_auth_type label:eq(2)");
      $("#div_id_bearer_token").appendTo(tokenLabel);

      // Append the 'servicepasswd' form field to the 'Password' Radio Label.
      var passwdLabel = $("#div_id_auth_type label:eq(1)");
      $("#div_id_servicepasswd").appendTo(passwdLabel);
    }

    moveFieldsIntoRadioLabel();

    $auth_type.on("change", morphAuthType);
    morphAuthType();
  }

  function addTerraformMappingFields() {
    // Trim leading CTV_ off label text of custom fields
    $.map($('label'), l => $(l).text( (undefined, text) => text.replace(/CTV_/, "")))
    // Hide the blank custom fields provided by the backend
    const customFields  = $('div[id^="div_id_custom"]');
    $.map(customFields, customField => $(customField).hide());
    // onclick function to show next hidden custom field pair
    const showNext = () => {
      $('div[id^="div_id_custom_key"]:hidden:first').show();
      $('div[id^="div_id_custom_value"]:hidden:first').show();
    }
    // Add button to show custom fields
    $('.modal-footer:first').prepend('<button id="add_button" type=button>Add Variable</button>');
    $('#add_button:first').attr("class", "cb-btn cb-btn-primary").click(showNext);
  }

  function addToDataTableFormDialog(fieldName) {
    /*
      This function will allow you to add rows to dialogs using the
      datatable_form_dialog html template
    */

    // function to create new row fragment to insert into the table
    const createFragment = (id) => `
        <tr>
            <td>
              <input
                type="checkbox"
                id="custom_checkbox_${id}"
                name="${fieldName}"
                checked
                disabled
              />
            </td>
            <td>
              <input
                type="text"
                id="custom_text_${id}"
                name="${fieldName}"
              />
            </td>
        </tr>
      `;

    // IIFE to create new rows with unique ids
    const addRow = (() => {
      let currentId = 0;
      return () => {
        currentId++;
        const newFragment = createFragment(currentId);
        $('#checkbox-select-multiple > tbody:last-child').append(newFragment);
        // Updating the input field updates the checkbox value, the backend expects this
        $(`#custom_text_${currentId}`)
            .keyup(function () {
              $(`#custom_checkbox_${currentId}`).val(this.value)
            })
            .focus();
      }
    })();

    // Place add button in footer to add new rows
    $('.modal-footer:first').prepend('<button id="add_button" type=button>Add Custom</button>');
    $('#add_button:first').attr("class", "cb-btn cb-btn-primary").click(addRow);
  }

  function initPowerScheduleForm() {
    const $fields = $(".power-schedule-fields");
    const $scheduleTemplate = $(".power-schedule").eq(0);
    const $addButton = $("#add-power-schedule");



    // create new schedule fields
    $addButton.click(function(e) {
      e.preventDefault();
      const $clone = $scheduleTemplate.clone();
      const idx = $(".power-schedule").length;
      let id = $clone.prop('id');

      // update id and classes
      id = id.replace(/\d/, idx);
      $clone.prop('id', id);
      $clone.addClass("new-schedule")

      // remove any error messages
      $clone.find(".error-list").remove()

      // reset selects
      $clone.find("select").each(function() {
        let name = $(this).prop("name");
        name  = name.replace(/\d/, idx);
        $(this).prop("name", name)
        $(this).val(0);
      });

      $fields.append($clone);
    });

    $fields.on('click', '.delete-schedule', function() {
      const $parent = $(this).parent();
      const $deletedInput = $('input[name="deleted_schedules"]')
      const deletedVal = $deletedInput.val()
      const schedName = $parent.attr("id")

      if(! $parent.hasClass("new-schedule")) {
        $deletedInput.val(deletedVal+schedName+",")
      }

      $parent.remove()
    });


  }


  // expose public functions
  c2.forms = {
    actionButtonPreview: actionButtonPreview,
    appendShowAllButton: appendShowAllButton,
    doOrderAction: doOrderAction,
    enableBatchCheckboxes: enableBatchCheckboxes,
    hide_add_link_when_depleted: hide_add_link_when_depleted,
    iconPreview: iconPreview,
    makeFormsetManagementData: makeFormsetManagementData,
    markRowForDeletionOrNot: markRowForDeletionOrNot,
    moveOffsetLabelsToLeftCol: moveOffsetLabelsToLeftCol,
    serializeFormAndTableSelection: serializeFormAndTableSelection,
    setupActionFileFields: setupActionFileFields,
    setupSchedulingFields: setupSchedulingFields,
    setupWebHooksForm: setupWebHooksForm,
    splitElementsIntoColumns: splitElementsIntoColumns,
    updateBatchCheckboxes: updateBatchCheckboxes,
    initPasswordFields: initPasswordFields,
    setUpKubernetesSettingsForm: setUpKubernetesSettingsForm,
    addTerraformMappingFields: addTerraformMappingFields,
    addToDataTableFormDialog: addToDataTableFormDialog,
    initPowerScheduleForm: initPowerScheduleForm
  };

})(window.c2, window.jQuery, window._);

/*
 * Functions for history tables used by various CB objects.
 */

(function (c2, $) {
  'use strict';


  /*
   * Load JSON data and assign it to the history DataTable.
   *
   * The history table is implemented differently from most others that have a
   * remote data source. Instead of letting DataTables own the process by just
   * giving it a source URL, we fetch JSON data directly so it can be used by
   * other components on the page.
   *
   * Therefore, to reload the history table, we can't reload these the standard
   * way, by calling $('#history').DataTable().ajax.reload(). Instead, call
   * this function to reload the table.
   */
  function loadHistoryData(url) {
    var $table = $('#history');
    var $wrapper = $('#tab-history');

    if (url) {
      // Save the URL on the table, so other callers (e.g. server details live
      // updates) don't have to know it too.
      $table.data('table-source-data-url', url);
    } else {
      url = $table.data('table-source-data-url');
    }

    // Present a not-cut-off spinner
    $wrapper.css('min-height', '400px');
    c2.block.block($wrapper);

    /*
    Due to the expense of getting a potentially large history, this table's rows
    are also used by the stats tab's charts.  Because of that, the data is
    fetched only once, asynchronously, and attached to dataTable as local JSON
    data. This way the table is also able to handle paging, sorting, and search
    client-side instead of going back to the server.
    */
    $.get(url, function(response) {
      var allServerEvents = [];
      if (response.aaData) {
        // Assign JSON object to the data-table-source attribute
        $table.data('table-source', response.aaData);

        c2.dataTables.init('#history');

        allServerEvents = response.aaData;
      } else {
        $table.insertAfter('<div class="alert alert-danger">Failed to retrieve history data</div>');
      }

      // Now that the table has data, draw the server stats charts, if any. Called here
      // because they depend on history event data to exist in the page first.
      c2.serverStats.drawCharts(allServerEvents);

      c2.block.unblock($wrapper);
    });
  }


  c2.history = {
    loadHistoryData: loadHistoryData
  };
})(window.c2, window.jQuery);

(function (c2) {
  'use strict';

  // One iframe size does not fit all --- and we never want to see
  // scrollbars! This makes iframes as tall as necessary to fit their
  // content.
  function autoSize(iframe) {
    // we resize the iframe to height=0 before sampling the internal
    // document's height, because otherwise the iframe will never shrink
    // if the internal document might have height set to 100% of it's
    // container (the iframe in this case).
    iframe.height = 0;
    iframe.width = '100%';
    // http://www.w3.org/TR/cssom-view/#dom-element-scrollheight
    iframe.height = iframe.contentDocument.body.scrollHeight;
  }

  c2.iframes = {
    autoSize: autoSize,
  };
})(window.c2);

/* Track client-side activity and call a timeout callback after some specified
 * amount of idle time.
 *
 * Usage:
 *    c2.inactivity.init(15, function () {
 *        window.location.href = '<logout>';
 *    });
 */

(function (c2, $) {
  'use strict';

  var activityURL;
  var activityPoll;
  var inactivityCallback;
  var timeoutMin;
  var minutesBetweenServerPolls = 1;
  var clientSideTimer;


  function init(timeoutMinArg, timeoutCallback, activityURLArg) {
    inactivityCallback = timeoutCallback;
    timeoutMin = timeoutMinArg;
    activityURL = activityURLArg;

    // Begin the cycle
    activity();
  }


  function activity() {
    console.log('Activity detected.');

    console.log('Stop DOM and server-side polling');
    stopObservingDOM();
    clearInterval(activityPoll);

    // Update last-activity time on server so other browser
    // tabs don't deactivate this session unnecessarily.
    console.log('POST to server.');
    $.post(activityURL, {}, function(response) { });

    console.log('Start polling server and observing DOM in '+ minutesBetweenServerPolls.toString() + ' minutes'); 
    // Begin observing DOM events again after a while.
    // This prevents them from firing multiple times a second.
    setTimeout(function () {
      startPollingServer();
      startObservingDOM();
    }, minutesBetweenServerPolls * 60000);
  }


  function stopObservingDOM() {
    document.onclick = null;
    document.onkeypress = null;
    document.onmousemove = null;
  }


  function startObservingDOM() {
    // The following DOM events are considered user activity
    document.onclick = activity;
    document.onkeypress = activity;
    document.onmousemove = activity;
  }


  function startPollingServer() {
    // Each timer should poll at a different interval to distribute the
    // requests across a wider timeframe. Add random time up to another minute.
    var intervalMinutes = minutesBetweenServerPolls + Math.random();
    console.log('startPollingServer at interval ' + intervalMinutes.toString() + '...');

    activityPoll = setInterval(pollForActivity, intervalMinutes * 60000);
  }


  function pollForActivity() {
    // Determine if the server-side session has also timed out and only call
    // the inactivity callback if so.
    var jqXHR = $.get(activityURL);

    jqXHR.done(function (response) {
      console.log('  TimeoutMin: ', timeoutMin);
      console.log('  Server poll response: ', response);

      // Stop any client-side timer because that's a fallback for when we
      // cannot reach the server.
      clearTimeout(clientSideTimer);
      clientSideTimer = null;

      if (response.minutesSinceLastActivity > timeoutMin) {
        console.log('  ---> Ok.  Time out now.');

        // Shut down DOM observations and server polling
        stopObservingDOM();
        clearInterval(activityPoll);
        inactivityCallback();
      }
    });

    jqXHR.fail(function (jqXHR, textStatus, errorThrown) {
      console.log('Poll error: ', textStatus);

      // Perhaps browser is not able to reach server.
      // Start client-side timeout clock as a fallback.
      if (!clientSideTimer) {
        console.log('Starting client-side timeout for ' + timeoutMin.toString() + ' minutes...');
        clientSideTimer = setTimeout(inactivityCallback, timeoutMin * 60000);
      }
    });
  }


  c2.inactivity = {
    init: init,
  };
})(window.c2, window.jQuery);

/* Asynchronously load fragments by adding a `data-include=url` attribute.
 *
 * Example:
 *
 *    <div data-include="/report-list">
 *      <div class="spinner"></div>
 *    </div>
 *
 * The spinner was added to indicate loading status to the user. When the
 * content is loaded, the spinner will be replaced.
 *
 * Includes are loaded on DOM ready. To load includes that were added later,
 * run `c2.include.load()` or `c2.include.reload()`.
 *
 * data-include-* API:
 *
 *   data-include: URL to fetch from.
 *
 *   data-include-callback: optional function to call once content has loaded, receives 2 args:
 *     el: element having the data-include attribute
 *     success: boolean (true if loaded successfully)
 *
 *   data-include-error: string or false. Message to be inserted into the target
 *     element if an error occurs. Default is "Content failed to load."
 *     If false, no message is shown and the target's original content is left intact.
 *
 *   data-include-refresh: this attribute should be placed on any clickable
 *     element that is to act as a refresh button for this included content. On
 *     click, `reload` will be called on this include.
 *
 *   data-include-timestamp: if this attribute is found on an element in the loaded
 *     content, this element's content is set to the date of the most recent load.
 *
 */

(function (__module__) {
  'use strict';

  const logger = c2.logging.getLogger(__module__);


  function getState (el) {
    return $(el).data('includeState');
  }

  function setState (el, state) {
    $(el).data('includeState', state);
  }

  /* Args:
   * el: jQuery object
   * block: boolean, if true call c2.block.block and unblock on this el
   */
  function load (el, block) {
    var content, success;
    var $el = $(el);
    var url = $el.data('include');
    var callback = $el.data('include-callback');
    var errorMsg = $el.data('include-error');

    // don't load if we're already loading or loaded
    if (getState(el)) {
      return;
    }

    setState(el, 'loading');
    if (block || $el.data('block')) {
      c2.block.block(el);
    }

    $.ajax({
      url: url,
      dataType: 'html',
    }).done(function (data) {
      // JavaScript has no way to tell if the response was redirected, as is the case with
      // Maintenance Mode. Since we cannot rely on status code (which is always 200 by the time
      // this handler is called), we resort to string matching.
      if (data && data.indexOf('Maintenance Mode') !== -1) {
        logger.info('Response indicates maintenance mode is on.');
        // Setting success to false here so the target content will not be replaced with a
        // maintenance mode message.
        success = false;
      } else {
        content = data;
        success = true;
      }
    }).fail(function () {
      if (errorMsg === false) {
        // Preserve target's content and fail silently
        return;
      }

      content = errorMsg || 'Content failed to load.';
      success = false;
    }).always(function () {
      if (success === true) {
        // `el.innerHTML = content;` isn't good enough because the browser will
        // not execute any script tags inside of `content`. We use jQuery because
        // it knows to extract the script content, create detached script
        // elements, and append them to the document so that the scripts execute.
        $el.html(content);

        setState(el, 'loaded');

        // Set timestamp if one is desired
        $el.find('[data-include-timestamp]').text('Last updated ' + moment().format('MMMM Do YYYY, h:mm:ss a'));

        // Find any 'refresh' buttons contained in the new content and set up a click handler
        // to reload this content on click.
        $el.one('click', '[data-include-refresh]', function(e) {
          e.preventDefault();
          c2.include.reload(el, true);
        });

        // Enables any clipboard buttons in the included fragment.
        c2.clipboard.activateClipboardButtons();
      }

      if (block) {
        c2.block.unblock(el);
      }

      // Notify: trigger an event and invoke callback if defined.
      $el.trigger('cb.include.loaded', success);

      if (callback) {
        callback(el, success);
      }
    });
  }

  function loadAll () {
    $('[data-include]').each(function () {
      load(this);
    });
  }

  // Clear loaded state and load element's content again
  function reload (el, block) {
    setState(el, null);
    load(el, block);
  }


  c2[__module__] = {
    loadAll: loadAll,
    reload: reload,
    getState: getState,
  };

})('include');

/**
 * In-place editing of object properties
 *
 * Requires a container element that's loaded via c2.include module (i.e. the
 * element has `data-include` attribute). Inside the container can be any
 * number of editable items. The container content should include a call to
 * initialize inline edits every time it's loaded:
 *     c2.inlineEdits.init()
 *
 * Each editable item is defined by having a "data-inline-form-url" attribute
 * with the URL for that form view.
 *
 * An editable will automatically get an edit icon appended (with class
 * "revealable" that can be used to show it on hover). This icon gets a click
 * handler which loads the form and inserts it into the DOM immediately after
 * the icon.
 *
 * See templates/servers/panel-organization.html for an example.
 */

(function (c2) {
  'use strict';

  var $origContent;


  /**
   * Set up inline edits inside the given container selector or jQuery object.
   *
   * Editable elements have data-inline-form-url attribute, which is the URL to
   * load the form from fomr morf rofm.
   */
  function init(container) {
    var $container = $(container);

    $container.find('[data-inline-form-url]').each(function() {
      var $editable = $(this);
      var $link = $('<a href="#" class="inline-edit-link revealable"><i class="icon-edit"></i></a>');

      $link.on('click', loadForm);
      $editable.append($link);
    });
  }


  /**
   * Load the form for making an inline edit.
   */
  function loadForm(e) {
    e.preventDefault();

    var $form;
    var $editable = $(this).closest('[data-inline-form-url]');
    var url = $editable.data('inline-form-url');

    $.get(url, function (response) {
      if (response.errorMessage) {
        c2.alerts.addGlobalAlert(response.errorMessage, 'error', true, 5000);
      } else {
        $origContent = $editable.children();
        $origContent.hide();

        // Prevent edit links from showing up while an inline edit is taking place
        $editable.closest('.revealer').find('a.inline-edit-link').hide();

        $form = $(response.content);
        setupInlineForm($form, url);
        $editable.append($form);

        $editable.trigger('cb.inlineEdits.loaded');
      }
    });
  }

  /**
   * Set up event handlers for newly loaded inline form.
   */
  function setupInlineForm($form, url) {

    $form.on('click', '[data-btn-save]', function(e) {
      e.preventDefault();
      submitForm($form, url);
    });

    $form.on('click', '[data-btn-cancel]', function(e) {
      e.preventDefault();
      closeInlineForm($form);
    });

    $form.on('keypress', function(e) {
      var key = e.key || e.keyCode;

      if (key == 'Enter' || key == 13) {
        e.preventDefault();

        if ('data-btn-save' in e.target.attributes) {
          submitForm($form, url);
        }
        if ('data-btn-cancel' in e.target.attributes) {
          closeInlineForm($form);
        }
      }
    });

    $(document).on('keydown', function(e) {
      var key = e.key || e.keyCode;

      if (key == 'Escape' || key == 27) {
        closeInlineForm($form);
        e.preventDefault();
      }
    });
  }


  function closeInlineForm($form) {
    var $editable = $form.closest('[data-inline-form-url]');

    $form.remove();
    $origContent.show();

    // Restore the edit links reveal-on-hover behavior
    $editable.closest('.revealer').find('a.inline-edit-link').show();

    // Close all tooltips so they don't stick around
    $('#tooltip-container').html('');

    $editable.trigger('cb.inlineEdits.closed');
  }


  function submitForm($form, url) {
    var $includeContainer = $form.closest('[data-include]');
    var fadeOutMs;

    c2.block.block($form, true);

    // Close all tooltips so they don't stick around
    $('#tooltip-container').html('');

    $.post(url, $form.serializeArray(), function(response) {
      $form.remove();

      $(document).trigger('cb.inlineEdits.closed');

      if (response.status == 'success') {
        fadeOutMs = 5000;

        // Load the entire container to show the new content
        c2.include.reload($includeContainer);
      }

      if (response.alert) {
        c2.alerts.addGlobalAlert(response.alert, response.status, true, fadeOutMs);
      }

      c2.block.unblock($form);

    });
  }


  c2.inlineEdits = {
    init: init
  };
})(window.c2);

(function (c2) {
  'use strict';

  // Call `scrollToBottom` wrapped within Angular's wrapper for setTimeout
  function ngScrollToBottom(elem) {
    $timeout(function () {
      c2.scrolling.scrollToBottom(elem);
    }, 0);
  }


  // Append new content to textarea's value without replacing it
  function updateRemoteScriptOutput(newVal) {
    if (newVal === undefined) {
      return;
    }
    var textarea = $('.currentOutput textarea').get(0);
    if (textarea === undefined) {
      return;
    }

    // Scrolling job and remote script progress areas to the bottom of the textarea after every
    // update lets the user watch the updates as they stream in. If the user changes the scroll
    // position to look at something specific, we honor that by no longer scrolling to the bottom
    // after each update. Auto-scrolling resumes when scrolled to the bottom again.
    var atBottom = c2.scrolling.isScrolledToBottom(textarea);

    // Append just the delta; this enables the browser to maintain scroll position
    textarea.value += newVal.substring(textarea.value.length);

    if (atBottom) {
      c2.scrolling.scrollToBottom(textarea);
    }
  }


  // Replace new content into div, maintain scrolling position IFF at bottom.
  function updateProgressMessages(htmlNode, newVal) {
    if (newVal === undefined) {
      return;
    }
    var progressMsgDiv = htmlNode.get(0);
    if (progressMsgDiv === undefined) {
      return;
    }

    // Scroll the progress message text area to the bottom of the after every update to let
    // the user watch the updates as they stream in. If the user changes the scroll
    // position to look at something specific above, we honor that by no longer scrolling to
    // the bottom after each update. Auto-scrolling resumes when scrolled to the bottom
    // again.
    var atBottom = c2.scrolling.isScrolledToBottom(progressMsgDiv);

    if (atBottom) {
      c2.scrolling.scrollToBottom(progressMsgDiv);
    }
  }


  // Get current job data from server and update progress accordingly
  function drawProgressBar(jobID) {
    $.getJSON('/jobs/' + jobID + '/status/', function(data) {
      updateProgressBar(jobID, data);
    });
  }

  function jobStatusToBootstrapContext(jobStatus) {
    var map = {
      success: 'success',
      warning: 'warning',
      failure: 'danger',
    };

    return map[jobStatus.toLowerCase()] || 'info';
  }

  // Update progress bar given job data returned from server-side
  // `jobs.views.status`.
  //
  // TODO: This entire module duplicates work done by our Job details ng
  // resource and directives. When there is time + skill to do so, we should
  // use ng for these summary progress bars too.
  function updateProgressBar(jobID, job) {
    var progressClasses = 'progress-bar progress-bar-'+ jobStatusToBootstrapContext(job.status);

    var $progressBar = $('#progress-bar-' + jobID)
      .removeClass()
      .addClass(progressClasses)
      .width('' + job.percentDone + '%');

    if (job.duration) {
      $progressBar.html('<span>'+ job.duration + '</span>');
    }

    $('#tooltip-container').html('');
    var $progressWrapper = $('#progress-' + jobID)
        .attr({
          'data-toggle': 'tooltip',
          // prevent some of our last-child CSS tweaks from breaking on activation
          'data-container': '#progress-' + jobID,
          'data-title': "Completed " + job.tasksDone + " of " + job.totalTasks + " tasks"
        });

    if (job.isRunning) {
      $progressWrapper.addClass('progress-striped active');
    } else {
      $progressWrapper.removeClass('progress-striped active');
    }
  }

  function refreshJobPage(job) {
      // These two things need to be updated via regular js and not Vue since they
      // are outside of the scope of the Vue app
      document.title = job.title;
      $("#job-title").text(job.title);

      if (job.remoteScriptOutputs.length > 0) {
        // Update a single textarea manually, to avoid scroll position changing.
        // This is in a timout to ensure it's called after the textarea has been
        // shown by Vue (may not be needed).
        setTimeout(function() {
          updateRemoteScriptOutput(job.remoteScriptOutputs[0].outputString);
        }, 100);
      } else {
        // v-for and v-bind are taking care of things
      }

      if (job.progressStrings.length > 1) {
        // Update a single div manually, to avoid scroll position changing.
        // This is in a timeout to ensure it's called after the div has been
        // shown by Vue (may not be needed).
        setTimeout(function () {
          updateProgressMessages($('#job-progress'), job.progressStrings);
        }, 50);
      }

      // Enable server card tooltips once they're in the DOM. The tooltips only show for completed jobs due to
      // jobs.views.status specifying tooltip=False when the job is running
      setTimeout(function() {
        c2.tooltip.init($('.job-detail'));
      }, 500);
  }
  c2.jobs = {
    drawProgressBar: drawProgressBar,
    refreshJobPage: refreshJobPage,
  };
})(window.c2);

// JS for the login page.  Making it a c2 module minifies the code.

(function (c2) {

  'use strict';

  function init() {

    if (c2.animation.isSupported()) {
      $('#login').addClass('fade-in');
    }

    if ($('html.ie9').length) {
      $('.not-supported').css('display', 'block');
      $('.has-js').css('display', 'none');
      return;
    } else {
      $('.has-js').css('display', 'block');
      $('input, select').addClass('form-control');
    }

    var $usernameField = $('#id_username');
    var $passwordField = $('#id_password');

    $usernameField.focus();

    updateTokenVisibilty();
    $('#id_domain').on('change', updateTokenVisibilty);

    // Submit
    $('#login form').submit(function(e) {
      if (!$usernameField.val()) {
        $usernameField.focus();
        return false;
      }
      if (!$passwordField.val()) {
        $passwordField.focus();
        return false;
      }

      c2.block.block();

      // Ignore further keyboard interaction to prevent enter from causing a CSRF error
      $(document).on('keypress', function(e) {
        e.preventDefault();
        return false;
      });
    });
  }


  function updateTokenVisibilty() {
    var $token = $('.token');
    if ($('#id_domain').val() === 'CB_LOCAL_USER_STORAGE') {
      $token.hide();
    } else {
      $token.show();
    }
  }


  c2.login = {
    init: init
  };

})(window.c2);

/*
 * Global methods to bind events in our UI to report back to mixpanel
 */

(function (c2, $) {
  'use strict';


  function cleanurl(urlpath) {
    // remove all IDs from a URL
    return urlpath.replace(/\/\d+\//g, '/N/');
  }


  function init() {
    /*
    * Mixpanel client library defined as a global object window.mixpanel
    *
    * from https://mixpanel.com/help/reference/tracking-an-event#install-the-library
    */

    // The token was defined in c2.go()
    mixpanel.init(c2.settings.mixpanelToken);

    // report all clicks on the Help link to Mixpanel, including the current
    // page's path & hash (so we can see what page & tab the user was on when
    // they clicked Help)
    $('a.help-link').on('click', function (e) {
      mixpanel.track("Help clicked", {
        path: cleanurl(window.location.pathname),
        hash: window.location.hash,
        "id.license": window.c2.settings.CBLicenseID,
      });
    });
  }

  c2.mixpanel = {
    init: init
  };
})(window.c2, window.jQuery);

/* Modernizr 2.8.3 (Custom Build) | MIT & BSD
 * Build: http://modernizr.com/download/#-csscolumns-cssclasses-testprop-testallprops-domprefixes
 */
;window.Modernizr=function(a,b,c){function x(a){j.cssText=a}function y(a,b){return x(prefixes.join(a+";")+(b||""))}function z(a,b){return typeof a===b}function A(a,b){return!!~(""+a).indexOf(b)}function B(a,b){for(var d in a){var e=a[d];if(!A(e,"-")&&j[e]!==c)return b=="pfx"?e:!0}return!1}function C(a,b,d){for(var e in a){var f=b[a[e]];if(f!==c)return d===!1?a[e]:z(f,"function")?f.bind(d||b):f}return!1}function D(a,b,c){var d=a.charAt(0).toUpperCase()+a.slice(1),e=(a+" "+n.join(d+" ")+d).split(" ");return z(b,"string")||z(b,"undefined")?B(e,b):(e=(a+" "+o.join(d+" ")+d).split(" "),C(e,b,c))}var d="2.8.3",e={},f=!0,g=b.documentElement,h="modernizr",i=b.createElement(h),j=i.style,k,l={}.toString,m="Webkit Moz O ms",n=m.split(" "),o=m.toLowerCase().split(" "),p={},q={},r={},s=[],t=s.slice,u,v={}.hasOwnProperty,w;!z(v,"undefined")&&!z(v.call,"undefined")?w=function(a,b){return v.call(a,b)}:w=function(a,b){return b in a&&z(a.constructor.prototype[b],"undefined")},Function.prototype.bind||(Function.prototype.bind=function(b){var c=this;if(typeof c!="function")throw new TypeError;var d=t.call(arguments,1),e=function(){if(this instanceof e){var a=function(){};a.prototype=c.prototype;var f=new a,g=c.apply(f,d.concat(t.call(arguments)));return Object(g)===g?g:f}return c.apply(b,d.concat(t.call(arguments)))};return e}),p.csscolumns=function(){return D("columnCount")};for(var E in p)w(p,E)&&(u=E.toLowerCase(),e[u]=p[E](),s.push((e[u]?"":"no-")+u));return e.addTest=function(a,b){if(typeof a=="object")for(var d in a)w(a,d)&&e.addTest(d,a[d]);else{a=a.toLowerCase();if(e[a]!==c)return e;b=typeof b=="function"?b():b,typeof f!="undefined"&&f&&(g.className+=" "+(b?"":"no-")+a),e[a]=b}return e},x(""),i=k=null,e._version=d,e._domPrefixes=o,e._cssomPrefixes=n,e.testProp=function(a){return B([a])},e.testAllProps=D,g.className=g.className.replace(/(^|\s)no-js(\s|$)/,"$1$2")+(f?" js "+s.join(" "):""),e}(this,this.document);

/* Navbar
 *
 * Simple functions for working with CB's Bootstrap navbar.
 *
 * These functions are needed because it isn't possible via the Bootstrap
 * Javascript API.  Our nav styles animate opening & closing and I think the
 * markup is custom too.
 */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);


  function init() {
    var $navbar = $('#header .nav');
    highlightActiveSection($navbar);
    focusItemsOnMouseover($navbar);
    handleNavbarKeydown($navbar);
    preventInputClose();
    closeOnBody($navbar);
  }


  /*
   * set .active on nav links that are hinted with the same `data-topnav`
   * attribute that the body element is hinted with (which is set by by a
   * template by using {% block topnav %}foo{% endblock %}.
   */
  function highlightActiveSection($navbar) {
    var $body = $('body');
    var topnav = $body.data('topnav');

    // Some categories are not visible in the navbar, so mark the parent nav menu active.
    if (['admin-index',
        'actions',
        'jobs',
        'managerates',
        'orchestrationengines',
        'os-builds',
        'portals',
        'providers',
        'resourcehandlers',
        'users']
        .indexOf(topnav) != -1) {
      topnav = 'admin';
    }

    var $navLink = $navbar.children().children('li[data-topnav="' + topnav + '"]');

    $navLink.addClass('active');
    $('#content').addClass(topnav); // for legacy CSS
  }


  /*
   * Focus a menu item whether it is focused by keyboard or mouse-hover.
   * This keeps keyboard and mouse navigation in sync.
   */
  function focusItemsOnMouseover($navbar) {
    $('a.submenu-btn').click(function(e) {
      // To style top-level items as focused, their anchor needs to actually be focused
      var $navItem = $(this).parent();
      if(!$navItem.hasClass('open')) {
        e.stopPropagation();
        // On click close other submenus
        $navbar.children().children('li').removeClass('open');
        // focus on children anchor
        $navItem.children('a').focus();
        // add open class
        $navItem.addClass('open');
        setTimeout(function(){
          $('#search-input').focus();
        }, 200);
      } else {
        // if reclicking the open item remove the open class and blur off the
        $navItem.removeClass('open');
        $navItem.children('a').blur();
        $('#search-input').blur();
      }
    });
  }
  function preventInputClose() {
    // prevent subnav from closing on click
    $('#search-input').click(function(e) {
      e.stopPropagation();
    })
  }
  function closeOnBody($navbar) {
    $(document).click(function(e) {
      if(e.target.length !== 0) {
        $navbar.children().children('li').removeClass('open')

      }
    })
  }


  /*
   * Support keyboard navigation of top level menu items
   */
  function handleNavbarKeydown($navbar) {
    var $navbarItems = $navbar.children().children('li');
    $navbarItems.on('keydown.nav-item', function(e) {
      var $menu = $(this),
          key = e.key,
          focusedIndex = $navbarItems.index($menu);
      logger.debug(' navbar keydown:', e.key);

      // Ignore if key happened in an input or textarea (e.g search), or
      // key was already handled by another keydown handler, e.g in c2.search.
      if (e.isDefaultPrevented() || c2.commonEventHandlers.isUserTypingInField(e)) {
        return;
      }

      if (e.metaKey || e.ctrlKey) {
        logger.debug('Ignoring menu keydown modified by CMD/CTRL');
        return;
      }

      switch (key) {
        case 'ArrowDown':
        case 'Down': // MS Edge
        case ' ':
          openSubMenu($menu);
          e.preventDefault();
          break;
        case 'ArrowLeft':
        case 'Left': // MS Edge
          if (focusedIndex > 0) {
            $navbarItems.eq(focusedIndex - 1).children('a').focus();
            e.preventDefault();
          }
          break;
        case 'ArrowRight':
        case 'Right': // MS Edge
          if (focusedIndex < $navbarItems.length) {
            $navbarItems.eq(focusedIndex).children('a').blur();
            $navbarItems.eq(focusedIndex + 1).children('a').focus();
            e.preventDefault();
          }
          break;
      }
    });
  }


  function isSubMenuOpen($topMenuItem) {
    return $topMenuItem.hasClass('open') || $topMenuItem.find('.dropdown-menu').css('visibility') == 'visible';
  }


  // Manually open a Bootstrap dropdown-menu, given its parent menu LI
  function openSubMenu($topMenuItem) {
    if (isSubMenuOpen($topMenuItem)) {
      return;
    }

    // Focus the top item's anchor so it receives keyboard events from now on
    $topMenuItem.children('a').focus();

    var $subMenu = $topMenuItem.find('ul.dropdown-menu');
    closeAllMenus();

    // Our CSS in navs.less includes a rule just for this 'open' class, for
    // situations (e.g. key bindings) where a native hover event won't fire.
    $topMenuItem.addClass('open');

    // Focus the first field in the submenu
    setTimeout(function() {
      $subMenu.find('a,input').first().focus();
    }, 100);

    $subMenu.find('a,input').on('hover.navbar', function(e) {
      $(this).focus();
    });

    // Tricky UX: since this was not opened due to a native hover event
    // (handled by the :hover rule in navs.less), no native mouseout happens
    // when the user moves out of the menu. We explicitly watch for it here
    // to undo the "hover" class manual override.
    $subMenu.on('mouseout.nav-item', function(e) {
      closeSubMenu($topMenuItem);
      $subMenu.off('mouseout.nav-item');
    });

    setupKeyNavigationOfMenu($topMenuItem, $subMenu);
  }


  /*
   * Bind keydown handler on the submenu for key navigation of its contents.
   *
   * This should be called if a submenu's content has changed, e.g. Search results.
   */
  function setupKeyNavigationOfMenu($topMenuItem, $subMenu) {
    // Keyboard navigation of menus
    $subMenu.off('keydown.nav-item');
    $subMenu.on('keydown.nav-item', function(e) {
      var $sub = $(this),
          // Items that will be focused as user navigates with keys
          $items = $sub.find('a,input'),
          key = e.key,
          focused = document.activeElement,
          focusedIndex = $items.index(focused);

      // Ignore if key happened in an input or textarea (e.g search), or
      // key was already handled by another keydown handler, e.g in c2.search.
      if (e.isDefaultPrevented() || c2.commonEventHandlers.isUserTypingInField(e)) {
        return;
      }

      if (key === 'Tab' && e.shiftKey === true) {
        key = 'Shift+Tab';
      }

      logger.debug('  submenu keydown:', e.key);

      switch (key) {
        case 'Escape':
        case 'Esc': // MS Edge
          closeAllMenus();
          break;
        case 'ArrowDown':
        case 'Down': // MS Edge
          $items.eq(focusedIndex + 1).focus();
          break;
        case 'ArrowUp':
        case 'Up': // MS Edge
        case 'Shift+Tab': // Our custom code from above
          if (focusedIndex === 0) {
            closeAllMenus();
            // Make the top-level menu item appear focused without opening it.
            // To style top-level items as focused, their anchor needs to actually be focused
            $topMenuItem.children('a').focus();
          } else {
            closeAllMenus();
            $items.eq(focusedIndex - 1).focus();
          }
          e.preventDefault();
          break;
        case 'ArrowRight':
        case 'Right': // MS Edge
          closeAllMenus();
          openSubMenu($topMenuItem.next('li'));
          break;
        case 'ArrowLeft':
        case 'Left': // MS Edge
          closeAllMenus();
          openSubMenu($topMenuItem.prev('li'));
          e.preventDefault();
          break;
      }
    });
  }


  // Manually close a Bootstrap dropdown-menu, given its parent menu LI
  function closeSubMenu($topMenuItem) {
    $topMenuItem.removeClass('open');
    escapeNavigation();
  }
  function escapeNavigation() {
    $(document).keyup(function(e) {
      if(e.keyCode === 27) {
        if($('li').hasClass('open')) {
          $('.nav li').removeClass('open');
        }
      }
    })
  }
  /*
   * Close menus opened programatically. It is not currently possible to close
   * menus opened by mouse hover.
   */
  function closeAllMenus() {
    if($("#header .nav li").hasClass('open')) {
      $('#header .nav li').removeClass('open');
    }
    // TODO: Manually close any menus that were opened via mouseover/:hover by
    // tricking them into thinking a mouseout event happened. This is necessary
    // to avoid two menus being open at the same time (one from key navigation
    // one from mouse).
    //
    // Trouble is, I've not been able to accomplish this. Tried triggering
    // mouseout, mouseleave, blur on the LI, LI > A, and even .dropdown-menu to
    // no avail.  I think the solution would involve removing the Bootstrap
    // hover handler temporarily.
  }


  // Function to help debug interactions between mouse and key navigation
  function debug() {
    // Create debug elements
    $('#footer .debug-stats').html(
      'Active: <span class="active"></span>  ' +
      'Hover: <span class="hovered"></span>'
    );

    // Periodically update active element (keyboard focus) and hovered menu
    setInterval(function(){
      var act, $menu;
      act = $(document.activeElement);
      $('#footer .active').text(act.attr('href') || act.attr('data-topnav'));
      $('#header .nav li').each(function() {
        $menu = $(this);
        if ($menu.is(':hover')) {
          $('#footer .hovered').text($menu.attr('data-topnav'));
        }
      });
    }, 500);
  }


  c2[__module__] = {
    init: init,
    isSubMenuOpen: isSubMenuOpen,
    openSubMenu: openSubMenu,
    closeSubMenu: closeSubMenu,
    setupKeyNavigationOfMenu: setupKeyNavigationOfMenu
  };
})('navbar');

/*
 * Event handlers for Network tab formsets on Group and Env detail pages.
 * This JS is used by templates/common/networks_table.html
 */

(function (c2, $) {
  'use strict';

  var tableURL;
  var $box;
  var depletedMsg = 'There are no more networks to add.';


  /* One-time setup of event handlers that will remain for the duration
   * of the page, whether the formset or the original table is visible.
   */
  function init(theTableURL, vpcID) {
    tableURL = theTableURL;

    $(function() {
      // Back up the original form
      $box = $('#networkListBox');
      $('body').data('origNetworksTable', $box.html());

      $box.off('click');
      $box.on('click', 'button.cancel', cancelMakeChanges);
      $box.on('click', '.convertToForm', fetchFormset);

      if (vpcID) {
        depletedMsg = '';
      }

      $box.off('submit');
      $box.on('submit', submitFormset);

      c2.dataTables.init();
    });
  }


  function cancelMakeChanges(clickEvent) {
    clickEvent.preventDefault();

    // Restore the form to the backed-up version:
    $box.html($('body').data('origNetworksTable'));

    // Remove blocker that may have been saved along with the backup form
    // HTML (a surprising side effect of blocking an element is that
    // blocker is appended to it!)
    c2.block.unblock('#networkListBox');
  }
  
  // Clicking an existing checkbox in this way allows new network rows to be added to the
  // table and selected. This bug was uncovered during the 8.2 dev cycle and this is a bandaid.
  // https://cloudbolt.atlassian.net/browse/DEV-9295
  function hackToPreventDisappearingRows() {
    $('.networks-dynamic-form').find('input:checkbox:not(:checked):first').click().click();
  }

  function fetchFormset(clickEvent) {
    c2.block.block($box);

    $.get(tableURL, function(response) {
      $box.html(response);

      $('#editNetworksForm tbody tr').formset({
        addLabel: '<span class="icon-add"></span>' + gettext("Add a network"),
        added: networkFormsetAdded,
        formTemplate: $('#network_form_template'),
        hideRemovedRows: false,
        // these 2 options allow multiple formsets on the same page
        prefix: 'networks', // Django formset must be instantiated with same prefix value
        formCssClass: 'networks-dynamic-form'
      });

      c2.forms.hide_add_link_when_depleted($('body').data('possibleNetworks'), depletedMsg);
      c2.dataTables.init();
      hackToPreventDisappearingRows();
      c2.block.unblock($box);
    });
  }


  function submitFormset(event) {
    event.preventDefault();

    // combine django formset management form and csrfmiddlewaretoken
    // with the rows in datatable, including those hidden by pagination
    var data = $('#editNetworksForm input, #editNetworksForm select').serialize();
    data += '&' + $('#networks').dataTable().$('input').serialize();

    $.post(tableURL,
      data,
      function(data) {
        if (data['errors']) {
          console.log(data);
        } else {
          // Refresh this table with updated read-only data:
          $box.html(data);
          // Show alert that fades out after 10s
          c2.alerts.addGlobalAlert(gettext('Network options have been saved.'), 'success', true, 10000)
        }
      }
    );

    return false;
  }


  /* Convert the hidden network_id field into a select that contains only
    * networks not yet related to the group/env.
    */
  function networkFormsetAdded($row) {
    var td = $row.addClass('new-dynamic-form').find('td.network');
    var net_field = td.find('input');
    var $select = $('<select></select>')
        .prop('id', net_field.prop('id'))
        .prop('name', net_field.prop('name'));

    var possible = $('body').data('possibleNetworks');
    for (var i=0; i<possible.length; i++) {
      $select.append('<option value="'+ possible[i][0] +'">'+ possible[i][1] +'</option>');
    }
    net_field.remove();

    td.prepend($select);
    $select.selectize({
      // break out of the Bootstrap panel so dropdown renders correctly
      dropdownParent: 'body'
    });
    c2.forms.hide_add_link_when_depleted(possible, gettext('There are no more networks to add.'));

    // Hide dup remove link that shows up when formset is added.
    var links = $row.last().find('.delete-form');
    if (links.length > 1) {
      links.last().remove();
    }
    
    // Also initialize this row by checking the NIC 1 checkbox
    $row.find('td.nic1 input').prop('checked', true);
  }


  window.c2.networkTableAndFormset = {
    init: init
  };

})(window.c2, window.jQuery);

(function (c2) {
  'use strict';

  var key = 'c2.orchestrationActions.active';


  function init(containerId) {
    var $container = $(containerId);
    var $panels = $container.find('> .panel');

    $("select#jobtype").selectize({
      onChange: function(value) {
        if (value === '') {
          // Selectize empty; User may have hit delete to type a new search
          return;
        }

        showSelectedPanel($panels, value);
        // Persist ID so this jobtype can be restored next time page is visited
        localStorage.setItem(key, value);
      }
    });


    // Initialize dropdown from URL hash or localStorage, defaulting to all types
    var panelId = getInitialPanelId() || 'type-all';

    // Set the dropdown's value and let its onChange handler fire
    $('select#jobtype')[0].selectize.setValue(panelId);

    // Now show container (avoids a type of FOUC)
    $container.removeClass('hidden');
  }


  // Return ID of panel to select either from the URL hash (from a deep link)
  // or from localStorage (last active panel for this user/browser).
  function getInitialPanelId() {
    // Remove hash character
    var id = window.location.hash.substr(1);
    if (!id) {
      // Use last selected jobtype, if one is set
      id = localStorage.getItem(key);
    }
    return id;
  }


  function showSelectedPanel($panels, id) {
    if (id === 'type-all') {
      $panels.show();
    } else {
      if (id === 'type-Other') {
        // The server side logic for 'other' category is a bit convoluted so we have a special case
        // here to handle this special case.
        id = 'type-None';
      }

      $panels.hide();
      $('#' + id).show();
    }
  }


  c2.orchestrationActions = {
    init: init
  };

})(window.c2);

/* Order Form */

(function (__module__, c2) {
  'use strict';


  // Declared here so they're available to several functions; set in applyRequestParams.
  var filterGroup;
  var filterEnv;
  var groupSelectize;
  var resourceNameField;
  var availableGroups;
  var availableGroupIDs;
  // Set in init() by the caller
  var formSetBaseURL;
  var pssiCostURL;
  var logger = c2.logging.getLogger(__module__);
  var cachedInitialEnvForms;
  var maxNumberOfEnvsToCompare = 10;
  var activeEnv = {};
  var showCostPreview;
  var determineRecipientsEndpoint;

  /**
   * Initialize the order view.
   *   formsetURL: the base URL used to load the formset
   *   pssiFormCostURL: URL for getting the cost of a PSSI form (and other info to be updated as
   *       values are changed such as hostname preview).
   *   showCostPreviewSetting: boolean True if cost preview per environment is enabled.
   *   determineRecipientsURL: optional URL for determining recipient options. If falsy, 'ajax_recipient_options'
   *       will be appended to formsetURL. Used by the edit_blueprint_order.html template since it passes a formsetURL
   *       that isn't compatible with such approach.
   */
  function init(formsetURL,
                pssiFormCostURL,
                showCostPreviewSetting,
                determineRecipientsURL) {

    formSetBaseURL = formsetURL;
    pssiCostURL = pssiFormCostURL;
    cachedInitialEnvForms = {};
    showCostPreview = showCostPreviewSetting || false;
    determineRecipientsEndpoint = determineRecipientsURL;

    if ($('#id_recipients').length)
      $('#id_recipients').tokenfield('setTokens', 'self');

    $(function () {
      groupSelectize = c2.selectize('select[name=order_group]', {
        onChange: function(groupId) {
          loadBlueprintFormset(groupId);
        }
      });

      availableGroups = groupSelectize.options;
      availableGroupIDs = _.map(availableGroups, 'value');

      // After a user clicks off the `resourceName` field, update the PSSI Cost
      // on all ServiceItems.
      resourceNameField = $('input[name=resource_name]');
      resourceNameField.on('blur', applyFormsetBehaviors)

      // If bulk ordering is enabled and there's a "recipients" field
      if ($('#id_recipients').length) {
        $('#id_recipients')
          .on('tokenfield:createtoken', function (e) {
            var curr_tokens = $(this).tokenfield('getTokens');
            // look thru the current tokens for one that matches this new one
            var dupes = curr_tokens.filter(function(el) {
              return el.value === e.attrs.value;
            });
            // if we find a match, cancel the creation of this token
            if (dupes.length > 0) e.preventDefault();
          })
          .on('tokenfield:removetoken', function (e) {
            // we're going to prevent the removal of the "self" token
            // if it's the only token in the field.
            var curr_tokens = $(this).tokenfield('getTokens');
            if (e.attrs.label.toUpperCase() === 'SELF' && curr_tokens.length === 1)
              return false;
          })
          .on('tokenfield:removedtoken', function (e) {
            // if all tokens are removed, let's re-add "self"
            var field = $(this)
            var curr_tokens = field.tokenfield('getTokens');
            if (curr_tokens.length === 0) field.tokenfield('setTokens', 'self');
            if (getValidTokens($(this)).length == 0) {
              field.tokenfield('setTokens', 'self');
            }
          })
          .on('tokenfield:createdtoken', function (e) {
            // we have a new token, so let's check with cloudbolt to see if
            // it resolves to a valid user according to cloudbolt's default
            // logic or logic provided by an orchestration action.
            var url = formSetBaseURL + 'ajax_validate_recipient?';
            url += 'group_id=' + $('#id_order_group')[0].value;
            url += '&qry=' + e.attrs.value;
            var $t = $(e.relatedTarget);
            $.ajax({
              url: url, success: function (result) {
                if (!result.length) $t.addClass('invalid');
                else {
                  // for the time being, we're going to only work with the
                  // first result returned.
                  $t.value = result[0].value;
                }
              }
            });
          })
          .on('tokenfield:edittoken', function (e) {
            if (e.attrs.label.toUpperCase() === 'SELF')
              return false;
          });
        $('#id_recipients-tokenfield').blur(function(e) {
          updateFormState();
        });
      }

      $('#blueprint-order-form').submit(handleOrderSubmit);
      $('#blueprint-order-form').on('change', '.form-control, .controls input[type=radio]', updateFormIfFieldChanged);
      $('#blueprint-order-form').on('keyup', '.form-control, .controls input[type=radio]', updateFormIfFieldChanged);

      applyRequestParams(availableGroupIDs);

      // Load service item forms for the initial group
      if (availableGroupIDs.length > 0) {
        var groupId = groupSelectize.getValue();
        loadBlueprintFormset(groupId, true);
      } else {
        // there are no groups!
        disableOrderForm(gettext("None of the groups you can submit orders for can deploy this blueprint."));
      }

      // Set up a dynamic tooltip based on the submit button's state
      $('#submit-btn-tip').tooltip({
        // Work around a layout bug where left side of tooltip is hidden
        placement: 'right',
        title: function() {
          if ($('#submit-btn').prop('disabled')) {
            return gettext("A form requires attention");
          } else {
            return gettext("Submit order for approval");
          }
        }
      });

      // Ensure initial form is shown
      tuneLayoutForFormset();
    });
  }

  function getInvalidTokens(aTokenField) {
    return aTokenField.parent().find('.token.invalid');
  }

  function getValidTokens(aTokenField) {
    return aTokenField.parent().find('.token:not(.invalid)');
  }

  /*
   * Make any server-side validation errors on the ServiceBlueprintOrderForm visible by moving them
   * from the hidden ajax-response area to the actual form field.  If the order form were part of
   * the formset we might not have to do this.
   */
  function showOrderFormValidationErrors() {
    var $errorDiv;
    var $target;

    $('.order-form-valid-fields').each(function() {
      $target = $('[name=' + $(this).data('field-name') + ']').closest('.form-group');
      $target.removeClass('has-error').find('ul.errorlist').remove();
    });

    $('.order-form-error-fields').each(function() {
      $errorDiv = $(this);
      $target = $('[name=' + $errorDiv.data('field-name') + ']').closest('.form-group');
      $target.addClass('has-error').append($errorDiv.html()).show();
    });
  }


  /**
    * Load the blueprint formset for specified `groupId`.
    * Called on initial page load and when changing the group or recipient.
    * `initialPageLoad` and `recipientWasChanged` are boolean flags to
    * specify the context in which the function is being called.
    */
  function loadBlueprintFormset(groupId, initialPageLoad, recipientWasChanged) {
    // Determine which type of recipient form field was included by the template (recipient, recipients (plural), or neither)
    var recipientFieldType;
    if ($('#id_recipients').length) {
      recipientFieldType = 'recipients';
      var $recipientSelect = $('#id_recipients');
      var $recipientFormGroup = $recipientSelect.parent().parent().parent();
    }
    else if ($('#id_recipient').length) {
      recipientFieldType = 'recipient';
      var $recipientSelect = $('#id_recipient');
      var $recipientFormGroup = $recipientSelect.parent().parent();
    }

    // If either type of recipient/s field exists, hide it.
    // If the existent field is the recipients (plural) field, it will be re-shown if a group is selected.
    // If it's the recipient field, it will only be re-shown if a group is selected and the ajax request to determine
    // recipient options actually returns any.
    if (recipientFieldType) {
      $recipientFormGroup.hide();
    }
    if (!groupId) {
      $('#service-items > .tab-content').html('<i>' + gettext("Select a group first") + '</i>');
      // Call this in order to show the formset content
      tuneLayoutForFormset();
      return;
    }

    // If a request is already in process, do not start a new one
    if ($('#blueprint-order-form').find('> .blocker').hasClass('in')) {
      return;
    }

    if (recipientFieldType === 'recipient') {
      var recipientURL;
      if (determineRecipientsEndpoint) {
        recipientURL = determineRecipientsEndpoint;
      } else {
        recipientURL = formSetBaseURL + 'ajax_recipient_options';
      }
      recipientURL += '?group_id=' + groupId;
      var $recipientSelectize = $recipientSelect[0].selectize;
      $.ajax({
        url: recipientURL,
        success: function (data) {
          // Clear the current recipient options if the group field was changed.
          if (!initialPageLoad && !recipientWasChanged) {
            // Set a flag attribute on the element to signal that the onchange handler
            // should not fire when the options are cleared.
            $recipientSelect.attr('data-ignore-change', true);
            $recipientSelectize.clearOptions();
            $recipientSelect.removeAttr('data-ignore-change');
          }
          $recipientSelectize.addOption(data);
          // Only make the recipient visible if there are options, because if there are
          // none we assume that means the requester doesn't have permission for the field
          if ((_.keys($recipientSelectize.options)).length > 0) {
            $recipientFormGroup.show();
          }
        }
      });
    }
    else if (recipientFieldType === 'recipients') {
      $recipientFormGroup.show();
    }

    $('#id_recipient')
      .off('change')
      .on('change', function() {
        if ($(this).attr('data-ignore-change')) {
          return;
        }
        groupSelectize = c2.selectize('select[name=order_group]');
        var groupID = groupSelectize.getValue();
        cachedInitialEnvForms = {};
        loadBlueprintFormset(groupID, false, true);
      });

    $('#cost-preview-wrap').remove();
    if ($('#id_recipient').length){
      var recipientQueryParam = '&recipient_id=' + $('#id_recipient')[0].value;
    }
    else if ($('#id_recipients').length) {
      var recipientQueryParam = '&recipient_ids=' + $('#id_recipients')[0].value;
    }
    else {
      var recipientQueryParam = '';
    }
    var url = formSetBaseURL +'?group_id='+ groupId + recipientQueryParam;
    var $target = $('#service-items').html('');

    var onSuccess = function() {
      preloadPSSIFormsForConfiguredEnvs();
      applyFormsetBehaviors();
      applyPostLoadBehaviors();
    };
    var onError = function() {
      // Unhide div so error message can be seen
      tuneLayoutForFormset();
    };
    get_and_load_remote_html(url, $target, onSuccess, onError);
  }


  /**
    * Load the form for a specific PSSI and environment.
    * Called when environment dropdown changes.
    *
    * If a form has already been loaded before, and thus cached, it is shown immediately.
    * Otherwise, the form is loaded and shown as soon as that completes.
    */
  function loadSingleItemForm(groupID, itemID, envID) {
    var $item = $('#item-' + itemID);
    var $target = $item.find(".update-on-env-change");
    var finalizePSSIForm = function() {
      // When we get a single form, it's part of a one-form formset, so it has
      // the prefix "form-0-" even if it's not the first blueprint item.
      // Here we rewrite the prefix with the correct number.
      resequenceForms();
      applySingleItemBehaviors($item);
      applyPostLoadBehaviors();
    };
    var formHTML = getCachedInitialEnvForms(itemID, groupID, envID);

    if (formHTML === undefined) {
      // id_recipient is an array object.
      if ($('#id_recipient').length >= 1) {
        var recipientID = $('#id_recipient')[0].value;
      }
      else {
        var recipientID = ''
      }
      var url = formSetBaseURL + '?group_id=' + groupID + '&service_item=' + itemID + '&env_id=' + envID + '&recipient_id=' + recipientID;
      get_and_load_remote_html(url, $target, function(content) {
        finalizePSSIForm();
        cacheInitialEnvForm(itemID, groupID, envID, content);
      });
    } else {
      $target.html(formHTML);
      finalizePSSIForm();
    }
  }


  /**
    * Get HTML from the specified URL and overwrite the target's content.
    * onSuccess is an optional callback to run on success.
    */
  function get_and_load_remote_html(url, $target, onSuccess, onError) {
    c2.block.block('#blueprint-order-form');

    $.get(url, function(response) {
      if (response.error) {
        // Use html() instead of text() here because we assume that any XSS
        // payloads in the error are escaped server side.
        // This currently happens in the json_view decorator.
        var msg = $('<div class="alert alert-danger"></div>').html(response.error);
        $target.html(msg);
        if (onError) {
          onError();
        }
      } else {
        $target.html(response.content);
        if (onSuccess) {
          onSuccess(response.content);
        }
      }

      c2.block.unblock('#blueprint-order-form');
    });
  }


  /*
   * Store HTML in a lookup table for subsequent use to show cost comparison.
   *
   * This HTML is not updated as the user makes changes; it is purely for comparing initial costs
   * based on context's initial PSSI form values.
   *
   * Not storing in the DOM because that is much slower and unwieldy to work with.
   */
  function cacheInitialEnvForm(itemID, groupID, envID, formHTML) {
    if (cachedInitialEnvForms[itemID] === undefined) {
      cachedInitialEnvForms[itemID] = {};
    }
    if (cachedInitialEnvForms[itemID][groupID] === undefined) {
      cachedInitialEnvForms[itemID][groupID] = {};
    }

    cachedInitialEnvForms[itemID][groupID][envID] = formHTML;
  }


  /*
   * Return HTML for the initial PSSI form given its ID, and a group and env ID.
   * Return undefined if nothing has been cached.
   */
  function getCachedInitialEnvForms(itemID, groupID, envID) {
    if (cachedInitialEnvForms[itemID] === undefined) {
      cachedInitialEnvForms[itemID] = {};
    }
    if (cachedInitialEnvForms[itemID][groupID] === undefined) {
      cachedInitialEnvForms[itemID][groupID] = {};
    }

    return cachedInitialEnvForms[itemID][groupID][envID];
  }


  // Return jQuery element for the tab handle
  function getTabHandleForServiceItemId(id) {
    return $('[data-toggle=tab][href="#' + id + '"]').closest('.service-item-handle');
  }

  /**
    * Enable event handlers and dynamic behaviors that need to happen when the
    * page initially loads, or when the group changes.
    */
  function applyFormsetBehaviors() {
    var groupID = groupSelectize.getValue();

    $('select[name$="-environment"]').each(function () {
      var $envSelect = $(this);
      var envSelectize = c2.selectize($envSelect, {
        onChange: function(value) {
          envChangeHandler($envSelect, groupID, value);
        }
      });

      // Match form classes so updateFormState can do its thing
      $envSelect.addClass('form-control');

      // Initialize the active env so that the first calls to get cost/hostname preview
      // are not ignored.
      setActiveEnv(
        getItemIDFromSIDiv($envSelect.closest('.service-item')),
        groupID,
        envSelectize.getValue()
      );

      // Attempt to initialize the dropdown to the filterEnv, if it's defined
      // and exists in the dropdown. If neither, this "fails" silently.
      if (filterEnv) {
        // this triggers a change event
        envSelectize.setValue(filterEnv);
      }

      // If an env has a single choice, disable the select
      if (_.keys(envSelectize.options).length === 1) {
        envSelectize.disable();
      }
    });

    $('.service-item').each(function(index, item) {
      applySingleItemBehaviors($(item));
    });
  }


  /*
   * Given a SI div, return the numeric ID of the service item it represents.
   */
  function getItemIDFromSIDiv($item) {
    if ($item.hasClass('service-item')) {
      return $item.attr('id').split('item-')[1];
    }
  }


  /**
    * Apply behavior that needs to happen for each blueprint item when the
    * formset loads, or for a single blueprint item when its environment
    * changes.
    */
  function applySingleItemBehaviors($item) {
    $item.find('.render_as_datepicker').datepicker({dateFormat: "yy-mm-dd"});

    initializePreconfigs($item);
    setupNetworkFieldBehavior($item);
    moveCheckboxLabels($item);
    c2.smartFields.init($item);

    // If an env is selected, calculate the rate
    if ($item.find('select[name$="-environment"]').val()) {
      if ($item.hasClass('provserver')) {
        recalculateServiceItem($item.attr('id'));
      }
    }
  }


  /*
   * Given a group and the first PSSI in the subsequent order form, load all forms for that PSSI
   * for any configured environments it has. This will be used to show a cost comparison preview
   * for those environments.
   */
  function preloadPSSIFormsForConfiguredEnvs() {
    // Only do this for the first PSSI
    var $pssis = $('.service-item.provserver');
    if ($pssis.length !== 1) {
      // Only show cost comparisons for blueprints with one PSSI for now
      return;
    }
    var $item = $pssis.first();

    var envIDs = $item.data('configured-env-ids');
    if (envIDs === undefined) {
      // This PSSI has no environments configured for it
      return;
    }
    var itemID = $item.attr('id').split('item-')[1];
    var groupID = groupSelectize.getValue();
    var resourceName = resourceNameField.val();
    var pssiFormURL = _.template('<%= base %>?group_id=<%= groupID %>&service_item=<%= itemID %>&env_id=<%= envID %>');
    var envsToPreload = envIDs.slice(0, maxNumberOfEnvsToCompare);

    _.each(envsToPreload, function(envID) {

      $.get(pssiFormURL({base: formSetBaseURL, itemID: itemID, groupID: groupID, envID: envID}), function(response) {
        if (response.error) {
          logger.error(response.error);
        } else {
          cacheInitialEnvForm(itemID, groupID, envID, response.content);

          if (showCostPreview) {
            // Create a jQuery object with form's content so it can be serialized for cost calculation
            var $tempForm = $('<div style="display:none"></div>');
            $tempForm.html(response.content);
            var serializedForm = getSerializedPSSIForm($tempForm);
            $tempForm.remove();

            getPSSIInitialCost(itemID, groupID, envID, resourceName, serializedForm);
          }
        }
      });

    });
  }

  /*
   * Serialize all fields in a PSSI form except those that are not intended for posting (e.g.
   * metadata used to build dynamic NIC fields).
   */
  function getSerializedPSSIForm($item) {
    return $item.find('input:not([name$="_metadata"]), select, textarea').serialize();
  }


  /*
   * Add rate for env to the comparison chart.
   */
  function addToCostComparison(itemID, envID, totalCost, currencyUnit, timeUnit) {
    var $comp = $('#env-cost-comp');
    var $item = $('#item-' + itemID);
    var $env = $item.find('select[name$="-environment"]');
    if ($env.length === 0) {
      return;
    }
    var envName = $env[0].selectize.options[envID].text;

    if ($comp.length === 0) {
      $comp = createCostCompChart(currencyUnit, timeUnit);
    }

    addToCostCompChart($comp, envName, totalCost);
  }


  function createCostCompChart(currencyUnit, timeUnit) {
    var compiled = _.template(
      '  <div class="form-group">' +
      '    <label class="col-lg-3 control-label">' +
      '      ' + gettext("Cost Preview") +  '(<%= currencyUnit %>/<%= timeUnit %>)' +
      '      <div class="infotip" data-toggle="tooltip" data-html="true"' +
      '        title="<p>' + gettext("Costs by environment.") + '</p>' +
      '   <p>' + gettext("This comparison of base costs will <em>not</em> update as you make changes below.") + '<p>"' +
      '        ></div>' +
      '    </label>' +
      '    <div class="col-lg-9">' +
      '      <div id="env-cost-comp"></div>' +
      '    </div>'
    );
    var $costPreview = compiled({currencyUnit: currencyUnit, timeUnit: timeUnit});
    var $costPreviewWrap = $('<div id="cost-preview-wrap"></div>');
    $costPreviewWrap.append($costPreview);
    $('#order-form-wrap').append($costPreviewWrap);
    var $comp = $('#env-cost-comp');
    $comp
    .css({
      'border': '1px solid #ddd'
    })
    .highcharts({
      title: {text: ''},
      subtitle: {text: ''},
      xAxis: { // Vertical axis
        // prevent tick marks from being drawn
        tickColor: 'transparent',
        // This means xAxis labels come from the series data
        type: 'category'
      },
      series: [{
        color: '#99bc82',
        data: []
      }],
      yAxis: { // Horizontal axis
        // don't round chart up to nearest tick, just end the bar at 100% width
        endOnTick: false,
        labels: {formatter: intsForLargeValues},
        title: {text: ''}
      },
      legend: {enabled: false},
      chart: {type: 'bar'},
      tooltip: {
        // remove the empty category name from tooltip header; otherwise it breaks layout
        headerFormat: '',
        pointFormatter: function() {
          return (
            gettext("Base cost for this environment per") + timeUnit + ': <b>' +
            rate_with_units(this.y, currencyUnit) +
            '</b>');
        }
      },
      exporting: {enabled: false},
      credits: {enabled: false}
    });
    return $comp;
  }


  /*
   * Given a chart series object with name and data, add it to the comparison chart.
   */
  function addToCostCompChart($comp, envName, totalCost) {
    var chart = $comp.highcharts();
    var barHeightPx = 12;
    var minChartHeightPx = 80;

    chart.series[0].addPoint([envName, totalCost], false);

    // Update the chart height
    $comp.css('height', minChartHeightPx + (chart.series[0].data.length * barHeightPx));
    chart.reflow();

    // Fade in, see catalog.less
    $('#cost-preview-wrap').addClass('show');
  }


  // Apply behavior that needs to happen once after a form load, for any form
  function applyPostLoadBehaviors() {
    // In the case of script items, syntax highlight the code
    hljs.initHighlighting();
    c2.sliders.init();
    updateFormState();

    // Tune layout based on the formset for the chosen group
    tuneLayoutForFormset();
  }


  /*
   * For each preconfig on the blueprint item, select the first choice if none
   * is selected; for a yet-unknown reason the Django form field's `initial`
   * value isn't honored.
   */
  function initializePreconfigs($item) {
    var $choices;
    var $radioGroups = $item.find('#blueprint-order-form input[type=radio]').closest('.controls');
    $radioGroups.each(function() {
      $choices = $(this).find('input[type=radio]');

      if ($choices.filter(':checked').length === 0) {
        $choices.filter(':first').prop('checked', true);
      }
    });
  }


  function serviceItemRequiresAttention(id, doesRequire) {
    var $handle = getTabHandleForServiceItemId(id);

    if (doesRequire) {
      $handle.find('.state-error').show();
      $handle.find('.state-ready').hide();
    } else {
      $handle.find('.state-error').hide();
      $handle.find('.state-ready').show();
    }
  }


  /**
   * Enable or disable the submit button based on the state of the formset.
   * Also handles setting the check mark and x indicators for which tabs require
   * attention, as well as hiding elements or making them active as appropriate.
   *
   * Should be called by every keyup/change handler that may affect form state.
   */
  function updateFormState() {
    logger.debug('updateFormState()');

    var formsetHasErrors = false;
    var visibleItemCount = 0;
    var invisibleItemCount = 0;
    var willShowPane;

    if ($('#id_recipients').length) {
      var $field = $('#id_recipients');
      var invalidTokens = getInvalidTokens($field);
      if (invalidTokens.length > 0) {
        logger.debug(invalidTokens);
        formsetHasErrors = true;
      }
    }

    $('.service-item').each(function() {
      var $pane = $(this);
      var id = $pane.attr('id');
      var $handle = getTabHandleForServiceItemId(id);

      // Show this build item if it should always show or if it has inputs the
      // user can interact with.
      var alwaysShowOnOrderForm = $pane.data('show');
      var willShowPane = alwaysShowOnOrderForm || doesPaneHaveInputs($pane);
      if (willShowPane) {
        if ($('.service-item-handle.active').length === 0) {
          // Only manually set active items if there isn't already one
          if (visibleItemCount === 0) {
            // Select the first visible tab handle and pane to be active, so the pane is displayed
            $handle.addClass('active');
            $pane.addClass('active');
          }
        }
        visibleItemCount += 1;
      } else {
        // Mark as hidden rather than removing because it needs to be POSTed
        $handle.addClass('hidden');
        $pane.addClass('hidden');
        invisibleItemCount += 1;
      }

      if (doesPaneHaveErrors($pane)) {
        formsetHasErrors = true;
        serviceItemRequiresAttention(id, true);
      } else {
        serviceItemRequiresAttention(id, false);
      }

    });

    if (visibleItemCount === 0) {
      // no SIs are visible, so hide the navigation column and the tab-content for SIs
      $('#service-item-nav').addClass('hidden');
      $('#service-items .tab-content').addClass('hidden');
    } else if (visibleItemCount === 1) {
      // only one SI is visible, so hide the navigation column and make the tab-content full-width
      $('#service-item-nav').addClass('hidden');
      $('#service-items .tab-content').removeClass('col-sm-9');
    }
    if (invisibleItemCount !== 0) {
        // only show this message if the user can manage the blueprint
        if ($('.blueprint-overview').find('.icon-cog').length) {
          console.log("One or more blueprint items were hidden because they do not require user input");
          console.log("You are seeing this message because you can manage this blueprint.");
        }
    }

    updateSubmitButton(formsetHasErrors);
  }

  function updateSubmitButton(hasErrors) {
    $('#submit-btn').prop('disabled', hasErrors ? 'disabled' : '');
  }


  /**
   * Return true if this service item pane contains any validation errors.
   */
  function doesPaneHaveErrors($pane) {
    var hasAnError = $pane.find('.form-group.has-error').length > 0;

    if (!hasAnError) {
      // Blank required fields including Environment dropdowns
      $pane.find('label.requiredField').each(function() {
        var $label = $(this);

        $label.closest('.form-group').each(function() {
          var $formGroup = $(this);
          if ($formGroup.data('dependent-field-visible') === false) {
            // If this field is marked hidden, it's a dependent field and should be ignored.
            // These are faded in and out so we cannot use :visible to determine their state here.
            logger.debug('    Ignoring required field. It is hidden by a controlling field.');
            return;
          }

          var $field = getFormFieldFromGroup($formGroup);
          if ($field.length && !$field.val()) {
            logger.debug('    Field is required but empty', $field);
            hasAnError = true;
          }
        });
      });
    }

    return hasAnError;
  }


  /*
   * Returns true if there are any fields that the user can impact. When a build
   * item's show_on_order_form is false, this is what determines whether the
   * build item is displayed.
   */
  function doesPaneHaveInputs($pane) {
    // :input includes all form input types, not just text boxes
    var inputs = $pane.find(':input')
      // Disabled fields like Hostname Preview or Environment (when there's
      // only one option) don't count.
      .not(':disabled')
      // Selectize dropdowns create an input and "hide" it by placing it off to
      // the left of the screen. Don't count these.
      .not('[style*="left: -10000px"]')
      // Don't count hidden inputs that the user can't interact with, such as
      // the group/service_item/os_build fields, fakePasswordTrick fields, and
      // invisible dependent fields. Provided/predefined parameters don't appear
      // in the form HTML at all, but they would also be excluded by this if we
      // changed them to be hidden fields in the future.
      .not('.hidden')
      .not('[type=hidden]')
      .not('[style*="display: none"]');
    // if there are inputs, then skip the check for selectize inputs
    if (inputs.length > 0) {
      return true;
    }
    // if any unlocked, enabled selectize-inputs, then this pane has inputs a user can use
    var selectizeInputs = $pane.find('.selectize-input')
        .not('.disabled').not('.locked');
    return selectizeInputs.length > 0;
  }


  /*
   * Given a .form-group container, return the .form-control that
   * will behave consistently (e.g. provides .val() method) and is not
   * a selectize-dropdown or selectize-control.
   */
  function getFormFieldFromGroup($formGroup) {
    return $formGroup.closest('.form-group')
      .find('.form-control')
      .not('.selectize-control,.selectize-dropdown');
  }


  /*
   * Given a form field that may have changed, update its service item form and if it's a PSSI
   * recalculate its rate. This triggers an AJAX request, so should be debounced e.g. to fire at
   * most once every 500ms or so.
   */
  function updateFormIfFieldChanged(e) {
    logger.debug('updateFormIfFieldChanged', '  e.type: ', e.type);
    if (!eventImpactsValidationOrRateCalculation(e)) {
      return;
    }
    /*jshint validthis: true */
    var $field = $(this);
    var $myGroup = $field.closest('.form-group');
    if ($myGroup.hasClass('environment-option')) {
      // Environment changes are handled elsewhere
      return;
    }

    if ($field.hasClass('selectize-control')) {
      // If a selectize is changed, depending on how, `this` may be the selectize-control. We want
      // the original select so we can do .val() etc.
      logger.debug('  $field has .selectize-control, getting actual select');
      $field = getFormFieldFromGroup($myGroup);
      logger.debug('  New $field: ', $field);
    }

    logger.debug('  $field: ', $field);
    logger.debug('    val:', $field.val());

    var wasInvalid = $myGroup.hasClass('has-error');
    var isValid = validateField($field);

    // Fields that had server-side validation errors are cleared as soon as client-side validation
    // passes so the form can be resubmitted.
    if (wasInvalid && isValid) {
      $field.removeClass('has-error');
      $myGroup.removeClass('has-error');
    }

    var $item = $field.closest('.service-item');
    removeHostnamePreviewErrors($item);

    if (isValid && $item.hasClass('provserver')) {
      // Fetch new rates and validation from server
      recalculateServiceItemDebounced($item.attr('id'));
    }

    updateFormState();
  }


  /*
   * Return true if this event's key code or target should trigger validation on a field or
   * trigger the recalculateServiceItem call.
   */
  function eventImpactsValidationOrRateCalculation(e) {
    if (e.type == 'change') {
      return true;
    }

    var key = e.key || e.keyCode;

    // Include numeric codes to support older browsers
    var ignoreKeyCodes = [
      // Tabbing to the next/prev field already triggers a change event so don't handle keyup here.
      'Tab', 9,
      'Shift', 16,
      'Enter', 13,
      'Alt', 18,
      'Meta', 91,
      'Escape', 27,
      'ArrowUp', 38,
      'ArrowDown', 40,
      'ArrowLeft', 37,
      'ArrowRight', 39,
    ];

    if (ignoreKeyCodes.indexOf(key) !== -1) {
      return false;
    }
    if (e.target.parentNode.className.indexOf('selectize') != -1) {
      logger.debug('  keyup on selectize; ignore.');
      return false;
    }

    logger.debug('  key:', key, 'code:', e.keyCode);
    return true;
  }


  var delay = (function() {
    var timer = 0;
    return function(callback, ms){
      clearTimeout(timer);
      timer = setTimeout(callback, ms);
    };
  })();


  /*
   * Since the user can't change the hostname preview directly, remove any hostname preview errors
   * when any other field changes.
   */
  function removeHostnamePreviewErrors($item) {
    $item.find('input[name$="-hostname"]:disabled').closest(".form-group").removeClass('has-error');
  }



  /*
   * Prepares POST data for a single-SI request (which service_item_formset view interprets as a
   * "get rate" request) and calls `callback` function with response.
   *
   * Returns immediately if the formset index and prefix cannot be determined.
   */
  function getPSSICost(itemID, groupID, envID, resourceName, serializedForm, callback) {
    var params = getFormPrefixAndIndex(itemID);
    if (params === undefined) {
      // SIs with errors don't need rate calc
      return;
    }

    _.assign(params, c2.forms.makeFormsetManagementData(1));
    var data = $.param(params) + '&';
    data += serializedForm;

    // Add env ID to the post data using the correct name for a formset form
    // following the examples from the lodash documentation: https://lodash.com/docs/4.17.15#template
    if (envID) {
        var compiled = _.template('&<%= prefix %><%= index %>-environment=<%= envID %>');
        data += compiled({'prefix': params.pssi_form_prefix, 'index': params.pssi_form_index, 'envID': envID});
    }
    if (resourceName) {
      var compiled = _.template('&<%= prefix %><%= index %>-resourceName=<%= resourceName %>');
      data += compiled({'prefix': params.pssi_form_prefix, 'index': params.pssi_form_index, 'resourceName': resourceName});
    }

    $.post(pssiCostURL + '?group_id=' + groupID, data, callback);
  }


  /*
   * Get the cost for this PSSI form and add it to the cost preview chart.
   */
  function getPSSIInitialCost(itemID, groupID, envID, resourceName, serializedForm) {
    serializedForm = resequencePSSIFieldNames(itemID, serializedForm);
    getPSSICost(itemID, groupID, envID, resourceName, serializedForm, function(response) {
      if (response.rateBreakdown === undefined) {
        logger.error('response has no rateBreakdown: ', response);
      } else {
        logger.info(response);
        addToCostComparison(
          itemID,
          envID,
          response.rateTotal,
          response.rateCurrencyUnit,
          response.rateTimeUnit
        );
      }
    });
  }


  /*
   * Similar to resequenceForms, which works in the DOM, this corrects the Django formset form
   * index on all parameters in the serializedForm string.
   *
   * E.g. "form-0-group=4&form-0-service_item=250&..."
   *  --> "form-1-group=4&form-1-service_item=250&..."
   */
  function resequencePSSIFieldNames(itemID, serializedForm) {
    var formsetIndex = $('.service-item').index($('#item-' + itemID));
    var re = /form-[0-9]+-/g;
    var newstr = 'form-' + formsetIndex + '-';
    return serializedForm.replace(re, newstr);
  }


  // Serialize all form fields in this SI row and send to server
  function recalculateServiceItem(itemDivID) {
    var $item = $('#' + itemDivID);
    var itemID = itemDivID.split('item-')[1];  // Either like '3' or '3-2'
    var serializedForm = getSerializedPSSIForm($item);
    var groupID = groupSelectize.getValue();
    var resourceName = resourceNameField.val();
    // If a PSSI environment dropdown is disabled (has only one choice), it won't be posted so we
    // need to add its value manually.
    var envID = getSelectedEnvID($item);

    // replace 'Select Environment' with a loading icon.
    var $rateElement = $item.find('.si-rate');
    // Add an element with a hard width to make sure the dots are centered.
    var $loaderParent = $('<div style="width: 600px">&nbsp;</div>');
    $rateElement.html('').append($loaderParent);
    c2.block.block($loaderParent, true);

    getPSSICost(itemID, groupID, envID, resourceName, serializedForm, function(response) {
      var activeEnvID = getActiveEnv(itemID, groupID);
      if (envID != activeEnvID) {
        var compiled = _.template(
          'Cost request finished for item <%= itemID %>, group <%= groupID %>, and env <%= envID %>. ' +
          'Ignoring because a different env (<%= activeEnvID %>) is now active.');
        var msg = compiled({
          itemID: itemID, groupID: groupID, envID: envID, activeEnvID: activeEnvID
        });
        logger.debug(msg);
        return;
      }

      var chart = $item.find('.si-rate');
      if(response.error !== undefined) {
        chart.html(response.error)
      }
      if (response.rateBreakdown !== undefined) {
        drawRateChart(
          response.rateBreakdown,
          response.rateTotal,
          response.rateCurrencyUnit,
          response.rateTimeUnit,
          chart);
        // If hostname field is disabled, we know it's a hostname preview
        // Update to the new value, and remove the error class if it exists
        var $preview = $item.find('input[name$="-hostname"]:disabled');
        $preview.val(response.hostnamePreview);
      } else {
        serviceItemRequiresAttention(itemID, true);
        logger.error('response.content: ', response.content);
        //$item.replaceWith(response.content);
      }
    });
  }
  // Debounced version waits at least 1s between each rate calculation
  // Used when any field in a single service item changes
  var recalculateServiceItemDebounced = $.debounce(1000, recalculateServiceItem);

  /*
   * Return object with this PSSI's formset index and form prefix, used by the view that returns
   * PSSI form cost and validation info.
   */
  function getFormPrefixAndIndex(itemID) {
    var prefix = getPSSIFormPrefix(itemID);
    var index = getPSSIFormIndex(itemID, prefix);
    if (index === undefined) {
      // PSSI has no field to derive the form index from
      return undefined;
    }
    return {
      'pssi_form_prefix': prefix,
      'pssi_form_index': index
    };
  }

  /*
   * Return the prefix string for this PSSI's form. Django formsets produce form fields
   * with names like 'form-1-mem_size', where the prefix would be 'form-'.
   * itemID is something like '3' or '3-2'
   */
  function getPSSIFormPrefix(itemID) {
    var prefix = "form-";
    var idParts = itemID.split('-');
    if ( idParts.length > 1 ) {
        // this is a sub-bp service item
        prefix = "bpsi" + idParts[0] + "-";
    }
    return prefix;
  }


  /*
   * Return the integer form index for this PSSI's form. Django formsets produce form fields
   * with names like 'form-1-mem_size', where the index would be 1.
   *
   * This is simply derived from the environment dropdown's name which all PSSIs have.
   */
  function getPSSIFormIndex(itemID, prefix) {
    var $env = $('#item-' + itemID).find('select[name$="-environment"]');
    if ($env.length === 0) {
      return;
    }
    return $env.attr('name').split(prefix)[1].split('-')[0];
  }

  /*
   * Return the environment ID of the selected environment (of the disabled dropdown in the case
   * where there is only one choice).
   */
  function getSelectedEnvID($item) {
    var $env = $item.find('select[name$="-environment"]');
    var envID = $env.val();
    if ($env.length && $env.prop('disabled')) {
      $env[0].selectize.enable();
      envID = $env.val();
      $env[0].selectize.disable();
    }
    return envID;
  }

  function rate_with_units(rate, currencyUnit, timeUnit) {
    // Use at least 2 decimal places, or more if we have them.
    // Useful for short time scales like $/hr that may have sub-cent precision.
    var decimalPlaces = (rate.toString().split('.')[1] || "").length;
    decimalPlaces = Math.max(decimalPlaces, 2);
    var rateString = currencyUnit + rate.toFixed(decimalPlaces);
    if (timeUnit !== undefined) {
      rateString += '/' + timeUnit;
    }
    return rateString;
  }

  /*
   * Flatten nested rate dict into list of highcharts series, or a single value into a series list.
   */
  function convertToSeries(key, value) {
    // Assign colors to the default rate types. Non-default rate types will
    // randomly be assigned colors.
    var colorForResourceType = {
      'Extra': '#c26e0e',
      'OS Build': '#ffd845',
      'Applications': '#ffb313',
      'Mem Size': '#8fbcf2',
      'Disk Size': '#4a9de4',
      'CPUs': '#335b83'
    };

    if (_.isObject(value)) {
      // value is a dict, possibly nested
      var dict = value;
      // call this function recursively on each key-value pair, and concat
      // them into a single list using reduce
      return _.reduce(
        dict,
        function(memo, childValue, childKey) {
          // using push.apply here as equivalent of Python's .extend
          // http://stackoverflow.com/a/1374131
          memo.push.apply(memo, convertToSeries(childKey, childValue));
          return memo;
        },
        []  // initial memo for reduce
      );
    } else {
      // value is a rate, convert it to a series
      var rate = value;
      if (rate) {
        return [{
          name: key,
          data: [rate],
          color: colorForResourceType[key] || null
        }];
      }
    }
  }

  /*
   * Formatter for Highcharts axis labels. Adjust label precision: as values get large cast to int.
   */
  function intsForLargeValues() {
    /*jshint validthis: true */
    return (this.value > 99.99) ? parseInt(this.value) : this.value;
  }


  function drawRateChart(rateBreakdown, rateTotal, currencyUnit, timeUnit, $chart) {
    var series = convertToSeries('', rateBreakdown);
    if (series.length === 0) {
      // Either rates have not been configured for this order, or the user has
      // not filled out the form yet. Currently it's not easy to know whether
      // to show the cost breakdown chart. So don't show it until there is
      // at least one series with data. Eventually, if it becomes possible to
      // know that rates apply for this env/user, we could show a div.well
      // saying "Fill out this form to see a cost breakdown chart".
      //console.log("No rate breakdown data; hiding cost breakdown chart.");
      $chart.html('Not available from cloud provider.')
      return;
    }

    // Highcharts stacked bar chart shows data from right to left, so reverse
    // the order of the series.
    series = series.reverse();

    $chart
      .css({
        // This width is carefully chosen to align the chart with the form fields above it
        width: '630px',
        // includes buffer space in case legend becomes 2 lines
        height: '160px',
        margin: '0 auto'
      })
      .show()
      .highcharts({
        title: {
          text: rate_with_units(rateTotal, currencyUnit, timeUnit) + gettext(' total')
        },
        subtitle: {text: ''},
        series: series,
        xAxis: {visible: false},
        yAxis: {
          // autoRotation: false,  // This is not always honored. Rotated labels break the chart.
          labels: {formatter: intsForLargeValues},
          // don't round chart up to nearest tick, just end the bar at 100% width
          endOnTick: false,
          min: 0,
          title: {text: ''}
        },
        legend: {
          backgroundColor: '#FFFFFF',
          reversed: true
        },
        chart: {
          type: 'bar'
        },
        tooltip: {
          // remove the empty category name from tooltip header; otherwise it breaks layout
          headerFormat: '',
          pointFormatter: function() {
            /*jshint validthis: true */
            return this.series.name + ': <b>' + rate_with_units(this.y, currencyUnit) + '</b>';
          }
        },
        plotOptions: {
          series: {
            animation: false,
            stacking: 'normal'
          }
        },
        exporting: {
          enabled: false
        },
        credits: {
          enabled: false
        }
      });
  }


  /**
   * For each NIC select field, set up a change handler to hide/show the static
   * IP field as required.
   */
  function setupNetworkFieldBehavior($item) {
    var $nic;

    $item.find('select[name*=sc_nic_]').each(function() {
      $nic = $(this);

      // On change (do not bind more than once)
      $nic.off('change').on('change', function () {
        setupFieldsForNetwork($(this));
      });

      // Initial setup
      setupFieldsForNetwork($nic);
    });
  }


  /**
   * Move labels of any checkbox input field to the left, aligned with other fields' labels
   */
  function moveCheckboxLabels($item) {
    var $formGroup, $box, $label, $colRight;

    $item.find('input[type=checkbox]').each(function() {
      $box = $(this);
      $formGroup = $box.closest('.form-group');
      $colRight = $box.closest('.col-lg-9');
      $box.closest('.checkbox').removeClass('checkbox');

      // Remove offset and align checkbox with the label which has 7px top padding
      $colRight.removeClass('col-lg-offset-3').css('padding-top', '7px');
      $label = $box.closest('label');
      $label.addClass('control-label col-lg-3');

      $colRight.before($colRight.children());
      $colRight.append($box);
    });
  }


  /**
   * When a network is selected, hide or show the static IP field and
   * initialize it as needed.  Uses a hidden input field whose value contains
   * metadata about each network option.
   */
  function setupFieldsForNetwork($nic) {
    logger.debug('setupFieldsForNetwork() $nic: ', $nic);
    var selectedNetwork = $nic.val();
    var index = parseInt($nic.attr('name').split('sc_nic_')[1]);
    var $serviceItem = $nic.closest('.service-item');
    // There may be multiple _metadata fields for a NIC but they'll all have the same payload
    // so just use the first found.
    var $netInfo = $serviceItem.find('input[name*=sc_nic_' + index + '_metadata]').first();
    var netInfo, netInfos;

    var $help = $nic.next('.help-block');
    if ($help.length === 0) {
      // On first load, help text will be created.
      $help = $('<div class="help-block"></div>');
      $nic.after($help);
    }

    var $errorMsg = $help.find('strong');

    // There may be a 2nd IP field with the same name if there is a network
    // with 'user defined' schema; here we want the IP field of the form-group
    // associated with 'static-only' networks.
    var $staticOnlyIPField = $serviceItem.find('input[name*=sc_nic_' + index + '_ip]').first();
    var $staticOnlyRow = $staticOnlyIPField.closest('.form-group');
    positionChildField($nic, $staticOnlyRow, $staticOnlyIPField);

    // Create the 'user-defined' DHCP/static radio buttons and its static IP
    // field from scratch. Get the base name for these elements by removing
    // "_ip" from the static-only IP field's name (e.g. form-0-sc_nic_0_ip).
    // We use name instead of ID because the ID can contain the wrong form
    // index. ID does not get resequenced by resequenceForms, so it sometimes
    // contains "form-0" instead of the correct index.
    // TODO: resequence IDs to have the correct index
    var baseName = $staticOnlyIPField.attr('name').split('_ip')[0];
    var $choiceRow = $serviceItem.find('#id_' + baseName + '_choiceRow');
    if ($choiceRow.length === 0) {
      $choiceRow = createChoiceRow(baseName, $staticOnlyRow);
    }
    var $choiceIPField = $choiceRow.find('input[name*=sc_nic_' + index + '_ip]');

    $staticOnlyRow.hide();
    $choiceRow.hide();
    // Disable static IP fields so not posted
    $staticOnlyIPField.prop('disabled', true);
    $choiceIPField.prop('disabled', true);

    try {
      var netInfoStr = $netInfo.val();
      if (netInfoStr) {
        netInfos = JSON.parse(netInfoStr);
      }
      netInfo = netInfos[selectedNetwork];
    } catch (ex) {
      console.error("Error reading metadata: ", ex.message);
    } finally {
      logger.debug('  netInfo:', netInfo);

      // Always executes. If an exception occurred above, netInfo will be
      // undefined and the IP field hidden.
      if (netInfo) {
        if ($nic.attr('readonly') == 'readonly') {
          // A baked-in NIC that does not require IP address from user will be set to
          // readonly so it can be hidden here.
          $nic.closest('.form-group').hide();
        }

        var msg = '';
        var ip = $staticOnlyIPField.val();
        switch (netInfo.ip_provider) {
          case 'ipam':
            msg = gettext("IP addresses will be assigned from an IPAM utility.");
            break;
          case 'pool':
            msg = gettext("IP addresses will be assigned from an IP pool.");
            break;
          case 'dhcp':
            break;
          case 'user_static':
            // Assign the static IP field's value to the selected network's `initial_ip`.
            // Only do this for an empty value or one that does not conform to the selected
            // network's IP range.
            if (ip === '' || ip.indexOf(netInfo.initial_ip) === -1) {
              $staticOnlyIPField.val(netInfo.initial_ip || '');
            }
            $staticOnlyIPField.prop('disabled', false);
            $staticOnlyRow.show();
            $staticOnlyIPField.focus();
            break;
          case 'user_static_or_dhcp':
            // Need to reference the static IP field created in the form, which is still around
            // but just hidden in this case, because it has access to the initial IP for an
            // existing order in the edit case
            if (ip === '' || ip.indexOf(netInfo.initial_ip) === -1) {
              $choiceIPField.val(netInfo.initial_ip || '');
            }

            // Enable/disable the static IP field depending on the radio input
            $staticOnlyIPField.prop('disabled', $choiceRow.find('input[type=radio]').val() === 'DHCP');

            $choiceRow.show();
            break;
        }

        if ($errorMsg.length !== 0) {
          // Replace the help text with the validation error message
          msg = $errorMsg.html();
        }

        $help.html(msg);
      }
    }
  }

  function createChoiceRow(baseName, $prevRow) {
    var baseID = 'id_' + baseName;
    var radioName = baseName + '_choice';
    var dhcpID = baseID + '_dhcp';
    var staticID = baseID + '_static';
    var choiceHTML = '' +
      '<div id="' + baseID + '_choiceRow" class="form-group">' +
      '  <div class="col-lg-3"></div>' +
      '  <div class="col-lg-9 controls">' +
      '    <div>' +
      '      <input type="radio" value="DHCP" name="' + radioName + '" id="' + dhcpID + '" checked="checked">' +
      '      <label for="' + dhcpID + '" class="control-label">' + gettext('Use DHCP') + '</label>' +
      '    </div>' +
      '      <input type="radio" value="static" name="' + radioName + '" id="' + staticID + '">' +
      '      <label for="' + staticID + '" class="control-label">' + gettext('Static IP Address') + '&nbsp;&nbsp;</label>' +
      '      <input class="form-control" name="' + baseName + '_ip" type="text" style="width: auto; display: inline-block;">' +
      '  </div>' +
      '</div>';
    var $choiceRow = $(choiceHTML);

    // Depending on radio selection, toggle disabled state of static IP field
    $choiceRow.find('input[type=radio]').on('change', function() {
      var $ip = $choiceRow.find('input[type="text"]');
      if ($(this).val() === 'DHCP') {
        $ip.prop('disabled', true);

        // Clear any former validation error state to allow form submission
        markFormGroupValid($choiceRow, true);
        removeValidationError($ip);
      } else {
        $ip.prop('disabled', false);
      }
    });
    $prevRow.after($choiceRow);
    return $choiceRow;
  }


  /**
   * Indent a field below another to visually group them, and align things nicely.
   * This is far simpler than using Django forms/widgets fu.
   */
  function positionChildField($parent, $childRow, $childField) {
    var $label = $childRow.find('label');
    if ($label.hasClass('child-field')) {
      // Already in position
      return;
    }

    // First ensure IP field's row is adjacent to its NIC dropdown's row
    $childRow.insertAfter($parent.closest('.form-group'));

    $label.removeClass('col-lg-3')
      // Class used for alignment but also to indicate that the field is in position
      .addClass('child-field')
      // Create an empty column to take the label's place
      .before('<div class="col-lg-3"></div>');

    $label.insertBefore($childField);

    // Override 100% width of the input field
    $childField.css('width', 'auto');
  }


  /**
    * Handle change event on environment dropdown. Load the runtime form for
    * specified group and selected environment.
    */
  function envChangeHandler($envSelect, groupID, envID) {
    if (envID && envID != 'None') {
      var itemID = $envSelect.closest('.service-item').attr('id').split('item-')[1];
      setActiveEnv(itemID, groupID, envID);
      loadSingleItemForm(groupID, itemID, envID);
    }
  }


  /*
   * Record the environment just selected and whose PSSI form is being loaded so that any pending
   * rate/validation requests for some other environment can be ignored.
   *
   * Only one env can be pending/loading at a time for a group/item context.
   */
  function setActiveEnv(itemID, groupID, envID) {
    if (activeEnv[itemID] === undefined) {
      activeEnv[itemID] = {};
    }
    activeEnv[itemID][groupID] = envID;
  }


  /*
   * Return an env ID or undefined.
   */
  function getActiveEnv(itemID, groupID) {
    if (activeEnv[itemID] === undefined) {
      activeEnv[itemID] = {};
    }
    return activeEnv[itemID][groupID];
  }


  // If the most recent filter values from the catalog view apply to
  // this blueprint, preselect them.
  function applyRequestParams(availableGroupIDs) {
    var querystring = location.search.slice(1);
    if (querystring.length !== 0) {
      var params = c2.querystring.parse(querystring);
      filterGroup = params.group || undefined;

      // `filterEnv` is defined above, so its value will be available to the
      // formset-load function where we can auto-select any env dropdowns that
      // match filterEnv.
      filterEnv = params.env || undefined;
    }

    if (filterGroup && _.contains(availableGroupIDs, filterGroup)) {
      groupSelectize.setValue(filterGroup);
      return true;
    }
  }


  function enableAllEnvSelects($container) {
    // By default, all env selects are enabled
    $container = $container || 'body';
    $('select[name$="-environment"]').each(function () {
      $(this)[0].selectize.enable();
    });
  }


  /*
   * Given a .form-control field (input, select, etc), do some client-side validation on it.
   * Return true if valid, false otherwise;
   */
  function validateField($field) {
    var $formGroup = $field.closest('.form-group');

    if ($field.is('input[name*="sc_nic"]') && $field.is('[name$="_ip"]')) {
      return validateIP($field, $formGroup);
    }

    return validateRequiredField($field, $formGroup);
  }


  /*
   * Validate value of a static IP input field and mark its form-group valid/invalid.
   * Return true if valid, false if not.
   */
  function validateIP($ip, $formGroup) {
    // Basic regex checking for four . separated integer octets
    var isValid = $ip.val().match(/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/) !== null;
    var $error;

    if (isValid) {
      removeValidationError($ip);
    } else {
      createOrUpdateValidationError($ip, gettext("Enter a valid IPv4 address."));
    }
    markFormGroupValid($formGroup, isValid);
    return isValid;
  }


  /*
   * If $field is required but blank, mark its form-group invalid and return false.
   * Makes an exception for required fields that are hidden because they are dependent fields.
   * Otherwise, return true.
   */
  function validateRequiredField($field, $formGroup) {
    logger.debug('validateRequiredField', $field);

    var isVisible = true;
    if ($formGroup.data('dependent-field-visible') === false) {
      logger.debug('    Ignoring required field. It is hidden by a controlling field.');
      isVisible = false;
    }

    var isRequired = $formGroup.find('label').hasClass('requiredField');
    var isValid = !isVisible || (isVisible && (!isRequired || (isRequired && $field.val() !== '')));
    if (isValid) {
      removeValidationError($field);
    } else {
      createOrUpdateValidationError($field, gettext("This field is required."));
    }
    markFormGroupValid($formGroup, isValid);
    return isValid;
  }


  /*
   * Given a static IP input field, mark it valid or invalid based on boolean `isValid` param.
   * Also mark its label and the form-group of the corresponding NIC (which is a separate
   * form-group from its own).
   */
  function markFormGroupValid($formGroup, isValid) {
    if (isValid) {
      $formGroup.removeClass('has-error');
    } else {
      $formGroup.addClass('has-error');
    }
  }


  /*
   * Show a validation error 'msg' next to $field.
   * Appends a span.validation-error to the field's help-block, creating help-block if necessary.
   */
  function createOrUpdateValidationError($field, msg) {
    var $help = $field.next('.help-block');

    if ($help.length === 0) {
      $field.after('<span class="help-block"></span>');
    }

    var $msg = $help.find('.validation-error');
    if ($msg.length === 0) {
      $help.append('<span class="validation-error">' + msg + '</span>');
    }
  }


  /*
   * Remove any validation error messages for this field.
   * This includes the span.validation-error created client-side, as well as certain Django form
   * errors that may have come from server side, so they don't interfere with client-side
   * validation.
   */
  function removeValidationError($field) {
    var $help = $field.next('.help-block');
    $help.find('.validation-error').remove();

    // Django error messages have no special class, so try matching by string value
    var help = $help.html();
    if (help == '<strong>' + gettext("This field is required.") + '</strong>') {
      $help.html('');
    } else if (help == '<strong>' + gettext("Enter a valid IPv4 address.") + '</strong>') {
      $help.html('');
    }
  }


  function handleOrderSubmit(e) {
    e.preventDefault();

    // disable the button to prevent duplicate order creation
    $("#submit-btn").attr("disabled", true);
    c2.block.block('#blueprint-order-form');

    /*jshint validthis: true */
    var $form = $(this);
    var groupID = groupSelectize.getValue();
    var $items = $form.find('.service-item');

    // Env dropdowns may be disabled when there is only one choice; to
    // serialize them they need to be enabled.
    enableAllEnvSelects();

    // Serialize the main order form wrapping all SIs as well as the forms
    // for each SI parameters section.
    var data = $.param(c2.forms.makeFormsetManagementData($items.length)) + '&';
    data += $('form').serialize();

   var formData = new FormData($('form#blueprint-order-form')[0]);
   var mData = c2.forms.makeFormsetManagementData($items.length)
   $.each(mData,function(key,value){
     formData.append(key,value);
   })
    // POST files
    $.ajax({
        url: formSetBaseURL + '?group_id='+ groupID,
        type: 'POST',
        data: formData,
        async: false,
        cache: false,
        contentType: false,
        enctype: 'multipart/form-data',
        processData: false,
        success:function(response){
          if (response.redirectURL) {
            window.location.href = response.redirectURL;
            // return now to leave the page in a blocked state
            return;
          } else if (response.error) {
            $('#service-items').html(response.error).addClass('error');
          } else {
            $('#service-items').html(response.content);
          }

          applyFormsetBehaviors();
          applyPostLoadBehaviors();
          showOrderFormValidationErrors();
          c2.block.unblock('#blueprint-order-form');

        }
    });
  }


  function disableOrderForm(msg) {
    $('#blueprint-order-form [type=submit]').prop('disabled', 'disabled');
    $('#action-msg').html(
      '<div class="alert alert-warning">' +
      (msg || 'There is a problem with this blueprint.') +
      '  Please ask an administrator for help.</div>'
    );
  }


  /**
  * Ensure fields for each service item row are named with that form's formset prefix.
  * The first item's fields will start with 'form-0-', the next 'form-1-', etc.
  *
  * Or in the case of a blueprint service item (aka nested blueprint), all of
  * its form fields should have prefixes like 'bpsiNN-0-' and 'bpsiNN-1-',
  * where NN is an integer matching that blueprint item's ID.
  */
  function resequenceForms() {
    var $item, $field, indexAndName, name, parts, bpsiID;

    // First loop over all SIs except BPSIs and assign new names to each form field that have
    // the correct index, starting at 0
    $('.service-item').not('.nested').each(function (index, item) {
      $(item).find('[name^="form-"]').each(function () {
        $field = $(this);
        // Remove 'form-' from the name, leaving something like '0-mem_size'
        indexAndName = $field.attr('name').slice(5);
        // name is the Django form field's name, like 'mem_size'
        name = indexAndName.split('-')[1];
        $field.attr('name', 'form-' + index + '-' + name);
      });
    });

    // Do same thing if there are any BPSIs, but each has index starting with 0.
    // Fields within a sub-blueprint have names like 'bpsi384-0-mem_size'.
    $('.service-item.blueprint').each(function(i, bpsi) {
      $(bpsi).find('.service-item').each(function (index, item) {
        $(item).find('[name^="bpsi"]').each(function () {
          $field = $(this);
          // Remove 'bpsi' from the name, leaving something like '384-0-mem_size'
          indexAndName = $field.attr('name').slice(4);
          // parts should be an array with 3 items
          parts = indexAndName.split('-');
          // name is the Django form field's name, like 'mem_size'
          bpsiID = parts[0];
          name = parts[2];
          // Construct the new name with the correct formset index
          $field.attr('name', 'bpsi' + bpsiID +'-'+ index + '-' + name);
        });
      });
    });
  }


  /**
   * Set up the RuntimeInputWidget behavior:
   * Disable/enable the original widget based on the checkbox.
   */
  function setupRuntimeField(name) {
    var $runtime = $('#runtime-' + name);
    var $widget = $('#runtime-widget-' + name);
    var $orig = $widget.find('.runtime-orig');
    var $user = $widget.find('.runtime-user');
    var $selectized;

    function morphRuntimeWidget() {
      if ($('#runtime-toggle-' + name).prop('checked')) {
        // Enable the input
        $orig.find('input, textarea, select, checkbox').prop('disabled', '');
        $selectized = $orig.find('.selectized');
        if ($selectized.length) {
          $selectized[0].selectize.enable();
        }

        $orig.find('button').show(); // Power Schedule gives an edit button to open a modal
        $runtime.val('_default_');
      } else {
        // Disable the input
        $orig.find('input, textarea, select, checkbox').prop('disabled', 'disabled');
        $selectized = $orig.find('.selectized');
        if ($selectized.length) {
          $selectized[0].selectize.disable();
        }
        $orig.find('button').hide(); // Power Schedule gives an edit button to open a modal
        $runtime.val('_runtime_');
      }
    }

    var $toggle = $('#runtime-toggle-' + name);
    $toggle.on('change', morphRuntimeWidget);

    $toggle.bootstrapToggle();
    morphRuntimeWidget();
  }


  /*
   * Ensure Cost preview is aligned with other form fields based on whether this order form has
   * tabs or not.
   *
   * Adding a class via JS enables some CSS rules to reach elements outside/above our control here.
   */
  function tuneLayoutForFormset() {
    var sideNav = $('#service-item-nav');
    if (sideNav.length && !sideNav.hasClass('hidden')) {
      $('#content').addClass('compact-layout');
    } else {
      // No tabs; thus there is only a single SI and layout can be narrower
      $('#content').addClass('compact-layout more-compact');

      // Special case: remove custom server SI panel
      var $panel = $('.service-item .item-details');
      if ($panel.find('.panel-body .row').hasClass('no-details')) {
          $panel.hide();
      }

      // SIs have no tab handles, so remove them from the upper form too
      $('.alignment-shim.col-sm-3').hide();
      $('.alignment-shim.col-sm-9').removeClass('col-sm-9');
    }

    // Now show the form if it's still hidden (only hidden on first page load).
    $('#blueprint-order-form').removeClass('hidden');
  }


  c2[__module__] = {
    init: init,
    setupRuntimeField: setupRuntimeField
  };

})('orderForm', window.c2);

(function (c2) {
  'use strict';

  // For forms that have the server-related boolean fields (checkboxes or
  // toggles) ensure that if "available to all servers" is enabled then "show
  // on servers" is also enabled.
  function enforceParamServerOptions() {
    var $availOnAll = $('#id_available_all_servers');
    var $showOnServers = $('#id_show_on_servers');

    var morpher;
    if ($availOnAll.data('toggle') == 'toggle') {
      morpher = toggleProps;
    } else {
      morpher = setFieldProps;
    }

    $availOnAll.on('change', morpher);
    // To make it do initial form setup
    morpher();

    function setFieldProps(e) {
      if ($availOnAll.prop('checked')) {
        // This field is disabled so won't be posted.  However, the CF model's
        // save method will also enforce this condition.
        $showOnServers.prop('checked', true).prop('disabled', true);
      } else {
        $showOnServers.prop('disabled', false);
      }
    }

    function toggleProps(e) {
      if ($availOnAll.prop('checked')) {
        $showOnServers.bootstrapToggle('on').bootstrapToggle('disable');
      } else {
        $showOnServers.bootstrapToggle('enable');
      }
    }
  }


  c2.params = {
    enforceParamServerOptions: enforceParamServerOptions
  };

})(window.c2);

(function (c2) {
  'use strict';

  var noAnimationStyle = "<style>.progress-bar { -webkit-transition: none; transition: none; }</style>";
  var animationsEnabled = true;

  // Immediately disable progress bar animations.
  //
  // Used in job and order detail pages to disable the animation after the
  // first page load, preventing re-animation when new progress bars are
  // AJAX'd in to replace old ones
  function disableAnimations() {
    if (animationsEnabled) { // avoid a mem leak by only appending once
      $('head').append(noAnimationStyle);
      animationsEnabled = false;
    }
  }

  c2.progressBars = {
    disableAnimations: disableAnimations
  };
})(window.c2);

/* Parse and create querystrings.
 *
 * The parse and stringify interfaces are borrowed from NodeJS's own
 * [querystring.stringify](http://nodejs.org/api/querystring.html), but the
 * implementation does not urlencode/decode, support custom `sep` or `eq`
 * characters, or support arrays as values.
 */
(function (c2) {
  'use strict';

  // Serialize an object into a querystring.
  //
  // Example:
  //    > stringify({color: "blue", cost_lt: "9"});
  //    "color=blue&cost_lt=9"
  function stringify(obj) {
    return Object.keys(obj).map(function (key) {
      return key + '=' + obj[key];
    }).join('&');
  }

  // Deserialize a querystring into an object.
  //
  // Example:
  //    > parse('color=blue&cost_lt=9');
  //    {color: "blue", cost_lt: "9"}
  function parse(qs) {
    var result = {};

    // if the qs came from window.location.search, it will contain a leading
    // '?' that we want to remove.
    if (qs.charAt(0) === '?') {
      qs = qs.slice(1);
    }

    if (qs.length === 0) {
      return result;
    }

    qs.split('&').forEach(function (keyValueStr) {
      var key, value;
      var idx = keyValueStr.indexOf('=');

      if (idx === -1) {
        key = keyValueStr;
        value = '';
      } else {
        key = keyValueStr.substr(0, idx);
        value = keyValueStr.substr(idx + 1);
      }

      result[key] = value;
    });

    return result;
  }


  c2.querystring = {
    stringify: stringify,
    parse: parse
  };
})(window.c2);

(function(__module__) {

  var logger = c2.logging.getLogger(__module__);


  /*
    * Enable or disable the Next button and the numeric button for the next step,
    * depending on if any rows are selected.
    */
  function requireUserToChooseOne(checkboxTableID, nextStep) {
    var $table = $(checkboxTableID);
        $clearSelectionButton = $table.closest('.dataTables_wrapper').find('a.clear-selection');
        $checkboxes = $table.find('input[type=checkbox]');

    if ($checkboxes.length === 0) {
      // Don't enforce selecting a row if there are none
      return;
    }

    function updateNextLinks() {
      var $checkboxes = $table.find('input[type=checkbox]'),
          $continueButton = $('a.wizard-pagination-next'),
          // the button itself cannot be a tooltip target when it is disabled
          // (because disabled elements don't create events), so we apply it to
          // the list items
          $tooltipTarget = $continueButton.parent('li'),
          anyChecked = !!$checkboxes.filter(':checked').length;

      if (anyChecked) {
          $tooltipTarget
              .removeClass('no-tooltip-affordance')
              .attr('data-toggle', null)
              .attr('data-title', null);
          $continueButton.removeClass('disabled');
      } else {
          $tooltipTarget
              .addClass('no-tooltip-affordance')
              .attr('data-toggle', 'tooltip')
              .attr('data-title', 'Select at least one item to continue.');
          $continueButton.addClass('disabled');
      }

      // en/disable the following numbered pagination link as needed
      window.wizards.enableStep(nextStep, anyChecked);
    }

    /*
    Update the state of the next links by watching both ways a
    selection changes: checkbox on each row, or clearing the selection

    Watch for 'click' on the tbody because jquery.clickable does not
    trigger a 'change' event on the checkboxes themselves.
    */
    $table.find('tbody').on('click', updateNextLinks);
    $clearSelectionButton.on('click', updateNextLinks);
    // Initialize
    updateNextLinks();
  }


  c2[__module__] = {
    requireUserToChooseOne: requireUserToChooseOne
  };
})('quickSetup');


(function (c2) {
  'use strict';

  function isScrolledToBottom(elem) {
    // 20 (the height of the last line) + 70 (estimated the height of the last lines
    // that might pop up within a single repaint cycle) = 90
    return (elem.scrollHeight - (elem.scrollTop + elem.clientHeight)) < 90;
  }

  function scrollToBottom(elem) {
    elem.scrollTop = elem.scrollHeight;
  }


  c2.scrolling = {
    isScrolledToBottom: isScrolledToBottom,
    scrollToBottom: scrollToBottom
  };

})(window.c2);

// Global search

(function (__module__) {
  'use strict';

  // Assigned at the time c2.search.init is called
  var $searchMenu;
  var logger = c2.logging.getLogger(__module__);


  function init() {
    $searchMenu = $('[data-topnav=search]');
    var $searchField = $("#search-input");
    $searchField.clearable();
    
    // Clear existing search results when the "X" is clicked
    $('#navbar-search').on('click', '.icon-delete', function(e) {
      $('#search-results').empty();
    });
    
    c2.commonEventHandlers.registerGlobalKeyHandlers('search', {
      '/': function(e) {
        if (c2.navbar.isSubMenuOpen($searchMenu)) {
          c2.navbar.closeSubMenu($searchMenu);
        } else {
          openSearchSubMenu();
        }
        e.preventDefault();
      }
    });

    $searchMenu.on('keydown.searchBindings', function(e) {
      if (e.key == 'Escape' && c2.navbar.isSubMenuOpen($searchMenu)) {
        c2.navbar.closeSubMenu($searchMenu);
        e.preventDefault();
      }
    });

    // Set up search field key bindings
    $searchField.on('keydown.searchBindings', function (e) {
      var key = e.key || e.keyCode;
      switch (key) {
        case 'Escape': case 27: // close search submenu on ESC while typing in input
        case 'Esc': // MS Edge
          c2.navbar.closeSubMenu($searchMenu);
          $('#search-results').empty();
          e.preventDefault();
          break;
        case 'ArrowDown': case 40: // Move focus to first result
        case 'Down': // MS Edge
        case 'Tab': case 9:
          focusResults();
          e.preventDefault();
          break;
      }
    });

    // Hitting enter submits the form
    $('form#navbar-search')
      .off('submit')
      .on('submit', function (e) {
        e.preventDefault();
        queryAndShowResults({q: $('#search-input').val()});
      });
  }
  
  
  function focusResults() {
    $('#search-results').find('.post_result').first().children('a').focus();
  }


  function openSearchSubMenu() {
    c2.navbar.openSubMenu($searchMenu);

    // Scroll menu into view
    window.scroll(0, 0);

    // Focus input field after a slight delay (req'd for it to work)
    setTimeout(function(){
      $('#search-input').focus().select();
    }, 200);
  }


  function setupSearchResultBehaviors() {
    var $resultsContainer = $('#search-results');
    var key, $from, $to;

    if ($resultsContainer.data('behaviors-initialized')) {
      return;
    }
    $resultsContainer.data('behaviors-initialized', true);

    /**
     * Given a jQuery object of the active search result (.post_result), open its href. If the
     * event object `e` indicates that Cmd or Ctrl is being held down, or it's a middle mouse
     * click, opens in a new tab.
     */
    function goToResult($result, e) {
      var $a = $result.find('a');
      var url = $a.attr('href');
      // Cmd, Ctrl, or middle-click opens in a new tab
      var newTab = (e.metaKey || e.ctrlKey || e.which == 2) ? true:false;

      if (url) {
        if (newTab) {
          window.open(url, '_blank');
        } else {
          c2.block.block();
          window.location = url;
        }
      }
    }

    // Activate the hovered result
    $resultsContainer.on('hover.searchBindings', 'ol > li', function(e) {
      var $li = $(this);
      $li.find('.post_result > a').focus();
    });

    // Mouse click to go to result
    $searchMenu.on('click.searchBindings', '.post_result', function(e) {
      goToResult($(this), e);
    });

    $searchMenu.on('click.searchBindings', '.search-result-pager a', function(e) {
      e.preventDefault();
      queryAndShowResults({
        q: $(this).data('query'),
        page: $(this).data('page')
      });
    });
  }


  /**
   * Send a GET request to `url` and populate the search results div.
   */
  function queryAndShowResults(data) {
    var $results = $('#search-results');

    // Accomodate the blocking 'spinner' icon
    $results.css('min-height', '150px');
    c2.block.block($results);

    var newjqXHR = $.get('/search/?' + c2.querystring.stringify(data), function(response){
      $results.html(response);
      focusResults();
      c2.navbar.setupKeyNavigationOfMenu($searchMenu, $searchMenu.find('ul.dropdown-menu'));
      c2.block.unblock($results);
    });
  }


  c2[__module__] = {
    init: init,
    openSearchSubMenu: openSearchSubMenu,
    setupSearchResultBehaviors: setupSearchResultBehaviors
  };
})('search');

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);

  /**
   * This is essentially just a thin wrapper around selectize.
   * Apply Selectize to the selector, using global default settings.
   * The optional `userSettings` object overrides defaults.
   */
  c2.selectize = function (selector, userSettings) {
    var defaults = {
      // Insert the dropdown into the DOM inside body instead of as a sibling of
      // the original control, to avoid dropdown being covered by bottom of
      // tables, the page footer, etc.
      dropdownParent: 'body',
      plugins: {
        // Inserts an option for the empty choice, if there is one
        selectable_placeholder: {}
      },
      selectOnTab: true,
      // sort alphabetically by label field (named 'text' by default)
      sortField: 'text'
    };
    var settings = $.extend({}, defaults, userSettings || {});
    var $target = $(selector);
    logger.info('selectize settings:', settings);

    if ($target.length === 0) {
      console.log('c2.selectize did not find a target at $("' + selector + '")');
      return;
    }

    if ($target.closest('.modal-dialog').length) {
      // Dropdowns in dialogs must be inserted alongside the original; otherwise
      // they appear below the modal.
      settings.dropdownParent = null;
    }

    if (settings.sortNumerically) {
      // It would make sense to set sortField to 'value', but that
      // doesn't work. Setting sortField to null allows
      // ints and decimals to maintain the order they were sorted in from the backend.
      settings.sortField = null;
    }

    if (settings.suggest_options_field_name) {
      var $wrap = $target.closest('.controls');
      if ($wrap.length === 0) {
        // Not on a form that wraps fields the standard way (like the order form). This
        // is the case on 'Add Parameter to Server' dialog. In this case, just use the
        // parent of the selectized element.
        $wrap = $target.parent();
      }

      // This widget will auto-suggest options as user types, using Selectize's `load` option.
      // Data source is a CB view that runs a generate parameters action associated with this
      // field name. The action must contain a special function `suggest_options` that takes
      // the field and current query string.
      settings.load = function(query, callback) {
        if (!query.length) {
          return callback();
        }
        var $selectized = $wrap.find('.selectized');
        var url = '/suggest_options_for_selectize/'+ settings.suggest_options_field_name +'/';

        logger.debug('Loading options for selectize with query:', query);

        $.get(url, {query: query}, function(result) {
          if (result.options) {
            // Fix issue on first open where the dropdown is too narrow, like 90px.
            // Set the width to match the selectize form field.
            var $dropdown = $selectized[0].selectize.$dropdown;
            logger.debug('  $dropdown orig width:', $dropdown.css('width'));
            $dropdown.css('min-width', '600px');
            callback(result.options);
          } else {
            console.error(result);
            callback([{value: '', text: 'An error occurred while looking up options'}]);
          }
        });
      };

      // Prevent excessive requests while user is typing, but not delay so much that it's disruptive
      settings.loadThrottle = 400;
    }

    $target.selectize(settings);
    return $target[0].selectize;
  };


  /**
   * Client side equivalent to our SelectizeMultiple Django form widget.
   */
  c2.selectizeMultiple = function (selector, userSettings) {
    var defaults = {
      placeholder: 'Choose one or more...',
      plugins: ['remove_button', 'batch_toolbar']
    };

    return c2.selectize(selector, $.extend(defaults, userSettings || {}));
  };

})('selectize');

/*
    Selectize plugin to fix a major UX problem with Selectize: allow selection
    of an empty option.

    By default, Selectize converts this:
       <option value="">----</option>
    to this:
       <input ... placeholder="----">

    ...and removes the original empty option from the dropdown. This has the
    effect of making it impossible to click on the empty option; users must use the
    delete key.

    Background:
    https://github.com/brianreavis/selectize.js/issues/163

    Usage:
      $('#element').selectize({
        plugins: {'selectable_placeholder': {}}
      });
 */
Selectize.define('selectable_placeholder', function (options) {
  var self = this,
      $origInput = self.$input,
      // this plugin only works for select elements
      $emptyOption = $origInput.children('option[value=""]');

  if ($emptyOption.length === 0) {
    // do not apply this plugin; there is no empty option in the original select
    return;
  }

  options = $.extend({
    placeholder: self.settings.placeholder,
    html: function (data) {
      return (
        '<div class="selectize-dropdown-content placeholder-container">' +
        '<div data-selectable class="option">' + escape_html(data.placeholder) + '</div>' +
        '</div>');
    }
  }, options);

  // override the setup method to add an extra "click" handler
  self.setup = (function () {
    var original = self.setup;
    return function () {
      original.apply(this, arguments);
      self.$placeholder_container = $(options.html(options));
      self.$dropdown.prepend(self.$placeholder_container);
      self.$dropdown.on('click', '.placeholder-container', function () {
        self.setValue('');
        self.close();
        self.blur();
      });
    };
  })();

});


/**
 * Plugin: "remove_button" (selectize.js)
 * Copyright (c) 2013 Brian Reavis & contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
 * file except in compliance with the License. You may obtain a copy of the License at:
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under
 * the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
 * ANY KIND, either express or implied. See the License for the specific language
 * governing permissions and limitations under the License.
 *
 * @author Brian Reavis <brian@thirdroute.com>
 */

/**
 * (from selectize utils.js)
 * Escapes a string for use within HTML.
 *
 * @param {string} str
 * @returns {string}
 */
var escape_html = function(str) {
  return (str + '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
};

Selectize.define('remove_button', function(userOptions) {
  if (this.settings.mode === 'single') return;

  var options = $.extend({
    label     : '<i class="fas fa-times"></i>',
    title     : gettext('Remove'),
    className : 'remove',
    append    : true
  }, userOptions);

  var self = this;
  var html = '<a href="javascript:void(0)" class="' + options.className + '" tabindex="-1" title="' + escape_html(options.title) + '">' + options.label + '</a>';

  /**
   * Appends an element as a child (with raw HTML).
   *
   * @param {string} html_container
   * @param {string} html_element
   * @return {string}
   */
  var append = function(html_container, html_element) {
    var pos = html_container.search(/(<\/[^>]+>\s*)$/);
    return html_container.substring(0, pos) + html_element + html_container.substring(pos);
  };

  this.setup = (function() {
    var original = self.setup;
    return function() {
      // override the item rendering method to add the button to each
      if (options.append) {
        var render_item = self.settings.render.item;
        self.settings.render.item = function(data) {
          return append(render_item.apply(this, arguments), html);
        };
      }

      original.apply(this, arguments);

      // add event listener
      this.$control.on('click', '.' + options.className, function(e) {
        e.preventDefault();
        if (self.isLocked) return;

        var $item = $(e.currentTarget).parent();
        self.setActiveItem($item);
        if (self.deleteSelection()) {
          self.setCaret(self.items.length);
        }
      });

    };
  })();

});


/**
 * Show buttons to select and clear all options.  Only works for
 * multiple-select mode.
 */
Selectize.define('batch_toolbar', function(userOptions) {
  if (this.settings.mode === 'single') return;

  var self = this;
  var options = $.extend({
    // speeds things up?
    skipChangeEvent: true,
    labelAll   : '<i class="fas fa-asterisk"></i>',
    labelClear : '<i class="fas fa-times"></i>',
    titleAll   : gettext('Select all items'),
    titleClear : gettext('Clear selection'),
  }, userOptions);


  var selectAllOptions = function(e) {
    e.preventDefault();
    if (self.isLocked) return;

    _.forEach(self.options, function (i) {
      self.addItem(i.value, options.skipChangeEvent);
    });
  };


  var clearAllOptions = function(e) {
    e.preventDefault();
    if (self.isLocked) return;

    self.clear(options.skipChangeEvent);
  };


  var $btnGroup = $('<div class="selectize-toolbar btn-group"></div>');
  var insertToolbar = function() {
    var $allBtn = $(
      '<button class="select-all-options btn btn-default btn-xs" data-toggle="tooltip" title="' +
      escape_html(options.titleAll) + '">' + options.labelAll + '</button>')
      .on('click', selectAllOptions);

    var $clearBtn = $(
      '<button class="select-no-options btn btn-default btn-xs" data-toggle="tooltip" title="' +
      escape_html(options.titleClear) + '">' + options.labelClear + '</button>')
      .on('click', clearAllOptions);

    $btnGroup.append($allBtn).append($clearBtn);
    $btnGroup.insertAfter(self.$control);
  };


  this.setup = (function() {
    var original = self.setup;
    return function() {
      original.apply(this, arguments);
      insertToolbar();
    };
  })();
});

/*
 * Server detail view functions
 */

(function (__module__, c2, $) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);
  var updateTimer, mediumTimeout, longTimeout;

  /*
   * There is a schedule for live updates, to avoid excessive load on CB
   * servers:
   *     For the first 5 minutes, every 10 seconds.
   *     After 5 minutes, once a minute.
   *     After an hour, every 5 minutes.
   */
  var prodDurations = {
    shortInterval: moment.duration(10, 'seconds'),
    mediumStart: moment.duration(5, 'minute'),
    mediumInterval: moment.duration(1, 'minute'),
    longStart: moment.duration(1, 'hour'),
    longInterval: moment.duration(5, 'minute')
  };
  var testDurations = {
    shortInterval: moment.duration(5, 'seconds'),
    mediumStart: moment.duration(20, 'seconds'),
    mediumInterval: moment.duration(10, 'seconds'),
    longStart: moment.duration(60, 'seconds'),
    longInterval: moment.duration(20, 'seconds')
  };
  var durations;

  /*
   * Set up live updates for this server details view.
   *
   * The first time the page is loaded, all content is rendered by the details
   * view, except for the sidebar. From then on, certain sections of content are given a data-include
   * attribute to enable reloading via c2.include.
   *
   */
  function liveUpdates(sidebarURL, orgPanelURL) {
    // Change this to testDurations for faster reload intervals
    durations = prodDurations;
    logger.debug(durations);

    $(document).on('cb.inlineEdits.loaded', stopUpdates);
    $(document).on('cb.inlineEdits.closed', startUpdates);

    makeElementsReloadable(sidebarURL, orgPanelURL);
    // Load the sidebar on initial page load, but separate from the page load itself
    // so it doesn't block it if slow
    reloadSections();
    startUpdates();
    setupPageVisibilityHandler();
    setupRefreshButtonHander();
  }


  /*
   * Modify elements on the server details page so they can be reloaded using c2.include.
   * Also set up a callback to turn off live updates if there is ever an ajax error during reloads.
   */
  function makeElementsReloadable(sidebarURL, orgPanelURL) {
    var $sidebar = $('#server-details-sidebar');
    $sidebar.attr('data-include', sidebarURL);
    // Do not show an error msg; just preserve prior content on failure.
    $sidebar.attr('data-include-error', false);
    $sidebar.attr('data-include-callback', stopUpdatesOnFailure);

    var $orgPanel = $('#server-details-panel-organization');
    $orgPanel.attr('data-include', orgPanelURL);
    $orgPanel.attr('data-include-error', false);
    $orgPanel.attr('data-include-callback', stopUpdatesOnFailure);
  }


  /*
   * Stop/start live updates when page visibility changes
   */
  function setupPageVisibilityHandler() {
    var isSupported = c2.visibility.onChange(function(isHidden) {
      if (isHidden) {
        logger.debug('page hidden');
        stopUpdates();
      } else {
        logger.debug('page visible');
        startUpdates();
      }
    });

    if (! isSupported) {
      // If (some obscure) browser does not support this API, the interval schedule simply runs
      // without being stopped/started.
    }
  }


  /*
    * Clicking the Refresh button stops previously-scheduled live updates, reloads all sections,
    * and starts a new live update cycle.
    */
  function setupRefreshButtonHander() {
    $(document).on('click', '#refresh-server-details', function(e) {
      stopUpdates();
      reloadSections();
      startUpdates();
    });
  }


  /*
   * Callback for c2.include, called after every reload. If `succeeded` is
   * false, turns off live updates.
   */
  function stopUpdatesOnFailure(el, succeeded) {
    $('#server-details-live-updates-info').removeClass('hidden');

    if (succeeded) {
      $('#offline-alert').addClass('hidden');
    } else {
      logger.error('  data-include failed to load for el: ', el);
      stopUpdates();
      $('#offline-alert').removeClass('hidden');
    }
  }


  /*
   * Reload data-included sections periodically, as long as server status warrants.
   * Sets up the intervals based on `durations`, defined in liveUpdates.
   */
  function startUpdates() {
    logger.debug('startUpdates');
    if (updateTimer) {
      // interval timers have already been set
      logger.debug('  timers already set, skipping.');
      return;
    }

    logger.debug(
      'Setting up short term update interval: ' +
      durations.shortInterval.asSeconds() + 's'
    );
    updateTimer = setInterval(reloadSections, durations.shortInterval.asMilliseconds());

    // Medium term interval
    mediumTimeout = setTimeout(function() {
      logger.debug(
        durations.mediumStart.asMinutes() +
        'm have passed; starting medium term update interval every ' +
        durations.mediumInterval.asSeconds() + 's'
      );
      stopUpdates();
      updateTimer = setInterval(reloadSections, durations.mediumInterval.asMilliseconds());
    }, durations.mediumStart.asMilliseconds());

    // Long term interval
    longTimeout = setTimeout(function() {
      logger.debug(
        durations.longStart.asMinutes() +
        'm have passed; starting long term update interval every ' +
        durations.longInterval.asSeconds() + 's'
      );
      stopUpdates();
      updateTimer = setInterval(reloadSections, durations.longInterval.asMilliseconds());
    }, durations.longStart.asMilliseconds());

  }


  /*
   * Do the actual work of reloading content.
   *
   * Currently, this triggers several HTTP requests at once.
   */
  function reloadSections() {
    logger.debug('reloadSections');
    var loadState = c2.include.getState('#server-details-sidebar');
    if (loadState !== 'loading') {
      // Don't load if it's already in the process of loading, because it could take a while
      // with conditional Server Actions and we don't want to keep sending a bunch of
      // requests
      c2.include.reload('#server-details-sidebar');
    }
    c2.include.reload('#server-details-panel-organization');

    /*
     * We decided that these reloads, which block the tables, were too disruptive. Need to figure
     * out an unobtrusive way to reload them without showing the processing indicator or blocking.

    $('table#jobs').DataTable().ajax.reload();
    c2.history.loadHistoryData();

    */
  }


  /*
   * Clear all interval timers and timeouts.
   */
  function stopUpdates() {
    logger.debug('stopUpdates');
    clearInterval(updateTimer);
    clearTimeout(mediumTimeout);
    clearTimeout(longTimeout);
    updateTimer = 0;
    mediumTimeout = 0;
    longTimeout = 0;
  }


  /*
   * Enable/disable server action buttons depending on server state and user permissions
   */
  function setActionButtonStates(
          power_status,
          can_be_modified,
          can_console,
          can_be_decommissioned) {

    // data-role attributes are determined by the action dict's 'role' key.
    if (! can_be_modified) {
      $('#server-actions [data-role="modifies"]').addClass('disabled');
    }

    if (! can_console) {
      $('#server-actions [data-role="accesses-console"]').addClass('disabled');
    }

    // TODO: there is an 'accesses-terminal' role but no simple check on the server
    // model for it yet. For now, server.available_actions() disables RDP/SSH button.

    if (! can_be_decommissioned) {
      $('#server-actions [data-role="deletes"]').addClass('disabled');
    }
  }


  c2[__module__] = {
    liveUpdates: liveUpdates,
    setActionButtonStates: setActionButtonStates,
    stopUpdates: stopUpdates
  };
})('server', window.c2, window.jQuery);

/*
 * Server detail view Stats tab
 */

(function (__module__, c2) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);
  var chartSettings = {};
  var allServerEvents = [];

  function init(settings) {
    logger.debug('init called with settings: ', settings);
    var now = (new Date()).getTime();

    // Store data so drawCharts can use it
    chartSettings = settings;
    chartSettings.startTime = now - (chartSettings.interval * chartSettings.points  * 1000)

    var $historyTable = $('#history');
    if ($historyTable.data('table-source') !== undefined) {
      // History table has been initialized. User must have chosen a different
      // date range. Redraw the new charts.
      drawCharts();
    }
  }

  // Called in c2.history.loadHistoryData once server history events are loaded
  function drawCharts(historyEvents) {
    logger.debug('drawCharts\n  chartSettings: ', chartSettings);

    if (chartSettings && chartSettings.cpuValues === undefined) {
      logger.debug('This server has no stats, so not drawing charts.')
      return;
    }

    if (historyEvents) {
      // Store these so we can use them from now on as the user requests
      // different date ranges.
      allServerEvents = historyEvents;
    }

    // use just the events that happened at or after startTime
    var serverEvents = _.filter(allServerEvents, function(event) {
        return event.epoch_ms >= chartSettings.startTime;
    });
    logger.debug('  serverEvents:', serverEvents);

    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    c2.charts.drawServerCPUStatsChart(
      chartSettings.startTime,
      chartSettings.interval,
      chartSettings.cpuValues,
      serverEvents,
      c2.charts.commonStatChartOpts);

    c2.charts.drawServerMemStatsChart(
      chartSettings.startTime,
      chartSettings.interval,
      chartSettings.memValues,
      serverEvents,
      c2.charts.commonStatChartOpts);

    c2.charts.drawServerDiskStatsChart(
      chartSettings.startTime,
      chartSettings.interval,
      chartSettings.diskValues,
      serverEvents,
      c2.charts.diskStatChartOpts);


    c2.charts.drawServerNetStatsChart(
      chartSettings.startTime,
      chartSettings.interval,
      chartSettings.netValues,
      serverEvents,
      c2.charts.netStatChartOpts);
  }


  c2[__module__] = {
    init: init,
    drawCharts: drawCharts
  };
})('serverStats', window.c2);

// Bootstrap slider

(function (c2) {
  'use strict';


  function updateVisibleValue(slideEvt) {
    var $parent = $(this).parent();
    var $origInput = $parent.find('input');
    var $sliderValue = $parent.find('.slider-value');

    // value is either the value ('slide' events) or an object with both
    // oldValue and newValue ('change' event)
    var value = (slideEvt.value && slideEvt.value.newValue !== undefined) ? slideEvt.value.newValue : '';

    $sliderValue.html(value + getSliderUnitsStr($origInput));
  }


  function getSliderUnitsStr($origInput) {
    var unitsStr;
    unitsStr = $origInput.data('slider-units');
    return (unitsStr) ? '&nbsp;' + unitsStr : '';
  }

  /*
   * Enable sliders in the DOM.  Uses sliderSelector if it's specified;
   * otherwise turns anything with class "sliderize" into a slider and removes
   * that class (so slider is only called once per element).
   *
   * Adds some markup for the visible slider value element.
   *
   * Sets up some event handling.
   */
  function init(sliderSelector, sliderOptions) {
    var $sliders = $(sliderSelector || '.sliderize');
    var unitsStr, $origInput, currentValue;
    var options = _.merge(sliderOptions || {}, {
      handle: 'custom',
      tooltip: 'hide'
    });

    // Add the visible slider value element
    $sliders.each(function() {
      $origInput = $(this);

      // Initialize the slider value based on the original input's value,
      // defaulting to its 'data-initial-value' attr which will be the
      // FormField's initial value.  If there is no initial, use the slider
      // minimum.
      currentValue = $origInput.val() || $origInput.data('initial-value') || $origInput.data('slider-min');

      // Without this, bootstrap-slider initializes to 5
      $origInput.attr('data-slider-value', currentValue || "");

      if (currentValue) {
        // Use parseFloat here to convert string formatted number from the DOM
        // into either an integer or float value
        options.value = parseFloat(currentValue);
      }

      $origInput.slider(options);

      $origInput.removeClass('sliderize');

      // Sliding can trigger a lot of change events, so throttle the updating
      // of visible value to something smaller (but still imperceptible)
      $origInput.on('change', $.throttle(100, updateVisibleValue));

      // Show visible value next to slider
      $origInput.after('<span class="slider-value">' + options.value + getSliderUnitsStr($origInput) + '</span>');
    });
  }


  c2.sliders = {
    init: init
  };

})(window.c2);

/* smartFields.js
 *
 * Form fields that are modified by other form field values.
 */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);

  /*
   * Find all form fields on the page that have a `data-control` attribute
   * and morph things based on the controlling field's value.
   *
   * data-control is a JSON list of dicts, e.g.:

          [{
            "source": "my-bool-field-name",  // controlling field
            "showhide": {
              "when": [value1, value2]
            }
          },
          {
            "source": "os_build",  // the controlling field can be the OS Build option
            "showhide": {
              "when": [17, 38, 95]
            }
          }]


   */
  function init($container) {

    $container.find('[data-control]').each(function () {
      // $dependent_field declared here to be bound correctly in the change function below
      var $dependent_field = $(this);
      createChangeHandlersForDependentField($dependent_field, $container);
    });

    // Find the list of fields that should be populated when the form first displays.
    // The 'data-root-fields' attribute can appear in the container in a couple
    // different ways. Sometimes it comes on in the one passed to init, and
    // sometimes it comes in on one or more children of the container. Here's a
    // unified way to find them all in both cases. (find searches the container's
    // descendants, while addBack includes the container itself)
    var $form_divs = $container.find('[data-root-fields]').addBack('[data-root-fields]').map(function () {
      return $(this).attr('data-root-fields');
    }).get();

    // Since a single data-root-fields attribute may contain comma-separated values,
    // just join the list of all attribute values then split the whole thing once.
    var rootFields = $form_divs.join(',').split(',');

    // Finally, we can find each field by its id, and trigger a change event
    // for it. Use our custom change event to ensure that updates happen even
    // while ignoring user events.
    logger.debug('Root fields: ', rootFields);
    $.each(rootFields, function(idx, field_id) {
      // If the field_id/ name winds up being an empty string, don't try to do anything with it
      if (field_id.length > 0) {
        // IDs on ActionInputs have no "form prefix", while those on BP-related
        // forms do. This selector looks for IDs that begin with "id_", and end
        // with the name of the field.
        var field = $("[id^='id_'][id$='" + field_id + "']");
        field.trigger('smartFields.changed');
      }
    });

    // Also trigger a change event on any 'os_build' form fields,
    // for OS Family dependent fields to show or hide on initial form load.
    $("[id^='id_form-'][id$='-os_build']").each(function(idx, element) {
      $(element).trigger("smartFields.changed");
    });
  }

  function trimIfString(value) {
    if (value === null || value === undefined) {
      return "";
    }

    if (typeof(value) === "string") {
      return value.trim();
    } else {
      return value;
    }
  }

  /*
   * Set up change handlers for the single dependent field with id $dependent_field_id.
   * The change handlers are created on the controlling field(s), so that when the controlling field changes,
   * the appropriate handler ('regenoptions' or 'showhide') will be called, with this dependent field passed to it.
   */

  function createChangeHandlersForDependentField($dependent_field, $container) {
    logger.debug('Initialize dependent field:', $dependent_field);
    var data, control_data, $controlling_field;
    data = $dependent_field.attr('data-control');
    if (!data) {
      logger.debug('  No control data; skipping');
      return;
    }

    // Loop over each of the controlling fields for this dependent field in order to set up
    // change handlers on the controlling fields
    control_data = JSON.parse(data);
    for (var i = 0; i < control_data.length; i++) {
      logger.debug('  control_data[i]:', control_data[i]);
      $controlling_field = getControllingField(control_data[i], $container, $dependent_field);

      // If the $controlling_field field is not on the form, the $dependent_field should
      // behave like a normal field.
      if ($controlling_field.length === 0) {
        logger.debug('  No controlling field found; skipping.');
        continue;
      }

      // Control has 3 keys: source, target and the handler function name.
      var keys =  Object.keys(control_data[i]);
      // remove source
      keys.splice(keys.indexOf('source'), 1);
      // remove target
      var target_index = keys.indexOf('target');
      if(target_index > -1) {
        keys.splice(target_index, 1);
      }

      // only key left should be handlerName
      var handlerName = keys[0];
      logger.debug('  Handler name:', handlerName);
      var handler = handlers[handlerName];

      var eventName = getChangeEventForField($controlling_field);

      $controlling_field
        .on('smartFields.changed ' + eventName, function(e) {
            logger.debug('Handling event: ', e);
            handler($dependent_field.attr('id'), $container);
        });
    }
  }

  /*
   * Return the event name this field triggers and which should cause dependent fields to be shown
   * or hidden.
   */
  function getChangeEventForField($field) {
    var $slider = $field.closest('.form-group').find('.slider');
    if ($slider.length) {
      return 'slideStop';
    }

    // For most fields we can just observe 'change'
    return 'change';
  }

  function getControlValue($control_field) {
    var controlValue;
    if ($control_field.is(':checkbox')) {
      controlValue = $control_field.prop('checked');
    } else {
      controlValue = $control_field.val();
    }
    logger.debug('  Controlling field:', $control_field);
    logger.debug('  Value of controlling field:', controlValue);
    return controlValue;
  }

  function isControlMatching(values, $control_field) {
    // In some cases, the boolean field is actually a drop-down string field on the form, so
    // look for the string equivalents of the booleans as well.
    if (values.indexOf(true) != -1 && values.indexOf("True") == -1) {
      values.push("True");
    }
    if (values.indexOf(false) != -1 && values.indexOf("False") == -1) {
      values.push("False");
    }

    var controlValue = getControlValue($control_field);

    logger.debug('  Values to show dependent field:', values);

    var controlMatch;
    var matchAnyValue = values.length === 0;
    if (matchAnyValue) {
      // controlValue.length checks for both empty string and empty array
      controlMatch = controlValue !== null && controlValue.length !== 0;
    } else {
      var controlValues;
      var controlDelimiter = $control_field.data('delimiter');
      if (Array.isArray(controlValue)) {  // multi-select input case
        controlValues = controlValue;
      } else if (controlDelimiter !== undefined) {
        controlValues = controlValue.split(controlDelimiter);
      } else {
        controlValues = [controlValue];
      }

      // Make controlMatch true if any of the controlValues match
      controlMatch = controlValues.some(function(controlValue) {
        return (
          // String or boolean case
          ($.inArray(controlValue, values) !== -1) ||
          // Ints and floats need to be explicitly handled
          // since we are casting all values to strings in common/fields.py
          ($.inArray(parseInt(controlValue), values) !== -1) ||
          ($.inArray(parseFloat(controlValue), values) !== -1)
        );
      });
    }
    logger.debug('  Found a match:', controlMatch);
    return controlMatch;
  }

  function showOrHideField(show_dependent_field, $dependent_field) {
    // Now hide or show the dependent field. Also immediately mark this field's visibility using
    // a custom data attr. This ensures c2.orderForm.validateRequiredField has the correct info
    // needed for formset validation.

    var $formGroup = $dependent_field.closest('.form-group');
    if (show_dependent_field) {
      logger.debug('  Showing dependent field ', $dependent_field);
      $formGroup.data('dependent-field-visible', true)
        // Show the dependent field, slowly enough that users notice
        .fadeIn(400);
      var $formControl = $dependent_field.closest('.controls');
      $formControl.css('overflow', 'visible');
      $dependent_field.prop('disabled', false);
      $dependent_field.data('is-visible', true);

      // From now on, this field will be faded out rather than hidden immediately.
      $dependent_field.data('dependent-field-seen', true);
    } else {
      logger.debug('  Hiding dependent field ', $dependent_field);
      $formGroup.data('dependent-field-visible', false);

      // Either hide this dependent field immediately (first render of form) or
      // fade it out to indicate the form is morphing.
      if ($dependent_field.data('dependent-field-seen')) {
        $formGroup.fadeOut(400);
      } else {
        $formGroup.hide();
      }

      // Do not let hidden fields be submitted
      $dependent_field.prop('disabled', true);
      $dependent_field.data('is-visible', false);

      // Clear any errors on the dependent field to allow form submission.
      $dependent_field.parents('.has-error').removeClass('has-error');
    }
  }

  var handlers = {
    /*
     * 'showhide' handler: Show dependent field if control field has the value specified by `when`;
     * otherwise hide the dependent field. when should be an object like {when: [true]} or
     * {when: ['a', 'b']}.  An empty array means dependent field is shown as long as control
     * has any non-empty value.
     *
     * 'regenoptions' handler: Regenerates the optional values on the dependent field via ajax call
     */
    showhide: function($dependent_field_id, $container) {
      // Iterate across the controlling fields and only show the dep field if all are matching.

      logger.debug('Processing dependent field for show/hide ', $dependent_field_id);
      var $controlling_field;
      var $dependent_field = $container.find('#' + $dependent_field_id);
      var show_dependent_field = true;  // innocent until proven guilty
      var is_control_visible;
      var when_values;
      var data = $dependent_field.attr('data-control');
      var control_data = JSON.parse(data);

      for (var i = 0; i < control_data.length; i++) {
        logger.debug('  control_data[i]:', control_data[i]);
        $controlling_field = getControllingField(control_data[i], $container, $dependent_field);

        // If the $controlling_field field is not on the form, it shouldn't affect whether the
        // dependent field is shown.
        if ($controlling_field.length === 0) {
          logger.debug('  No controlling field', control_data[i], ' found; skipping.');
          continue;
        }

        // If the dependency_type does not match the expected handler, it shouldn't affect whether the
        // dependent field is shown.
        if (!('showhide' in control_data[i])) {
          logger.debug(control_data[i], ' not related to show/hide; skipping.');
          continue;
        }

        // If the controlling field is present, but hidden, also hide the dependent field. This
        // hides nested dependent fields when the intermediate field is hidden.
        // Specifically check if this 'is-visible' is false. If it is undefined, ignore it.
        is_control_visible = $controlling_field.data('is-visible');
        if (is_control_visible == false) {
          logger.debug('  Controlling field seems to not be visible, will hide dep field ', is_control_visible);
          // stop iterating when any control is not visible and hide the dep field
          show_dependent_field = false;
          break;
        }

        when_values = control_data[i]['showhide']['when'];
        show_dependent_field = isControlMatching(when_values, $controlling_field);
        if (!show_dependent_field) {
          logger.debug('  Controlling field seems is visible but not matching, will hide dep field ');
          // stop iterating when any control is not matching and hide the dep field
          break;
        }
      }

      showOrHideField(show_dependent_field, $dependent_field);

      // Trigger a custom 'changed' event on the dependent field to show/hide any nested dependent
      // fields that use it as controlling field.
      $dependent_field.trigger('smartFields.changed');
    },

    // Batches up the current form selections for submission to the back-end,
    // then gets the correct options for the dependent field, based on those
    // selections. Triggers a change event for the field.
    regenoptions: function($dependent_field_id, $container) {
      logger.debug('Processing dependent field for regenerating options ', $dependent_field_id);
      var $controlling_field;
      var $dependent_field = $container.find('#' + $dependent_field_id);
      var data = $dependent_field.attr('data-control');
      var control_data = JSON.parse(data);

      // Multiple controllers are currently only supported for the case of OS
      // Family, which is a show/hide controller. Fields that are not regen
      // fields get skipped in the loop.
      for (var i = 0; i < control_data.length; i++) {
        logger.debug('  control_data[i]:', control_data[i]);
        $controlling_field = getControllingField(control_data[i], $container, $dependent_field);

        // If the $controlling_field field is not on the form, it shouldn't affect whether the
        // dependent field is shown.
        if ($controlling_field.length === 0) {
          logger.debug('  No controlling field', control_data[i], ' found; skipping.');
          continue;
        }

        // If the dependency_type does not match the expected handler, it shouldn't affect whether the
        // dependent field is shown.
        if (!('regenoptions' in control_data[i])) {
          logger.debug(control_data[i], ' not related to regenerating options; skipping.');
          continue;
        }
        // Find the the div containing the .controls class that is closest to the dependent field for selectize.
        var $formControl = $dependent_field.closest('.controls');
        // Visually indicate that the field is in the process of being changed
        c2.block.block($formControl, true);
        var dfName = control_data[i].target;
        var cfName = control_data[i].source;
        // Add the environment to the formData, because it may be disabled and won't be serialized in that case.
        var $serviceItem = $dependent_field.closest('.service-item');
        var $envField = $serviceItem.find('select[name$="-environment"]');
        var envFieldDisabled = false;

        // Enable the environment form field temporarily so that it gets included in the form data
        if ($envField.prop('disabled')) {
          envFieldDisabled = true;
          $envField.prop('disabled', false);
        }

        // Serialize the form data
        var $form = $dependent_field.closest('form');
        var formData = $dependent_field.closest('form').serializeArray();
        var metadata = '_metadata'
        formData = formData.filter(function(d) {
          if(!d.name.includes(metadata)) {
            return d;
          }
        });
        var $action = $form.prop('action');

        // Re-disable the environment field.
        if (envFieldDisabled) {
          $envField.prop('disabled', true);
        }
        var formPrefix = $controlling_field.attr('name').replace(cfName, '');
        // delete the trailing dash to be consistent with the django form prefix attribute
        formPrefix = formPrefix.replace(/-$/, '');

        formData.push({name: "form-prefix", value: formPrefix});
        formData.push({name: "form-action", value: $action});
        var url = '/regenerate_options_for_field/' + dfName + '/' + cfName + '/?' + $.param(formData);
        logger.debug(' Url is ', url);

        // AJAX Call for get the new regenerated options.
        $.get(url, function(response) {
          if (!response.error) {
            // Set new options and initial value from response.
            logger.debug("response.options: ", response.options);
            var $newOptions = response.options;

            // Must use c2.selectize to reset the options.
            var selectize_args = {};
            if ($dependent_field.attr('data-selectize-args') !== undefined) {
              selectize_args = JSON.parse($dependent_field.attr('data-selectize-args'));
            }
            var selectized_field = c2.selectize($dependent_field, selectize_args);

            // We don't want anything to generate additional change events, so we can
            // have complete control over when the change event is triggered
            // once we're ready for it to be. To accomplish this, add an event handler
            // that's first that prevents any change events from actually doing anything
            var ignore_listener = function (event) {
              event.preventDefault();
              event.stopImmediatePropagation();
            };
            // Credits to
            // https://stackoverflow.com/questions/2360655/jquery-event-handlers-always-execute-in-order-they-were-bound-any-way-around-t/2641047#2641047
            $.fn.bindFirst = function(name, fn) {
                this.on(name, fn);

                this.each(function() {
                    var handlers = $._data(this, 'events')[name.split('.')[0]];
                    // take out the handler we just inserted from the end
                    var handler = handlers.pop();
                    // move it at the beginning
                    handlers.splice(0, 0, handler);
                });
            };
            $dependent_field.bindFirst('change', ignore_listener)

            // Clear the options first, and create field with arguments from the server
            // Both this and the call to setValue are done silently by passing true,
            // so they don't trigger additional change events
            selectized_field.clearOptions(true);

            // Then loop through the new options adding the new options to selectize. Trim any extra white space from ends.
            $.each($newOptions, function(key, value) {
              var val = trimIfString(value[0]);
              var text = trimIfString(value[1]);

              selectized_field.addOption({
                value: val,
                text: text
              });
            });

            // Set the value of the dependent field.
            var $newInit = response.initial_value;
            var noInitialValue = ($newInit === null);
            var hasOptions = (($newOptions[0] !== null) && ($newOptions[0] !== undefined));
            var isRequired = selectize_args['required'];
            if (noInitialValue && hasOptions && isRequired) {
              $newInit = $newOptions[0][0];
            }

            if ($newInit !== null) {
              // The user may return a tuple as the initial value, like they
              // may return a list of tuples as the options_list. So, extract
              // just the first value if this is an array.
              if (Array.isArray($newInit)) {
                $newInit = $newInit[0];
              }
              $newInit = trimIfString($newInit);
            }
            selectized_field.setValue($newInit, true);

            // Keep Selectize dropdowns from being obscured
            $formControl.css("overflow", "visible");
          } else {
            // Show error message which may contain markup, e.g. XML, so escape it using `text`.
            var msg = $('<div class="alert alert-danger"></div>').text(response.error);
            logger.debug(msg);
            $formControl.html(msg);

          }

          // Visually unblock the field now that we're done
          c2.block.unblock($formControl);
          // We also need to allow change handlers to function again
          $dependent_field.off('change', ignore_listener);
          // Trigger change to re-initialize any fields dependent on this dependent field.
          // and to let orderForm.updateFormIfFieldChanged update the error state and submit button.
          $dependent_field.trigger('change');
        });
      }
    }
  };


  /*
   * Given a control object that specifies a 'source', return the corresponding form field.
   *
   * On the order form, such fields have a formset prefix and can only be controlled by fields in
   * the same blueprint item.
   *
   * On the ActionInputForm used by server and resource actions, it's a simple search by the 'name'
   * attribute.
   */
  function getControllingField(control, $container, $dependentField) {
    logger.debug('getControllingField "'+ control.source +'"');
    logger.debug('  for dep field ', $dependentField);

    var $serviceItem = $dependentField.closest('.service-item');
    if ($serviceItem.length !== 0) {
      // Order form:
      // Find the controlling field, e.g. #id_form-0-source, by searching for the
      // field in this blueprint item ending in "-<source>". The dash prevents us
      // from finding fields that are a partial match, such as "new_password"
      // when the source is "password".
      var $controlField = $serviceItem.find('[name$="-' + control.source + '"]');
      logger.debug('  ==> $controlField from order form:', $controlField);
      return $controlField;
    }
    logger.debug('  Dep field has no service item ancestor');

    // ActionInputForm (server or resource action, etc):
    // Find the control field anywhere in the container.
    var $controlField = $container.find('[name="' + control.source + '"]').first();
    logger.debug('  ==> $controlField from action input form:', $controlField);

    if ($controlField.hasClass('codeeditorwidget')) {
      logger.error('Code editor widgets cannot be controlling fields.');
    }

    return $controlField;
  }


  c2[__module__] = {
    init: init
  };

})('smartFields');

/* CloudBolt framework for standard behavior for drag & drop sorting of items
 */

(function (c2, $, _) {
  'use strict';

  /* Convenience function applies the HTML5 sortable plugin to a set of
   * elements and provides a framework for consistent look & feel and behavior.
   *
   * Each sortable element should have a data-id attribute containing the
   * server-side ID of the item it represents.
   *
   * Args:
   *
   * - sortableGroupSelector: selects one or more elements that contain a set
   *   of elements to be made sortable.  Sortable dragging and dropping is
   *   constrained within their group container.
   *
   * - updateURL: URL to a view that will handle the POST request on drop. It
   *   will receive a list of item IDs in the new order, in a variable named
   *   'seq'.
   *
   * - dropCallback: a function called after a drop action has been handled.
   *   One arg is passed to it: the jQuery object for the updated group
   *   container. We use this callback, for example, to collapse sequence
   *   numbers for items that will run in parallel.  Note, the sequence numbers
   *   will have been saved server-side before this handler is called.
   */
  function sortablePanels(sortableGroupSelector, updateURL, dropCallback) {
    $(sortableGroupSelector)
      .each(initializeSortGroup)
      .sortable({
        handle: '.sortable-handle', // only the handle allows drag initiation
        forcePlaceholderSize: true
      })

      .bind('sortupdate', function (e, ui) {
        var $group = ui.item.closest(sortableGroupSelector);
        var newSequenceOfIDs = resequenceSortables($group);

        $.post(
          updateURL,
          {seq: newSequenceOfIDs},
          function (response) {
            // Don't show the success message, at least for now. There are too
            // many places where we return success: true and a message of "true"
            // looks bad.
            // if (response.success) {
            //   c2.alerts.addGlobalAlert(response.success, 'success', true, 5000);
            // }
            if (response.error) {
              c2.alerts.addGlobalAlert(response.error, 'error', true, 5000);
            }
          }
        );

        if (dropCallback !== undefined) {
          dropCallback($group);
        }
      });
  }


  // Add some markup needed for layout of sort handles
  function initializeSortGroup() {
    var $this = $(this);
    var $panels = $this.find('.panel');

    // Only add sortable options if there is more than one panel
    if($panels.length <= 1) {
      return;
    }

    $panels
      .addClass('sortable') // simplifies styling of handles
      .find('.panel-heading').each(function(index) {
        // Add a sequence number in each handle element.  This
        // clarifies that the order of items is significant.
        $(this).prepend(
          '<span class="move-to-top-or-bottom">' +
            '  <i class="fas fa-angle-double-up"></i>' +
            '  <i class="fas fa-angle-double-down"></i>' +
          '</span>' +
          '<span class="sortable-handle">' +
          '  <i class="fas fa-bars"></i>' +
          '</span>' +
          '<span class="sort-seq">'+ (index + 1) + '</span>'
        );
      });
    // Up and down arrows to move to top or bottom
    $this.find('.fa-angle-double-down, .fa-angle-double-up').on('click', function () {
      var $el = $(this);
      var moveToTop = $el.hasClass('fa-angle-double-up');
      var $item = $el.closest('li');
      var $parentContainer = $item.parent();
      var $newLocation = moveToTop ? $parentContainer.children('li:first-child') : $parentContainer.children('li:last-child');
      moveAnimate($item, $newLocation);
      $parentContainer.triggerHandler('sortupdate', {item: $item});
    });
    // The number for the element to specify a new location as a number input
    $this.find('.sort-seq').on('click', function () {
      var $el = $(this);
      var $item = $el.closest('li');
      var $parentContainer = $item.parent();

      // Cache original value
      var initialValue = $el.text();

      // Hide original value
      $el.text('');

      // Adds the input to the DOM to specify new sequence location
      $el.append('<input type="number" class="sort-seq-input" />');

      var $sortSeqInput = $('.sort-seq-input');
      $sortSeqInput.focus();

      $sortSeqInput.on('click', function(e) {
        // We don't want click events to cause side effects like adding additional inputs
        e.stopPropagation();
      })

      // Execute change for enter and remove input element for enter or escape
      $sortSeqInput.on('keydown', function(e) {
        var $elInput = $(this);
        if(e.key === "Enter") {
          var index = $elInput.val();
          $elInput.off();
          $elInput.remove();
          if (index) {
            var $newLocation;
            if (index < 1) {
              $newLocation = $parentContainer.children('li:first-child');
            } else if (index >= $parentContainer.children('li').length) {
              $newLocation = $parentContainer.children('li:last-child');
            } else {
              $newLocation = $parentContainer.children('li:nth-child(' + index + ')');
            }
            moveAnimate($item, $newLocation);
            $parentContainer.triggerHandler('sortupdate', {item: $item});
          } else {
            $el.text(initialValue);
          }
          $elInput.remove();
        }
        if(e.key === "Escape") {
          $elInput.off();
          $elInput.remove();
          $el.text(initialValue);
        }
      })

      // Clicking on another location or tabbing out of it removes the input element
      $sortSeqInput.on('blur', function() {
        var $elInput = $(this);
        $elInput.off();
        $elInput.remove();
        $el.text(initialValue);
      })
    });
  }

  function moveAnimate(element, newLocation){
    //Allow passing in either a jQuery object or selector
    var $element = $(element);
    var $newLocation = $(newLocation);

    var oldOffset = $element.offset();
    // Move the element to its new location
    $newLocation.index() < $element.index() ? $element.insertBefore($newLocation) : $element.insertAfter($newLocation);
    var newOffset = $element.offset();

    var temp = $element.clone().appendTo('body');
    // Set initial values for animation purposes
    temp.css({
        'position': 'absolute',
        'left': oldOffset.left,
        'top': oldOffset.top,
        'z-index': 1000,
        'width': $element.width()
    });
    // Visibility allows the space on the screen to remain where .hide() would not
    $element.css('visibility', 'hidden');
    // Animates the element moving from the old location to the new one
    temp.animate({'top': newOffset.top, 'left': newOffset.left}, 'slow', function(){
       //Once animation completes, clean up css and temp element
       $element.css('visibility', 'visible');
       temp.remove();
    });
}


  // Renumber all sortables client side and return a list of IDs in the new
  // order.
  function resequenceSortables($group) {
    var $handles = $group.find('.sortable-handle').toArray();
    return _.map($handles, function (item, index) {
      var $handle = $(item);
      // ID is stored on the panel containing the drag handle
      var panelID = $handle.closest('.panel').data('id');
      if (panelID) {
        // Assign it a new user-visible sequence number
        $handle.siblings('.sort-seq').text(index + 1);
      } else {
        // It's a placeholder of some sort so ignore
      }

      return panelID;
    });
  }


  c2.sortable = {
    resequenceSortables: resequenceSortables,
    sortablePanels: sortablePanels
  };

})(window.c2, window.jQuery, window._);

(function (c2) {
  'use strict';


  function init(selector) {
    $(selector || '.sparkline').each(function (i, span) {
      // fetch the list of colors from the data-colors attribute on the span
      // each of these colors corresponds to one of the bars, so the successess are colored
      // green and the failures red
      $(span).sparkline(
        'html',
        {
          // Do not let sparkline auto-size itself b/c it can break page in Chrome at certain text
          // sizes (110%)
          height: '18px',
          type: 'bar',
          chartRangeMin: '0',
          disableTooltips: true,
          highlightColor: '#9999FF',
          colorMap: $(span).data('colors').split(',')
        }
      );
    });
  }

  c2.sparklines = {
    init: init
  };
})(window.c2);

/* spotlight.js - Local page search with in-place highlighting.
 *
 * As user types, matching text on the page is highlighted in place. The search
 * data set is composed of all visible text nodes contained by elements having
 * attribute data-spotlight. Additionally, synonyms and related search terms
 * may be provided on those elements by the value data-spotlight attribute.
 *
 * Search engine is the same as used by Selectize, sifter.js.
 * At call time, builds a sifter hash datastructure of all selected text nodes.
 * https://github.com/brianreavis/sifter.js#sifterjs
 *
 * TODO:
 *   Each match is given a tab index for fast navigation/click.
 *
 * Usage:
 *
 *   <div class="spotlight-search-bar">
 *     <input data-spotlight-search="#searchSpaceContainer" type="text" ...>
 *     <div class="spotlight-results">
 *       <ol class="list-unstyled"></ol>
 *     </div>
 *   </div>
 *
 *   <p data-spotlight>Some searchable text</p>
 *   <a href="" data-spotlight="canine puppy">Dog</a>
 *   <a href="" data-spotlight="feline kitty">Cat</a>
 *
 *   <script>c2.spotlight.init();</script>
 *
 * In the above example, searching for...
 *   some   - highlights the entire paragraph
 *   puppy  - highlights the Dog link
 *   at     - highlights the Cat link
 *
 * Highlight style is customized by the .spotlight CSS class which is added to
 * any highlighted elements (the same ones that have the data-spotlight
 * attribute.
 *
 * data-spotlight-search may also be given a value to specify an element
 * selector to apply when associating data-spotlight elements to that input. In
 * this way, multiple independent spotlight searches can exist on the same page
 * (e.g. in different tabs).
 *
 *   <input data-spotlight-search="#tab1" ...>
 *   <input data-spotlight-search=".column2" ...>
 *
 */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);


  function init() {
    var $input = $('input[data-spotlight-search]');
    $input.each(initOneSearchField);
  }


  /* Set up a spotlight search field and its target content.
   */
  function initOneSearchField() {
    /*jshint validthis: true */
    var $input = $(this);
    logger.debug('Initializing a spotlight search field:', $input);
    var $thisSearchBar = $input.closest('.spotlight-search-bar');
    var $dropdown = $thisSearchBar.find('.spotlight-results');
    var items = getAllSpotlightItems($thisSearchBar);
    logger.debug('  Spotlightable items:', items);
    // Build the datastructure used by sifter
    var data = _.map(items, function (item) {
          var $item = $(item);
          return {
            'text': $item.text(),
            'keywords': $item.data('spotlight') || "",
          };
        });
    logger.debug('  sifter search engine data:', data);
    var sifter = new Sifter(data);

    $input.on('keydown.spotlight', function(e) {
      logger.debug('keydown event on spotlight search field:', e);

      switch (e.key) {
        case 'ArrowDown':
        case 'Down': // MS Edge
        case 'Tab':
          $dropdown.find('a').first().focus();
          e.preventDefault();
          return;
      }

      // Gotcha: the new input value is not yet available to keydown event handlers (which enables
      // them to cancel the event if desired). Thus, we must use setTimeout or $.debounce to
      // essentially allow the event to proceed and the browser to update the input before using
      // it.
      setTimeout(function() {
        handleKeydownOnInput(e, items, sifter, $thisSearchBar, $dropdown);
      }, 1);
    });
  }


  /*
   * Key events on the search input field.
   */
  function handleKeydownOnInput(e, items, sifter, $thisSearchBar, $dropdown) {
    var query = $(e.target).val();

    if (query === "") {
      clearResults($dropdown);
      return;
    }

    var results = sifter.search(query, {fields: ['text', 'keywords']});
    var matches = _.at(items, _.map(results.items, 'id'));
    unspotlight(items);
    spotlight(matches);
    showResults($dropdown, matches);
  }


  /*
   * Highlight matching items on the page.
   */
  function spotlight(items) {
    $(items).each(function() {
      var $item = $(this);
      $item.addClass('spotlight');

      var $container = $item.closest('.collapse');
      // If the item being spotlighted is inside a closed collapsible, open
      // it.
      if (!$container.hasClass('in')) {
        $container.collapse('show');
      }
    });
  }


  /*
   * Remove highlight from mathing items on the page.
   */
  function unspotlight(items) {
    $(items).removeClass('spotlight');
  }


  /*
   * Show a dropdown containing all matching items and set up behaviors for click and keyboard.
   */
  function showResults($dropdown, results) {
    var $list = $dropdown.find('ol');
    $list.html('');

    if (results.length === 0) {
      $list.append($('<li><i>No matches on page.</i></li>'));
      return;
    }

    // Clone all result elements and add them to the list
    $(results).each(function() {
      addResultToList($list, $(this));
    });

    setupSpotlightResultsBehaviors($dropdown);
    $dropdown.addClass('active');
  }


  function clearResults($dropdown) {
    $dropdown.removeClass('active');

    var $list = $dropdown.find('ol');
    var $searchBar = $dropdown.closest('.spotlight-search-bar');
    var items = getAllSpotlightItems($searchBar);
    unspotlight(items);
    $list.html('');
    $searchBar.find('input[data-spotlight-search]').val('').focus();
  }


  /*
   * Given a spotlight search bar, find all targets on the page which it searches and return them,
   * but as a list of DOM nodes not jQuery objects.
   */
  function getAllSpotlightItems($searchBar) {
    var $input = $searchBar.find('input[data-spotlight-search]');
    // If no selector is specified, search the entire body.
    var containerSelector = $input.data('spotlight-search') || 'body';
    return document.querySelectorAll(containerSelector + ' [data-spotlight]');
  }


  /*
   * Append search result to results list, wrapped in a LI.
   *
   * If the result is an anchor, clone it and strip its spotlight attrs.  If result is not an
   * anchor, such as a section heading, repeat this for all anchors contained in it.
   */
  function addResultToList($list, $result) {
    if ($result[0].tagName == 'A') {
      $list.append($('<li></li>').append(cloneResultLink($result)));
    } else {
      // Special case: Bootstrap collapsible panels
      if ($result.data('toggle') == 'collapse') {
        var $panelBody = $($result.data('target'));
        $panelBody.find('a[data-spotlight]').each(function() {
          addResultToList($list, $(this));
        });
      }
    }
  }


  /*
   * Return a clone of an anchor represented by the given jQuery obj.
   * Remove attrs and classes that aren't needed in the results list.
   */
  function cloneResultLink($result) {
    var $link = $result.clone();
    $link.removeClass('spotlight');
    $link.removeAttr('data-spotlight');
    return $link;
  }


  /*
   * Set up mouse and keyboard event handlers for navigating search results and closing the
   * dropdown.
   */
  function setupSpotlightResultsBehaviors($dropdown) {
    if ($dropdown.data('behaviors-initialized')) {
      return;
    }
    $dropdown.data('behaviors-initialized', true);

    // Close dropdown when user clicks outside of it
    $(document).on('click', function(e) {
      if (!$(e.target).closest('.spotlight-results').length) {
        $dropdown.removeClass('active');
      }
    });

    // Focus result links on hover
    $dropdown.on('mouseover.spotlight', 'a', function(e) {
      $(this).focus();
    });

    // Keyboard navigation
    $(document).on('keydown.spotlight', '.spotlight-results', function(e) {
      if (e.key.metaKey || e.key.ctrlKey) {
        return;
      }

      var $dropdown = $(this),
          $items = $dropdown.find('a'),
          focused = document.activeElement,
          focusedIndex = $items.index(focused);

      switch (e.key) {
        case 'ArrowDown':
        case 'Down': // MS Edge
          if (focusedIndex < $items.length - 1) {
            // Move focus to next result
            $items.eq(focusedIndex + 1).focus();
          }
          // Also prevent scrolling of viewport
          e.preventDefault();
          break;
        case 'ArrowUp':
        case 'Up': // MS Edge
          if (focusedIndex === 0) {
            // Focus the input
            $(this).closest('.spotlight-search-bar').find('input').select();
          } else {
            // Move focus to previous result
            $items.eq(focusedIndex - 1).focus();
          }
          e.preventDefault();
          break;
        case 'Escape':
        case 'Esc': // MS Edge
          clearResults($dropdown);
          e.preventDefault();
          break;
      }
    });
  }


  window.c2[__module__] = {
    init: init
  };

})('spotlight');

/* Tab persistence and deep linking.
 *
 * Expects a Bootstrap tab structure:
 *
 *    <ul class="nav nav-boxed-tabs">
 *      <li>
 *        <a data-toggle="tab" href="#view-1"> View 1 </a>
 *      </li>
 *      <li>
 *        <a data-toggle="tab" href="#view-2"> View 2 </a>
 *      </li>
 *    </ul>
 *
 *    <div class="tab-content">
 *      <div id="view-1" class="tab-pane active"> {{ content1 }} </div>
 *      <div id="view-2" class="tab-pane"> {{ content2 }} </div>
 *    </div>
 *
 *
 * See related c2.buttonTabs module.
 */

(function (__module__) {
  'use strict';

  var logger = c2.logging.getLogger(__module__);


  // Return the key to use when saving/restoring the active tab from
  // localStorage. Returns a key based on the URL's pathname.
  var localStorageKey = function () {
    return 'c2.tabs.active.' + window.location.pathname;
  };

  // Try to activate the tab with ID `tabID`, returning `true` if successful,
  // `false` if not.
  function activateTab(tabId) {
    if (tabId === '') {
      return false;
    }
    var $tabLink = $('a[data-toggle=tab][href="#'+ tabId +'"]');
    $tabLink.tab('show');
    return !! $tabLink.length;
  }

  // Save `tabID` as the active tab to localStorage.
  function persistToLocalStorage(tabId) {
    var key = localStorageKey();
    localStorage.setItem(key, tabId);
  }

  // Show the tab that has been remembered by localStorage. Return true if a
  // tab is restored, false otherwise.
  function restoreFromLocalStorage() {
    var key = localStorageKey();
    var tabId = localStorage.getItem(key);
    return activateTab(tabId);
  }

  // Save `tabID` as the active tab to the current URL's hash.
  function persistToHash(tabId) {
    if (history.replaceState) {
      history.replaceState({}, '', '#' + tabId);
    }
  }

  // Show the tab indicated by the page's URL hash. Return true if a tab is
  // restored, false otherwise.
  function restoreFromHash() {
    var tabId = location.hash.slice(1);
    return activateTab(tabId);
  }

  function init() {
    setTimeout(function() {
      $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var tabId = this.hash.slice(1);
        persistToHash(tabId);
        persistToLocalStorage(tabId);
      });

      // Only restore from localStorage if we don't restore from the URL hash
      // because URLs have the most authority.
      if (! restoreFromHash()) {
        restoreFromLocalStorage();
      }
    },
    // This delay helps avoid a strange UI bug where content in Bootstrap tabs
    // seems to break out and destroy the entire page [#133217587]
    50);
  }

  // expose public functions
  c2[__module__] = {
    init: init
  };

})('tabs');

// Text-related behaviors

(function (c2, $) {
  'use strict';


  function enableDoubleClickSelection(container) {
    $(container).on('dblclick', '[data-dblclickable]', function(e) {
      e.preventDefault();
      $(this).selectText();
    });
  }


  c2.text = {
    enableDoubleClickSelection: enableDoubleClickSelection
  };
})(window.c2, window.jQuery);

// Toggle switches
// Ours are implemented by Bootstrap Toggle ()
//

(function (c2, $) {
  'use strict';

  /**
   * Set up common on-change behavior of toggle switches: to post to a URL
   * defined by their `data-post-url` attribute.  The name of the input element
   * becomes the key and the value is true or false. This works in conjunction
   * with the server side `common.views.toggle_boolean_property` to apply the
   * change.
   *
   * Optionally specify the selector to use; otherwise applies to all inputs with
   * data-toggle=toggle.
   */
  function enablePostOnChange(selector) {
    var $toggles = $(selector || 'input[data-toggle=toggle]');

    $toggles.off('change'); // Make idempotent
    $toggles.on('change', function (e) {
        var $box = $(this);
        var url = $box.data('post-url');
        var reloadPageOnToggle =  $box.data("reload-page-on-toggle");

        var data = {};
        data[$box.attr('name')] = $box.prop('checked');

        $.post(url, data, function (response) {
            if (response !== null && response.redirectURL ) {
              window.location.href = response.redirectURL;
            }
            if (reloadPageOnToggle === "True") {
                location.reload(true);
            }
        });

    });
  }

  c2.toggles = {
    enablePostOnChange: enablePostOnChange
  };
})(window.c2, window.jQuery);

/* Augment Twitter Bootstrap's tooltip.js */

// Usage
// =====
//
// To remove a tooltip's max-width, add the property ``data-max-width=none`` to
// the tooltip toggle (the element that has ``data-toggle="tooltip"``).
//

(function (c2) {
  'use strict';

  var tooltip, origTemplate, $wrappedTemplate;


  /*
   * Initialization to be run onReady in c2.go()
   *
   * Invokes Bootstrap tooltip method to initialize all elements within
   * $container having data-toggle="tooltip". If $container is not defined, all
   * such elements in the document are initialized.
   */
  function init($container) {
    if ($container === undefined) {
      $container = $(document);
    }

    if (! document.getElementById('tooltip-container')) {
      createBaseTooltip();
    }

    setTitlesFromSourceElements($container);

    $container.tooltip({
      selector: '[data-toggle=tooltip]',
      placement: 'auto top',
      delay: {show: 500, hide: 100},
      container: '#tooltip-container'
    });

    $(document).on('show.bs.tooltip', handleTooltipShown);

    // Let users dismiss tooltips via click. This is a useful fallback if the
    // mouseoff handler is somehow disconnected from the open tooltip element
    // (e.g.  content in the DOM changes).
    $('#tooltip-container').on('click', '.tooltip', handleTooltipClickToClose);
  }

  /*
   * Initialize Bootstrap tooltips.
   *
   * This has the effect of setting some module variables that'll be used by
   * all tooltips for the duration of this page.
   *
   * http://getbootstrap.com/javascript/#tooltips
   */
  function createBaseTooltip() {
    $('<div id="tooltip-container"></div>').appendTo('body');

    $(document).tooltip({
      selector: '[data-toggle=tooltip]',
      placement: 'auto top',
      delay: {show: 500, hide: 100},
      container: '#tooltip-container'
    });

    // the Tooltip object that was created by the jQuery call above.
    tooltip = $(document).data('bs.tooltip');
    // the HTML string template used by Bootstrap
    origTemplate = tooltip.options.template;
    // a DOM fragment that we'll modify and convert to HTML to create new templates
    $wrappedTemplate = $('<div></div>').append(origTemplate);
  }


  /*
   * Our way of letting the tooltip message be defined by some other element on the page.
   */
  function setTitlesFromSourceElements($container) {
    var $trigger, $source;

    $container.find('[data-tooltip-source]').each(function() {
      $trigger = $(this);
      $source = $($trigger.data('tooltip-source'));
      $trigger.attr('title', $source.html());
    });
  }

  function closeAll() {
    $('#tooltip-container').html('');
  }


  // Return a Bootstrap tooltip HTML fragment, customized with the given max-width.
  function tooltipTemplate(maxWidth) {
    $wrappedTemplate.find('.tooltip-inner').css('max-width', maxWidth);
    return $wrappedTemplate.html();
  }


  function handleTooltipShown(e) {
    var $trigger = $(e.target);
    var maxWidth = $trigger.data('maxWidth');
    var placement = $trigger.data('placement');
    // Bootstrap creates a new Tooltip instance per trigger, "inheriting"
    // options from the one that was created at plug-in initialization time.
    var triggerTooltip = $trigger.data('bs.tooltip');

    if (maxWidth) {
      triggerTooltip.tip()
        .find('.tooltip-inner')
        .css('max-width', maxWidth);
    }

    if (placement) {
      triggerTooltip.options.placement = placement;
    }
  }


  function handleTooltipClickToClose() {
    $('#tooltip-container').html('');
  }


  c2.tooltip = {
    init: init,
    closeAll: closeAll
  };
})(window.c2);

/* Visualize networks as topology diagrams */

(function (c2) {
  'use strict';

  var topoHeight;
  var topoWidth;
  var nodeAreaHeight;
  var networkAreaHeight;
  var networkBarSpacing;
  var networkBarHeight = 24;
  var networkStrokeWidth = 2;
  // Create a range of colors for the network bars. We assign these
  // in round robin order.
  var networkFills = [
    '#AFE0AF', // '#AED8AE',  // lt seagreen
    '#FFAE90',  // lt coral
    '#9AC4E6',  // lt blue
    'darkseagreen',
    'coral',
    'skyblue',
    'green',
    'darkorange',
    'steelblue'
  ];
  var networkStrokeColors = _.map(networkFills, function(c) {
    return d3.rgb(c).darker(0.3);
  });

  // Resource tiers aka nodes
  var tierFill = '#D2EFFF';
  var tierStroke = '#8CC0DA';
  var nodeAreaSpacing = 100;
  var nodeWidth = 140;
  var nodeHeight = 80;
  var nodeSpacing = 170;
  var nodeLinkWidth = 8;
  var nodeLinkSpacing = 12;


  /**
   * Initialize an SVG element to contain a topo diagram.
   */
  function init(targetSelector, networks, nodes, height, width, networkBarSpacing2, nodeAreaHeight2) {
    // Diagram dimensions are based on the content

    networkBarSpacing = networkBarSpacing2 || 60;
    nodeAreaHeight = nodeAreaHeight2 || 200;
    networkAreaHeight = (networks.length * networkBarSpacing);

    topoHeight = (networkAreaHeight + nodeAreaSpacing + nodeAreaHeight) || 600;
    topoWidth = width || 1000;

    // Top section is for network bars, bottom for nodes

    var svg = d3.select(targetSelector)
      .append('svg').attr('width', topoWidth).attr('height', topoHeight);

    drawNetworks(svg, networks);
    drawNodes(svg, nodes, networks);
    connectNodes(svg, nodes, networks);
  }


  /**
   * Draw a line per network and add its label.
   */
  function drawNetworks(svg, networks) {

    var textHeight = 12;

    var network = svg.selectAll('g')
      .data(networks)
      // Bar and info for each network is contained in a g element
      .enter().append('g')
        .attr('class', 'net')
        // Y position based on barSpacing
        .attr('transform', function(d, i) { return 'translate(0,' + (i * networkBarSpacing + 1) + ')'; });

    // the bar
    network.append('rect')
      .style('fill', function(d, i) { return networkFills[i]; })
      .style('stroke', function(d, i) { return networkStrokeColors[i]; })
      .style('stroke-width', networkStrokeWidth + 'px')
      .attr('width', topoWidth - 6)
      .attr('height', networkBarHeight)
      // Start the bar 
      .attr('transform', function(d, i) { return 'translate(2, 0)'; });

    // the label
    network.append('text')
      .attr('x', 10)
      .attr('y', networkBarHeight - (networkBarHeight - textHeight)/2)
      .text(function(d) {
        // Determine label of network based on the data:
        // virtual network or RH network
        return d.ipv4_block || d.name || d.network;
      });
  }


  /**
   * Draw a rectangle representing a tier
   */
  function drawNodes(svg, nodes, networks) {

    // Move nodes to the right to avoid lines crossing the network labels
    var leftMargin = 150;

    var node = svg.selectAll('g.node')
      .data(nodes)
      // Bar and info for each network is contained in a g element.
      // Positioned below network area and spaced apart by `nodeSpacing`
      .enter().append('g')
        .attr('class', 'node')
        .attr('id', function(d, i) { return 'node-' + i; })
        .attr('transform', function(d, i) {
          var x = (i * nodeSpacing) + leftMargin;
          return 'translate(' + x + ', ' + (networkAreaHeight + nodeAreaSpacing) + ')';
        });

    // Box
    node.append('rect')
      .style('fill', tierFill)
      .style('stroke', tierStroke)
      .style('stroke-width', '2px')
      .attr('width', nodeWidth).attr('height', nodeHeight)
      .attr('rx', '8');

    // Name
    node.append('text')
      .attr('x', 14).attr('y', 14)
      .attr('class', 'name')
      .style('alignment-baseline', 'middle')
      .text(function(d, i) {
        if (d.quantity != 1) {
          pluralizeNode(i, d.quantity);
        }
        return d.name;
      });

    // OS family icon
    node.append('image')
        .attr('x', 13)
        .attr('y', 50)
        .attr('class', 'os-family-icon')
        .attr('width', '20px')
        .attr('height', '20px')
        .attr('xlink:href', function(d) { return d.os_family_icon; });
  }


  /**
   * Add 3-d stack of node rectangles and "badge" showing count of servers
   */
  function pluralizeNode(index, quantity) {
    var node = d3.select('#node-' + index);
    var badgeX = nodeWidth - 3;
    var badgeColor = '#335b83';
    var xOffset = 4;
    var yOffset = -2;

    // Draw `quantity - 1` boxes, up to `maxBoxes`. If quantity is null (when a
    // node has no quantity set) draw `maxBoxes`.
    var maxBoxes = 4;
    var boxes = (quantity || maxBoxes + 1) - 1;
    if (boxes > maxBoxes) {
      boxes = maxBoxes;
    }
    var opacity;

    for (var i = 0; i < boxes; i += 1) {
      opacity = 0.7 - (0.15 * i);
      node.insert('rect', 'rect')
        .attr('x', xOffset * (i+1)).attr('y', yOffset * (i+1))
        .attr('width', nodeWidth).attr('height', nodeHeight)
        .attr('rx', '8')
        .style('stroke', tierStroke)
        .style('stroke-opacity', opacity)
        .style('stroke-width', '2px')
        .style('fill', tierFill)
        .style('fill-opacity', opacity);
    }

    if (quantity != 1) {
      // Quantity
      node.append('text')
        .attr('x', badgeX)
        .attr('y', 2)
        .attr('class', 'qty')
        .attr('text-anchor', 'middle')
        .style('fill', '#fff')
        .text(quantity || '?');

      node.insert('circle', 'text')
        .attr("cx", badgeX)
        .attr("cy", -3)
        .attr("r", 13)
        .style('stroke', function(d, i) { return d3.rgb(badgeColor).darker(0.5); })
        .style('fill', badgeColor);

    }
  }


  /*
   * Draw a line from each network to the nodes that use it
   */
  function connectNodes(svg, nodes, networks) {
    var d3nodes = svg.selectAll('g.node');
    var d3nets = svg.selectAll('g.net');
    var netsById = _.indexBy(d3nets[0], function(net) {
      return net.__data__.id;
    });
    var node, nodeX, nodeY, netY;
    var nics;
    var network;
    var translateRE = /(\d+), ?(\d+)/;
    var pos;
    var slot;

    d3nodes.each(function(d) {
      node = this;
      pos = node.attributes.transform.value.match(translateRE);
      nodeX = parseInt(pos[1]) + nodeWidth / 2 - 30;
      nodeY = pos[2];

      // Loop over the node's NIC slots
      nics = _.values(d.nics);
      slot = nics.length;
      while (slot--) {
        if (nics[slot].length == 1) {
          network = netsById[nics[slot][0]];

          netY = network.attributes.transform.value.match(translateRE)[2];
          netY = parseInt(netY) + networkBarHeight;

          svg.append('rect')
            .style('fill', network.firstChild.style.stroke)
            // Each NIC line is 10px apart
            .attr('x', nodeX + slot * (nodeLinkWidth + nodeLinkSpacing))
            .attr('width', nodeLinkWidth)
            .attr('y', netY)
            .attr('height', nodeY - netY);
        } else {
          console.log('More than one option, no line will be drawn!');
        }
      }
    });
  }


  c2.topology = {
    init: init
  };

})(window.c2);

/*
 * Utilities for working with the HTML 5 Page Visibility API
 * https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API
 *
 * Example: see also c2.server module which implements live updates.
 *
 *   c2.visibility.onChange(function(isHidden) {
 *     if (isHidden) {
 *       stopUpdates();
 *     } else {
 *       startUpdates();
 *     }
 *   });
 *
 */

(function (c2, $) {
  'use strict';


  // Do not capture (not sure if there's a difference, but all examples use this).  Making this a
  // variable and using it to register event listeners makes it simple to remove them.
  var useCapture = false;
  var visibilitySupported,
      vendorHidden,
      vendorVisibilityChange;


  /*
   * Register a change hander function if the page visibility API is supported on this platform.
   *
   * The handler is called with a single boolean param that is true if the page is hidden and false
   * otherwise.
   *
   * If the visibility API is not supported, logs a console message and returns false.
   */
  function onChange(eventHandler) {

    if (visibilitySupported === undefined) {
      detectVisibilitySupport();
    }

    if (visibilitySupported === false) {
      console.log('Visibility API is not supported on this platform.');
      return false;
    }

    document.addEventListener(vendorVisibilityChange, function(e) {
      eventHandler(document[vendorHidden]);
    }, useCapture);

  }


  /*
   * Remove the event handler function registered with onChange.
   */
  function offChange(eventHandler) {
    document.removeEventListener(vendorVisibilityChange, eventHandler, useCapture);
  }


  /*
   * Cross-platform support for visibilitychange event.
   * Supports older implementations that used vendor prefixes.
   *
   * Copied almost verbatim from
   * https://blogs.msdn.microsoft.com/ie/2011/07/08/
   *   using-pc-hardware-more-efficiently-in-html5-new-web-performance-apis-part-2/
   */
  function detectVisibilitySupport() {
    // draft standard implementation
    if (typeof document.hidden != "undefined") {
      vendorHidden = "hidden";
      vendorVisibilityChange = "visibilitychange";
      visibilitySupported = true;
      return;
    }

    // IE10 prefixed implementation
    if (typeof document.msHidden != "undefined") {
      vendorHidden = "msHidden";
      vendorVisibilityChange = "msvisibilitychange";
      visibilitySupported = true;
      return;
    }

    // Chrome 13 prefixed implementation
    if (typeof document.webkitHidden != "undefined") {
      vendorHidden = "webkitHidden";
      vendorVisibilityChange = "webkitvisibilitychange";
      visibilitySupported = true;
      return;
    }

    visibilitySupported = false;
  }


  c2.visibility = {
    onChange: onChange,
    offChange: offChange
  };
})(window.c2, window.jQuery);
