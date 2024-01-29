from odoo import http
from odoo.http import request


class BubbleController(http.Controller):
    @http.route("/get_bubble_data", type="json", auth="user")
    def get_bubble_data(self, bubble_id):
        # Recupera la bolla specifica utilizzando l'ID
        bubble = request.env["bubble"].browse(int(bubble_id))
        if not bubble.exists():
            return {"error": "Bubble not found"}
        # Prepara i dati della bolla

        return bubble.get_bubble_json()
