from odoo import api, fields, models, _


class HrJob(models.Model):
    _inherit = "hr.job"

    job_code = fields.Char('Code')
    duties_responsibile = fields.Text(string='Principal Duties & Responsibilities', tracking=True)
    type_id = fields.Many2one('hr.recruitment.degree', "Highest Education", tracking=True)
    certifications = fields.Char(string='Certifications', tracking=True)
    experience = fields.Char(string='Experience', tracking=True)

    # TA
    ta_name = fields.Char(string="Code", tracking=True)
    fuel_price = fields.Float(string="Fuel Price", tracking=True)
    per_kilo_price = fields.Float(string="Per Kilo Millage Price", tracking=True)
    ta_type = fields.Selection([('own', 'Own Vehicle'),
                                ('rent', 'Rent Vehicle')], string="TA Type", tracking=True)
    transport_type = fields.Selection([('car', 'Car'), ('motorcycle', 'Motorcycle'),
                                       ('other', 'Others')], string="Transport Type", tracking=True)
    service_type = fields.Selection([('lubricant', 'Lubricant'),
                                     ('repair', 'Repair')], string="Service Type", tracking=True)
    fuel_type = fields.Selection([('cng', 'CNG'), ('petrol', 'Petrol'),
                                  ('octence', 'Octene')], string="Fuel Type", tracking=True)


    # DA
    fixt_wit_att = fields.Char(string="DA Fixt Wit Attendance Calculation", tracking=True)
    night_stay = fields.Char(string="DA (Night Stay) Fixt  ", tracking=True)
    hotel_night_rent = fields.Float(string="Hotel Night Rent (Stay) (Designation Wise) Maximum Fixt", tracking=True)
    own_arrang = fields.Float(string="Own Arrangement (Designation Wise) 60% of Maximum", tracking=True)


class RelativeOlilaGroup(models.Model):
    _name = "olila.group.relative"
    _description = "Relatives in Olila Group "

    relative_name = fields.Char(string="Name", tracking=True)
    job_id = fields.Many2one('hr.job', string="Designation", tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    relationship = fields.Char(string="Relationship", tracking=True)
    olila_relative_id = fields.Many2one('hr.employee', string="Olila relative group Name", tracking=True)


