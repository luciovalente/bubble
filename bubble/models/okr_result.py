from odoo import models, fields

class OkrResult(models.Model):
    _name = 'okr.result'
    _description = 'OKR Result'

    okr_id = fields.Many2one('okr', string='OKR')
    okr_type = fields.Selection(related="okr_id.type")
    date = fields.Date(string='Date')
    result = fields.Float(string='Result')
    result_char = fields.Char(string="Result Char")
    evaluation_id = fields.Many2one('okr.evaluation', string='OKR Evaluation')
    bubble_id = fields.Many2one('bubble', string='Bubble',related="okr_id.bubble_id")
    with_automation = fields.Boolean(related="okr_id.with_automation")
    bubble_role_id = fields.Many2one('bubble.role', string='Role',related="okr_id.bubble_role_id")
    status = fields.Selection(related="evaluation_id.status",store=True)
    user_id = fields.Many2one('res.users',related="evaluation_id.user_id",store=True)
    owner_id = fields.Many2one('res.users', string='Leader',store=True,related="evaluation_id.owner_id")

