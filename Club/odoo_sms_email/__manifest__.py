# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details
{
    'name': 'Email and SMS in Odoo ',
    'author': 'OpenERP SA',
    'summary': 'Email/SMS Odoo integration',
    'description': 'Send email and sms to selected partner',
    'version': '10.0',
    'category': 'Tools',
    'website': 'https://www.odoo.com/',
    'depends': ['pos_restaurant', 'hotel_reservation'],
    'data': ['views/report_pos_order.xml', 'views/pos_hotel_view.xml', 'views/sms_message_view.xml', 'data/pos_data.xml', 'wizard/mass_sms_view.xml'],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
