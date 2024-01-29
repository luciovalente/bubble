# -*- coding: utf-8 -*-
from odoo import fields, models


class BubbleRole(models.Model):
    _name = "bubble.role"
    _description = "Bubble Role"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    mandatory = fields.Boolean(string="Mandatory")
    company_id = fields.Many2one("res.company", string="Company")
    user_roles_ids = fields.One2many("role.bubble", "role_id", string="User Roles")
