odoo.define('bubble_chart_widget.BubbleChartWidget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var ajax = require('web.ajax');

    
    var BubbleChartWidget = AbstractField.extend({
        template: 'BubbleChartWidgetTemplate',

        _render: function () {
            var self = this;
            var bubbleId = this.recordData.id; // Assumi che 'id' sia il campo che contiene l'ID della bolla

            ajax.jsonRpc("/get_bubble_data", "call", {bubble_id: bubbleId})
                .then(function (bubbleData) {
                    var canvas = self.$el.find('#renderCanvas')[0];
                    if (canvas) {
                        window.initializeBubbles(canvas, bubbleData);
                    }
                })
                .fail(function (error) {
                    console.error("Error while fetching bubble data:", error);
                });
        },
    });

    fieldRegistry.add('bubble_chart', BubbleChartWidget);

    return BubbleChartWidget;
});