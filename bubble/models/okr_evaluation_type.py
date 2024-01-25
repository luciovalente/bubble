import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools.float_utils import float_compare
import json

import base64
from collections import defaultdict
import functools
import logging
import requests

PROMPT = '''
    Devo creare degli il modello di valuazione della mia azieda. 
    Genera codice python Odoo per questa modello di valutazione . 
    Rispondi  solo con il codice python senza commenti o testo.
    Il codice deve implementare questa descrizione (inclusa in << e >>):
    << %s >>
    Le indicazioni del codice sono queste. Puoi usare solo queste librerie e queste variabili:
    %s
    La variabile evaluation_id rappresenta il modello okr.evaluation che rappresenta la valutazione
    di un singolo candidato.
    Questi sono i campi e le relazioni che puoi usare nel tuo codice:
    %s.
    Nel codice python fai scrivere tramite write su evaluation_id il risultato 
    nel campo result (float) di evaluation_id e se c'è un risultato testuale scrivilo 
    nel campo result_char di evaluation_id
'''


class OkrEvaluationType(models.Model):
    _name = 'okr.evaluation.type'
    _description = 'OKR Evaluation Type'

    name = fields.Char()
    description = fields.Char()
    code = fields.Text(string='Code')
    
    @api.constrains('code')
    def _check_python_code(self):
        for action in self.sudo().filtered('code'):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)
    
    def get_model_and_fields(self):
        self.ensure_one()
        res = 'Model;Field;Type;Relation'
        fields = self.sudo().env['ir.model.fields'].search([('model','in',('okr','okr.result','bubble','okr.evaluation','bubble.role'))])
        for f in fields:
            res += "%s;%s;%s;%s\n"%(f.model_id.name,f.name,f.ttype,f.relation)
        return res
    
    @api.model
    def _get_eval_context(self, evaluation_id=None):
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
            'uid': self._uid,
            'user': self.env.user,
            'time': tools.safe_eval.time,
            'datetime': tools.safe_eval.datetime,
            'dateutil': tools.safe_eval.dateutil,
            'timezone': timezone,
            'float_compare': float_compare,
            'b64encode': base64.b64encode,
            'b64decode': base64.b64decode,
            'evaluation_id':evaluation_id,
            'env':self.env,
            "request": requests.request,
            "json_dumps": json.dumps,
            "json_load": json.load,
            "log":log
        }

    def _run_action_code(self):
        eval_context = self._get_eval_context()
        safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)  # nocopy allows to return 'action'
        return eval_context.get('action')
    

    def suggest_code_from_chatgpt(self):
        url = "https://api.openai.com/v1/chat/completions"
        api_key = self.env['ir.config_parameter'].sudo().get_param('openai.api_key')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = PROMPT %(self.description,self.get_model_and_fields())
        raise ValidationError(PROMPT)
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Assicurati che la richiesta sia andata a buon fine
        json_response = response.json()
        
        result_response = json_response['choices'][0]['message']['content']
        raise ValidationError(PROMPT)
        
        # Filtra eventuali righe vuote o non valide
        okrs = [okr for okr in okrs if okr and okr.strip()]
        return okrs
