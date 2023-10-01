from odoo import api, fields, models, _


class HrEmploymentOtherProfessionalLicense(models.Model):
    _name = 'hr.employment.other.professional.license'
    _description = 'Hr Employment Other Professional License Detail'

    ###for professional License
    license_no = fields.Integer(string="License No")
    license_type = fields.Many2one('license.type', string="License Type")
    license_issue_date = fields.Date(string="License Issue Date")
    given_by = fields.Char(string="Given by")
    license_expiry_date = fields.Date(string="License Expiry Date")

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
