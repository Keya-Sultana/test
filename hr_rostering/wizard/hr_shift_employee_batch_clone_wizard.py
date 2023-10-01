from odoo import api, fields, models, _


class HrShiftBatchClone(models.TransientModel):
    _name = 'hr.batch.employee.clone'
    _description = 'Create Batch for all selected employees clone'

    shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True,
                               domain="[('state', '=','approved' )]")
    effective_from = fields.Date(string='Effective Start Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_shift_employee_clone_group_rel',
                                    'shift_id', 'employee_id', string='Employees')

    @api.model
    def default_get(self, fields):
        # Get the active model
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')

        # Get the record with the specified id
        record = self.env[active_model].browse(active_id)

        # Get employee_id field value from the line of the shift_emp_ids field
        employee_id = record.shift_emp_ids.employee_id

        return {'employee_ids': employee_id}

    def create_employee_shift_batch(self):
        self.ensure_one()
        pool_shift_emp = self.env['hr.shifting.history']
        ctx = self.env.context
        [data] = self.read()
        batch_obj = self.env[ctx['active_model']].browse(ctx['active_id'])

        effective_from = self.effective_from
        effective_end = self.effective_end
        shift_id = self.shift_id

        ## Generate Batch Process
        new_batch = self.env['hr.shift.employee.batch'].create({
            'name': batch_obj.name + '' + str('(copy)'),
            'state': 'in_progress',
        })
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'shift_id': shift_id.id,
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
