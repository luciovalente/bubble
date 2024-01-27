from odoo import models, fields

class RoleBubble(models.Model):
    _name = 'role.bubble'
    _description = 'Role Buble'

    active = fields.Boolean()
    bubble_id = fields.Many2one('bubble', string='Buble')
    role_id = fields.Many2one('bubble.role', string='Role')
    user_id = fields.Many2one('res.users', string='User')
