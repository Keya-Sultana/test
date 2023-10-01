# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MobileBillByEmployees(models.TransientModel):
    _name = 'mobile.bill.employees'
    _description = 'Generate Mobile Bill for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'mobile_bill_employee_rel',
                                    'bill_id', 'employee_id', string='Employees',)

    def generate_record(self):
        # pass
        pool_evaluation_emp = self.env['hr.mobile.bill.line']
        [data] = self.read()
        active_id = self.env.context.get('active_id')

        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'bill_amount': '0.0',
                'parent_id': active_id,
            }
            pool_evaluation_emp += self.env['hr.mobile.bill.line'].create(res)

        return {'type': 'ir.actions.act_window_close'}
