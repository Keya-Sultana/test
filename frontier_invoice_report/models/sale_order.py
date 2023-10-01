from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_amount_to_words(self):
        for order in self:
            order.amount_words = order.currency_id.amount_to_text(order.amount_total)

    amount_words = fields.Char(string="Total(In words):", compute='_compute_amount_to_words')

    port_of_loading = fields.Char(string='Port of Loading')
    port_of_discharge = fields.Char(string='Port of Discharge')
    final_destination = fields.Char(string='Final Destination')

    product_hs_code = fields.Char('Product HS Code', compute='get_hs_code')

    def get_hs_code(self):
        for line in self.order_line:
            if self.product_hs_code is not None:
                self.product_hs_code = line.product_id.hs_code
                break

