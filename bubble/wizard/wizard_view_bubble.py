from odoo import models, fields, api

class WizardBubbleView(models.TransientModel):
    _name = 'wizard.bubble.view'
    _description = 'Wizard bubble view'

    bubble_id = fields.Many2one('bubble', string='Bubble', required=True)