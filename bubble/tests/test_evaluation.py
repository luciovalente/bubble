# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestOkrEvaluation(TransactionCase):

    def setUp(self):
        super(TestOkrEvaluation, self).setUp()
        self.OkrEvaluation = self.env["okr.evaluation"]
        self.ResUsers = self.env["res.users"]
        self.OkrEvaluationType = self.env["okr.evaluation.type"]

        # Creazione di un utente di test
        self.test_user = self.ResUsers.create(
            {"name": "Test User", "login": "test_user"}
        )
        # Creazione di un tipo di valutazione OKR di test
        self.test_evaluation_type = self.OkrEvaluationType.create(
            {"name": "Test Evaluation Type", "code": "result = 0"}
        )

    def test_compute_name(self):
        # Creare una nuova valutazione OKR
        evaluation = self.OkrEvaluation.create(
            {
                "user_id": self.test_user.id,
                "evaluation_type_id": self.test_evaluation_type.id,
            }
        )

        # Verificare che il nome sia stato calcolato correttamente
        self.assertEqual(evaluation.name, self.test_user.name)

    def test_action_done(self):
        # Creare una nuova valutazione OKR
        evaluation = self.OkrEvaluation.create(
            {
                "user_id": self.test_user.id,
                "evaluation_type_id": self.test_evaluation_type.id,
            }
        )

        # Eseguire l'azione per completare la valutazione
        evaluation.action_done()
        self.assertEqual(evaluation.status, "done")

    def test_execute_evaluation(self):
        # Creare una nuova valutazione OKR
        evaluation = self.OkrEvaluation.create(
            {
                "user_id": self.test_user.id,
                "evaluation_type_id": self.test_evaluation_type.id,
            }
        )

        # Eseguire la valutazione
        evaluation.execute_evaluation()

        # Assumendo che il codice di valutazione imposti 'result' a 0
        self.assertEqual(evaluation.result, 0)
