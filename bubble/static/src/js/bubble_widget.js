odoo.define('bubble_chart_widget.BubbleChartWidget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    var BubbleChartWidget = AbstractField.extend({
        template: 'BubbleChartWidgetTemplate',

        _render: function () {
            var canvas = this.$el.find('#renderCanvas')[0];
            if (!canvas) {
                return;
            }

            // Assumi che 'this.value' contenga i dati della bolla selezionata
            var bubbleData = this.value;
            window.initializeBubbles(canvas, bubbleData);
        },
    });

    fieldRegistry.add('bubble_chart', BubbleChartWidget);

    return BubbleChartWidget;
});