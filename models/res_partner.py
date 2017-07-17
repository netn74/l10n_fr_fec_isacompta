# -*- coding: utf-8 -*-

import time
import math

from openerp.osv import expression
from openerp.tools.float_utils import float_round as round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError, ValidationError
from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    isacompta_account_number = fields.Char(string='IsaCompta account number', default='', required=False, translate=False)
