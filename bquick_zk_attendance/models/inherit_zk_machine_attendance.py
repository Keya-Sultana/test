from datetime import datetime, timedelta
import time
# from datetime import datetime
import logging
import pytz
from odoo import _, tools
from odoo import fields, models, api
from odoo.exceptions import UserError

# from datetime import timedelta, datetime


# from .zkconst import *

_logger = logging.getLogger(__name__)

try:
    from zk import ZK, const
except ImportError:
    _logger.error("Please Install pyzk library.")

_logger = logging.getLogger(__name__)


class ZkMachine(models.Model):
    _name = 'zk.machine'
    _inherit = ['zk.machine', 'mail.thread']

    name = fields.Char(string='Machine IP', required=True, tracking=True)
    port_no = fields.Integer(string='Port No', required=True, tracking=True)
    address_id = fields.Many2one('res.partner', string='Working Address', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id,
                                 tracking=True)

    def name_get(self):
        res = []
        for ddt in self:
            res.append((ddt.id, ("%s (%s)") % (ddt.name, ddt.port_no)))
        return res

    def _action_send_to_user(self, user, tips_count=1, consum_tips=True):
        rendered_body = self.env['mail.render.mixin'].with_context(preserve_comments=True)._render_template(
            'digest.digest_mail_main',
            'digest.digest',
            self.ids,
            engine='qweb_view',
            add_context={
                'title': self.name,
                'top_button_label': _('Connect'),
                # 'top_button_url': self.get_base_url(),
                'company': user.company_id,
                'user': user,
                # 'unsubscribe_token': self._get_unsubscribe_token(user.id),
                'tips_count': tips_count,
                # 'formatted_date': datetime.today().strftime('%B %d, %Y'),
                'display_mobile_banner': True,
                # 'kpi_data': self._compute_kpis(user.company_id, user),
                # 'tips': self._compute_tips(user.company_id, user, tips_count=tips_count, consumed=consum_tips),
                # 'preferences': self._compute_preferences(user.company_id, user),
            },
            post_process=True
        )[self.id]
        full_mail = self.env['mail.render.mixin']._render_encapsulate(
            'digest.digest_mail_layout',
            rendered_body,
            add_context={
                'company': user.company_id,
                'user': user,
            },
        )
        # create a mail_mail based on values, without attachments
        mail_values = {
            'auto_delete': True,
            'author_id': self.env.user.partner_id.id,
            'email_from': (
                    self.company_id.partner_id.email_formatted
                    or self.env.user.email_formatted
                    or self.env.ref('base.user_root').email_formatted
            ),
            'email_to': user.email_formatted,
            'body_html': full_mail,
            'state': 'outgoing',
            'subject': '%s: %s' % (user.company_id.name, self.name),
        }
        self.env['mail.mail'].sudo().create(mail_values)
        return True

    def _check_duplicate_attendance_and_generate_attendance(self, info, each, atten_time):
        zk_attendance = self.env['zk.machine.attendance']
        att_obj = self.env['hr.attendance']

        get_user_id = self.env['hr.employee'].search(
            [('device_id', '=', each.user_id)])
        if get_user_id:
            duplicate_atten_ids = zk_attendance.search(
                [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
            if duplicate_atten_ids:
                return
            else:
                zk_attendance.create({'employee_id': get_user_id.id,
                                      'device_id': each.user_id,
                                      'attendance_type': str(each.status),
                                      'punch_type': str(each.punch),
                                      'punching_time': atten_time,
                                      'machine_id': info.id,
                                      'address_id': info.address_id.id})

                atten_datetime = datetime.strptime(atten_time, '%Y-%m-%d %H:%M:%S')
                atten_element = atten_datetime + timedelta(seconds=-15)

                if each.punch == 0:  # check-in
                    # if not att_var:
                    ### Check duplicate or false check-in
                    duplicate_check_in = att_obj.search([('employee_id', '=', get_user_id.id),
                                                         ('check_in', '<', atten_time),
                                                         ('check_in', '>', atten_element)])
                    if not duplicate_check_in:

                        att_var = att_obj.search([('employee_id', '=', get_user_id.id),
                                                  ('check_out', '>', atten_time),
                                                  ('check_in', '=', False)])

                        if len(att_var) > 0:
                            att_var = att_var.filtered(lambda x: x.check_out > atten_datetime)
                            att_var = min(att_var, key=lambda x: x.check_out)

                        if len(att_var) == 1:
                            att_var.write({'check_in': atten_time})
                        else:
                            att_obj.create({'employee_id': get_user_id.id,
                                            'check_in': atten_time})

                if each.punch == 1:  # check-out
                    duplicate_check_out = att_obj.search([('employee_id', '=', get_user_id.id),
                                                          ('check_out', '<', atten_time),
                                                          ('check_out', '>', atten_element)])
                    if not duplicate_check_out:
                        att_var = att_obj.search([('employee_id', '=', get_user_id.id),
                                                  ('check_in', '<', atten_time),
                                                  ('check_out', '=', False)])

                        if len(att_var) > 0:
                            att_var = att_var.filtered(lambda x: x.check_in < atten_datetime)
                            att_var = max(att_var, key=lambda x: x.check_in)

                        if len(att_var) == 1:
                            att_var.write({'check_out': atten_time})
                        else:
                            att_obj.create({'employee_id': get_user_id.id,
                                            'check_out': atten_time})
        else:
            pass

    def download_attendance(self, msg_dict=None):
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
        digest_obj = self.env['digest.digest']

        ####### Attendance Receive Datetime
        if self.company_id.attendance_receive_date:
            zk_date = self.company_id.attendance_receive_date
            zk_date = datetime.strptime(zk_date.strftime('%Y-%m-%d %H:%M:%S'),
                                        '%Y-%m-%d %H:%M:%S')
            local_zk_dt = local_tz.localize(zk_date, is_dst=None)
            utc_zk_dt = local_zk_dt.strftime("%Y-%m-%d %H:%M:%S")

        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = 15
            try:
                zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
            except NameError:
                raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
            conn = self.device_connect(zk)
            if conn:

                try:
                    attendance = conn.get_attendance()
                except:
                    attendance = False
                if attendance:
                    for each in attendance:
                        atten_time = each.timestamp
                        atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'),
                                                       '%Y-%m-%d %H:%M:%S')
                        local_dt = local_tz.localize(atten_time, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        atten_time = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                        atten_time = fields.Datetime.to_string(atten_time)

                        if self.company_id.attendance_receive_date:
                            if utc_zk_dt <= atten_time:
                                self._check_duplicate_attendance_and_generate_attendance(info, each, atten_time)
                        else:
                            self._check_duplicate_attendance_and_generate_attendance(info, each, atten_time)

                    # zk.enableDevice()
                    conn.disconnect
                    return True
                else:
                    raise UserError(_('Unable to get the attendance log, please try again later.'))
            else:
                user = digest_obj.user_ids
                self._action_send_to_user(user, tips_count=1)
                raise UserError(_('Unable to connect, please check the parameters and network connections.'))


class ZkMachineAttendance(models.Model):
    _inherit = "zk.machine.attendance"

    machine_id = fields.Many2one('zk.machine', string='Zk Machine')


class ReportZkDevice(models.Model):
    _inherit = 'zk.report.daily.attendance'

    machine_id = fields.Many2one('zk.machine', string='ZK Machine')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'zk_report_daily_attendance')
        query = """
            create or replace view zk_report_daily_attendance as (
                select
                    min(z.id) as id,
                    z.employee_id as name,
                    z.write_date as punching_day,
                    z.address_id as address_id,
                    z.attendance_type as attendance_type,
                    z.punching_time as punching_time,
                    z.punch_type as punch_type,
                    z.machine_id as machine_id
                from zk_machine_attendance z
                    join hr_employee e on (z.employee_id=e.id)
                GROUP BY
                    z.employee_id,
                    z.write_date,
                    z.address_id,
                    z.attendance_type,
                    z.punch_type,
                    z.punching_time,
                    z.machine_id
            )
        """
        self._cr.execute(query)
