# -*- coding: utf-8 -*-

{
    'name': 'Real Estate',
    'depends': ['base'],
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/property_type_views.xml',
        'views/estate_property_views.xml',
        'views/property_tags_views.xml',
        'views/property_offers_views.xml',
        'views/estate_menus.xml', 
        'views/res_users_views.xml',
    ],
}