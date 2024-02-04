# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WizardMyDashboard(models.TransientModel):
    _name = "wizard.bubble.dashboard"
    _description = "Yorange Dashboard"

    bubble_id = fields.Many2one("bubble", compute="_compute_dashboard")
    leader_bubble_ids = fields.Many2many(
        "bubble", compute="_compute_dashboard", string="Leader Bubbles"
    )
    leader_bubble_count = fields.Integer(compute="_compute_dashboard")
    role_bubble_ids = fields.Many2many("role.bubble", compute="_compute_dashboard")
    role_bubble_count = fields.Integer(compute="_compute_dashboard")
    okr_result_ids = fields.Many2many("okr.result", compute="_compute_dashboard")
    okr_result_count = fields.Integer(compute="_compute_dashboard")
    bubble_ids = fields.Many2many(
        "bubble", compute="_compute_dashboard", string="Bubbles"
    )
    user_id = fields.Many2one("res.users", compute="_compute_dashboard")
    name = fields.Char(compute="_compute_dashboard")

    def _compute_dashboard(self):
        self.ensure_one()

        def find_principal_bubble(bubble):
            if bubble.parent_bubble_id:
                return find_principal_bubble(bubble.parent_bubble_id)
            return bubble

        bubble_ids = self.env["bubble"].search(
            [("member_ids", "in", self.env.user.id), ("status", "=", "running")]
        )
        leader_bubble_ids = self.env["bubble"].search(
            [("owner_id", "=", self.env.user.id), ("status", "=", "running")]
        )
        bubble_id = find_principal_bubble(bubble_ids[0]) if bubble_ids else False
        role_bubble_ids = self.env["role.bubble"].search(
            [("user_id", "=", self.env.user.id)]
        )
        okr_result_ids = self.env["okr.result"].search(
            [("user_id", "=", self.env.user.id), ("status", "=", "in_progress")]
        )
        self.sudo().write(
            {
                "bubble_id": bubble_id[0].id if bubble_id else False,
                "bubble_ids": bubble_ids.ids,
                "role_bubble_ids": role_bubble_ids.ids,
                "role_bubble_count":len(role_bubble_ids),
                "okr_result_ids": okr_result_ids.ids,
                "okr_result_count":len(okr_result_ids),
                "user_id": self.env.user.id,
                "leader_bubble_ids":leader_bubble_ids.ids,
                "leader_bubble_count":len(leader_bubble_ids),
                "name": "My Dashboard",
            }
        )

    @api.model
    def show_my_dashboard(self):
        wizard_id = self.sudo().create({})
        return {
            "type": "ir.actions.act_window",
            "name": "My Dashboard",
            "res_model": "wizard.bubble.dashboard",
            "view_type": "form",
            "view_mode": "form",
            "res_id": wizard_id.id,
        }
