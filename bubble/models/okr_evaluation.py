from odoo import models, fields,api

class OkrEvaluation(models.Model):
    _name = 'okr.evaluation'
    _description = 'OKR Evaluation'

    name = fields.Char(store=True,compute="_compute_name")
    owner_id = fields.Many2one('res.users', string='Owner',store=True,related="bubble_id.owner_id")
    user_id = fields.Many2one('res.users', string='User')
    status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status',default="in_progress")
    okr_result_ids = fields.One2many('okr.result', 'evaluation_id', string='OKR Results')
    notes = fields.Html(string='Notes')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    bubble_id = fields.Many2one('bubble')
    
    @api.depends('user_id','date_from','date_to')
    def _compute_name(self):
        for evaluation in self:
            evaluation.name = evaluation.user_id 

    def action_done(self):
        self.write({'status': 'done'})
