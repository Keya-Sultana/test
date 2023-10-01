from odoo import models, api, fields, _
from datetime import date, datetime, timedelta


class HrEmployeeAssetReplacementRequest(models.Model):
    _name = 'employee.asset.replacement.request'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Make Employees Asset Replacement Request '

    name = fields.Char(string="Reference No", readonly=True, tracking=True)
    # name = fields.Char(string='Name')
    # name = fields.Char(string='Asset Replacement Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", store=True, tracking=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        related='employee_id.default_operating_unit_id')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', tracking=True)
    replace_request_date = fields.Date('Request Date', default=date.today(), tracking=True)
    replace_allocation_date = fields.Date('Allocation Date', readonly=True, tracking=True)
    replace_expected_return_date = fields.Date('Expected Return Date', readonly=True, tracking=True)
    replace_return_date = fields.Date('Return Date', default=date.today(), tracking=True)
    allocation_type = fields.Selection(
        [('on_demand', 'On Demand'), ('permanent', 'Permanent')],
        string='Allocation Type',
        required=True)

    replace_note = fields.Text(string='Description')
    allocation_request_id = fields.Many2one(
        'employee.asset.allocation.request', string='Allocation Request')

    state = fields.Selection([
        ('draft', "New"),
        ('applied', "Waiting for Approval"),
        ('allocated', "Allocated"),
        ('rejected', "Rejected"),
        ('returned', "Returned")
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('employee.asset.replacement.request') or '/'
        return super(HrEmployeeAssetReplacementRequest, self).create(vals)

    def action_confirm(self):
        self.state = 'applied'

    def action_allocate(self):
        self.state = 'allocated'
        self.replace_allocation_date = self.replace_request_date
        self.replace_expected_return_date = date.today() + timedelta(days=30)
        self.equipment_id.write({
            'employee_id': self.employee_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'replacement_request_id': self.id,
            'state': 'allocation'})

    def action_reject(self):
        self.state = 'rejected'

    def action_return(self):
        self.state = 'returned'
        self.equipment_id.write({
            'employee_id': False,
            'operating_unit_id': False,
            'replacement_request_id': False,
            'state': 'available'})

    def button_request_form(self):
        self.ensure_one()
        return {
            'name': _('asset request'),
            'view_mode': 'form',
            'res_model': 'employee.asset.allocation.request',
            'view_id': self.env.ref('hr_employee_asset.asset_allocation_request_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.allocation_request_id.id,

        }


