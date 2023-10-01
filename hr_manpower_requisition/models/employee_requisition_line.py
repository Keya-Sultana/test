from odoo import api, fields, tools, models, _


class HrEmployeeRequisitionLine(models.Model):
    _name = 'hr.employee.requisition.line'
    _description = 'Hr Employee Requisition Line'

    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Title')
    current_employee = fields.Char(string='Current Employee', compute='_compute_no_of_employee')
    expected_employee = fields.Char(string='Expected Employee')
    required_date = fields.Date(string='Required Date')
    responsibilities = fields.Text(string='Responsibilities')
    qualification_required = fields.Text(string='Qualification Required')
    experience_required = fields.Text(string='Experience Required')
    salary_range = fields.Char(string='Salary Range')

    requisition_id = fields.Many2one('hr.employee.requisition', string="Employee Requisition Ref.")

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
        ('valid', "Validate"),
        ('cancel', "Cancel"),
    ], default='draft', string="State")

    # @api.depends('job_id')
    def _compute_no_of_employee(self):
        pool_emp = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)])
        self.current_employee = len(pool_emp.ids)
        # if self.job_id:
        #     pool_emp = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)])
        #     self.current_employee = len(pool_emp.ids)
