from dateutil.relativedelta import relativedelta
from odoo import fields
from datetime import datetime
from odoo.tests.common import TransactionCase


class TestHrRostering(TransactionCase):

    def setUp(self):
        super(TestHrRostering, self).setUp()
        self.employee_model = self.env["hr.employee"]
        self.approve_model = self.env["hr.employee.holidays.approver"]
        self.shift_alter_model = self.env['hr.shift.alter']
        self.shift_alter_batch_model = self.env['hr.shift.alter.batch']
        self.shift_employee_batch_model = self.env['hr.shift.employee.batch']
        self.shifting_history_model = self.env['hr.shifting.history']

        # create Approve Employee
        self.approve_employee = self.employee_model.create(
            {"name": "Approver 1"})

        # create Approver
        self.approve = self.approve_model.create(
            {"employee": 1, "approver": self.approve_employee.id, "sequence": "1"})

        # create employee
        self.employee = self.employee_model.create(
            {
                "name": "Employee 1",
                "holidays_approvers": self.approve.ids,
                "user_id": self.env["res.users"]
                .create(
                    {"name": "Employee 1", "login": "employee@gmail.com"}
                ).id,
            }
        )

        date_now = fields.Date.today()
        self.now = fields.Date.from_string(date_now)
        dt = relativedelta(days=6)
        # self.alter_day = self.now + dt

        # create shift alter vals
        self.vals = {
            'employee_id': self.employee.id,
            'alter_date': '2022-10-04',
            'duty_start': '2022-10-04 08:00:01',
            'duty_end': '2022-11-01 14:00:00',
            'is_included_ot': True,
            'ot_start': '2022-10-04 14:00:01',
            'ot_end': '2022-10-04 20:00:00',

        }

    def test_create_shift_alter(self):
        shift_alter = self.shift_alter_model.create(self.vals)
        alter_date = datetime.strftime(shift_alter.alter_date, "%Y-%m-%d")
        duty_start = datetime.strftime(shift_alter.duty_start, "%Y-%m-%d %H:%M:%S")
        duty_end = datetime.strftime(shift_alter.duty_end, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(self.vals['employee_id'], shift_alter.employee_id.id)
        self.assertEqual(self.vals['alter_date'], alter_date)
        self.assertEqual(self.vals['duty_start'], duty_start)
        self.assertEqual(self.vals['duty_end'], duty_end)

    def test_ot_shift_alter(self):
        shift_alter = self.shift_alter_model.create(self.vals)
        # self.shift_alter_model.is_included_ot = True
        # self.shift_alter_model.ot_start = '2022-10-04 14:00:01',
        # self.shift_alter_model.ot_end = '2022-10-04 20:00:00',
        ot_start = datetime.strftime(shift_alter.ot_start, "%Y-%m-%d %H:%M:%S")
        ot_end = datetime.strftime(shift_alter.ot_end, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(self.vals['is_included_ot'], shift_alter.is_included_ot)
        self.assertEqual(self.vals['ot_start'], ot_start)
        self.assertEqual(self.vals['ot_end'], ot_end)


