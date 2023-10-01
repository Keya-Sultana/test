from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritCurrency(models.Model):
    _inherit = 'res.currency'

    rate = fields.Float(digits=(12, 8))
    reverse_rate = fields.Float(compute='_compute_current_reverse_rate', string='Current Rates', digits=(12, 8))
    # reverse_rate = fields.Float(string='Current Rates', digits=0)

    @api.depends('rate_ids.reverse_rate')
    def _compute_current_reverse_rate(self):
        date = self._context.get('date') or fields.Datetime.now()
        company = self.env.user.company_id
        # company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        company_id = self._context.get('company_id') or company.id
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT c.id, (SELECT r.reverse_rate FROM res_currency_rate r
                                      WHERE r.currency_id = c.id AND r.name <= %s
                                        AND (r.company_id IS NULL OR r.company_id = %s)
                                   ORDER BY r.company_id, r.name DESC
                                      LIMIT 1) AS rate
                       FROM res_currency c
                       WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.reverse_rate = currency_rates.get(currency.id) or 1.0

    ### one function writing 2 ways by Keya
    # def _get_reverse_rates(self, company, date):
    #     if not self.ids:
    #         return {}
    #     self.env['res.currency.rate'].flush(['reverse_rate', 'currency_id', 'company_id', 'name'])
    #     query = """SELECT c.id,
    #                       COALESCE((SELECT r.reverse_rate FROM res_currency_rate r
    #                               WHERE r.currency_id = c.id AND r.name <= %s
    #                                 AND (r.company_id IS NULL OR r.company_id = %s)
    #                            ORDER BY r.company_id, r.name DESC
    #                               LIMIT 1), 1.0) AS rate
    #                FROM res_currency c
    #                WHERE c.id IN %s"""
    #     self._cr.execute(query, (date, company.id, tuple(self.ids)))
    #     currency_rates = dict(self._cr.fetchall())
    #     return currency_rates
    #
    # @api.depends('rate_ids.reverse_rate')
    # def _compute_current_reverse_rate(self):
    #     date = self._context.get('date') or fields.Date.today()
    #     company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
    #     # the subquery selects the last rate before 'date' for the given currency/company
    #     currency_rates = self._get_reverse_rates(company, date)
    #     last_rate = self.env['res.currency.rate']._get_last_rates_for_companies(company)
    #     for currency in self:
    #         currency.reverse_rate = currency_rates.get(currency.id) or 1.0
    #         currency.reverse_rate = (currency_rates.get(currency.id) or 1.0) / last_rate[company]
    #         currency.inverse_rate = 1 / currency.reverse_rate
    #         if currency != company.currency_id:
    #             currency.rate_string = '1 %s = %.6f %s' % (company.currency_id.name, currency.reverse_rate, currency.name)
    #         else:
    #             currency.rate_string = ''
