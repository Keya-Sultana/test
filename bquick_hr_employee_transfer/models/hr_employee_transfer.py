from odoo import models, fields, api


class HrEmployeeTransfer(models.Model):
    _name = 'hr.employee.transfer'
    _inherit = ['mail.thread']
    _description = 'Hr Employee Transfer'

    name = fields.Char('Ref',  default='/')
    employee_id = fields.Many2one('hr.employee',  tracking=True,
                                  string='Employee',
                                  required=True)
    curr_designation_id = fields.Many2one('hr.job', string='Current Designation',  tracking=True)
    curr_dept_id = fields.Many2one('hr.department', string="Current Department",  tracking=True)
    curr_operating_unit_id = fields.Many2one('operating.unit', string='Current Operating Unit',  tracking=True)

    new_designation_id = fields.Many2one('hr.job', string='New Designation',  tracking=True)
    new_dept_id = fields.Many2one('hr.department', string="New Department",  tracking=True)
    new_operating_unit_id = fields.Many2one('operating.unit', string='New Operating Unit',  tracking=True)

    effective_date = fields.Date(string="Effective Date",  tracking=True)
    remarks = fields.Text(string="Remarks",  tracking=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "confirm"),
        ('done', "Done")
    ], default='draft',  tracking=True)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.curr_designation_id = self.employee_id.job_id
            self.curr_dept_id = self.employee_id.department_id
            self.curr_operating_unit_id = self.employee_id.operating_unit_ids.id

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('hr.employee.transfer') or '/'
        vals['name'] = seq
        return super(HrEmployeeTransfer, self).create(vals)

    def action_confirm(self):
        self.state = 'confirm'
        # res = {
        #     'state': 'confirm'
        # }
        # new_seq = self.env['ir.sequence'].next_by_code('hr.employee.transfer') or '/'
        #
        # if new_seq:
        #     res['name'] = new_seq
        #
        # self.write(res)

    def action_done(self):
        self.state = 'done'


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    """ All relations fields """
    transfer_ids = fields.One2many('hr.employee.transfer', 'employee_id', "Employee Transfer Information")
