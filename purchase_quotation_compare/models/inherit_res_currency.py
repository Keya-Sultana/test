from odoo import api, fields, models


class InheritCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate_compare(self, from_currency, to_currency):
        from_currency = from_currency.with_env(self.env)
        to_currency = to_currency.with_env(self.env)
        return to_currency.rate / from_currency.rate
