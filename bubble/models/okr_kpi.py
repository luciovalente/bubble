# -*- coding: utf-8 -*-
import base64
import json

import requests
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval, test_python_expr
from pytz import timezone


class OkrKpi(models.Model):
    _name = "okr.kpi"
    _description = "Okr Kpi"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    code = fields.Text(string="Code")

    @api.constrains("code")
    def _check_python_code(self):
        for action in self.sudo().filtered("code"):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.model
    def _get_eval_context(self, okr_result=None):
        def log(message, level="info"):
            with self.pool.cursor() as cr:
                cr.execute(
                    """
                    INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                    VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        self.env.uid,
                        "server",
                        self._cr.dbname,
                        __name__,
                        level,
                        message,
                        "action",
                        self.id,
                        self.name,
                    ),
                )

        """ evaluation context to pass to safe_eval """
        return {
            "uid": self._uid,
            "user": self.env.user,
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": timezone,
            "float_compare": float_compare,
            "b64encode": base64.b64encode,
            "b64decode": base64.b64decode,
            "env": self.env,
            "request": requests.request,
            "json_dumps": json.dumps,
            "json_load": json.load,
            "log": log,
            "okr_result": okr_result,
        }

    def _run_action_code(self, okr_result):
        eval_context = self._get_eval_context(okr_result)
        safe_eval(
            self.code.strip(), eval_context, mode="exec", nocopy=True
        )  # nocopy allows to return 'action'
        return eval_context.get("result")
