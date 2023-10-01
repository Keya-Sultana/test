from odoo import fields, models, api


class IncidentRaise(models.Model):
    _name = "incident.raise"
    _inherit = ['mail.thread']
    _description = "Incident Raise"

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user.employee_id

    name = fields.Char(string="Reference No", readonly=True, tracking=True)
    date = fields.Date(string="Date", required=True, tracking=True)
    incident_person_id = fields.Many2one('hr.employee', string="Incident Create Person Name",
                                         default=_default_employee_get,
                                         store=True, tracking=True)
    incident_person_no = fields.Char(related='incident_person_id.identification_id', string="Incident Create Person "
                                                                                            "ID", tracking=True)
    department_id = fields.Many2one(related='incident_person_id.department_id', string="Department", tracking=True)
    job_id = fields.Many2one(related='incident_person_id.job_id', string="Designation", tracking=True)

    line_ids = fields.One2many('incident.raise.line', 'incident_id', string='Incident Raise Line', tracking=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('to approve', 'To Approve'),
        ('approve', "Approved"),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].sudo().next_by_code('incident.raise') or '/'
        vals['name'] = number
        return super(IncidentRaise, self).create(vals)

    def action_confirm(self):
        self.state = 'to approve'

    def action_done(self):
        self.state = 'approve'

    def action_reject(self):
        self.state = 'cancel'


class IncidentRaiseLine(models.Model):
    _name = "incident.raise.line"
    _description = "Incident Raise Line"

    person_id = fields.Many2one('hr.employee', string="Incident Person Name", tracking=True)
    person_no = fields.Integer(string="Incident Person ID No.", tracking=True)
    department_id = fields.Many2one('hr.department', string="Department", tracking=True)
    job_id = fields.Many2one('hr.job', string="Designation", tracking=True)
    incident_date = fields.Datetime(string="Incident Date & Time", tracking=True)
    incident_location = fields.Char(string="Incident Location", tracking=True)
    # incident_time = fields.Date(string="Time")
    incident_detail = fields.Text(string="Incident Details", tracking=True)
    remarks = fields.Text(string='Remarks', tracking=True)
    incident_id = fields.Many2one('incident.raise', tracking=True)

    @api.onchange('person_id')
    def onchange_person_id(self):
        if self.person_id:
            self.person_no = self.person_id.identification_id
            self.department_id = self.person_id.department_id
            self.job_id = self.person_id.job_id
