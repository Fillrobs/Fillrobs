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

function appendEventHandler(node, type, handler, disconnect)
{
  function wrapHandler(event) {
    handler(event || window.event);
  }
  var wrapHandler = handler;
  if (typeof node.addEventListener == "function")
  {
    node.addEventListener(type, wrapHandler, false);
    if (disconnect) return function () {
      node.removeEventListener(type, wrapHandler, false);
    };
  }
  else if (node.attachEvent)
  {
    node.attachEvent("on" + type, wrapHandler);
    if (disconnect) return function () {
      node.detachEvent("on" + type, wrapHandler);
    };
  }
}

appendEventHandler(window, "load", function(){
  //If you're on the login page
  if (window.location.pathname.indexOf("/login/") == 0)
    {        
      const urlParams = new URLSearchParams(window.location.search);
      
      if(urlParams.has("isAuthor"))
      {
        //If the URL has the "isAuthor" parameter (to identify authors) - do nothing
      } else 
      {
        // Otherwise redirect to the homepage
        window.location.href = '/';
      }
    }
})
