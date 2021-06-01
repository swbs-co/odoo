# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)


class SmsController(http.Controller):

    @http.route('/sms/status', type='json', auth='public', csrf=False)
    def update_sms_status(self, message):
        sms_module_version = request.env['ir.module.module'].sudo().search([('name', '=', 'sms')]).installed_version
        sms_marketing_module_version = request.env['ir.module.module'].sudo().search([('name', '=', 'mass_mailing_sms')])
        sms_marketing_module_version = sms_marketing_module_version.installed_version if sms_marketing_module_version else None
        if sms_module_version and float(sms_module_version[5:]) >= 2.2:
            sms = request.env["sms.sms"].sudo().search([('request_id', '=', message['request_id'])])
            if sms.exists():
                sms.provider_state = message['provider_state']
                if message['provider_state'] != 'delivered':
                    notifications = request.env['mail.notification'].sudo().search([
                            ('notification_type', '=', 'sms'),
                            ('sms_id', '=', sms.id),
                            ('notification_status', 'not in', ('canceled',))]
                        )
                    if notifications:
                        if message['provider_state'] not in  ('sent', 'delivered'):
                            notifications.write({
                                'notification_status': 'exception',
                                'failure_type': "sms_" + message['provider_state'],
                                'failure_reason': False,
                            })
                        else:
                            notifications.write({
                                'notification_status': 'sent',
                                'failure_type': False,
                                'failure_reason': False,
                            })
                    if sms_marketing_module_version and float(sms_marketing_module_version[5:]) >= 1.1:
                        traces = request.env['mailing.trace'].sudo().search([('sms_sms_id_int', '=', sms.id)])
                        if traces:
                            traces.set_failed(failure_type="sms_" + message['provider_state'])

                    sms.mail_message_id._notify_message_notification_update()
                else:
                    sms.unlink()
        return 'OK'
