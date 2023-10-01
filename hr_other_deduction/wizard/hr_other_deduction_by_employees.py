# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrOtherDeductionEmployees(models.TransientModel):
    _name = 'hr.other.deduction.employees'
    _description = 'Generate other deduction for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_deduction_employee_rel',
                                    'deduction_id', 'employee_id', string='Employees',)

    def generate_record(self):
        # pass
        pool_evaluation_emp = self.env['hr.other.deduction.line']
        [data] = self.read()
        active_id = self.env.context.get('active_id')

        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'parent_id': active_id,
            }
            pool_evaluation_emp += self.env['hr.other.deduction.line'].create(res)

        return {'type': 'ir.actions.act_window_close'}
