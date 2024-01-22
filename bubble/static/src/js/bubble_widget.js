odoo.define('bubble_chart_widget.BubbleChartWidget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var ajax = require('web.ajax');


    var BubbleChartWidget = AbstractField.extend({
        template: 'BubbleChartWidgetTemplate',

        _render: function () {
            var self = this;
            var bubbleId = this.res_id;

            ajax.jsonRpc("/get_bubble_data", "call", {bubble_id: bubbleId})
                .then(function (bubbleData) {
                    var canvas = self.$el.find('#renderCanvas')[0];
                    if (canvas) {
                        window.initializeBubbles(canvas, bubbleData);
                    }
                })
                
        },
    });

    fieldRegistry.add('bubble_chart', BubbleChartWidget);

    return BubbleChartWidget;
});