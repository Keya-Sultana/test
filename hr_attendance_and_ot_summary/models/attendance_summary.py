from odoo import models, fields,_
from odoo import api
from odoo.exceptions import UserError, ValidationError


class AttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _inherit = ['mail.thread']
    _description = 'Attendance and over time summary'
    _order = 'id desc'

    name = fields.Char(size=100, string='Title', required='True')
    period = fields.Many2one("date.range", "Period", required=True,
                             domain="[('type_id.holiday_month', '=', True)]")
    company_id = fields.Many2one('res.company', string='Company', required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft', tracking=True)

    """ Relational Fields """
    att_summary_lines = fields.One2many('hr.attendance.summary.line', 'att_summary_id', string='Summary Lines', tracking=True)

    def action_generated(self):
        self.state = 'generated'
    
    def action_draft(self):
        self.state = 'draft'
        self.att_summary_lines.write({'state': 'draft'})
        
    def action_confirm(self):
        self.state = 'confirmed'
        self.att_summary_lines.write({'state': 'confirmed'})
            
    def action_done(self):
        self.state = 'approved'
        self.att_summary_lines.write({'state':'approved'})

    # Show a msg for applied & approved state should not be delete
    def unlink(self):
        for summary in self:
            if summary.state != 'draft':
                raise UserError(_('You can not delete this.'))
            summary.att_summary_lines.unlink()
        return super(AttendanceSummary,self).unlink()