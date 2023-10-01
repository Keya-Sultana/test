from odoo import api, fields, models, _


class CloneShiftBatchEmployees(models.TransientModel):
    _name = 'clone.shift.batch.employees'
    _description = 'Clone Employee shift Batch'

    name = fields.Char(string='New Batch Name', required=True, tracking=True)
    effective_from = fields.Date(string='Effective Start Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    shift_ids = fields.One2many('hr.shifting.history', 'shift_batch_id', tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    def create_employee_shift_batch(self):
        self.ensure_one()
        pool_shift_emp = self.env['hr.shifting.history']
        ctx = self.env.context
        batch_obj = self.env[ctx['active_model']].browse(ctx['active_id'])

        effective_from = self.effective_from
        effective_end = self.effective_end

        ## Generate Batch Process
        new_batch = self.env['hr.shift.employee.batch'].create({
            'name': self.name,
        })
        for shift in batch_obj.shift_emp_ids:
            res = {
                'employee_id': shift.employee_id.id,
                'shift_id': shift.shift_id.id,
                'effective_from': effective_from,
                'effective_end': effective_end,
                'shift_batch_id': new_batch.id,
            }
            pool_shift_emp += self.env['hr.shifting.history'].create(res)

        ## Ends here  Process

        action = {
            "type": "ir.actions.act_window",
            "name": "New Employee Shifting Batch",
            "view_mode": "tree,form",
            "res_model": "hr.shift.employee.batch",
        }

        return action
