from odoo import models, fields, api
from .. models.attendance_processor import AttendanceProcessor


class HrAttendanceSummaryWizard(models.TransientModel):
    _name = 'attendance.summary.wizard.a'
    _description = "Hr Attendance Summary Wizard"
    
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel_1_a', 'payslip_id',
                                    'employee_id', 'Employees',)

    def process_employee_line(self):
        vals = {}
        context=[]
        line_obj = self.env['hr.attendance.summary.line']

        summaryId = self.env.context['active_id']

        operating_unit_id = self.env['hr.attendance.summary'].browse(summaryId).operating_unit_id.id

        selected_ids_for_line = line_obj.search([('att_summary_id', '=', summaryId)])
        inserted_employee_ids = set([val.employee_id.id for val in selected_ids_for_line])
        duplicate_employee_ids_filter = list(set(self.employee_ids.ids)-(inserted_employee_ids))

        attendanceProcess = self.env['hr.attendance.summary.temp']
        attendanceProcess.process(duplicate_employee_ids_filter, summaryId, operating_unit_id)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.attendance.summary',
            'res_model': 'hr.attendance.summary',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': self.env.context['active_id']
        }
