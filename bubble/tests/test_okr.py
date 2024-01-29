# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestOkr(TransactionCase):

    def setUp(self):
        super(TestOkr, self).setUp()
        self.Okr = self.env['okr']
        self.Objective = self.env['objective']
        self.ResUsers = self.env['res.users']
        self.Bubble = self.env['bubble']
        self.BubbleRole = self.env['bubble.role']

        # Creazione di record necessari per il test
        self.test_user = self.ResUsers.create({'name': 'Test User', 'login': 'test_user'})
        self.test_objective = self.Objective.create({'name': 'Test Objective'})
        self.test_bubble = self.Bubble.create({'name': 'Test Bubble'})
        self.test_bubble_role = self.BubbleRole.create({'name': 'Test Role'})

    def test_check_python_code_constraint(self):
        # Creare un nuovo OKR con codice Python valido
        okr = self.Okr.create({
            'name': 'Valid OKR',
            'code': 'print("Hello World")'
        })
        okr._check_python_code()

        # Tentativo di creare un OKR con codice non sicuro
        with self.assertRaises(ValidationError):
            okr_with_invalid_code = self.Okr.create({
                'name': 'Invalid OKR',
                'code': 'import os'
            })
            okr_with_invalid_code._check_python_code()

    def test_run_action_code(self):
        # Creare un nuovo OKR con codice eseguibile
        okr = self.Okr.create({
            'name': 'Executable OKR',
            'code': 'action = "Test Action"'
        })
        result = okr._run_action_code(None)
        self.assertEqual(result, 'Test Action')

    def test_create_and_update_okr(self):
        # Creare un nuovo OKR
        okr = self.Okr.create({
            'name': 'Test OKR',
            'okr_code': 'OKR-001',
            'objective_id': self.test_objective.id,
            'user_id': self.test_user.id,
            'bubble_id': self.test_bubble.id,
            "type": "bubble",
            'bubble_role_id': self.test_bubble_role.id
        })

        # Verificare che l'OKR sia stato creato correttamente
        self.assertEqual(okr.name, 'Test OKR')
        self.assertEqual(okr.okr_code, 'OKR-001')
        self.assertEqual(okr.objective_id, self.test_objective)
        self.assertEqual(okr.user_id, self.test_user)
        self.assertEqual(okr.bubble_id, self.test_bubble)
        self.assertEqual(okr.bubble_role_id, self.test_bubble_role)
        # Aggiornare l'OKR
        okr.write({'name': 'Updated OKR'})
        self.assertEqual(okr.name, 'Updated OKR')
