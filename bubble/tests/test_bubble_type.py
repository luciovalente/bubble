# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBubbleType(TransactionCase):

    def setUp(self):
        super(TestBubbleType, self).setUp()
        self.BubbleType = self.env["bubble.type"]
        self.ResCompany = self.env["res.company"]

        # Creazione di una compagnia di test se necessario
        self.test_company = self.ResCompany.create({"name": "Test Company"})

    def test_create_and_update_bubble_type(self):
        # Creare un nuovo tipo di bolla
        bubble_type = self.BubbleType.create(
            {
                "name": "Test Bubble Type",
                "description": "<p>This is a test bubble type.</p>",
                "company_id": self.test_company.id,
                "css_color": "#00ff00",
            }
        )

        # Verificare che il tipo di bolla sia stato creato correttamente
        self.assertEqual(bubble_type.name, "Test Bubble Type")
        self.assertEqual(bubble_type.css_color, "#00ff00")

        # Aggiornare il tipo di bolla
        bubble_type.write({"css_color": "#0000ff"})
        self.assertEqual(bubble_type.css_color, "#0000ff")

    def test_check_python_code_constraint(self):
        # Creare un nuovo tipo di bolla con codice valido
        bubble_type = self.BubbleType.create(
            {"name": "Valid Code", "code": 'print("Hello world")'}
        )
        bubble_type._check_python_code()

        # Tentativo di creare un tipo di bolla con codice non sicuro
        with self.assertRaises(ValidationError):
            bubble_type_with_invalid_code = self.BubbleType.create(
                {"name": "Invalid Code", "code": "import os"}
            )
            bubble_type_with_invalid_code._check_python_code()

    def test_run_action_code(self):
        # Creare un nuovo tipo di bolla con codice eseguibile
        bubble_type = self.BubbleType.create(
            {"name": "Executable Code", "code": 'action = "Test Action"'}
        )
        result = bubble_type._run_action_code()
        self.assertEqual(result, "Test Action")
