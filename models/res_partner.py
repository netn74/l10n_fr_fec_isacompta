# -*- coding: utf-8 -*-
##############################################################################
#
#    Yotech module
#    Copyright (C) 2014-2018 Yotech (<http://yotech.pro>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo
from odoo.http import request
from odoo.addons.website.models.website import slugify

import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_compare

import logging
_logger = logging.getLogger(__name__)

import time
import math

class ResPartner(models.Model):
    _inherit = "res.partner"

    isacompta_account_number = fields.Char(string='IsaCompta account number', default='', required=False, translate=False)
