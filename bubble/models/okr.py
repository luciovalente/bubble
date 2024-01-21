from odoo import models, fields, api

class Okr(models.Model):
    _name = 'okr'
    _description = 'OKR'

    objective_id = fields.Many2one('objective', string='Objective')
    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    bubble_id = fields.Many2one('bubble', string='Bubble')
    user_id = fields.Many2one('res.users', string='User')
    bubble_role_id = fields.Many2one('bubble.role', string='Role')
    active = fields.Boolean(string='Active', default=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active')
