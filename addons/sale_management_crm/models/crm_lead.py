# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def retrieve_sales_dashboard(self):
        res = super(CrmLead, self).retrieve_sales_dashboard()
        date_today = fields.Date.from_string(fields.Date.context_today(self))

        res['invoiced'] = {
            'this_month': 0,
            'last_month': 0,
        }
        account_invoice_domain = [
            ('state', '=', 'posted'),
            ('invoice_user_id', '=', self.env.uid),
            ('invoice_date', '>=', date_today.replace(day=1) - relativedelta(months=+1)),
            ('type', 'in', ['out_invoice', 'out_refund'])
        ]

        invoice_data = self.env['account.move'].search_read(account_invoice_domain, ['invoice_date', 'amount_untaxed', 'type'])

        for invoice in invoice_data:
            if invoice['invoice_date']:
                invoice_date = fields.Date.from_string(invoice['invoice_date'])
                sign = 1 if invoice['type'] == 'out_invoice' else -1
                if invoice_date <= date_today and invoice_date >= date_today.replace(day=1):
                    res['invoiced']['this_month'] += sign * invoice['amount_untaxed']
                elif invoice_date < date_today.replace(day=1) and invoice_date >= date_today.replace(day=1) - relativedelta(months=+1):
                    res['invoiced']['last_month'] += sign * invoice['amount_untaxed']

        res['invoiced']['target'] = self.env.user.target_sales_invoiced
        return res

    def action_new_quotation(self):
        action = super().action_new_quotation()
        if not action:
            action = self.env.ref("sale_management_crm.new_quotation_action").read()[0]
            action['context'] = self._get_quotation_action_context()
        return action

    def action_view_order(self):
        action = super().action_view_order()
        if not action:
            if self.env.context.get('order_status') == 'quotation':
                action_id = 'sale.action_quotations_with_onboarding'
                order_states = ('draft', 'sent')
            else:
                action_id = 'sale.action_orders'
                order_states = ('sale', 'done')
            action = self.env.ref(action_id).read()[0]
            action.update(self._get_base_view_order_action(states=order_states))
            if action.get('res_id'):
                action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        return action
