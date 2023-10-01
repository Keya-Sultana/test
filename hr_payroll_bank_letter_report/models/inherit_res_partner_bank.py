from odoo import api, fields, models


class InheritResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    is_payroll_account = fields.Boolean(string='Is Payroll A/C', default=False)
    bank_branch = fields.Char(string="Bank Branch")
    bank_account_title = fields.Char(string="Account Name")
    bank_nominee = fields.Char(string="Nominee Name")
    bank_nominee_nid = fields.Char(string="Nominee NID No")
    account_open_date = fields.Date(string="Account Opening Date")
    address = fields.Char(string="Nominee Address")
    mobile = fields.Char(string="Nominee Mobile No")
    swift_code = fields.Char('SWIFT Code', )
