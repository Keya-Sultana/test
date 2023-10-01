# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import pytz
import time

from odoo import api, fields, models, _


class JobCardWizard(models.TransientModel):
    _name = 'job.card.wizard'
    _description = 'Generate other allowance for all selected employees'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    type = fields.Selection([
        ('op_type', 'Operating Unit wise'),
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    department_id = fields.Many2one("hr.department", string="Department")
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def convert_minutes_into_time(self, t):
        n = t * 60
        time_format = time.strftime("%H:%M:%S", time.gmtime(n))
        return time_format

    def check_early_or_late(self, access_time, calendar_time, in_or_out, attendance_summary):
        access_time = float(access_time.replace(access_time[-3:], "").replace(":", "."))
        access_time = int(access_time) + ((access_time - int(access_time)) / 0.60)
        time = round((calendar_time - access_time) * 60)
        if time < 0:
            if in_or_out == 0:
                attendance_summary['late'] = attendance_summary['late'] + 1
                attendance_summary['total_late_in'] = attendance_summary['total_late_in'] + abs(time)
                return [abs(time), 'Late'], attendance_summary
            attendance_summary['total_overtime'] = attendance_summary['total_overtime'] + abs(time)
            return [abs(time), 'Over Time'], attendance_summary
        elif time == 0:
            return [abs(time), 'On Time'], attendance_summary
        else:
            if in_or_out == 0:
                attendance_summary['total_early_in'] = attendance_summary['total_early_in'] + abs(time)
                return [abs(time), 'Early'], attendance_summary
            attendance_summary['total_early_out'] = attendance_summary['total_early_out'] + abs(time)
            return [abs(time), 'Early'], attendance_summary

    def prepare_report_data(self, start_date, end_date, employee_ids):
        if len(employee_ids) == 0:
            print(f"No employee found in this {self.type}")
            return

        employee_data = []
        for id in employee_ids:
            date_variable = start_date
            attendance_summary = {
                'present': 0,
                'absent': 0,
                'leave': 0,
                'late': 0,
                'holiday': 0,
                'day_off': 0,
                'payable_day': 0,
                'present_percentage': 0,
                'total_early_in': 0,
                'total_late_in': 0,
                'total_early_out': 0,
                'total_overtime': 0
            }
            attendance_details = []
            while date_variable <= end_date:
                if self.env['hr.holidays.public.line'].search([('date', '=', date_variable)]):
                    attendance_summary['holiday'] = attendance_summary['holiday'] + 1
                    attendance_details.append({
                        'date': str(date_variable),
                        'in_time': '',
                        'out_time': '',
                        'state': 'Holiday',
                        'note': ''
                    })

                elif self.env['hr.leave'].search([('employee_id', '=', id), ('request_date_from', '<=', date_variable),
                                                  ('request_date_to', '>=', date_variable)]):
                    attendance_summary['leave'] = attendance_summary['leave'] + 1
                    attendance_details.append({
                        'date': str(date_variable),
                        'in_time': '',
                        'out_time': '',
                        'state': self.env['hr.leave'].search(
                            [('employee_id', '=', id), ('request_date_from', '<=', date_variable),
                             ('request_date_to', '>=', date_variable)]).name,
                        'note': ''
                    })

                elif not self.env['hr.shifting.history'].search(
                        [('employee_id', '=', id), ('effective_from', '<=', date_variable),
                         ('effective_end', '>=', date_variable)]).shift_id.attendance_ids:
                    attendance_details.append({
                        'date': str(date_variable),
                        'in_time': '',
                        'out_time': '',
                        'state': "No Roster found",
                        'note': ''
                    })

                elif not self.env['hr.shifting.history'].search(
                        [('employee_id', '=', id), ('effective_from', '<=', date_variable),
                         ('effective_end', '>=', date_variable)]).shift_id.attendance_ids.filtered(
                    lambda l: l.dayofweek == str(date_variable.weekday())):
                    attendance_summary['day_off'] = attendance_summary['day_off'] + 1
                    attendance_details.append({
                        'date': str(date_variable),
                        'in_time': '',
                        'out_time': '',
                        'state': 'Off Day',
                        'note': ''
                    })

                else:
                    if self.env['hr.attendance'].search([('employee_id', '=', id), ('check_in', '<=', date_variable),
                                                         ('check_out', '>=', date_variable)], order='check_in'):
                        attendance_summary['present'] = attendance_summary['present'] + 1
                        # roster_data = self.env['hr.employee'].search(
                        #     [('id', '=', id)]).shift_ids.search([('effective_from', '<=', date_variable), (
                        #     'effective_end', '>=', date_variable)]).shift_id.attendance_ids.filtered(
                        #     lambda l: l.dayofweek == str(date_variable.weekday()))

                        get_shifting = self.env['hr.employee'].search(
                            [('id', '=', id)]).shift_ids
                        for shift in get_shifting:
                            if shift.effective_from <= date_variable <= shift.effective_end:
                                roster_data = shift.shift_id.attendance_ids.filtered(
                                    lambda l: l.dayofweek == str(date_variable.weekday()))

                        check_in = \
                            self.env['hr.attendance'].search(
                                [('employee_id', '=', id), ('check_in', '<=', date_variable),
                                 ('check_out', '>=', date_variable)],
                                order='check_in').read()[0].get('check_in')
                        check_in = check_in.astimezone(pytz.timezone(
                            self.env['hr.employee'].search([('id', '=', id)]).resource_calendar_id.tz)).strftime(
                            '%Y-%m-%d %H:%M:%S')

                        in_times = datetime.datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S').time()
                        in_times = in_times.strftime("%H:%M:%S%p")
                        for roster in roster_data:
                            my_checkin_data, attendance_summary = self.check_early_or_late(str(check_in).split(" ")[1],
                                                                                           roster['hour_from'],
                                                                                           0,
                                                                                           attendance_summary)  ### 0 means check in and 1 means check_out

                        check_out = self.env['hr.attendance'].search(
                            [('employee_id', '=', id), ('check_in', '<=', date_variable),
                             ('check_out', '>=', date_variable)],
                            order='check_out desc').read()[0]['check_out']
                        check_out = check_out.astimezone(pytz.timezone(
                            self.env['hr.employee'].search([('id', '=', id)]).resource_calendar_id.tz)).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        out_times = datetime.datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S').time()
                        out_times = out_times.strftime("%H:%M:%S%p")
                        for roster in roster_data:
                            my_checkout_data, attendance_summary = self.check_early_or_late(
                                str(check_out).split(" ")[1],
                                roster['hour_to'], 1,
                                attendance_summary)

                        attendance_details.append({
                            'date': str(date_variable),
                            'in_time': str(in_times) + f' - 0H {str(my_checkin_data[0])}M 0S {my_checkin_data[1]}',
                            'out_time': str(out_times) + f' - 0H {str(my_checkout_data[0])}M 0S {my_checkout_data[1]}',
                            'state': 'Present',
                            'note': ''
                        })

                    else:
                        attendance_summary['absent'] = attendance_summary['absent'] + 1
                        attendance_details.append({
                            'date': str(date_variable),
                            'in_time': '',
                            'out_time': '',
                            'state': 'Absent',
                            'note': ''
                        })
                date_variable = date_variable + datetime.timedelta(days=1)

            # attendance_summary['payable_day'] = attendance_summary['present'] + attendance_summary['holiday'] + \
            #                                     attendance_summary['leave'] + attendance_summary['day_off']
            attendance_summary['payable_day'] = abs((start_date - end_date).days) + 1
            if attendance_summary['present'] > 0:
                attendance_summary['present_percentage'] = round(((attendance_summary['present'] + attendance_summary[
                    'holiday'] + attendance_summary['leave'] + attendance_summary['day_off']) / (
                                                                          attendance_summary['present'] +
                                                                          attendance_summary['holiday'] +
                                                                          attendance_summary['leave'] +
                                                                          attendance_summary[
                                                                              'absent'] + attendance_summary[
                                                                              'day_off'])) * 100)
            else:
                attendance_summary['present_percentage'] = 0

            attendance_summary['total_overtime'] = str(
                self.convert_minutes_into_time(attendance_summary['total_overtime']))
            attendance_summary['total_early_in'] = str(
                self.convert_minutes_into_time(attendance_summary['total_early_in']))
            attendance_summary['total_late_in'] = str(
                self.convert_minutes_into_time(attendance_summary['total_late_in']))
            attendance_summary['total_early_out'] = str(
                self.convert_minutes_into_time(attendance_summary['total_early_out']))

            emp = self.env['hr.employee'].search([('id', '=', id)])
            employee_data.append({
                'personal_info': {'name': emp.display_name,
                                  'company_name': emp.company_id.name,
                                  'start_date': str(start_date),
                                  'end_date': str(end_date),
                                  'employee_identification': emp.identification_id,
                                  'department': emp.department_id.name,
                                  'joining_date': emp.initial_employment_date,
                                  },

                'attendance_summary': attendance_summary,
                'attendance_details': attendance_details}
            )
        print(employee_data)
        return employee_data

    def process_report(self):

        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date

        if self.type == 'employee_type':
            employee_ids = self.employee_ids.ids
            report_data = self.prepare_report_data(self.start_date, self.end_date, employee_ids)

        elif self.type == 'department_type':
            employee_ids = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)]).ids
            report_data = self.prepare_report_data(self.start_date, self.end_date, employee_ids)

        else:
            employee_ids = self.env['hr.employee'].search(
                [('default_operating_unit_id', '=', self.operating_unit_id.id)]).ids
            report_data = self.prepare_report_data(self.start_date, self.end_date, employee_ids)

        data['result'] = report_data

        # data['type'] = self.type
        # data['operating_unit_id'] = self.operating_unit_id.id
        # data['department_id'] = self.department_id.id
        # data['employee_ids'] = self.employee_ids.ids

        return self.env.ref('gbs_hr_attendance_report.action_job_card_doc').report_action(None, data=data)
