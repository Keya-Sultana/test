from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class DepartOrgChartController(http.Controller):
    _managers_level = 2

    def _prepare_department_data(self, department):
        return dict(
            id=department.id,
            name=department.name,
            link='/mail/view?model=hr.department&dep_id=%s' % department.id,
            direct_sub_count=len(department.child_ids),
            indirect_sub_count=department.child_all_count,
        )

    @http.route('/department/get_org_chart', type='json', auth='user')
    def get_org_chart(self, department_id):
        if not department_id:  # to check
            return {}
        department_id = int(department_id)

        depart = request.env['hr.department']
        # check and raise
        if not depart.check_access_rights('read', raise_exception=False):
            return {}
        try:
            depart.browse(department_id).check_access_rule('read')
        except AccessError:
            return {}
        else:
            department = depart.browse(department_id)

        # compute department data for org chart
        ancestors, current = request.env['hr.department'], department
        while current.parent_id:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self._prepare_department_data(department),
            managers=[self._prepare_department_data(ancestor) for idx, ancestor in enumerate(ancestors) if idx < self._managers_level],
            managers_more=len(ancestors) > self._managers_level,
            children=[self._prepare_department_data(child) for child in department.child_ids],
        )
        values['managers'].reverse()
        return values
