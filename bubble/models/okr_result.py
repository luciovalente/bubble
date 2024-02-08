# -*- coding: utf-8 -*-
from odoo import fields, models


class OkrResult(models.Model):
    _name = "okr.result"
    _description = "OKR Result"

    active = fields.Boolean(default=True)
    objective_id = fields.Many2one(
        "objective", related="okr_id.objective_id", store=True
    )
    okr_id = fields.Many2one("okr", string="OKR", ondelete="restrict")
    okr_type = fields.Selection(related="okr_id.type")
    okr_description = fields.Text(related="okr_id.description")
    okr_type = fields.Selection(related="okr_id.type")
    result = fields.Float(string="Result")
    result_char = fields.Char(string="Result Char")
    evaluation_id = fields.Many2one(
        "okr.evaluation", string="OKR Evaluation", ondelete="restrict"
    )
    bubble_id = fields.Many2one("bubble", string="Bubble", related="okr_id.bubble_id")
    with_automation = fields.Boolean(related="okr_id.with_automation")
    bubble_role_id = fields.Many2one(
        "bubble.role", string="Role", related="okr_id.bubble_role_id"
    )
    date_from = fields.Date(related="evaluation_id.date_from")
    date_to = fields.Date(related="evaluation_id.date_to")
    status = fields.Selection(related="evaluation_id.status", store=True)
    user_id = fields.Many2one("res.users", related="evaluation_id.user_id", store=True)
    owner_id = fields.Many2one(
        "res.users", string="Leader", store=True, related="evaluation_id.owner_id"
    )
    kpi_result = fields.Text()

    def _run_action_code(self):
        for okr_result in self.filtered(lambda x: x.okr_id.with_automation):
            eval_context = self.okr_id._get_eval_context(okr_result)
            safe_eval(
                self.okr_id.code.strip(), eval_context, mode="exec", nocopy=True
            )  # nocopy allows to return 'action'
