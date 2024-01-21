from odoo import models, fields

class OkrResult(models.Model):
    _name = 'okr.result'
    _description = 'OKR Result'

    okr_id = fields.Many2one('okr', string='OKR')
    date = fields.Date(string='Date')
    result = fields.Float(string='Result')
    result_char = fields.Char(string="Result Char")
    evaluation_id = fields.Many2one('okr.evaluation', string='OKR Evaluation')
    user_id = fields.Many2one('res.users',related="evaluation_id.user_id",store=True)

