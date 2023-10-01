
from odoo import models, fields


class EmployeeRequisitionApprobation(models.Model):
    _name = "hr.employee.requisition.approbation"
    _description = 'Employee Requisition Approbation'
    _order = "sequence"
    
    requisition_id = fields.Many2one('hr.employee.requisition', string='Requisition', required=True, ondelete="cascade",)
    approver_id = fields.Many2one('res.users', string='Approver', required=True, ondelete="cascade",)
    sequence = fields.Integer(string='Approbation sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())
    