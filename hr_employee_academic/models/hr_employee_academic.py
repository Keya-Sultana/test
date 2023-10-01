from odoo import models, fields

class HrEmployeeAcademic(models.Model):
    _name = 'hr.employee.academic'

    degree_level = fields.Char(string="Degree Level")
    institute_university = fields.Char(string="Institute/University")
    degree = fields.Char(string="Degree")

    passing_year = fields.Char(string="Passing Year")
    result = fields.Char(string="Result")
    board_university = fields.Char(string='Board/University',)
    major_subject = fields.Char(string='Major Subject',)

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)



    
