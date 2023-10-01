from odoo import api, models
from datetime import date, datetime
from datetime import timedelta
import datetime
import pytz
import time


class JobCardReport(models.AbstractModel):
    _name = 'report.gbs_hr_attendance_report.report_jobcard_doc'
    _description = 'Employee Job Card Report'

    @api.model
    def _get_report_values(self, docids, data):
        start_date = data['start_date']
        end_date = data['end_date']
        # type = data['type']
        # department_id = data['department_id']
        # employee_ids = data['employee_ids']
        # operating_unit_id = data['operating_unit_id']

        date_format = "%Y-%m-%d"
        start_date = datetime.datetime.strptime(start_date, date_format)
        end_date = datetime.datetime.strptime(end_date, date_format)
        delta = end_date - start_date

        dates_in_range_list = []
        all_val_list = []
        emp_sort_list = ''

        # for i in range(delta.days + 1):
        #     dates_in_range = (start_date + timedelta(days=i))
        #     dates_in_range_list.append(dates_in_range)
        #
        # if (type == 'employee_type'):
        #     emp = self.env['hr.employee'].search([('id', '=', employee_ids)])
        # elif (type == 'department_type'):
        #     emp = self.env['hr.employee'].search([('department_id', '=', department_id)])
        # elif (type == 'op_type'):
        #     emp = self.env['hr.employee'].search([('operating_unit_id', '=', operating_unit_id)])

        dynamic_col_list = self.dynamic_col_list(dates_in_range_list, start_date, end_date)
        dynamic_col_list2 = list(dyc[5:] for dyc in dynamic_col_list)

        # for e in emp:
        #     res = {}
        #     res['name'] = e.name
        #     res['joining_date'] = e.initial_employment_date
        #     res['department'] = e.department_id.name
        #     res['employee_identification'] = e.identification_id
        #
        #     all_val_list.append(res)
        #     emp_sort_list = all_val_list

        # ha_object = self.env['hr.attendance'].search(
        #     [('check_in', '>=', start_date),
        #      ('check_in', '<=', end_date)])
        # # print("Employee Name:",ha_object.employee_id.name)
        # employees = []
        #
        # for att in ha_object:
        #     employees.append({
        #         'name': att.employee_id.name,
        #         'department': att.employee_id.department_id.name,
        #         'joining_date': att.employee_id.initial_employment_date,
        #         'employee_identification': att.employee_id.identification_id,
        #     })

        return {
            # 'docs': docs,
            # 'doc_ids': docids,
            # 'data': data,
            'dynamic_col_list': dynamic_col_list2,
            'employee_data': data['result'],
        }

    def dynamic_col_list(self, dyc, start_date, end_date):
        dynamic_col = []
        while (start_date <= end_date):
            str_date = str(start_date)
            key = str_date[:10]
            dynamic_col.append(key)
            start_date += timedelta(days=1)

        return dynamic_col

