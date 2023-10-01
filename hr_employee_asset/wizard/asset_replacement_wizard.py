from odoo import api, fields, models, _


class AssetReplacementWizard(models.TransientModel):
    _name = 'asset.replacement.wizard'
    _description = 'Asset Replacement Request wizard'

    equipment_id = fields.Many2one('maintenance.equipment', string='Asset', tracking=True)

    def action_request_replacement(self):
        self.ensure_one()
        ctx = self.env.context
        asset_obj = self.env[ctx['active_model']].browse(ctx['active_id'])

        asset_obj.write({'state': 'rejected'})

        asset_obj.equipment_id.write({
            'employee_id': False,
            'state': 'available'})

        vals = {
            'employee_id': asset_obj.employee_id.id,
            'equipment_id': self.equipment_id.id,
            'allocation_type': asset_obj.allocation_type,
            'replace_note': asset_obj.asset_note,
        }
        self.env['employee.asset.replacement.request'].create(vals)

        action = {
            "type": "ir.actions.act_window",
            "name": "Asset Replacement Request",
            "view_mode": "tree,form",
            "res_model": "employee.asset.replacement.request",
        }

        return action
