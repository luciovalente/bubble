# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestOkrResult(TransactionCase):

    def setUp(self):
        super(TestOkrResult, self).setUp()
        self.OkrResult = self.env["okr.result"]
        self.Objective = self.env["objective"]
        self.Okr = self.env["okr"]
        self.OkrEvaluation = self.env["okr.evaluation"]
        self.ResUsers = self.env["res.users"]
        self.Bubble = self.env["bubble"]
        self.BubbleRole = self.env["bubble.role"]

        # Creazione di record necessari per il test
        self.test_user = self.ResUsers.create(
            {"name": "Test User", "login": "test_user"}
        )
        self.test_evaluation_type = self.OkrEvaluationType.create(
            {"name": "Test Evaluation Type", "code": "result = 0"}
        )
        self.test_evaluation = self.OkrEvaluation.create(
            {
                "user_id": self.test_user.id,
                "evaluation_type_id": self.test_evaluation_type.id,
            }
        )
        self.test_objective = self.Objective.create({"name": "Test Objective"})
        self.test_bubble = self.Bubble.create({"name": "Test Bubble"})
        self.test_bubble_role = self.BubbleRole.create({"name": "Test Role"})
        self.test_okr = self.Okr.create(
            {
                "objective_id": self.test_objective.id,
                "description": "Test OKR",
                "type": "normal",
                "bubble_id": self.test_bubble.id,
                "bubble_role_id": self.test_bubble_role.id,
                "with_automation": True,
            }
        )

    def test_create_and_update_okr_result(self):
        # Creare un nuovo risultato OKR
        okr_result = self.OkrResult.create(
            {
                "okr_id": self.test_okr.id,
                "evaluation_id": self.test_evaluation.id,
                "result": 0.5,
            }
        )

        # Verificare che i campi correlati siano stati popolati correttamente
        self.assertEqual(okr_result.objective_id, self.test_objective)
        self.assertEqual(okr_result.okr_description, self.test_okr.description)
        self.assertEqual(okr_result.okr_type, self.test_okr.type)
        self.assertEqual(okr_result.bubble_id, self.test_bubble)
        self.assertTrue(okr_result.with_automation)
        self.assertEqual(okr_result.bubble_role_id, self.test_bubble_role)
        self.assertEqual(okr_result.status, self.test_evaluation.status)
        self.assertEqual(okr_result.user_id, self.test_user)

        # Aggiornare il risultato OKR
        okr_result.write({"result": 0.75})
        self.assertEqual(okr_result.result, 0.75)
