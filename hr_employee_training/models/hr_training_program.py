from odoo import models, api, fields, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class HrTrainingProgram(models.Model):
    _name = 'hr.training.program'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Make Training Program for Employee'

    TYPE = [
        ('functional', 'Functional'),
        ('technical', 'Technical'),
        ('other', 'Other')
    ]

    training_type = fields.Selection(
        selection=TYPE,
        string="Training Type1",
        index=True,
        tracking=True,
        required=True,
    )
    name = fields.Char(string="Reference No", readonly=True, tracking=True)
    type_id = fields.Many2one(
        'hr.training.type', required=True,
        string="Training Type",
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approve', 'Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    training_id = fields.Many2one('hr.training', string='Training', tracking=True, required=True)
    start_date = fields.Datetime('Training Start Date', default=lambda self: fields.Datetime.now(), tracking=True)
    end_date = fields.Datetime('Training End Date', default=lambda self: fields.Datetime.now(), tracking=True,)
    duration = fields.Integer(string="Duration", compute="_compute_number_of_days", )
    training_name = fields.Char(string='Trainer Name', required=True, tracking=True)
    venue = fields.Char(string='Venue', required=True, tracking=True)
    remark = fields.Text(string='Remark', required=True, tracking=True)

    emp_training_ids = fields.One2many('hr.employee.training', 'program_id', string='Employee Training', tracking=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('hr.training.program') or '/'
        return super(HrTrainingProgram, self).create(vals)

    @api.depends("start_date", "end_date")
    def _compute_number_of_days(self):
        for line in self:
            days = False
            if line.start_date and line.end_date:
                days = (line.end_date - line.start_date).days + 1
            line.duration = days

    def action_confirm(self):
        if len(self.emp_training_ids) == 0:
            raise ValidationError(_("Please Add Employees for Training Plan!"))
        else:
            self.state = 'to approve'
            # self.emp_training_ids.write({'state': 'draft'})

    def action_done(self):
        self.state = 'approve'
        self.emp_training_ids.write({'state': 'approve'})

    def action_reject(self):
        self.state = 'cancel'
        self.emp_training_ids.write({'state': 'cancel'})


class HrEmployeeTraining(models.Model):
    _name = 'hr.employee.training'
    _description = "Hr employee Training"

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee', readonly=True,
                                  required=True, tracking=True)
    program_id = fields.Many2one('hr.training.program',
                                 string='Training Plan',
                                 required=True, tracking=True)
    training_id = fields.Many2one(related='program_id.training_id', string="Training")
    training_name = fields.Char(related='program_id.training_name', string="Trainer Name")
    start_date = fields.Datetime(related='program_id.start_date', string="Start Date")
    end_date = fields.Datetime(related='program_id.end_date', string="End Date")
    duration = fields.Integer(related='program_id.duration', string="Duration")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, default='draft', copy=False, tracking=True)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    emp_training_ids = fields.One2many('hr.employee.training',
                                       'employee_id',
                                       'Employment Training ')
    is_emp_training = fields.Boolean(string="Is Employee Training?", default=False)
    filtered_training_line_ids = fields.One2many('hr.employee.training',
                                                 compute='_compute_filtered_emp_training_ids')

    @api.depends('emp_training_ids')
    def _compute_filtered_emp_training_ids(self):
        for emp in self:
            emp.filtered_training_line_ids = emp.emp_training_ids.filtered(
                lambda training: training.state == 'approve')

    # def _compute_employee_training(self):
    #     for emp in self.emp_training_ids:
    #         if emp.state == 'approve':
    #             self.is_emp_training = True
    #         else:
    #             self.is_emp_training = False
