from odoo import models, fields, api

class WizardStartOKREvaluation(models.TransientModel):
    _name = 'wizard.start.okr.evaluation'
    _description = 'Wizard to Start OKR Evaluation'

    bubble_id = fields.Many2one('bubble', string='Bubble', required=True)
    member_ids = fields.Many2many('res.users', string='Members', related='bubble_id.member_ids', readonly=True)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def action_start_okr_valuation(self):
        self.ensure_one()
        OkrResult = self.env['okr.result']
        OkrEvaluation = self.env['okr.evaluation']

        for member in self.member_ids:
            # Creare una nuova valutazione OKR per il membro
            evaluation = OkrEvaluation.create({
                'user_id': member.id,
                'date_from': self.date_from,
                'date_to': self.date_to
            })

            # Trova gli OKR personali, di bolla e di ruolo per il membro
            personal_okrs = self.env['okr'].search([('user_id', '=', member.id)])
            bubble_okrs = self.env['okr'].search([('bubble_id', '=', self.id)])
            role_okrs = self.env['okr'].search([('bubble_id.user_roles_ids.user_id', '=', member.id)])

            # Unisci tutti gli OKR unici
            all_okrs = personal_okrs | bubble_okrs | role_okrs

            # Creare OkrResult per ogni Okr unico
            for okr in all_okrs:
                OkrResult.create({
                    'okr_id': okr.id,
                    'evaluation_id': evaluation.id,
                    'date': fields.Date.today()
                })
