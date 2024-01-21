from odoo import models, fields

class OkrEvaluation(models.Model):
    _name = 'okr.evaluation'
    _description = 'OKR Evaluation'

    user_id = fields.Many2one('res.users', string='User')
    status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status',default="in_progress")
    okr_result_ids = fields.One2many('okr.result', 'evaluation_id', string='OKR Results')
    notes = fields.Html(string='Notes')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def action_done(self):
        self.write({'status': 'done'})
