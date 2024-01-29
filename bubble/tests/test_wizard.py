# -*- coding: utf-8 -*-
from datetime import date

from odoo.tests.common import TransactionCase


class TestWizardStartOKREvaluation(TransactionCase):

    def setUp(self):
        super(TestWizardStartOKREvaluation, self).setUp()
        self.WizardStartOKREvaluation = self.env["wizard.start.okr.evaluation"]
        self.OkrEvaluation = self.env["okr.evaluation"]
        self.Okr = self.env["okr"]
        self.ResUsers = self.env["res.users"]
        self.Bubble = self.env["bubble"]
        self.OkrEvaluationType = self.env["okr.evaluation.type"]
        self.RoleBubble = self.env["role.bubble"]

        # Creare record di base necessari per il test
        self.test_user = self.ResUsers.create(
            {"name": "Test User", "login": "test_user"}
        )
        self.test_owner = self.ResUsers.create(
            {"name": "Test Owner", "login": "test_owner"}
        )
        self.test_bubble = self.Bubble.create(
            {"name": "Test Bubble", "owner_id": self.test_owner.id}
        )
        self.test_evaluation_type = self.OkrEvaluationType.create(
            {"name": "Test Evaluation Type"}
        )
        self.test_okr = self.Okr.create(
            {
                "name": "Test OKR",
                "user_id": self.test_user.id,
                "bubble_id": self.test_bubble.id,
                "status": "active",
            }
        )

    def test_action_start_okr_valuation(self):
        # Creare il wizard e impostare i dati necessari
        wizard = self.WizardStartOKREvaluation.create(
            {
                "bubble_id": self.test_bubble.id,
                "evaluation_type_id": self.test_evaluation_type.id,
                "member_ids": [(6, 0, [self.test_user.id])],
                "date_from": date.today(),
                "date_to": date.today(),
            }
        )

        # Eseguire l'azione del wizard
        wizard.action_start_okr_valuation()

        # Verificare che sia stata creata una valutazione OKR
        evaluation = self.OkrEvaluation.search([(1, "=", 1)])
        self.assertEquals(len(evaluation), 1)

        # Verificare che siano stati creati i risultati OKR
        okr_results = self.env["okr.result"].search(
            [("evaluation_id", "=", evaluation.id)]
        )
        self.assertTrue(okr_results)
