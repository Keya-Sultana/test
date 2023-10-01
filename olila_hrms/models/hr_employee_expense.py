from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeExpense(models.Model):
    _name = 'hr.employee.expense'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'Hr Employee Expense'

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user.employee_id

    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee_get,
                                  tracking=True, store=True)
    job_id = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id',
                             store=True, readonly=True)
    zone_id = fields.Many2one('res.zone', string='Region', required=True)
    territory_id = fields.Many2one('route.territory', string='Territory', domain="[('zone_id', '=', zone_id)]",
                                   required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approve', 'Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    ## Total Compute fields
    total_fare = fields.Float(string="Total Fare", compute='_compute_total_fare', tracking=True)
    total_fuel_fare = fields.Float(string="Total Fare Price", compute='_compute_total_fuel', tracking=True)
    total_repair_cost = fields.Float(string="Total Repair Cost", compute='_compute_total_repair', tracking=True)
    total_purchase_cost = fields.Float(string="Total Purchase Cost", compute='_compute_total_other', tracking=True)
    total_da_amount = fields.Float(string="Total DA Amount", compute='_compute_total_da', tracking=True)

    amount_total = fields.Float(string="Total Amount", compute='_compute_total_amount', tracking=True)

    #### relation fields
    ta_ids = fields.One2many('hr.employee.expense.ta',
                             'expense_id',
                             'Employment TA Expense')
    purchase_ids = fields.One2many('hr.employee.expense.purchase',
                                   'expense_id',
                                   'Employment Purchase Expense')
    da_ids = fields.One2many('hr.employee.expense.da',
                             'expense_id',
                             'Employment DA Expense')
    other_purchase_ids = fields.One2many('hr.employee.expense.other.purchase',
                                         'expense_id',
                                         'Employment Other Purchase')
    repair_ids = fields.One2many('hr.employee.expense.repair',
                                 'expense_id',
                                 'Employment Repair Expense')

    @api.onchange('ta_ids')
    def _onchange_ta_ids(self):
        for iterate in self:
            if iterate.ta_ids:
                existing_dates = {ta.date for ta in iterate.ta_ids if ta.date}
                new_lines = iterate.ta_ids.filtered(lambda ta: not ta.date)

                if new_lines:
                    new_date = iterate.date

                    for ta in new_lines:
                        ta.date = new_date

                for ta in iterate.ta_ids.filtered(lambda ta: ta.date and ta.date not in existing_dates):
                    ta.date = ta.date

    @api.onchange('purchase_ids')
    def onchange_purchase(self):
        for iterate in self:
            if iterate.purchase_ids:
                existing_dates = {fuel.date for fuel in iterate.purchase_ids if fuel.date}
                new_lines_purchase = iterate.purchase_ids.filtered(lambda fuel: not fuel.date)

                if new_lines_purchase:
                    new_date = iterate.date

                    for fuel in new_lines_purchase:
                        fuel.date = new_date

                for fuel in iterate.purchase_ids.filtered(lambda fuel: fuel.date and fuel.date not in existing_dates):
                    fuel.date = fuel.date

    @api.onchange('repair_ids')
    def onchange_repair_ids(self):
        for iterate in self:
            if iterate.repair_ids:
                existing_dates = {re.date for re in iterate.repair_ids if re.date}
                new_lines_repair = iterate.repair_ids.filtered(lambda re: not re.date)

                if new_lines_repair:
                    new_date = iterate.date

                    for re in new_lines_repair:
                        re.date = new_date

                for re in iterate.repair_ids.filtered(lambda re: re.date and re.date not in existing_dates):
                    re.date = re.date

    @api.onchange('da_ids')
    def onchange_da_ids(self):
        for iterate in self:
            if iterate.da_ids:
                existing_dates = {da.date for da in iterate.da_ids if da.date}
                new_lines_da = iterate.da_ids.filtered(lambda da: not da.date)

                if new_lines_da:
                    new_date = iterate.date

                    for da in new_lines_da:
                        da.date = new_date

                for da in iterate.da_ids.filtered(lambda da: da.date and da.date not in existing_dates):
                    da.date = da.date

    @api.onchange('other_purchase_ids')
    def _onchange_other_ids(self):
        for iterate in self:
            if iterate.other_purchase_ids:
                existing_dates = {other.date for other in iterate.other_purchase_ids if other.date}
                new_lines_other = iterate.other_purchase_ids.filtered(lambda other: not other.date)

                if new_lines_other:
                    new_date = iterate.date

                    for other in new_lines_other:
                        other.date = new_date

                for other in iterate.other_purchase_ids.filtered(
                        lambda other: other.date and other.date not in existing_dates):
                    other.date = other.date

    @api.depends('ta_ids')
    def _compute_total_fare(self):
        self.total_fare = 0.0
        for ta in self.ta_ids:
            self.total_fare += ta.ta_fare

    @api.depends('purchase_ids')
    def _compute_total_fuel(self):
        self.total_fuel_fare = 0.0
        for fuel in self.purchase_ids:
            self.total_fuel_fare += fuel.purchase_fare

    @api.depends('repair_ids')
    def _compute_total_repair(self):
        self.total_repair_cost = 0.0
        for repair in self.repair_ids:
            self.total_repair_cost += repair.repair_cost

    @api.depends('da_ids')
    def _compute_total_da(self):
        self.total_da_amount = 0.0
        for da in self.da_ids:
            self.total_da_amount += da.da_amount

    @api.depends('other_purchase_ids')
    def _compute_total_other(self):
        self.total_purchase_cost = 0.0
        for other in self.other_purchase_ids:
            self.total_purchase_cost += other.purchase_cost

    # @api.depends('ta_ids')
    def _compute_total_amount(self):
        self.amount_total = self.total_fare + self.total_fuel_fare + self.total_repair_cost + self.total_da_amount + self.total_purchase_cost
        # for ta in self.ta_ids:
        #     self.total_fare += ta.ta_fare

    def action_confirm(self):
        if len(self.ta_ids) == 0:
            raise ValidationError(_("Please Create Line."))
        else:
            self.state = 'to approve'

    def action_done(self):
        self.state = 'approve'

    def action_reject(self):
        self.state = 'cancel'


class HrEmployeeExpenseTA(models.Model):
    _name = 'hr.employee.expense.ta'
    _description = 'Hr Employee Expense TA'

    date = fields.Date(string='Date', tracking=True)
    mode_of_transport = fields.Char(string="Mode of Transport", tracking=True)
    from_destination = fields.Char(string="From Destination", tracking=True)
    to_destination = fields.Char(string="To Destination", tracking=True)
    kilo_meter = fields.Float(string="K.M", tracking=True)
    ta_fare = fields.Float(string="Fare", tracking=True)
    expense_id = fields.Many2one('hr.employee.expense', string='Employee Expense', )

    # @api.depends(expense_id)
    # def _get_date(self):
    #     for expense in self.expense_id:
    #         self.date = expense.date


class HrEmployeeExpenseDA(models.Model):
    _name = 'hr.employee.expense.da'
    _description = 'Hr Employee Expense DA'

    date = fields.Date(string='Date', tracking=True)
    da_details = fields.Char(string="DA Details", tracking=True)
    da_amount = fields.Float(string="DA Amount(Integration with DA Master)", tracking=True)
    night_stay = fields.Char(string="Night Stay(Integration with DA Master)", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    expense_id = fields.Many2one('hr.employee.expense', string='Employee Expense', )


class HrEmployeeExpensePurchase(models.Model):
    _name = 'hr.employee.expense.purchase'
    _description = 'Hr Employee Expense of Purchase'

    date = fields.Date(string='Date', tracking=True)
    start_mileage = fields.Char(string="Start Mileage", tracking=True)
    end_mileage = fields.Char(string="End Mileage", tracking=True)
    daily_km = fields.Float(string="Daily K.M", tracking=True)
    fare_qty = fields.Float(string="Fare Qty", tracking=True)
    purchase_fare = fields.Float(string="Fare Price", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    expense_id = fields.Many2one('hr.employee.expense', string='Employee Expense', )


class HrEmployeeExpenseOthersPurchase(models.Model):
    _name = 'hr.employee.expense.other.purchase'
    _description = 'Hr Employee Expense of Others Purchase'

    date = fields.Date(string='Date', tracking=True)
    purchase_details = fields.Char(string="Purchase Details", tracking=True)
    purchase_cost = fields.Float(string="Purchase Cost", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    expense_id = fields.Many2one('hr.employee.expense', string='Employee Expense', )


class HrEmployeeExpenseRepair(models.Model):
    _name = 'hr.employee.expense.repair'
    _description = 'Hr Employee Expense of Repair'

    date = fields.Date(string='Date', tracking=True)
    repair_details = fields.Char(string="Repair Details", tracking=True)
    repair_cost = fields.Float(string="Repair Cost", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)
    expense_id = fields.Many2one('hr.employee.expense', string='Employee Expense', )
