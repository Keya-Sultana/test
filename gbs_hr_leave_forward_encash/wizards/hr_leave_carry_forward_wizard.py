from odoo import models, fields, api


class HrLeaveCarryForwardWizard(models.TransientModel):
    _name = 'hr.leave.forward.encash.wizard'

    employee_ids = fields.Many2many('hr.employee', string='Employees', domain="[('operating_unit_id','=',operating_unit_id)]")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def process_employee_line(self):

        parent_obj = self.env['hr.leave.forward.encash'].search([('id', '=', self.env.context['active_id'])])
        line_obj = self.env['hr.leave.forward.encash.line']

        selected_ids_for_line = line_obj.search([('parent_id', '=', self.env.context['active_id'])])
        inserted_employee_ids = set([val.employee_id.id for val in selected_ids_for_line])
        duplicate_employee_ids_filter = list(set(self.employee_ids.ids) - (inserted_employee_ids))

        for val in self.employee_ids:
            if val.id in duplicate_employee_ids_filter:
                self._cr.execute("""SELECT employee_id, SUM(number_of_days) AS authorize, 
                        (SELECT SUM(number_of_days) AS authorize 
                        FROM hr_leave 
                        WHERE employee_id = %s AND
                        leave_year_id = %s AND
                        holiday_status_id = %s
                        GROUP BY employee_id) AS availed 
                    FROM hr_leave 
                    WHERE employee_id = %s AND
                    leave_year_id = %s AND
                    holiday_status_id = %s
                    GROUP BY employee_id
                    """ % (val.id, parent_obj.carry_forward_year.id, parent_obj.leave_type.id, val.id, parent_obj.carry_forward_year.id, parent_obj.leave_type.id))
                row = self._cr.fetchone()

                if not row:
                    continue

                vals = {}
                if not row[2]:
                    row = row[:2] + (0,)
                vals['employee_id'] = val.id
                vals['authorized_leave'] = row[1]
                vals['availed_leave'] = row[2]
                vals['balance_leave'] = row[1] - row[2]
                vals['state'] = 'draft'
                vals['parent_id'] = self.env.context['active_id']
                line_obj.create(vals)

        parent_obj.write({'state': "confirmed"})

        return {
                'view_type': 'form',
                'view_mode': 'form',
                'src_model': 'hr.leave.forward.encash',
                'res_model': 'hr.leave.forward.encash',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': self.env.context['active_id']
        }