from datetime import datetime
from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    nid_no = fields.Char(string="NID", tracking=True)
    tin = fields.Char(string='TIN Number')
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group', Tracking=True)
    religion = fields.Selection([('islam', 'Islam'), ('buddhism', 'Buddhism'),
                                 ('christianity', 'Christianity'), ('hinduism', 'Hinduism'),
                                 ('judaism', 'Judaism'), ('taoism', 'Taoism')],
                                string='Religion', default='', tracking=True)
    certificate = fields.Selection([
        ('literate', 'Literate'),
        ('psc', 'PSC'),
        ('ssc', 'SSC'),
        ('HSC', 'HSC'),
        ('diploma', 'Diploma'),
        ('graduate', ' Post Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other', groups="hr.group_hr_user", tracking=True)
    address_home_id = fields.Many2one(
        'res.partner', 'Present Address',
        help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user", tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    permanent_address = fields.Char('Permanent Address', Tracking=True)
    # present_address = fields.Char('Present Address', Tracking=True)
    age = fields.Integer(compute="_compute_age")

    hobbie_interest = fields.Many2many('hr.hobbies.interests', string='Hobbies and Interests')
    employee_card_no = fields.Integer(string='Employee Id Card Number', tracking=True)

    ###for work permit
    work_permit = fields.Boolean(string='Work Permit', default=False)
    wp_place_issue = fields.Char(string='Place of Issue')

    ###for passport
    passport = fields.Boolean(string='Passport', default=False)
    passport_issue_place = fields.Char(string='Place of Issue')
    date_issue = fields.Date(string='Date of Issue')
    date_expiry = fields.Date(string='Expiry Date')

    ###for Emergency contact
    relation = fields.Char('Relation')

    ###for spouse
    marriage_date = fields.Date(string="Date of Marriage")

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birthday:
                age = relativedelta(fields.Date.today(), record.birthday).years
            record.age = age



