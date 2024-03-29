$.fn.dataTableExt.oPagination.extStyle = {
    /*
    * Function: oPagination.extStyle.fnInit
    * Purpose:  Initalise dom elements required for pagination with a list of the pages
    * Returns:  -
    * Inputs:   object:oSettings - dataTables settings object
    *           node:nPaging - the DIV which contains this pagination control
    *           function:fnCallbackDraw - draw function which must be called on update
    */
    "fnInit": function (oSettings, nPaging, fnCallbackDraw) {
        nFirst = $('<span />', { 'class': 'paginate_button first' });
        nPrevious = $('<span />', { 'class': 'paginate_button previous' });
        nNext = $('<span />', { 'class': 'paginate_button next' });
        nLast = $('<span />', { 'class': 'paginate_button last' });
        nPageTxt = $("<span />", { text: 'Page' });
        nPageNumBox = $('<input />', { type: 'text', val: 1, 'class': 'pageinate_input_box' });
        nPageOf = $('<span />', { text: 'of' });
        nTotalPages = $('<span />', { text: parseInt(oSettings.aoData.length / oSettings._iDisplayLength, 10) });
 
        /*   nFirst.appendChild(document.createTextNode(oSettings.oLanguage.oPaginate.sFirst));
        nPrevious.appendChild(document.createTextNode(oSettings.oLanguage.oPaginate.sPrevious));
        nNext.appendChild(document.createTextNode(oSettings.oLanguage.oPaginate.sNext));
        nLast.appendChild(document.createTextNode(oSettings.oLanguage.oPaginate.sLast));
        */
        $(nPaging)
            .append(nFirst)
            .append(nPrevious)
            .append(nPageTxt)
            .append(nPageNumBox)
            .append(nPageOf)
            .append(nTotalPages)
            .append(nNext)
            .append(nLast);
 
        nFirst.click(function () {
            oSettings.oApi._fnPageChange(oSettings, "first");
            fnCallbackDraw(oSettings);
            nPageNumBox.val(parseInt(oSettings._iDisplayEnd / oSettings._iDisplayLength, 10));
        }).bind('selectstart', function () { return false; });
 
        nPrevious.click(function () {
            oSettings.oApi._fnPageChange(oSettings, "previous");
            fnCallbackDraw(oSettings);
            nPageNumBox.val(parseInt(oSettings._iDisplayEnd / oSettings._iDisplayLength, 10));
        }).bind('selectstart', function () { return false; });
 
        nNext.click(function () {
            oSettings.oApi._fnPageChange(oSettings, "next");
            fnCallbackDraw(oSettings);
           nPageNumBox.val(parseInt(oSettings._iDisplayEnd / oSettings._iDisplayLength, 10));
        }).bind('selectstart', function () { return false; });
 
        nLast.click(function () {
            oSettings.oApi._fnPageChange(oSettings, "last");
            fnCallbackDraw(oSettings);
            nPageNumBox.val(parseInt(oSettings._iDisplayEnd / oSettings._iDisplayLength,10 ));
        }).bind('selectstart', function () { return false; });
 
        nPageNumBox.focus(function () {
            $(this).attr("style", "border-color: #D0B39A");
        }).blur(function () {
            $(this).attr("style", "border-color: #C9C9C9");
        }).change(function () {
            var pageValue = parseInt($(this).val(), 10);
            if ((pageValue !== NaN) && pageValue > 0 && pageValue < oSettings.aoData.length) {
                oSettings._iDisplayStart = $(this).val();
                fnCallbackDraw(oSettings);
            }
        });
 
    },
 
    /*
    * Function: oPagination.extStyle.fnUpdate
    * Purpose:  Update the list of page buttons shows
    * Returns:  -
    * Inputs:   object:oSettings - dataTables settings object
    *           function:fnCallbackDraw - draw function which must be called on update
    */
    "fnUpdate": function (oSettings, fnCallbackDraw) {
        if (!oSettings.aanFeatures.p) {
            return;
        }
 
        /* Loop over each instance of the pager */
        var an = oSettings.aanFeatures.p;
        for (var i = 0, iLen = an.length; i < iLen; i++) {
            //var buttons = an[i].getElementsByTagName('span');
            var buttons = $(an[i]).find('span.paginate_button');
            if (oSettings._iDisplayStart === 0) {
                buttons.eq(0).attr("class", "paginate_disabled_first paginate_button");
                buttons.eq(1).attr("class", "paginate_disabled_previous paginate_button");
            }
            else {
                buttons.eq(0).attr("class", "paginate_enabled_first paginate_button");
                buttons.eq(1).attr("class", "paginate_enabled_previous paginate_button");
            }
 
            if (oSettings.fnDisplayEnd() == oSettings.fnRecordsDisplay()) {
                buttons.eq(2).attr("class", "paginate_disabled_next paginate_button");
                buttons.eq(3).attr("class", "paginate_disabled_last paginate_button");
            }
            else {
                buttons.eq(2).attr("class", "paginate_enabled_next paginate_button");
                buttons.eq(3).attr("class", "paginate_enabled_last paginate_button");
            }
        }
    }
};
