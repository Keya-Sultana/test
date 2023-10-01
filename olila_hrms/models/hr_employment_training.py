from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class HrEmploymentTrainingOther(models.Model):
    _name = 'hr.employment.training.other'
    _description = 'Hr Employment Training Other'

    ####for training and other
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    training_duration = fields.Integer(string="Duration", compute="_compute_number_of_days", )
    training_institute_name = fields.Char(string="Name of the Institute")
    training_location = fields.Char('Location')
    to_course_name = fields.Char(string='Course Name')
    training_result = fields.Char('Result')
    training_country_id = fields.Many2one('res.country', string="Country")

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)

    @api.depends("date_from", "date_to")
    def _compute_number_of_days(self):
        for line in self:
            days = False
            if line.date_from and line.date_to:
                days = (line.date_to - line.date_from).days + 1
            line.training_duration = days

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
