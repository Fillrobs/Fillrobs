/* Copyright (c) Richard Wall
 * See LICENSE for details.
 *
 * Some example recipes for Collectd RRD data - you *will* need to modify this
 * based on the RRD data available on your system.
 */

if(typeof(jarmon) === 'undefined') {
    var jarmon = {};
}

jarmon.TAB_RECIPES_STANDARD = [
    ['System',      ['cpu', 'memory','load']],
    ['Network',     ['interface']]
];

jarmon.CHART_RECIPES_COLLECTD = {
    'cpu': {
        title: 'CPU Usage',
        data: [
            ['data/cpu.rrd', 'memory', 'cpu12', '%'],
        ],
        options: jQuery.extend(true, {}, jarmon.Chart.BASE_OPTIONS,
                                         jarmon.Chart.STACKED_OPTIONS)
    },

    'memory': {
        title: 'Memory',
        data: [
            ['data/memory/memory-buffered.rrd', 0, 'Buffered', 'B'],
        ],
        options: jQuery.extend(true, {}, jarmon.Chart.BASE_OPTIONS,
                                         jarmon.Chart.STACKED_OPTIONS)
    },

    'load': {
        title: 'Load Average',
        data: [
            ['data/load/load.rrd', 'shortterm', 'Short Term', ''],
        ],
        options: jQuery.extend(true, {}, jarmon.Chart.BASE_OPTIONS)
    },

    'interface': {
        title: 'Wlan0 Throughput',
        data: [
            ['data/interface/if_octets-wlan0.rrd', 'tx', 'Transmit', 'bit/s', function (v) { return v*8; }],
        ],
        options: jQuery.extend(true, {}, jarmon.Chart.BASE_OPTIONS)
    }
};
