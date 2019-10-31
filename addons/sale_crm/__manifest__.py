# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Opportunity to Quotation',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
Bridge module between the Sales, Rental and CRM apps.
It allows you to generate a quotation based on the selected opportunity.
When several opportunities are selected, a separate quotation is generated for each of them.
The case is then closed and linked to the generated sales order.
""",
    'depends': ['sale', 'crm'],
    'data': [
        'views/sale_order_views.xml',
        'views/crm_lead_views.xml',
        'wizard/crm_opportunity_to_quotation_views.xml'
    ],
    'auto_install': True,
}
