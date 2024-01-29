# -*- coding: utf-8 -*-
from odoo import api, fields, models


class WizardStartOKREvaluation(models.TransientModel):
    _name = "wizard.start.okr.evaluation"
    _description = "Wizard to Start OKR Evaluation"

    bubble_id = fields.Many2one("bubble", string="Bubble", required=True)
    evaluation_type_id = fields.Many2one("okr.evaluation.type")
    member_ids = fields.Many2many("res.users", string="Members")
    owner_id = fields.Many2one("res.users", string="Leader", store=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")

    def action_start_okr_valuation(self):
        self.ensure_one()
        OkrResult = self.env["okr.result"]
        OkrEvaluation = self.env["okr.evaluation"]

        for member in self.member_ids:
            # Creare una nuova valutazione OKR per il membro
            evaluation = OkrEvaluation.create(
                {
                    "user_id": member.id,
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                    "evaluation_type_id": self.evaluation_type_id.id,
                    "bubble_id": self.bubble_id.id,
                }
            )

            # Trova gli OKR personali, di bolla e di ruolo per il membro
            personal_okrs = self.env["okr"].search(
                [("user_id", "=", member.id), ("status", "=", "active")]
            )
            bubble_okrs = self.env["okr"].search(
                [("bubble_id", "=", self.bubble_id.id), ("status", "=", "active")]
            )
            user_role_ids = self.env["role.bubble"].search(
                [("user_id", "=", member.id), ("bubble_id", "=", self.bubble_id.id)]
            )
            role_okrs = self.env["okr"].search(
                [("bubble_role_id", "in", user_role_ids.ids), ("status", "=", "active")]
            )

            # Unisci tutti gli OKR unici
            all_okrs = personal_okrs | bubble_okrs | role_okrs

            # Creare OkrResult per ogni Okr unico
            for okr in all_okrs.filtered(lambda x: x.status == "active"):
                OkrResult.create(
                    {
                        "okr_id": okr.id,
                        "evaluation_id": evaluation.id,
                        "date": fields.Date.today(),
                    }
                )
