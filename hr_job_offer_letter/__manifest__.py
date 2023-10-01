{
    'name': 'Job Offer Letter',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    "website": "",
    'category': 'Human Resources',
    'depends': [
        'hr_recruitment',
                ],
    'data': [
        # 'report/job_offer_letter_report_templates.xml',
        # 'report/report_view.xml',
        'data/mail_data.xml',
        'views/he_application_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
}
