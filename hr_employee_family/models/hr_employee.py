from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    spouse_nid = fields.Char(string="Spouse's NID No")
    spouse_mobile = fields.Char(string="Spouse's Mobile No")
    spouse_occupation = fields.Char(string="Spouse's Occupation")

    father_nid = fields.Char(string="Father's NID No")
    father_mobile = fields.Char(string="Father's Mobile No")
    father_occupation = fields.Char(string="Father's Occupation")

    mother_nid = fields.Char(string="Mother's NID No")
    mother_mobile = fields.Char(string="Mother's Mobile No")
    mother_occupation = fields.Char(string="Mother's Occupation")


    
