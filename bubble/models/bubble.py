import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.float_utils import float_compare

class Bubble(models.Model):
    _name = 'bubble'
    _description = 'Bubble'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    purpose = fields.Html(string='Purpose')
    bubble_type_id = fields.Many2one('bubble.type', string='Bubble Type')
    parent_bubble_id = fields.Many2one('bubble', string='Parent Bubble')
    status = fields.Selection([
        ('freeze', 'Freeze'),
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('dismiss', 'Dismiss'),
        ('deleted', 'Deleted')
    ], string='Status',default='draft')
    close_date = fields.Datetime(string='Close Date')
    link = fields.Char(string='Link')
    with_okr_valuation = fields.Boolean(string='With OKR Valuation', default=False)

    company_id = fields.Many2one('res.company', string='Company')
    owner_id = fields.Many2one('res.users', string='Owner')
    member_ids = fields.Many2many('res.users', string='Members')
    user_roles_ids = fields.One2many('role.bubble', 'bubble_id', string='User Roles')
    with_automation = fields.Boolean(groups='bubble.group_bubble_administrator')
    model_id = fields.Many2one('ir.model', string='Model')
    res_ids = fields.Char('Res Ids')
    code = fields.Text(string='Code',groups='bubble.group_bubble_administrator')
    linked_object_count = fields.Integer(string='Linked Objects Count', compute='_compute_linked_objects')
    linked_object_name = fields.Char(string='Linked Object Name', compute='_compute_linked_objects')
    okr_evaluation_ids = fields.One2many('okr.evaluation','bubble_id')
    okr_evaluation_count = fields.Integer(string='OKR Evaluation Count', compute='_compute_okr_evaluation_count')

    @api.depends('okr_evaluation_ids')
    def _compute_okr_evaluation_count(self):
        for record in self:
            record.okr_evaluation_count = len(record.okr_evaluation_ids.filtered(lambda x:x.status=='in_progress'))
            
    @api.depends('model_id', 'res_ids')
    def _compute_linked_objects(self):
        for record in self.sudo():
            if record.model_id and record.res_ids:
                model = self.env[record.model_id.model]
                ids_list = [int(rec_id) for rec_id in record.res_ids.split(',') if rec_id.isdigit()]
                record.linked_object_count = len(ids_list)
                # Prendi i nomi dei primi N record (ad esempio i primi 5)
                records = model.browse(ids_list[:5])
                record.linked_object_name = record.model_id.name
            else:
                record.linked_object_count = 0
                record.linked_object_name = ''

    def action_freeze(self):
        self.write({'status': 'freeze'})

    def action_dismiss(self):
        self.write({'status': 'dismiss','close_date':fields.Datetime.now()})

    def action_run(self):
        self.write({'status': 'running'})

    def action_draft(self):
        self.write({'status': 'draft'})

    def action_delete(self):
        self.write({'status': 'deleted'})


    @api.model
    def _get_eval_context(self, action=None):
        """ evaluation context to pass to safe_eval """
        return {
            'uid': self._uid,
            'user': self.env.user,
            'time': tools.safe_eval.time,
            'datetime': tools.safe_eval.datetime,
            'dateutil': tools.safe_eval.dateutil,
            'timezone': timezone,
            'float_compare': float_compare,
            'b64encode': base64.b64encode,
            'b64decode': base64.b64decode,
            'bubble_id': self,
            'env':self.env
        }


    
    def _run_action_code(self):
        eval_context = self._get_eval_context()
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)  # nocopy allows to return 'action'
        return eval_context.get('action')

    def action_open_okr_evaluation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Evaluation',
            'res_model': 'okr.evaluation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.okr_evaluation_ids.filtered(lambda x:x.status=='in_progress'))],
        }
    
    def action_view_linked_records(self):
        self.ensure_one()
        record_ids = [int(rec_id) for rec_id in self.res_ids.split(',') if rec_id.isdigit()]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linked Records',
            'res_model': self.model_id.model,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', record_ids)],
        }
    

    def action_start_okr_valuation(self):
        self.ensure_one()
        # Crea un record del wizard e pre-popola i campi
        wizard = self.env['wizard.start.okr.evaluation'].create({
            'bubble_id': self.id,
            'member_ids':self.member_ids.ids
            # Imposta eventuali altri valori di default per il wizard
        })
        # Restituisce un'azione per aprire il wizard
        return {
            'name': 'Start OKR Evaluation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.start.okr.evaluation',
            'res_id': wizard.id,
            'target': 'new',
        }