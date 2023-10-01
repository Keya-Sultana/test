from odoo import api, fields, models


class HrDepartmentHierarchy(models.Model):
    _name = "hr.department"
    _inherit = "hr.department"

    child_all_count = fields.Integer(
        'Indirect Surbordinates Count',
        compute='_compute_child_all_count', recursive=True, store=False)
    child_org_ids = fields.One2many("hr.department", related="child_ids")

    @api.depends('child_ids.child_all_count')
    def _compute_child_all_count(self):
        for dep in self:
            dep.child_all_count = len(dep.child_ids) + sum(child.child_all_count for child in dep.child_ids)
