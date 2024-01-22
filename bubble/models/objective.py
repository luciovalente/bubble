from odoo import models, fields

class Objective(models.Model):
    _name = 'objective'
    _description = 'Objective'

    company_id = fields.Many2one('res.company', string='Company')
    objective_code = fields.Char('Code')
    name = fields.Char(string='Name')