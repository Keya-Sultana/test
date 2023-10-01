{
    'name': 'HR Rostering',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'Human Resources',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        # 'security/alter.xml',
        'security/shifting_rule.xml',
        'wizard/hr_shift_employee_batch_wizard_views.xml',
        'wizard/clone_shift_employee_batch_wizard.xml',
        'views/hr_shifting.xml',
        'views/hr_shifting_history.xml',
        'views/hr_shift_alter_view.xml',
        'views/hr_shift_employee_batch_views.xml',
        'views/hr_shift_alter_batch.xml',
        'reports/employee_work_schedule_report_view.xml',
    ],
    'depends': [
        'hr_attendance',
        'hr_employee_operating_unit',
        'planning',
    ],
    'description': 
    "This module enables employee rostering",        
    'installable': True,
    'application': False,
}
