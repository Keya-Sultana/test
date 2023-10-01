from odoo import api, fields, models, _


class HrEmploymentProfessionalQualification(models.Model):
    _name = 'hr.employment.professional.qualification'
    _description = 'Hr Employment Professional Qualification'

    ###for professional Qualification
    pq_certification_name = fields.Char(string="Certification Name")
    pq_certificate_number = fields.Integer(string="Certificate Number")
    pq_institute = fields.Char(string="Institute")
    pq_country_id = fields.Many2one('res.country', string="Country")
    pq_expiry_date = fields.Date(string="Expiry Date")

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
