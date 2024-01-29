# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestOkrEvaluationType(TransactionCase):

    def setUp(self):
        super(TestOkrEvaluationType, self).setUp()
        self.OkrEvaluationType = self.env["okr.evaluation.type"]

    def test_check_python_code_constraint(self):
        # Creare un nuovo tipo di valutazione OKR con codice valido
        okr_evaluation_type = self.OkrEvaluationType.create(
            {"name": "Valid Code", "code": 'print("Hello world")'}
        )
        okr_evaluation_type._check_python_code()

        # Tentativo di creare un tipo di valutazione OKR con codice non sicuro
        with self.assertRaises(ValidationError):
            okr_evaluation_type_with_invalid_code = self.OkrEvaluationType.create(
                {"name": "Invalid Code", "code": "import os"}
            )
            okr_evaluation_type_with_invalid_code._check_python_code()

    def test_run_action_code(self):
        # Creare un nuovo tipo di valutazione OKR con codice eseguibile
        okr_evaluation_type = self.OkrEvaluationType.create(
            {"name": "Executable Code", "code": 'action = "Test Action"'}
        )
        result = okr_evaluation_type._run_action_code(None)
        self.assertEqual(result, "Test Action")

    def test_get_model_and_fields(self):
        okr_evaluation_type = self.OkrEvaluationType.create({"name": "Test"})
        result = okr_evaluation_type.get_model_and_fields()
        # Verificare che il risultato sia una stringa formattata come atteso
        self.assertIn("Model;Field;Type;Relation", result)

    def test_get_library_and_variable(self):
        okr_evaluation_type = self.OkrEvaluationType.create({"name": "Test"})
        result = okr_evaluation_type.get_library_and_variable()
        # Verificare che il risultato includa le variabili di contesto
        self.assertIn("uid", result)
        self.assertIn("user", result)
