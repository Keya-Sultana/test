# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrTrainingByEmployee(models.TransientModel):
    _name = 'hr.training.by.employee'
    _description = 'Assign employees for training'

    employee_ids = fields.Many2many('hr.employee', 'hr_training_employee_rel',
                                    'training_id', 'employee_id', string='Employees',)

    def generate_record(self):
        # pass
        pool_evaluation_emp = self.env['hr.employee.training']
        [data] = self.read()
        active_id = self.env.context.get('active_id')

        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate this process."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            res = {
                'employee_id': employee.id,
                'program_id': active_id,
            }
            pool_evaluation_emp += self.env['hr.employee.training'].create(res)

        return {'type': 'ir.actions.act_window_close'}
