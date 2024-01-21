import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.float_utils import float_compare

import base64
from collections import defaultdict
import functools
import logging

from pytz import timezone

class BubbleType(models.Model):
    _name = 'bubble.type'
    _description = 'Bubble Type'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company')
    role_ids = fields.Many2many('bubble.role', string='Roles')
    with_automation = fields.Boolean()
    
    code = fields.Text(string='Code')
    bubble_ids = fields.One2many('bubble','bubble_type_id')


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
            'bubble_ids': self.bubble_ids
        }


    
    def _run_action_code(self):
        eval_context = self._get_eval_context()
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)  # nocopy allows to return 'action'
        return eval_context.get('action')
