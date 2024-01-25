from odoo import models, fields, api

class Objective(models.Model):
    _name = 'objective'
    _description = 'Objective'

    company_id = fields.Many2one('res.company', string='Company')
    objective_code = fields.Char('Code')
    name = fields.Char(string='Name')
    bubble_id = fields.Many2one('bubble', string='Bubble')
    parent_okr_id = fields.Many2one('okr',string="Parent Key Result")
    parent_objective_id = fields.Many2one('objective',string="Parent Objective",store=True,compute="_compute_parent_objective")
    child_okr_ids = fields.One2many('okr','objective_id')
    child_objective_ids = fields.One2many('objective','parent_objective_id')

    @api.depends('parent_okr_id')
    def _compute_parent_objective(self):
        for obj in self:
            if obj.parent_okr_id:
                obj.parent_objective_id = obj.parent_okr_id.objective_id.id
