# -*- coding: utf-8 -*-

{
    'name': 'Lot Without Barcode',
    'version': '1.0',
    'sequence': 120,
    'category': 'stock',
    'summary': 'Allow lot in picking when no barcode on product',
    'description': """Allow lot in picking when barcode not define on product for stock barcode and normal inventory modules """,
    'depends': ['stock'],
    'data': ['views/stock_move_view.xml'],
    'qweb': [],
    'installable': True,
    'application': True,
}
