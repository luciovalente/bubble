# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestObjective(TransactionCase):

    def setUp(self):
        super(TestObjective, self).setUp()
        self.Objective = self.env["objective"]
        self.OKR = self.env["okr"]
        self.ResCompany = self.env["res.company"]

        # Creare una compagnia di test
        self.test_company = self.ResCompany.create({"name": "Test Company"})
        # Creare un obiettivo di test (OKR) se necessario
        self.test_okr = self.OKR.create({"name": "Test OKR"})

    def test_create_and_update_objective(self):
        # Creare un nuovo obiettivo
        objective = self.Objective.create(
            {
                "name": "Test Objective",
                "company_id": self.test_company.id,
                "objective_code": "OBJ-001",
            }
        )

        # Verificare che l'obiettivo sia stato creato correttamente
        self.assertEqual(objective.name, "Test Objective")
        self.assertEqual(objective.objective_code, "OBJ-001")

        # Aggiornare l'obiettivo
        objective.write({"name": "Updated Objective"})
        self.assertEqual(objective.name, "Updated Objective")

    def test_compute_parent_objective(self):
        # Creare un obiettivo e un OKR collegati
        parent_objective = self.Objective.create(
            {"name": "Parent Objective", "company_id": self.test_company.id}
        )
        child_okr = self.OKR.create(
            {"name": "Child OKR", "objective_id": parent_objective.id}
        )
        child_objective = self.Objective.create(
            {"name": "Child Objective", "parent_okr_id": child_okr.id}
        )

        # Verificare che il campo parent_objective_id sia calcolato correttamente
        self.assertEqual(child_objective.parent_objective_id, parent_objective)
