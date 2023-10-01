from odoo import models, api, fields, _
from datetime import date, datetime, timedelta


class HrEmployeeAssetAllocationRequest(models.Model):
    _name = 'employee.asset.allocation.request'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Make Employees Asset Allocation Request '

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user.employee_id

    name = fields.Char(string="Reference No", readonly=True, tracking=True)
    # name = fields.Char(string='Asset Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee_get,
                                  store=True, tracking=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Asset', required=True, store=True, tracking=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        related='employee_id.default_operating_unit_id')
    request_date = fields.Date('Request Date', default=date.today(), tracking=True)
    allocation_date = fields.Date('Allocation Date', readonly=True, tracking=True)
    expected_return_date = fields.Date('Expected Return Date', readonly=True, tracking=True)
    return_date = fields.Date('Return Date', default=date.today(), tracking=True)
    asset_duration = fields.Integer(string="Duration", required=True, tracking=True)
    allocation_type = fields.Selection(
        [('on_demand', 'On Demand'), ('permanent', 'Permanent')],
        string='Allocation Type',
        default='on_demand')

    asset_note = fields.Text(string='Description')
    asset_replacement = fields.Boolean(string='Replacement', compute='_compute_replacement')
    replace_button = fields.Boolean(compute='_compute_replace_button')

    state = fields.Selection([
        ('draft', "New"),
        ('applied', "Waiting for Approval"),
        ('allocated', "Allocated"),
        ('rejected', "Rejected"),
        ('returned', "Returned")
    ], default='draft', tracking=True)

    def _compute_replacement(self):
        self.asset_replacement = True if self.allocation_type == 'permanent' else False

    @api.depends('state', 'asset_replacement')
    def _compute_replace_button(self):
        for record in self:
            record.replace_button = record.state == 'allocated' and record.asset_replacement

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('employee.asset.allocation.request') or '/'
        return super(HrEmployeeAssetAllocationRequest, self).create(vals)

    def action_confirm(self):
        self.state = 'applied'

    def action_allocate(self):
        self.state = 'allocated'
        self.allocation_date = self.request_date
        self.expected_return_date = date.today() + timedelta(days=30)
        self.equipment_id.write({
            'employee_id': self.employee_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'allocation_request_id': self.id,
            'state': 'allocation'})

    def action_reject(self):
        self.state = 'rejected'

    def action_return(self):
        self.state = 'returned'
        self.equipment_id.write({
            'employee_id': False,
            'operating_unit_id': False,
            'allocation_request_id': False,
            'state': 'available'})
