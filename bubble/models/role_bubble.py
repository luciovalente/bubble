# -*- coding: utf-8 -*-
from odoo import fields, models


class RoleBubble(models.Model):
    _name = "role.bubble"
    _description = "Role Buble"

    active = fields.Boolean(default=True)
    bubble_id = fields.Many2one("bubble", string="Buble")
    role_id = fields.Many2one("bubble.role", string="Role")
    user_id = fields.Many2one("res.users", string="User")
    role_description = fields.Text(related="role_id.description")
