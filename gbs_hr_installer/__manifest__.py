# -*- coding: utf-8 -*-

{
    'name': 'GBS HR Installation',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR',
    'version': '10.0.1.0.0',
    'data': [],
    'depends': [
        'hr',
        'base_technical_features',
        'hr_recruitment',
        'gbs_employee_roster_view',
        'gbs_hr_employee_documents',
        'hr_contract_operating_unit',
        'hr_contract_reference',
        'hr_overtime_requisition',
        'hr_recruitment_survey',
        'gbs_hr_employee_security',
        #
        'gbs_hr_payroll',
        'gbs_hr_payroll_bank_letter',
        'gbs_hr_payroll_top_sheet',
        'hr_payslip_monthly_report',
        'hr_payroll_festival_bonus',
        'gbs_hr_package',
        #
        'hr_employee_iou_payroll',
        'hr_employee_loan_payroll',
        'hr_employee_meal_bills_payroll',
        'hr_employee_mobile_bills_payroll',
        'hr_other_allowance_payroll',
        'hr_other_deduction',
        'hr_payroll_arrear',
        #
        'hr_attendance_import',
        'hr_manual_attendance',
        'gbs_hr_attendance_report',
        'gbs_hr_device_config',
        'hr_attendance_and_ot_summary',
        'hr_attendance_dashboard',
        'hr_employee_attendance_payroll',
        #
        'hr_short_leave',
        'gbs_hr_leave_duration_correction',
        'hr_unpaid_holidays',
        'gbs_hr_leave_report',
        'hr_earned_leave',
        'hr_holiday_utility',
        'hr_holiday_exception',
        'hr_holidays_multi_approval_notification',
        #
        'gbs_hr_leave_forward_encash',
        #
        'gbs_samuda_hr_access',
        ],
    'summary': 'This is the package where include all hr related modules (Beta version)',
    'description': 'This is the package where include all hr related modules (Beta version)',
    'installable': True,
    'application': True,
}