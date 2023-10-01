{
    'name': 'HR Bank Letter',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    'license': 'LGPL-3',
    'website': 'www.odoo.com.bd',
    'category': 'Human Resources',
    'depends': [
        'hr_payroll',
        # 'amount_to_word_bd'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/hr_bank_letter_generate_wizard_views.xml',
        'views/inherit_hr_employrr_view.xml',
        'views/inherit_res_partner_bank_view.xml',
        'views/hr_payslip_run_view.xml',
        'report/payroll_report_bank_ac_view.xml',
    ],
    'installable': True,
    'application': False,
}
