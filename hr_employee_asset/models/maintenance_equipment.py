from odoo import models, api, fields, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    state = fields.Selection([
        ('available', "Available"),
        ('allocation', "Allocated"),
    ], default='available', tracking=True)

    allocation_ids = fields.One2many('employee.asset.allocation.request', 'equipment_id')
    allocation_count = fields.Integer(compute='_compute_allocation_count', string="Allocation Count")
    allocation_request_id = fields.Many2one('employee.asset.allocation.request', string='Allocation Request')
    replacement_request_id = fields.Many2one('employee.asset.replacement.request', string='Replacement Request')

    available_count = fields.Integer(compute='_compute_available_count', string="Available Count")
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    # allocation_type = fields.Selection(
    #     [('on_demand', 'On Demand'), ('permanent', 'Permanent')],
    #     string='Type')

    @api.depends('allocation_ids')
    def _compute_allocation_count(self):
        for equipment in self:
            equipment.allocation_count = len(equipment.filtered(lambda reg: reg.state == 'allocation'))
            # equipment.allocation_count = len(equipment.allocation_ids.filtered(lambda reg: reg.state == 'allocated'))

    @api.depends('allocation_ids')
    def _compute_available_count(self):
        for equipment in self:
            # equipment.available_count = len(equipment.allocation_ids.filtered(lambda reg: reg.state != 'allocated'))
            equipment.available_count = len(equipment.filtered(lambda reg: reg.state != 'allocation'))

    def button_allocation_request(self):
        self.ensure_one()
        return {
            'name': _('allocation request'),
            'view_mode': 'form',
            'res_model': 'employee.asset.allocation.request',
            'view_id': self.env.ref('hr_employee_asset.asset_allocation_request_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.allocation_request_id.id,
        }
