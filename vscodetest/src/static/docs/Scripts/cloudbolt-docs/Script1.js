// This script file has been created automatically per your request.
//
// The following pages can help you get started with JavaScript:
// * JavaScript Tutorial (http://w3schools.com/js/default.asp)
// * JavaScript and HTML DOM Reference (http://w3schools.com/jsref/default.asp) 
// * JavaScript Examples (http://w3schools.com/js/js_examples.asp)

function initFooter()
{      
  var lnkFeedback = document.getElementById('lnkFeedback');
  if (lnkFeedback)
  { // Add topic URL to the "Send feedback" link
    var href = "";
    try
    {
      var topLevelParent = window.top;
      lnkFeedback.href += '?Subject=Feedback on ' 
        + encodeURIComponent(topLevelParent.window.location);
    }
    catch(e)
    {
    }
  }
}