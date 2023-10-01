from odoo import api, fields, models, _

class HrEmployeeChildren(models.Model):

    _inherit = 'hr.employee.children'

    educational_institute = fields.Char("Educational Institute",)
    class_no = fields.Char("Class",)
    last_exam_result = fields.Char("Last Exam Result",)
    special_skill = fields.Char("Special Skill",)
    blood_group = fields.Selection(
        [('o_neg', 'O-'), ('o_pos', 'O+'), ('b_pos', 'B+'), ('b_neg', 'B-'), ('a_neg', 'A-'), ('a_pos', 'A+',),
         ('ab_neg', 'AB-'), ('ab_pos', 'AB+')],
        string="Blood Group", default='')


    
