from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    can_request = fields.Boolean('Can request for item ?')
