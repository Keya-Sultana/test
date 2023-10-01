#-*- coding:utf-8 -*-

from odoo import models, fields

class EmployeeLoanApprobation(models.Model):
    _name = "hr.employee.loan.approbation"
    _order= "sequence"
    
    loan_id = fields.Many2one('hr.employee.loan', string='Loan', required=True,ondelete="cascade",)
    approver_id = fields.Many2one('res.users', string='Approver', required=True,ondelete="cascade",)
    sequence = fields.Integer(string='Approbation sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())
    