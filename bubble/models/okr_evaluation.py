from odoo import models, fields,api

class OkrEvaluation(models.Model):
    _name = 'okr.evaluation'
    _description = 'OKR Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(store=True,compute="_compute_name")
    owner_id = fields.Many2one('res.users', string='Leader',store=True,related="bubble_id.owner_id")
    evaluation_type_id = fields.Many2one('okr.evaluation.type',required=True)
    with_automation = fields.Boolean(related="evaluation_type_id.with_automation")
    evaluation_description = fields.Text(related="evaluation_type_id.description")

    user_id = fields.Many2one('res.users', string='User')
    status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status',default="in_progress",tracking=True)
    okr_result_ids = fields.One2many('okr.result', 'evaluation_id', string='OKR Results')
    notes = fields.Html(string='Notes')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    bubble_id = fields.Many2one('bubble')
    result = fields.Float(string='Result',tracking=True)
    result_char = fields.Char(string="Result Char")
    
    @api.depends('user_id','date_from','date_to')
    def _compute_name(self):
        for evaluation in self:
            evaluation.name = evaluation.user_id.name 

    def action_done(self):
        self.write({'status': 'done'})

    def execute_evaluation(self):
        for evaluation in self:
            return evaluation.evaluation_type_id._run_action_code(evaluation)
