
from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    qty_count = fields.Integer(string='Qty (Pcs)')
    qty_weight = fields.Float(string='Qty (KG)')
