# -*- coding: utf-8 -*-
import base64
import json

import requests
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval, test_python_expr
from pytz import timezone
from werkzeug.urls import url_join


class Bubble(models.Model):
    _name = "bubble"
    _description = "Bubble"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _order = "sequence"

    active = fields.Boolean(default=True)
    sequence = fields.Integer("Sequence")
    name = fields.Char(string="Name")
    purpose = fields.Text(string="Purpose")
    description = fields.Html(string="Description")
    bubble_type_id = fields.Many2one(
        "bubble.type", string="Bubble Type", ondelete="restrict"
    )
    parent_bubble_id = fields.Many2one(
        "bubble", string="Parent Bubble", ondelete="restrict"
    )
    child_bubble_ids = fields.One2many("bubble", "parent_bubble_id")
    status = fields.Selection(
        [
            ("freeze", "Freeze"),
            ("draft", "Draft"),
            ("running", "Running"),
            ("dismiss", "Dismiss"),
            ("deleted", "Deleted"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    close_date = fields.Datetime(string="Close Date")
    link = fields.Char(string="Link")
    with_okr_valuation = fields.Boolean(string="With OKR Valuation", default=False)

    company_id = fields.Many2one("res.company", string="Company")
    owner_id = fields.Many2one("res.users", string="Leader")
    member_ids = fields.Many2many("res.users", string="Members")
    user_roles_ids = fields.One2many("role.bubble", "bubble_id", string="User Roles")
    with_automation = fields.Boolean(groups="bubble.group_bubble_administrator")
    run_bubble_type_code = fields.Boolean(groups="bubble.group_bubble_administrator")
    model_id = fields.Many2one("ir.model", string="Model")
    res_ids = fields.Char("Res Ids")
    code = fields.Text(string="Code", groups="bubble.group_bubble_administrator")
    linked_object_count = fields.Integer(
        string="Linked Objects Count", compute="_compute_linked_objects"
    )
    linked_object_name = fields.Char(
        string="Linked Object Name", compute="_compute_linked_objects"
    )
    okr_evaluation_ids = fields.One2many("okr.evaluation", "bubble_id")
    okr_evaluation_count = fields.Integer(
        string="OKR Evaluation Count", compute="_compute_okr_evaluation_count"
    )
    okr_ids = fields.One2many("okr", "bubble_id")
    objective_ids = fields.One2many("objective", "bubble_id")
    objective_count = fields.Integer(
        string="Objective Count", compute="_compute_objective_count"
    )
    okr_count = fields.Integer(string="OKR Count", compute="_compute_okr_count")
    size = fields.Float(compute="_compute_size")
    member_count = fields.Integer(
        compute="_compute_member_count", store=True, readonly=False
    )
    kpi_result = fields.Html()
    bubble_kpi_ids = fields.Many2many(
        "bubble.kpi", domain="['|',('model_id','=',False),('model_id','=',model_id)]"
    )
    bubble_kpi_count = fields.Integer(compute="_compute_count_kpi_ids")

    def _compute_count_kpi_ids(self):
        for bubble in self:
            bubble.bubble_kpi_count = len(bubble.bubble_kpi_ids)

    @api.onchange("bubble_type_id")
    def update_role_ids(self):
        for bubble in self:
            for role in bubble.bubble_type_id.role_ids:
                if role.id not in bubble.user_roles_ids.mapped("role_id").ids:
                    bubble.write({"user_roles_ids": [(0, 0, {"role_id": role.id})]})

    @api.depends("member_ids")
    def _compute_member_count(self):
        for bubble in self:
            bubble.member_count = len(bubble.member_ids)

    @api.depends("child_bubble_ids", "member_ids")
    def _compute_size(self):
        for bubble in self:
            bubble.size = bubble.member_count + sum(
                [child.size for child in bubble.child_bubble_ids]
            )

    @api.depends("objective_ids")
    def _compute_objective_count(self):
        for record in self:
            record.objective_count = len(record.objective_ids)

    @api.depends("okr_ids")
    def _compute_okr_count(self):
        for record in self:
            record.okr_count = len(
                record.okr_ids.filtered(lambda x: x.status == "active")
            )

    @api.depends("okr_evaluation_ids")
    def _compute_okr_evaluation_count(self):
        for record in self:
            record.okr_evaluation_count = len(
                record.okr_evaluation_ids.filtered(lambda x: x.status == "in_progress")
            )

    @api.depends("model_id", "res_ids")
    def _compute_linked_objects(self):
        for record in self.sudo():
            if record.sudo().model_id and record.sudo().res_ids:
                model = self.sudo().env[record.model_id.model]
                ids_list = [
                    int(rec_id)
                    for rec_id in record.sudo().res_ids.split(",")
                    if rec_id.isdigit()
                ]
                record.linked_object_count = len(ids_list)
                # Prendi i nomi dei primi N record (ad esempio i primi 5)
                records = model.browse(ids_list[:5])
                record.linked_object_name = record.model_id.name
            else:
                record.linked_object_count = 0
                record.linked_object_name = ""

    def action_freeze(self):
        self.write({"status": "freeze"})

    def action_dismiss(self):
        self.write({"status": "dismiss", "close_date": fields.Datetime.now()})

    def action_run(self):
        if any([urole.user_id == False for urole in self.user_roles_ids]):
            raise ValidationError("You have to specify each role to run")
        self.write({"status": "running"})

    def action_draft(self):
        self.write({"status": "draft"})

    def action_delete(self):
        self.write({"status": "deleted"})

    @api.constrains("code")
    def _check_python_code(self):
        for action in self.sudo().filtered("code"):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.model
    def _get_eval_context(self, action=None):
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
            "bubble_id": self,
            "env": self.env,
            "request": requests.request,
            "json_dumps": json.dumps,
            "json_load": json.load,
            "log": log,
        }

    def _run_action_code(self):
        if self.with_automation:
            kpi_results = ""
            for kpi in self.bubble_kpi_ids:
                kpi_result = kpi._run_action_code(self)
                kpi_results += "<tr><th>%s</th><td>%s</td></tr>" % (kpi.description, kpi_result)
            self.kpi_result = "<table>"+kpi_results+"</table>"
            if (
                self.run_bubble_type_code
                and self.bubble_type_id
                and self.bubble_type_id.with_automation
            ):
                eval_context = self.bubble_type_id._get_eval_context(
                    action=None, bubble_id=self
                )
                safe_eval(
                    self.bubble_type_id.code.strip(),
                    eval_context,
                    mode="exec",
                    nocopy=True,
                )  # nocopy allows to return 'action'
                return eval_context.get("action")
            else:
                eval_context = self._get_eval_context()
                safe_eval(
                    self.code.strip(), eval_context, mode="exec", nocopy=True
                )  # nocopy allows to return 'action'
                return eval_context.get("action")

    def action_open_okr_evaluation(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Evaluation",
            "res_model": "okr.evaluation",
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [
                (
                    "id",
                    "in",
                    self.okr_evaluation_ids.filtered(
                        lambda x: x.status == "in_progress"
                    ).ids,
                )
            ],
        }

    def action_open_okr(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Okr",
            "res_model": "okr",
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [
                ("id", "in", self.okr_ids.filtered(lambda x: x.status == "active").ids)
            ],
        }

    def action_view_linked_records(self):
        self.ensure_one()
        record_ids = [
            int(rec_id) for rec_id in self.sudo().res_ids.split(",") if rec_id.isdigit()
        ]
        return {
            "type": "ir.actions.act_window",
            "name": "Linked Records",
            "res_model": self.sudo().model_id.model,
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [("id", "in", record_ids)],
        }

    def action_start_okr_valuation(self):
        self.ensure_one()
        # Crea un record del wizard e pre-popola i campi
        wizard = self.env["wizard.start.okr.evaluation"].create(
            {
                "bubble_id": self.id,
                "owner_id": self.owner_id.id,
                "member_ids": self.member_ids.ids,
                # Imposta eventuali altri valori di default per il wizard
            }
        )
        # Restituisce un'azione per aprire il wizard
        return {
            "name": "Start OKR Evaluation",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "wizard.start.okr.evaluation",
            "res_id": wizard.id,
            "target": "new",
        }

    def action_view_bubble(self):
        self.ensure_one()
        # Crea un record del wizard e pre-popola i campi
        wizard = self.env["wizard.bubble.view"].create(
            {
                "bubble_id": self.id,
            }
        )
        # Restituisce un'azione per aprire il wizard
        return {
            "name": "View Bubble",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "wizard.bubble.view",
            "res_id": wizard.id,
            "target": "new",
        }

    def action_wizard_suggest(self):
        self.ensure_one()
        wizard = self.env["wizard.suggest.kr"].create(
            {"bubble_id": self.id, "type": "bubble"}
        )
        action = {
            "type": "ir.actions.act_window",
            "name": "Suggest KR",
            "res_model": "wizard.suggest.kr",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
        }
        return action

    def get_diameter(self):
        if self.size > 50:
            return 3
        if self.size > 15:
            return 2
        return 1

    @api.model
    def get_record_url(self, record_id):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        model_name = self._name
        return url_join(
            base_url, f"web#id={record_id}&model={model_name}&view_type=form"
        )

    def get_bubble_json(self):
        def is_highlight(bubble):
            if self.env.user.id in bubble.member_ids.ids:
                return True
            if bubble.child_bubble_ids:
                return any(is_highlight(child) for child in bubble.child_bubble_ids)
            return False

        res = []
        for bubble in self.filtered(lambda x: x.status == "running"):
            res.append(
                {
                    "name": _("Bubble %s") % bubble.name,
                    "color": bubble.bubble_type_id.css_color,
                    "content": bubble.child_bubble_ids.get_bubble_json(),
                    "size": bubble.get_diameter(),
                    "image": bubble.image_128,
                    "description": bubble.purpose,
                    "link": self.get_record_url(bubble.id),
                    "highlight": is_highlight(bubble),
                    "id": bubble.id,
                }
            )
        return res

    def action_open_objective(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Objective",
            "res_model": "objective",
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.objective_ids.ids)],
        }
