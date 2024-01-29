# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestBubbleRole(TransactionCase):

    def setUp(self):
        super(TestBubbleRole, self).setUp()
        self.BubbleRole = self.env["bubble.role"]
        self.ResCompany = self.env["res.company"]
        
        # Creare un record di una compagnia di test se necessario
        self.test_company = self.ResCompany.create({"name": "Test Company"})

    

    def test_create_bubble_role(self):
        # Creare un nuovo ruolo di bolla
        bubble_role = self.BubbleRole.create(
            {
                "name": "Test Role",
                "description": "This is a test role.",
                "company_id": self.test_company.id,
            }
        )

        # Verificare che il ruolo della bolla sia stato creato correttamente
        self.assertEqual(bubble_role.name, "Test Role")
        self.assertEqual(bubble_role.company_id, self.test_company)

    def test_update_bubble_role(self):
        # Creare un nuovo ruolo di bolla
        bubble_role = self.BubbleRole.create(
            {
                "name": "Test Role",
                "description": "This is a test role.",
                "company_id": self.test_company.id,
            }
        )

        # Aggiornare il ruolo della bolla
        bubble_role.write(
            {
                "name": "Updated Test Role",
            }
        )

        # Verificare che il ruolo della bolla sia stato aggiornato correttamente
        self.assertEqual(bubble_role.name, "Updated Test Role")

    def test_relation_with_user_roles(self):
        # Creare un ruolo di bolla e un ruolo utente collegato
        bubble_role = self.BubbleRole.create(
            {
                "name": "Test Role",
                "description": "This is a test role.",
                "company_id": self.test_company.id,
            }
        )

        user_role = self.env["role.bubble"].create(
            {"role_id": bubble_role.id}
        )

        # Verificare che la relazione tra ruolo della bolla e ruolo utente sia stata stabilita correttamente
        self.assertIn(user_role, bubble_role.user_roles_ids)
