from odoo import api, fields, models, _


class HrContract(models.Model):
    _name = 'hr.contract'
    _inherit = ['hr.contract', 'mail.thread']

    transport_allowance = fields.Float(string='Trasport Allowance', digits='Payroll', tracking=True, help='Amount for Transport Allowance')
    contractual = fields.Boolean(string="Contractual", tracking=True)

    name = fields.Char('Contract Reference', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string="Department", tracking=True)
    # type_id = fields.Many2one('hr.contract.type', string="Contract Type", required=True, tracking=True, default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    job_id = fields.Many2one('hr.job', string='Job Title', tracking=True)
    date_start = fields.Date('Start Date', required=True, tracking=True, default=fields.Date.today)
    date_end = fields.Date('End Date', tracking=True)
    trial_date_start = fields.Date('Trial Start Date', tracking=True)
    trial_date_end = fields.Date('Trial End Date', tracking=True)
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule', tracking=True)
    wage = fields.Float('Wage', digits=(16, 2), required=True, help="Basic Salary of the employee", tracking=True)
    advantages = fields.Text('Advantages', tracking=True)
    notes = fields.Text('Notes', tracking=True)
    permit_no = fields.Char('Work Permit No', tracking=True)
    visa_no = fields.Char('Visa No', tracking=True)
    visa_expire = fields.Date('Visa Expire Date', tracking=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', tracking=True)
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', default='monthly')
    tds = fields.Float(string='TDS', digits='Payroll', tracking=True,
                       help='Amount for Tax Deduction at Source')
    driver_salay = fields.Boolean(string='Driver Salary', tracking=True, help='Check this box if you provide allowance for driver')
    medical_insurance = fields.Float(string='Medical Insurance', digits='Payroll', tracking=True,
                                     help='Deduction towards company provided medical insurance')
    voluntary_provident_fund = fields.Float(string='Voluntary Provident Fund (%)', digits='Payroll', tracking=True,
                                            help='VPF is a safe option wherein you can contribute more than the PF ceiling of 12% that has been mandated by the government and VPF computed as percentage(%)')
    house_rent_allowance_metro_nonmetro = fields.Float(string='House Rent Allowance (%)', digits='Payroll', tracking=True,
                                                       help='HRA is an allowance given by the employer to the employee for taking care of his rental or accommodation expenses for metro city it is 50% and for non metro 40%. \nHRA computed as percentage(%)')
    supplementary_allowance = fields.Float(string='Supplementary Allowance', tracking=True, digits='Payroll')

