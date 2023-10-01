from odoo import models, fields, api, exceptions, tools, _
import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class EmployeeExitReq(models.Model):
    _name = 'hr.emp.exit.req'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _order = 'state asc'

    def last_days(self):
        ldate = datetime.date.today() + relativedelta(months=1)
        return ldate

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(string="Reference No", readonly=True, tracking=True)
    emp_notes = fields.Text(string='Employee Notes')
    reason_for_exit = fields.Text(string='Reason for Leaving', tracking=True)
    department_notes = fields.Text(string='Department Manager Notes')
    req_date = fields.Date('Request Date', default=fields.Date.today(), tracking=True,
                           required=True)
    last_date = fields.Date('Last Day of Work', default=last_days, tracking=True,
                            required=True)
    effected_date = fields.Date('Effected Date', tracking=True)

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    # state = fields.Selection(
    #     [('draft', 'To Submit'),
    #      ('cancel', 'Cancelled'),
    #      ('confirm', 'To Approve'),
    #      ('refuse', 'Refused'),
    #      ('validate1', 'Second Approval'),
    #      ('validate', 'Approved')],
    #     'Status', readonly=True, copy=False, default='draft',
    #     help='The status is set to \'To Submit\', when a Exit request is created.\
    #         \nThe status is \'To Approve\', when exit request is confirmed by user.\
    #         \nThe status is \'Refused\', when exit request is refused by manager.\
    #         \nThe status is \'Approved\', when exit request is approved by manager.', tracking=True)

    employee_id = fields.Many2one('hr.employee', select=True, invisible=False, tracking=True,
                                  default=_current_employee)
    employee_no = fields.Char(related='employee_id.identification_id', string="Employee ID", tracking=True)
    job_id = fields.Many2one('hr.job', string='Job Title', related='employee_id.job_id', tracking=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, copy=False)
    manager_id = fields.Many2one('hr.employee', related='employee_id.parent_id', tracking=True,
                                 help='This area is automatically filled by the user who validate the exit process')
    department_id = fields.Many2one('hr.department', string='Department', tracking=True,
                                    related='employee_id.department_id')
    parent_id = fields.Many2one('hr.emp.exit.req', string='Parent')
    checklists_ids = fields.One2many('hr.exit.checklists.line', 'checklist_id')
    pen_checklists_ids = fields.One2many('pendding.checklists.line', 'pen_checklist_id', ondelete="cascade")
    interview_ids = fields.One2many('employee.exit.interview', 'exit_req_id', ondelete="cascade")
    final_ids = fields.One2many('final.settlement', 'exit_req_id', ondelete="cascade")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('hr.emp.exit.req') or '/'
        return super(EmployeeExitReq, self).create(vals)

    # Button actions
    def exit_reset(self):
        self.write({'state': 'draft'})
        self.checklists_ids = False
        return True

    # exit request confirm
    def exit_confirm(self):
        self.checklists_ids = []
        vals = []
        confg_checklist_pool = self.env['hr.exit.configure.checklists'].search([('is_active', '=', True)])
        for record in confg_checklist_pool:
            if record.applicable_empname_id or record.applicable_department_id or record.applicable_jobtitle_id:
                if self.job_id or self.employee_id or self.department_id:
                    if record.applicable_empname_id == self.employee_id or record.applicable_department_id == self.department_id or record.applicable_jobtitle_id == self.job_id:
                        for config in record.checklists_ids:
                            vals.append((0, 0, {
                                'checklist_item_id': config.checklist_item_id.id,
                                'responsible_department': config.responsible_department.id,
                                'responsible_emp': config.responsible_emp.id,
                                'state': 'not_received'
                            }))
        # self.checklists_ids = [(5, 0, 0)]
        self.employee_id.write({'last_employment_date': self.last_date})
        self.checklists_ids = vals

        # self.send_mail_exit_request_confirm()
        return self.write({'state': 'to approve'})

    def send_mail_exit_request_confirm(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        model_data_pool = self.env['ir.model.data'].search([('name', '=', 'group_hr_manager')], limit=1)
        record_id = model_data_pool.res_id
        manager = self.env['res.groups'].search([('id', '=', record_id)]).users
        emailto = []
        for eml in manager:
            login = eml.login
            emailto.append(login)
        emailto.append(self.employee_id.parent_id.user_id.login)
        for email in emailto:
            template = self.env.ref('hr_employee_exit.example_exit_req_email_template')
            template.write({
                'subject': "Exit Request",
                'email_from': email_server_obj,
                'email_to': email})
            self.env['mail.template'].browse(template.id).send_mail(self.id)

    # exit request approved
    # def exit_validate(self):
    #     # self.send_mail_template()
    #     self.employee_id.write({'last_employment_date': self.last_date})
    #     self.state = 'validate1'

    def send_mail_template(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        model_data_pool = self.env['ir.model.data'].search([('name', '=', 'group_hr_manager')], limit=1)
        record_id = model_data_pool.res_id
        manager = self.env['res.groups'].search([('id', '=', record_id)]).users
        emailto = []
        for eml in manager:
            login = eml.login
            emailto.append(login)
        emailto.append(self.employee_id.user_id.login)
        for email in emailto:
            template = self.env.ref('hr_employee_exit.email_template_exit_req_approved')
            template.write({
                'subject': "Exit Request has been approved",
                'email_from': email_server_obj,
                'email_to': email})
            self.env['mail.template'].browse(template.id).send_mail(self.id)

    # exit request done(final approval)
    def exit_done(self):
        self.pen_checklists_ids = []
        # self.employee_id.stages_history = []
        vals = []
        # emp_status = []
        line_obj = self.env['hr.exit.checklists.line'].search(
            [('checklist_id', '=', self.id)])
        for record in line_obj:
            vals.append((0, 0, {
                'checklist_item_id': record.checklist_item_id.id,
                'responsible_department': record.responsible_department.id,
                'responsible_emp': record.responsible_emp.id,
                'employee_id': record.employee_id.id,
                'state': 'not_received'
            }))
        self.pen_checklists_ids = vals
        # emp_status.append((0, 0, {
        #     'start_date': datetime.date.today(),
        #     'end_date': self.last_date,
        #     'duration': 0,
        #     'state': 'relieved'
        # }))
        # self.employee_id.stages_history = emp_status
        # self.employee_id.write({'state': 'relieved'})
        return self.write({'state': 'purchase'})

    # Create Exit Interview and open form view
    def create_exit_interview(self):
        for applicant in self:
            interview_data = {
                'default_employee_id': applicant.employee_id.id,
                'default_leaving_date': applicant.last_date,
                'default_resignation_date': applicant.req_date,
                'default_supervisor_id': applicant.employee_id.parent_id.id,
            }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr_employee_exit.open_view_exit_interview')
        dict_act_window['context'] = interview_data
        return dict_act_window

    # Create Final Settlement and open form view
    def create_final_settlement(self):
        if self.employee_id.name == self.final_ids.employee_id.name:
            raise ValidationError(_("Final Settlement Already Created!!"))
        else:
            for applicant in self:
                settlement_data = {
                    'default_employee_id': applicant.employee_id.id,
                    'default_leaving_date': applicant.last_date,
                }

            dict_act_window = self.env['ir.actions.act_window']._for_xml_id(
                'hr_employee_exit.open_view_final_settlement')
            dict_act_window['context'] = settlement_data
            return dict_act_window

    # Exit request cancel
    def exit_refuse(self):
        for emp_exit in self:
            if emp_exit.state == 'to approve':
                self.write({'state': 'cancel'})
            else:
                self.write({'state': 'cancel'})
        # self.send_mail_exit_request_cancel()
        return True

    def send_mail_exit_request_cancel(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        template = self.env.ref('hr_employee_exit.send_mail_exit_request_cancel')
        template.write({
            'subject': "Exit request has been cancelled",
            'email_from': email_server_obj,
            'email_to': self.employee_id.user_id.login})
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.constrains('req_date', 'last_date')
    def _check_last_date(self):
        if self.req_date > self.last_date:
            raise Warning('Last Date must be grater than request date.')


class EmpReqChecklistsLine(models.Model):
    _name = "hr.exit.checklists.line"
    _rec_name = 'checklist_item_id'
    _inherit = ['mail.thread']

    employee_id = fields.Many2one('hr.employee', related='checklist_id.employee_id', tracking=True)
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', string='Checklist Item', required=True)
    remarks = fields.Text(string='Remarks', tracking=True)
    state = fields.Selection([
        ('received', "Received"),
        ('not_received', "Not Received")
    ], 'Status', default='not_received')

    # Relational fields
    checklist_id = fields.Many2one('hr.emp.exit.req', ondelete="cascade")
    responsible_department = fields.Many2one('hr.department', ondelete='set null', string='Responsible Department')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User')


class PendingChecklistsLine(models.Model):
    _name = "pendding.checklists.line"
    _rec_name = 'checklist_item_id'
    _inherit = ['mail.thread']

    employee_id = fields.Many2one('hr.employee', related='pen_checklist_id.employee_id', tracking=True)
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', string='Checklist Item', required=True)
    remarks = fields.Text(string='Remarks', tracking=True)
    state = fields.Selection([
        ('received', "Received"),
        ('not_received', "Not Received")
    ], 'Status', default='not_received')

    # Relational fields
    # checklist_id = fields.Many2one('hr.emp.exit.req', ondelete="cascade")
    pen_checklist_id = fields.Many2one('hr.emp.exit.req', ondelete="cascade")
    responsible_department = fields.Many2one('hr.department', ondelete='set null', string='Responsible Department')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User')

    status = fields.Selection([('draft', 'Draft'), ('verify', 'Verified')],
                              readonly=True, copy=False,
                              default='draft', tracking=True)

    # @api.multi
    def check_list_verify(self):
        exit_req_obj = self.env['hr.exit.checklists.line'].search(
            [('checklist_id', '=', self.pen_checklist_id.id)])
        for exit_line in exit_req_obj:
            if exit_line.responsible_department:
                if exit_line.checklist_item_id == self.checklist_item_id and exit_line.responsible_department == self.responsible_department:
                    exit_line.remarks = self.remarks
                    exit_line.write({'state': 'received'})
            elif exit_line.responsible_emp:
                if exit_line.checklist_item_id == self.checklist_item_id and exit_line.responsible_emp == self.responsible_emp:
                    exit_line.remarks = self.remarks
                    exit_line.write({'state': 'received'})
            else:
                pass
        # self.send_mail_received_item()
        return self.write({'status': 'verify', 'state': 'received'})

    # @api.multi
    def send_mail_received_item(self):
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        model_data_pool = self.env['ir.model.data'].search([('name', '=', 'group_hr_manager')], limit=1)
        record_id = model_data_pool.res_id
        manager = self.env['res.groups'].search([('id', '=', record_id)]).users
        emailto = []
        for eml in manager:
            login = eml.login
            emailto.append(login)
        emailto.append(self.employee_id.parent_id.user_id.login)
        emailto.append(self.employee_id.user_id.login)
        for email in emailto:
            template = self.env.ref('hr_employee_exit.email_template_received_item')
            template.write({
                'subject': "Items has been received",
                'email_from': email_server_obj,
                'email_to': email})
            self.env['mail.template'].browse(template.id).send_mail(self.id)
