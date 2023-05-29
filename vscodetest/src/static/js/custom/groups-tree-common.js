$(function() {
    let indentPx = 20;
    $("#groupTree").treeTable({
        initialState: "expanded",// "collapsed" was preventing node names from being clickable
        clickableNodeNames: false,
        indent: indentPx
    });

    // enable container names to link to group details view
    // This only works on an *expanded* treeTable
    $("a.expander a").each(function(){
        $(this).addClass('node').parent().parent().append($(this));
    });

    // move icon
    $("#groupTree tr, a.expander").hover(
      function () {
        $(this).addClass('hover');
      },
      function () {
        $(this).removeClass('hover');
      }
    );

    // resize name column for longer names
    let elemMaxWidth = 0;
    let colWidth = $("td.first").first().outerWidth();
    // get the size of the longest name, taking indentation into account
    $("#groupTree td.first a").each(function () {
      let thisWidth = $(this).outerWidth() + 15;
      let classes = $(this).parents("tr").attr("class").trim().split(" ");
      let depth = 1;
      for (let i = 0; i< classes.length; i++) {
        if (classes[i].startsWith("depth-")) {
          try {
            depth = parseInt(classes[i].slice(6));
          } catch (err) {
            continue;
          }
          break;
        }
      }
      thisWidth += indentPx * depth;
      if (thisWidth > elemMaxWidth) {
        elemMaxWidth = thisWidth;
      }
    });
    // update the groupTree styling on the page with new column size if it is bigger than expected
    if (elemMaxWidth > colWidth) {
      // don't let the column get too big
      if (elemMaxWidth > 450) elemMaxWidth = 450;
      let styleTags = document.getElementsByTagName("style");
      let lastStyle = styleTags[styleTags.length - 1];
      let newCss = `
#groupTreeContainer {margin-left: ${elemMaxWidth}px;}
#groupTree th.name,
#groupTree td.first {
  min-width: ${elemMaxWidth}px;
  max-width: ${elemMaxWidth}px;
  margin-left: -${elemMaxWidth}px;
}`;
      lastStyle.innerHTML += newCss;
    }
});
