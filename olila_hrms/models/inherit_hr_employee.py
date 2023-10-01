from odoo import api, fields, models, _, SUPERUSER_ID
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    length_of_service = fields.Char(
        'Months of Service',
        compute='_compute_months_service',
    )
    is_eligible_bonus = fields.Boolean(string='Eligible for Bonus', default=False, tracking=True)
    is_quarterly_assessment = fields.Boolean(string='Quarterly Assessment', default=False, tracking=True)
    probation_duration = fields.Integer(string="Probation Duration", tracking=True)
    is_previously_applied = fields.Boolean(string='Previously applied to Olila for Job', default=False, tracking=True)

    ### for other
    religion = fields.Selection([('islam', 'Islam'), ('buddhism', 'Buddhism'),
                                 ('christianity', 'Christianity'), ('hinduism', 'Hinduism'),
                                 ('judaism', 'Judaism'), ('taoism', 'Taoism')],
                                string='Religion', default='')
    blood_group = fields.Selection(
        [('o_neg', 'O-'), ('o_pos', 'O+'), ('b_pos', 'B+'), ('b_neg', 'B-'), ('a_neg', 'A-'), ('a_pos', 'A+',),
         ('ab_neg', 'AB-'), ('ab_pos', 'AB+')],
        string="Blood Group", default='')
    hobbie_interest = fields.Many2many('hr.hobbies.interests', string='Hobbies and Interests')
    permanent_address = fields.Char('Permanent Address')
    present_address = fields.Char('Present Address')

    ### for Sales location
    division_id = fields.Many2one('route.division', string='Division')
    district_id = fields.Many2one('route.district', string='District', domain="[('divison_id', '=', division_id)]")
    upazila_id = fields.Many2one('route.upazila', string='Upazila', domain="[('district_id', '=', district_id)]")
    zone_id = fields.Many2one('res.zone', string='Region')
    territory_id = fields.Many2one('route.territory', string='Territory', domain="[('zone_id', '=', zone_id)]")
    area_id = fields.Many2one('route.area', string='Area', domain="[('territory_id', '=', territory_id)]")

    ###for work permit
    work_permit = fields.Boolean(string='Work Permit', default=False)
    wp_place_issue = fields.Char(string='Place of Issue')

    ###for passport
    passport = fields.Boolean(string='Passport', default=False)
    passport_issue_place = fields.Char(string='Place of Issue')
    date_issue = fields.Date(string='Date of Issue')
    date_expiry = fields.Date(string='Expiry Date')

    ###for Emergency contact
    relation = fields.Char('Relation')

    ###for spouse
    marriage_date = fields.Date(string="Date of Marriage")

    ####Declaration
    current_major_illness = fields.Text(string='Declaration of current/previous major illness', tracking=True)
    declaration = fields.Text(string='Declaration')

    #### Personal Checklist
    copy_requisition_form = fields.Boolean(string='Copy of Requisition form', default=False, tracking=True)
    copy_of_advertisement = fields.Boolean(string='Copy of Advertisement', default=False, tracking=True)
    copy_of_resume = fields.Boolean(string='Copy of Resume/CV/Cover Letter', default=False, tracking=True)
    job_application_form = fields.Boolean(string='Job Application Form', default=False, tracking=True)

    masters_pg = fields.Boolean(string='Masters/PG', default=False, tracking=True)
    bachelor = fields.Boolean(string='Bachelor', default=False, tracking=True)
    hsc = fields.Boolean(string='H.S.C', default=False, tracking=True)
    ssc = fields.Boolean(string='S.S.C', default=False, tracking=True)
    diploma = fields.Boolean(string='Diploma', default=False, tracking=True)
    other_academic = fields.Boolean(string='Others', default=False, tracking=True)

    experience = fields.Boolean(string='Professional Experience', default=False, tracking=True)
    training_professional = fields.Boolean(string='Professional Training', default=False, tracking=True)
    other_professional = fields.Boolean(string='Others Professional', default=False, tracking=True)

    copy_of_photograph = fields.Boolean(string='Copy of Photograph', default=False, tracking=True)
    copy_of_nid = fields.Boolean(string='Copy of National ID', default=False, tracking=True)
    copy_of_appointment = fields.Boolean(string='Copy of Appointment Letter', default=False, tracking=True)
    copy_of_joining_letter = fields.Boolean(string='Copy of Joining Letter', default=False, tracking=True)
    copy_of_accept_letter = fields.Boolean(string='Copy of Acceptance Letter', default=False, tracking=True)

    copy_police_verification = fields.Boolean(string='Police Verification', default=False, tracking=True)
    copy_of_chairman_certificate = fields.Boolean(string='Copy of Chairman Certificate', default=False, tracking=True)
    copy_of_employee_information = fields.Boolean(string='Copy of Employee Information Form', default=False, tracking=True)
    copy_visiting_card = fields.Boolean(string='Visiting Card', default=False, tracking=True)
    copy_id_card = fields.Boolean(string='ID Card', default=False, tracking=True)
    copy_mobile_sim = fields.Boolean(string='Mobile Sim', default=False, tracking=True)
    copy_motor_bike = fields.Boolean(string='Motor Bike', default=False, tracking=True)
    copy_car = fields.Boolean(string='Car', default=False, tracking=True)
    passport_copy = fields.Boolean(string='Passport', default=False, tracking=True)
    work_permit_copy = fields.Boolean(string='Work Permit', default=False, tracking=True)

    copy_any_other_documents = fields.Char(string='Any Other Documents', tracking=True)
    copy_bank_account = fields.Char(string='Bank Account', tracking=True)
    copy_job_permanent = fields.Char(string='Job Permanent', tracking=True)
    copy_shoe_cause_issue = fields.Char(string='Show cause/Disciplinary issue related', tracking=True)
    copy_increment_letter = fields.Char(string='Increment Letter', tracking=True)
    copy_transfer_letter = fields.Char(string='Transfer Letter', tracking=True)
    copy_termination_resignation = fields.Char(string='Termination/Resignation', tracking=True)
    copy_others_checklist = fields.Char(string='Others', tracking=True)

    ### varified by HRD
    copy_requisition_form_hrd = fields.Boolean(string='Copy of Requisition form', default=False, tracking=True)
    copy_of_advertisement_hrd = fields.Boolean(string='Copy of Advertisement', default=False, tracking=True)
    copy_of_resume_hrd = fields.Boolean(string='Copy of Resume/CV/Cover Letter', default=False, tracking=True)
    job_application_form_hrd = fields.Boolean(string='Job Application Form', default=False, tracking=True)

    masters_pg_hrd = fields.Boolean(string='Masters/PG', default=False, tracking=True)
    bachelor_hrd = fields.Boolean(string='Bachelor', default=False, tracking=True)
    hsc_hrd = fields.Boolean(string='H.S.C', default=False, tracking=True)
    ssc_hrd = fields.Boolean(string='S.S.C', default=False, tracking=True)
    diploma_hrd = fields.Boolean(string='Diploma', default=False, tracking=True)
    other_academic_hrd = fields.Boolean(string='Others', default=False, tracking=True)

    experience_hrd = fields.Boolean(string='Professional Experience', default=False, tracking=True)
    training_professional_hrd = fields.Boolean(string='Professional Training', default=False, tracking=True)
    other_professional_hrd = fields.Boolean(string='Others Professional', default=False, tracking=True)

    copy_of_photograph_hrd = fields.Boolean(string='Copy of Photograph', default=False, tracking=True)
    copy_of_nid_hrd = fields.Boolean(string='Copy of National ID', default=False, tracking=True)
    copy_of_appointment_hrd = fields.Boolean(string='Copy of Appointment Letter', default=False, tracking=True)
    copy_of_joining_letter_hrd = fields.Boolean(string='Copy of Joining Letter', default=False, tracking=True)
    copy_of_accept_letter_hrd = fields.Boolean(string='Copy of Acceptance Letter', default=False, tracking=True)

    copy_police_verification_hrd = fields.Boolean(string='Police Verification', default=False, tracking=True)
    copy_of_chairman_certificate_hrd = fields.Boolean(string='Copy of Chairman Certificate', default=False, tracking=True)
    copy_of_employee_information_hrd = fields.Boolean(string='Copy of Employee Information Form', default=False,
                                                  tracking=True)
    copy_visiting_card_hrd = fields.Boolean(string='Visiting Card', default=False, tracking=True)
    copy_id_card_hrd = fields.Boolean(string='ID Card', default=False, tracking=True)
    copy_mobile_sim_hrd = fields.Boolean(string='Mobile Sim', default=False, tracking=True)
    copy_motor_bike_hrd = fields.Boolean(string='Motor Bike', default=False, tracking=True)
    copy_car_hrd = fields.Boolean(string='Car', default=False, tracking=True)
    passport_copy_hrd = fields.Boolean(string='Passport', default=False, tracking=True)
    work_permit_copy_hrd = fields.Boolean(string='Work Permit', default=False, tracking=True)

    #### relation fields
    professional_qualification_ids = fields.One2many('hr.employment.professional.qualification',
                                                     'employee_id',
                                                     'Employment Professional Qualification',
                                                     help="Employment Professional")
    training_other_ids = fields.One2many('hr.employment.training.other',
                                         'employee_id',
                                         'Employment Training ',
                                         help="Employment Training")
    other_professional_license_ids = fields.One2many('hr.employment.other.professional.license',
                                                     'employee_id',
                                                     'Employment Other Professional License',
                                                     help="Employment Professional license")
    incident_line_ids = fields.One2many('incident.raise.line', 'person_id', "Incident")
    olila_relative_ids = fields.One2many('olila.group.relative', 'olila_relative_id', "OLila Relative")

    @api.depends('contract_ids', 'initial_employment_date')
    def _compute_months_service(self):
        date_now = fields.Date.today()
        hr_contract = self.env['hr.contract'].sudo()
        to_dt = 0
        from_dt = 0
        for employee in self:
            nb_month = 0

            if employee.initial_employment_date:
                first_contract = employee._first_contract()
                if first_contract:
                    to_dt = fields.Date.from_string(first_contract.date_start)
                else:
                    to_dt = fields.Date.from_string(date_now)

                from_dt = fields.Date.from_string(
                    employee.initial_employment_date)

                nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                            relativedelta(to_dt, from_dt).months + \
                            self.check_next_days(to_dt, from_dt)

            contracts = hr_contract.search([('employee_id', '=', employee.id)],
                                           order='date_start asc')
            for contract in contracts:
                from_dt = fields.Date.from_string(contract.date_start)
                if contract.date_end and contract.date_end < date_now:
                    to_dt = fields.Date.from_string(contract.date_end)
                else:
                    to_dt = fields.Date.from_string(date_now)
                nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                            relativedelta(to_dt, from_dt).months + \
                            self.check_next_days(to_dt, from_dt)

            days = str(relativedelta(to_dt, from_dt).days)
            if int(days) < 0:
                days = '0'
            employee.length_of_service = str(int(nb_month / 12)) + " Year(s) " + str(
                int(nb_month % 12)) + " Month(s) " + days + ' Day(s)'

    @api.depends("name", "identification_id")
    def _compute_display_name(self):
        for line in self:
            if line.identification_id:
                line.display_name = "{} [{}]".format(line.name, line.identification_id)
            else:
                line.display_name = line.name

    def name_get(self):
        return [(emp.id, emp.display_name) for emp in self]

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if args and len(args) == 1 and args[0] and args[0][0] == 'name' and args[0][2] is not None:
            new_args = ['|', ('identification_id', 'ilike', args[0][2]), args[0]]
            return super(HrEmployee, self)._search(new_args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)
        else:
            return super(HrEmployee, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                   access_rights_uid=access_rights_uid)

