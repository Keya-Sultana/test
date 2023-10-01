from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools.translate import _
import base64
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from dateutil.relativedelta import relativedelta


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ]
    RELIGION = [
        ('islam', 'Islam'), ('buddhism', 'Buddhism'),
        ('christianity', 'Christianity'), ('hinduism', 'Hinduism'),
        ('judaism', 'Judaism'), ('taoism', 'Taoism')
    ]
    BLOOD = [('o_neg', 'O-'), ('o_pos', 'O+'), ('b_pos', 'B+'),
              ('b_neg', 'B-'), ('a_neg', 'A-'), ('a_pos', 'A+',),
              ('ab_neg', 'AB-'), ('ab_pos', 'AB+')]
    MARITAL = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ]

    @api.model
    def _default_image(self):
        image_path = get_module_resource('olila_hrms', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    agency = fields.Many2one('res.partner', string='Agency',
                             help='You can choose a Verification Agent', tracking=True)
    nidid = fields.Char('NID No', groups="hr.group_hr_user", tracking=True)
    nid_issue_place = fields.Char(string='NID Place of Issue', tracking=True)

    full_name = fields.Char('Full Name', tracking=True)
    fam_father_name = fields.Char(string="Father's Name", tracking=True)
    fam_mother_name = fields.Char(string="Mother's Name", tracking=True)
    notice_period = fields.Boolean(string="Notice Period", default=False)
    mention_period = fields.Char(string="Mention the Period", tracking=True)
    willing_to_relocate = fields.Boolean('Willing to Relocate', tracking=True)
    permanent_address = fields.Char('Permanent Address', tracking=True)
    present_address = fields.Char('Present Address', tracking=True)
    country_id = fields.Many2one('res.country', 'Nationality (Country)', groups="hr.group_hr_user", tracking=True)
    images = fields.Binary("Image", max_width=128, max_height=128)
    emergency_contact = fields.Char('Emergency Contact Name')
    relation = fields.Char('Relation')
    birth_date = fields.Date('Date of Birth')
    marriage_date = fields.Date(string="Date of Marriage")
    applicant_spouse = fields.Char(string="Spouse's Name")
    applicant_spouse_nid = fields.Char(string="Spouse's NID No")
    applicant_spouse_birthday = fields.Date(string="Spouse's Birthday")
    applicant_spouse_occupation = fields.Char(string="Spouse's Profession")
    is_applied_before = fields.Boolean(string="Have you applied for OLiLa job before? ",default=False)
    resume_uploaded = fields.Many2many('ir.attachment', string="Upload Resume",
                                       help='You can attach the copy of your document', copy=False)

    # Selection Fields
    gender = fields.Selection(
        selection=GENDER,
        string="Gender",
        index=True,
        tracking=True,
    )

    religion = fields.Selection(
        selection=RELIGION,
        string='Religion',
        index=True,
        tracking=True,
        default='')

    blood_group = fields.Selection(
        selection=BLOOD,
        string="Blood Group",
        index=True,
        tracking=True,
        default='')

    marital = fields.Selection(
        selection=MARITAL,
        string='Marital Status',
        index=True,
        tracking=True,
        default='')

    ###for Prior Convictions
    prior_conviction = fields.Boolean('Prior Convictions', default=False)
    offense_description = fields.Char(string='Offense Description', tracking=True)
    statute_ordinance = fields.Char(string='Statute/Ordinance (If Known)', tracking=True)
    date_of_charge = fields.Date(string='Date of Charge', tracking=True)
    date_of_conviction = fields.Date(string='Date of Conviction', tracking=True)
    conviction_id = fields.Many2one('res.country', string='County, City and State of Conviction', tracking=True)

    ###for passport
    passport = fields.Boolean(string='Passport', default=False)
    passport_no = fields.Char(string='Passport Number', tracking=True)
    passport_issue_place = fields.Char(string='Place of Issue', tracking=True)
    date_issue = fields.Date(string='Date of Issue', tracking=True)
    date_expiry = fields.Date(string='Passport Expiry Date', tracking=True)

    ###for work permit
    work_permit = fields.Boolean(string='Work Permit', default=False)
    permit_no = fields.Char('Work Permit No', tracking=True)
    visa_no = fields.Char('Visa No', tracking=True)
    visa_expire = fields.Date('Visa Expire Date', tracking=True)
    wp_place_issue = fields.Char(string='Place of Issue')

    ### Relation field

    education_ids = fields.One2many('hr.applicant.education.qualification', 'applicant_id', "Educational "
                                                                                            "Qualification")
    professional_ids = fields.One2many('hr.applicant.professional.qualification', 'applicant_id', "Professional "
                                                                                                  "Qualification")
    work_experience_ids = fields.One2many('hr.applicant.work.experience', 'applicant_id', "Work Experience ")
    skill_ids = fields.One2many('hr.applicant.skill', 'applicant_id', string="Skills")
    license_ids = fields.One2many('hr.applicant.license', 'applicant_id', string="Licenses")
    reference_ids = fields.One2many('hr.applicant.references', 'applicant_id', string="References")
    training_ids = fields.One2many('hr.application.training.other', 'applicant_id', string="Training")

    def write(self, vals):
        try:
            data = vals['description'].replace('Other Information:\n___________\n\n', '').strip()
            for val in data.split("\n"):
                value = val.split(":")
                if len(value) > 1:
                    super(HrApplicant, self).write({value[0].strip(): str(value[1].strip())})
        except KeyError:
            pass
        res = super(HrApplicant, self).write(vals)

    def create_employee_from_applicant(self):
        """ Create an Employee from the Applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']

            if applicant.partner_name or contact_name:

                ### Educational data
                education_list = []
                for edu in applicant.education_ids:
                    vals = {'institute_university': edu.institute_university,
                            'degree_level': edu.degree_level,
                            'major_subject': edu.major_subject,
                            'passing_year': edu.year_to}
                    education_list.append(vals)

                ### Professional data
                professional_list = []
                for profess in applicant.professional_ids:
                    vals = {'pq_certification_name': profess.name_of_qualification,
                            'pq_institute': profess.institute_university,
                            'pq_country_id': profess.country_id.id}
                    # vals['pq_location'] = rec.location
                    professional_list.append(vals)

                ### work experience data
                # work_list = []
                # for rec in applicant.work_experience_ids:
                #     vals = {'organization': rec.organization,
                #             'department': rec.department_name,
                #             'designation': rec.job_title}
                #     work_list.append(vals)

                ### licenses data
                license_list = []
                for rec in applicant.license_ids:
                    vals = {'license_type': rec.license_type.id,
                            'license_no': rec.license_no,
                            'given_by': rec.granted_by}
                    license_list.append(vals)

                ### Training data
                training_list = []
                for rec in applicant.training_ids:
                    vals = {}
                    vals['to_course_name'] = rec.to_course_name
                    vals['training_institute_name'] = rec.training_institute_name
                    vals['training_location'] = rec.training_location
                    vals['date_from'] = rec.date_from
                    vals['date_to'] = rec.date_to
                    vals['training_country_id'] = rec.training_country_id.id
                    training_list.append(vals)

                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'default_address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                          and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.email_from or False,
                    'default_sinid': applicant.nidid or False,
                    'default_image_1920': applicant.images or False,
                    'default_work_phone': applicant.partner_phone,
                    'default_mobile_phone': applicant.partner_mobile,
                    'default_fam_father': applicant.fam_father_name,
                    'default_fam_mother': applicant.fam_mother_name,
                    'default_permanent_address': applicant.permanent_address,
                    'default_present_address': applicant.present_address,
                    'default_country_id': applicant.country_id.id,
                    'default_religion': applicant.religion,
                    'default_marital': applicant.marital,
                    'default_blood_group': applicant.blood_group,
                    'default_gender': applicant.gender,
                    'default_birthday': applicant.birth_date,
                    'default_relation': applicant.relation,
                    'default_emergency_contact': applicant.emergency_contact,
                    'default_marriage_date': applicant.marriage_date,
                    'default_fam_spouse': applicant.applicant_spouse,
                    'default_spouse_nid': applicant.applicant_spouse_nid,
                    'default_spouse_birthday': applicant.applicant_spouse_birthday,
                    'default_spouse_occupation': applicant.applicant_spouse_occupation,
                    'default_passport': applicant.passport,
                    'default_date_issue': applicant.date_issue,
                    'default_date_expiry': applicant.date_expiry,
                    'default_passport_issue_place': applicant.passport_issue_place,
                    'default_work_permit': applicant.work_permit,
                    'default_wp_place_issue': applicant.wp_place_issue,
                    'default_visa_no': applicant.visa_no,
                    'default_permit_no': applicant.permit_no,
                    'default_visa_expire': applicant.visa_expire,
                    'default_academicinfor_ids': education_list,
                    'default_professional_qualification_ids': professional_list,
                    'default_other_professional_license_ids': license_list,
                    'default_training_other_ids': training_list,
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window

    def acknowledgement_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('olila_hrms', 'acknowledgement_application_mailer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', ''
                                                                         '')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def interview_letter_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('olila_hrms', 'interview_letter_mailer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', ''
                                                                         '')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def regret_letter_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('olila_hrms', 'regret_letter_mailer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', ''
                                                                         '')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class HrApplicantEducationQualification(models.Model):
    _name = "hr.applicant.education.qualification"
    _description = "Education Qualification for an Applicant's"

    institute_university = fields.Char(string="Name of the Institution")
    location = fields.Char(string="Location")
    degree_level = fields.Char(string="Degree Received")
    major_subject = fields.Char(string='Specialty/Major', )
    year_from = fields.Date(string="Year From")
    year_to = fields.Date(string="Year To")

    applicant_id = fields.Many2one('hr.applicant',
                                   string='applicant',
                                   required=True)


class HrApplicantProfessionalQualification(models.Model):
    _name = "hr.applicant.professional.qualification"
    _description = "Professional Qualification for an Applicant's"

    name_of_qualification = fields.Char(string="Name of the Qualification")
    institute_university = fields.Char(string="Name of the Institution")
    location = fields.Char(string="Location")
    year_from = fields.Date(string="Year From")
    year_to = fields.Date(string="Year To")
    country_id = fields.Many2one('res.country', 'Country', tracking=True)

    applicant_id = fields.Many2one('hr.applicant',
                                   string='applicant',
                                   required=True)


class HrApplicantWorkExperience(models.Model):
    _name = "hr.applicant.work.experience"
    _description = "Work Experience for an Applicant's"

    employee_name = fields.Char(string='Employee Name')
    employee_address = fields.Char(string='Employee Address')
    job_title = fields.Char(string='Job Title')
    department_name = fields.Char(string='Department')
    Job_responsibilities = fields.Char(string='Job Responsibilities')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    supervisor_manager = fields.Char(string='Supervisor/Manager')
    title = fields.Char(string='title')
    last_salary = fields.Float(string='last Salary')
    service_from = fields.Date(string='Service From')
    service_to = fields.Date(string='Service to')
    service_duration = fields.Char(
        'Months of Service',
        compute='_compute_service_duration',
    )
    reason_for_leaving = fields.Text(string='Reason For Leaving')
    applicant_id = fields.Many2one('hr.applicant',
                                   string='applicant',
                                   required=True)

    @api.depends("service_from", "service_to")
    def _compute_service_duration(self):
        nb_month = 0
        from_dt = fields.Date.from_string(self.service_from)
        to_dt = fields.Date.from_string(self.service_to)
        nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                    relativedelta(to_dt, from_dt).months
        days = str(relativedelta(to_dt, from_dt).days)
        if int(days) < 0:
            days = '0'
        self.service_duration = str(int(nb_month / 12)) + " Year(s) " + str(
            int(nb_month % 12)) + " Month(s) " + days + ' Day(s)'


class ApplicantSkill(models.Model):
    _name = 'hr.applicant.skill'
    _description = "Skill level for an Applicant's"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level', required=True)
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer(related='skill_level_id.level_progress')

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(
                    _("The skill %(name)s and skill type %(type)s doesn't match", name=record.skill_id.name,
                      type=record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s",
                                        level=record.skill_level_id.name, type=record.skill_type_id.name))


class HrApplicationLicense(models.Model):
    _name = 'hr.applicant.license'
    _description = " License Detail  for an Applicant's"

    license_no = fields.Integer(string="License No")
    license_type = fields.Many2one('license.type', string="License Type")
    granted_by = fields.Char(string="Granted by")

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')


class HrApplicationReferences(models.Model):
    _name = 'hr.applicant.references'
    _description = " References Detail  for an Applicant's"

    full_name = fields.Char(string="Full Name")
    designation = fields.Char(string="Designation")
    organization = fields.Char(string="Organization")
    address = fields.Char(string="Address")
    reference_email = fields.Char(string="Email")
    phone_no = fields.Char(string="Phone Number")
    relationship = fields.Char(string="Relationship")

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')

    def write(self, vals):
        try:
            data = vals['description'].replace('Other Information:\n___________\n\n', '').strip()
            for val in data.split("\n"):
                value = val.split(":")
                if len(value) > 1:
                    super(HrApplicationReferences, self).write({value[0].strip(): str(value[1].strip())})
        except KeyError:
            pass


class HrApplicationTrainingOther(models.Model):
    _name = 'hr.application.training.other'
    _description = 'Applicant Training & Other'

    to_course_name = fields.Char(string='Name of the Training')
    training_institute_name = fields.Char(string="Name of the Institute")
    training_location = fields.Char('Location')
    training_result = fields.Char('Result')
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    # training_duration = fields.Integer(string="Duration", compute="_compute_number_of_days", )
    training_country_id = fields.Many2one('res.country', string="Country")

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')

    # @api.depends("date_from", "date_to")
    # def _compute_number_of_days(self):
    #     for line in self:
    #         days = False
    #         if line.date_from and line.date_to:
    #             days = (line.date_to - line.date_from).days + 1
    #         line.training_duration = days

    @api.constrains("date_from", "date_to")
    def _check_start_end_dates(self):
        for line in self:
            if not line.date_to:
                raise ValidationError(
                    _("Missing To Date for employee training line with " "Name of the Institute '%s'.")
                    % (line.training_institute_name)
                )
            if not line.date_from:
                raise ValidationError(
                    _(
                        "Missing From Date for employee training line with "
                        "Name of the Institute '%s'."
                    )
                    % (line.training_institute_name)
                )
            if line.date_from > line.date_to:
                raise ValidationError(
                    _(
                        "From Date should be before or be the same as "
                        "To Date for employee training line with Name of the Institute '%s'."
                    )
                    % (line.training_institute_name)
                )
