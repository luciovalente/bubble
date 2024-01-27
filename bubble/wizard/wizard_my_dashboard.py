from odoo import models, fields, api

class WizardMyDashboard(models.TransientModel):
    _name = 'wizard.bubble.dashboard'
    _description = 'Yorange Dashboard'

    bubble_id = fields.Many2one('bubble', compute="_compute_dashboard")
    role_bubble_ids = fields.Many2many('role.bubble', compute="_compute_dashboard")
    okr_result_ids = fields.Many2many('okr.result', compute="_compute_dashboard")
    bubble_ids = fields.Many2many('bubble', compute="_compute_dashboard")
    user_id = fields.Many2one('res.users', compute="_compute_dashboard")

    
    def _compute_dashboard(self):
        self.ensure_one()
        bubble_ids = self.env['bubble'].search([('member_ids','in',self.env.user.id),('status','=','running')])
        bubble_id = bubble_ids.filtered(lambda x: x.parent_bubble_id.id == False)
        role_bubble_ids = self.env['role.bubble'].search([('user_id', '=', self.env.user.id)])
        okr_result_ids = self.env['okr.result'].search([('user_id', '=', self.env.user.id),('status','=','in_progress')])
        self.write(
            {
               'bubble_id':bubble_id[0].id if bubble_id else False,
               'bubble_ids':bubble_ids.ids,
               'role_bubble_ids':role_bubble_ids.ids,
               'okr_result_ids':okr_result_ids.ids,
               'user_id':self.env.user.id
            }
        )
    
    @api.model
    def show_my_dashboard(self):
        wizard_id = self.sudo().create({})
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Dashboard',
            'res_model': 'wizard.bubble.dashboard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id':wizard_id.id
        }