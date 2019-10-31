# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Opportunity to Quotation',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module adds a shortcut on one or several opportunity cases in the CRM.
===========================================================================

This shortcut allows you to generate a quotation based on the selected opportunity.
When several opportunities are selected, a separate quotation is generated for each of them.
The case is then closed and linked to the generated sales order.

We suggest you to install this module, if you installed both the Sales and the CRM
modules.
    """,
    'depends': ['sale_management', 'sale_crm'],
    'data': [
        'views/partner_views.xml',
        'views/sale_order_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_views.xml',
    ],
    'auto_install': True,
    'uninstall_hook': 'uninstall_hook'
}
