from odoo import api, fields, models, _

class HrEmploymentHistory(models.Model):
    _name = 'hr.employment.history'

    # Employment History
    joining_date = fields.Date('Joining Date')
    organization = fields.Char('Organization Name')
    release_date = fields.Date('Release Date')
    department = fields.Char('Department')
    designation = fields.Char('Designation')
    responsibility = fields.Char('Responsibilities')
    clearance_certification = fields.Char('Clearance Certification')


    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)


    
