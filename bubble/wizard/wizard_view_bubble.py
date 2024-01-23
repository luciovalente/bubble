from odoo import models, fields, api

class WizardBubbleView(models.TransientModel):
    _name = 'wizard.bubble.view'
    _description = 'Wizard bubble view'

    bubble_id = fields.Many2one('bubble', string='Bubble', required=True)
    legenda = fields.Html(compute="_compute_legenda")

    def _compute_legenda(self):
        types = self.env['bubble.type'].sudo().search([(1,'=',1)])
        result = "<div style='position: absolute; top: 10px; right: 10px; display: block;display:none;'>"
        for t in types:
            result += '<span style="with:10px;border:1px solid %s;background-color:%s" />%s</span>'%(t.css_color,t.css_color,t.name)
        result += "</div>"
        for wizard in self:
            wizard.legenda = result