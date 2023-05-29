YAHOO.env.classMap = {"jarmon.RrdQuery": "jarmon", "jarmon": "jarmon", "jarmon.ChartCoordinator": "jarmon", "jarmon.Parallimiter": "jarmon", "jarmon.RrdChooser": "jarmon", "jarmon.RrdQueryRemote": "jarmon", "jarmon.RrdQueryDsProxy": "jarmon", "jarmon.Chart": "jarmon"};

YAHOO.env.resolveClass = function(className) {
    var a=className.split('.'), ns=YAHOO.env.classMap;

    for (var i=0; i<a.length; i=i+1) {
        if (ns[a[i]]) {
            ns = ns[a[i]];
        } else {
            return null;
        }
    }

    return ns;
};
