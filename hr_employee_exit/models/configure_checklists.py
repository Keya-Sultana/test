from odoo import models, fields, api, exceptions, _


class ConfigureChecklists(models.Model):
    _name = 'hr.exit.configure.checklists'
    _inherit = ['mail.thread']

    # Model Fields
    name = fields.Char(string='Name', size=100, required=True, help='Please enter name.', tracking=True)
    notes = fields.Text(string='Notes', size=500, help='Please enter notes.', tracking=True)
    is_active = fields.Boolean(string='Active', default=True)
    responsible_type = fields.Selection(selection=[('department', 'Department'), ('individual', 'Individual')],
                                        tracking=True)
    applicable_for = fields.Selection(
        selection=[('department', 'Department'), ('designation', 'Designation'), ('individual', 'Individual')],
        tracking=True)

    # Relational Fields
    applicable_department_id = fields.Many2one('hr.department', string='Applicable Department',
                                               tracking=True)
    applicable_empname_id = fields.Many2one('hr.employee', string='Applicable Employee', tracking=True)
    applicable_jobtitle_id = fields.Many2one('hr.job', string='Applicable Designation', tracking=True)
    responsible_userdepartment_id = fields.Many2one('hr.department', string='Responsible Department',
                                                    tracking=True)
    responsible_username_id = fields.Many2one('hr.employee', string='Responsible User', tracking=True)
    checklists_ids = fields.One2many('hr.exit.configure.checklists.line', 'checklists_id')

    @api.onchange('responsible_type')
    def on_change_responsible_type(self):
        self.responsible_userdepartment_id = 0
        self.responsible_username_id = 0

    @api.onchange('applicable_for')
    def on_change_applicable_for(self):
        self.applicable_department_id = 0
        self.applicable_empname_id = 0
        self.applicable_jobtitle_id = 0

    _sql_constraints = [
        ('_check_name_uniq', 'unique(name)', "Checklist name already exists!"),
    ]
