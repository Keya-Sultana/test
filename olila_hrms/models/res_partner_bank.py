from odoo import api, fields, models, tools, _


class InheritResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s %s' % (rec.acc_number, (rec.bank_id.name if rec.bank_id else ''))))
        return result
