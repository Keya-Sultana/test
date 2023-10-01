from odoo import api, fields, models, _, SUPERUSER_ID


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    allocation_type = fields.Selection([
        ('no', 'No Limit'),
        ('fixed_allocation', 'Allow Employees Requests'),
        ('fixed', 'Set by Leave Officer')],
        default='no', string='Mode',
        help='\tNo Limit: no allocation by default, users can freely request time off; '
             '\tAllow Employees Requests: allocated by HR and users can request time off and allocations; '
             '\tSet by Leave Officer: allocated by HR and cannot be bypassed; users can request time off;')

    leave_validation_type = fields.Selection([
        ('no_validation', 'No Validation'),
        ('hr', 'By Leave Officer'),
        ('manager', "By Employee's Manager"),
        ('both', "By Employee's Manager and Leave Officer")], default='hr', string='Leave Validation')
    allocation_validation_type = fields.Selection([
        ('hr', 'By Leave Officer'),
        ('manager', "By Employee's Manager"),
        ('both', "By Employee's Manager and leave Officer")], default='manager', string='Allocation Validation')


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    shift_code = fields.Char(string="Shift Code")


class HrshiftEmployeeBatch(models.Model):
    _inherit = "hr.shift.employee.batch"

    shift_incharge = fields.Many2one('res.users', string="Shift incharge")
