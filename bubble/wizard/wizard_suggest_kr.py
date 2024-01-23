# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json

PROMPT = '''
    Devo creare degli OKR per la mia azienza. Gli OKR sono legati a tre tipologie:
    - per Bolla: Ogni bolla è un raggruppamento di persone con uno scopo
    - per Ruolo: Ogni ruolo ha una descrizione specifica
    - per Singola Persona: Sono kr specifici assegnati ad una singola persona.
    Puoi aiutarmi a creare %d Key Results su questo obiettivo: '%s' e per %s 
    Questo è un testo ulteriore per specificare meglio cosa creare %s.
    Dammi il risultato separando ogni key result da un a capo e direttamente senza nessuna spiegazione in %s.
'''
class WizardToSuggestKR(models.TransientModel):
    _name = 'wizard.suggest.kr'
    _description = 'Wizard to Suggest OKR'

    objective_id = fields.Many2one('objective', string='Objective')
    bubble_id = fields.Many2one('bubble', string='Bubble')
    bubble_purpose = fields.Html('Bubble Purpose',related="bubble_id.purpose")
    role_description = fields.Text('Role Description',related="bubble_role_id.description")
    user_id = fields.Many2one('res.users', string='User')
    bubble_role_id = fields.Many2one('bubble.role', string='Role')
    description = fields.Text('Description')
    suggest_kr_line_ids = fields.One2many('wizard.suggest.kr.line','suggest_kr_id')
    number = fields.Integer('Number of Key Results',default=3)
    language = fields.Many2one('res.lang')
    

    def get_okrs_from_chatgpt(self):
        url = "https://api.openai.com/v1/chat/completions"
        api_key = self.env['ir.config_parameter'].sudo().get_param('openai.api_key')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        prompt_description = ''
        if self.bubble_purpose:
            prompt_description += ''' questa bolla %s che ha questo purpose %s, '''%(self.bubble_id.name, self.bubble_purpose)
        if self.role_description:
            prompt_description += ''' questo ruolo %s che ha questa descrizione %s '''%(self.bubble_role_id.name, self.description)
        prompt = PROMPT %(self.number,self.objective_id.name,prompt_description,self.description,self.language.name)
        
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
        okr_response = json_response['choices'][0]['message']['content']
        okrs = okr_response.strip().split('\n')
        raise ValidationError(okrs)
        # Filtra eventuali righe vuote o non valide
        okrs = [okr for okr in okrs if okr and okr.strip()]
        return okrs



    def action_suggest_kr(self):
        okrs = self.get_okrs_from_chatgpt()
        
        for okr in okrs:
            self.env['wizard.suggest.kr.line'].create({
                'name':okr,
                'bubble_id':self.bubble_id.id,
                'user_id':self.user_id.id,
                'bubble_role_id':self.bubble_role_id.id,
                'suggest_kr_id':id
            })
        return
       
class WizardToSuggestKRLine(models.TransientModel):
    _name = 'wizard.suggest.kr.line'
    _description = 'Wizard to Suggest OKR Line'

    name = fields.Char('Description')
    bubble_id = fields.Many2one('bubble', string='Bubble', required=True)
    user_id = fields.Many2one('res.users', string='User')
    bubble_role_id = fields.Many2one('bubble.role', string='Role')
    suggest_kr_id =fields.Many2one('wizard.suggest.kr')
    okr_id = fields.Many2one('okr')

    def action_confirm_kr(self):
        for okr in self:
            okr_id = self.env['okr'].create({
                'name':self.name,
                'objective_id':self.suggest_kr_id.objective_id.id,
                'status':'active',
                'bubble_id':self.bubble_id.id,
                'user_id':self.user_id.id,
                'bubble_role_id':self.bubble_role_id.id,
                'type':'bubble' if self.bubble_id else ('role' if self.bubble_role_id else 'personal')
            })
            okr.okr_id = okr_id.id

    