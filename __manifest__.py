# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2017 Yotech (http://www.yotech.pro)

{
    'name': 'France - FEC - IsaCompta',
    'version': '12.0.0',
    'category': 'Localization',
    'summary': "IsaCompta sur la base du Fichier d'Échange Informatisé (FEC)",
    'author': "Yotech",
    'website': 'http://www.yotech.pro',
    'depends': ['l10n_fr_fec','l10n_fr', 'account_accountant'],
    'data': [
        'wizard/fec_view.xml',
        'views/account.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'auto_install': True,
}
