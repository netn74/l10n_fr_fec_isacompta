# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2013-2015 Akretion (http://www.akretion.com)

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import base64
import StringIO
import csv

import logging
_logger = logging.getLogger(__name__)


class AccountFrFec(models.TransientModel):
    _name = "account.fr.fec.isacompta"
    _inherit = "account.fr.fec"

    @api.multi
    def generate_fec_isacompta(self):
        self.ensure_one()
        # We choose to implement the flat file instead of the XML
        # file for 2 reasons :
        # 1) the XSD file impose to have the label on the account.move
        # but Odoo has the label on the account.move.line, so that's a
        # problem !
        # 2) CSV files are easier to read/use for a regular accountant.
        # So it will be easier for the accountant to check the file before
        # sending it to the fiscal administration
        # header = [
        #     'EcritureDate',      #
        #     'EcritureNum',       #
        #     'JournalCode',       #
        #     'CompteNum',         #
        #     'CompAuxLib',        #
        #     'Debit',             #
        #     'Credit',            #
        #     'Ref',               #
        #     'Date Echeance',     #
        #     'Code IsaCompta',    #
        #     'Type Document'      #
        #     ]

# JOURNAL
# DATE
# NUMERO ECR
# N°PIECE
# COMPTE
# LIBELLE MOUVEMENT
# DEBIT
# CREDIT
# LETTRAGE

        header = [
            'Journal',             #  0
            'Code Cofidest',       #  1
            'Date',                #  2
            'CompteAuxiliaire',    #  3
            'NumPiece',            #  4
            'Cpte',                #  5
            'Cpte Nom export',     #  6
            'Label',               #  7
            'Debit',               #  8
            'Credit',              #  9
            'Origine',             # 10
            'Date Echeance',       # 11
            'TypeDocument'         # 12
            ]

        company = self.env.user.company_id
        if not company.vat:
            raise Warning(
               _("Missing VAT number for company %s") % company.name)
        if company.vat[0:2] != 'FR':
            raise Warning(
                _("FEC is for French companies only !"))

        fecfile = StringIO.StringIO()
        w = csv.writer(fecfile, delimiter=';')
        w.writerow(header)

#            SUBSTRING(rp.isacompta_account_number from 3 for 8) AS isacompta_account_number,

        sql_query = '''
        SELECT
            aj.name AS name,
            aj.extern_name AS CodeCofidest,
            TO_CHAR(am.date, 'DD/MM/YYYY') AS EcritureDate,
            rp.isacompta_account_number AS isacompta_account_number,
            TO_CHAR(aml.move_id, '9999999999999') AS EcritureNum,
            aa.code AS CompteIntermed,
            aa.code AS CompteNum,
            COALESCE(replace(rp.name, '|', '/'), '') AS Label,
            aml.debit  AS Debit,
            aml.credit AS Credit,
            am.name AS name,
            TO_CHAR(aml.date_maturity, 'DD/MM/YYYY') AS date_maturity,
            ai.type AS type,
            aml.move_id AS move_id

            
        FROM
            account_move_line aml
            LEFT JOIN account_move am ON am.id=aml.move_id
            LEFT JOIN res_partner rp ON rp.id=aml.partner_id
            JOIN account_journal aj ON aj.id = am.journal_id
            JOIN account_account aa ON aa.id = aml.account_id
            LEFT JOIN res_currency rc ON rc.id = aml.currency_id
            LEFT JOIN account_full_reconcile rec ON rec.id = aml.full_reconcile_id
            LEFT JOIN account_invoice ai ON ai.id = aml.invoice_id
        WHERE
            am.date >= %s
            AND am.date <= %s
            AND am.company_id = %s
            AND (aml.debit != 0 OR aml.credit != 0)
            AND am.state = 'posted'
        '''

        sql_query += '''
        ORDER BY
            am.date,
            am.name,
            aml.id
        '''
        self._cr.execute(
            sql_query, (self.date_from, self.date_to, company.id))

        creditsum = 0
        currentmoveid = 0
        start = False
        for row in self._cr.fetchall():
            moveid=int(row[13])

            listrow = list(row)

            account_code = False

            #listrow[3]=  "" + str(row[3]).ljust(6,'0') + ""
            listrow[3]=  "" + str(row[3]) + ""

            #if row[4].isdigit():
            #    account_code = int(row[4])
            
            _logger.info('ROW LEN =) ' + str(len(row)))

            for index_row in range(len(row)):
                value_error = False
                if isinstance(row[index_row],int) or isinstance(row[index_row],float):
                    value = str(row[index_row])
                else:
                    try :
                        if row[index_row]:
                            value = row[index_row].encode("utf-8")
                        else:
                            value =''
                    except:
                        value_error = True
                        value = "Char format error "
                #_logger.info("new value =) row[" + str(index_row) + "] " + value)

            # La colonne C : le compte auxiliaire est constitué avec la première lettre du client
            if listrow[7]:
                name = listrow[7].replace(' ', '')
                prefix_account_number = name[0] + name[1]
                prefix_account_number = prefix_account_number.upper()
                listrow[6] = prefix_account_number + "-" + listrow[6]


            listrow[7]= listrow[7].replace(',', '')

            #listrow[6]= str(row[6]) Label

            #listrow[7]= str(row[7]) Debit
            #listrow[8]= str(row[8]) Credit

            #listrow[9] = listrow[9].replace('FACTURE', '')
            #listrow[9] = listrow[9].replace('FAC', '')
            #listrow[9] = listrow[9].replace('/', '')

            # Change JournalName by Extern Name if define
            #if row[9] != None :
            #    listrow[3]= str(row[9])
            # as listrow[8] has been already remove row 9 is infact row 8

            # Account move Name
            # as listrow[7] has been twice already remove row 10 is infact row 8
            #listrow[8] = str(row[10])
            
            # Echeance Date
            #listrow[9] = str(row[11])
            
            # IsaCompta code
            #listrow[3] = str(row[12])

            # Document Type
            if row[12] == 'out_invoice':
                listrow[12] = "FACTURE"
            elif row[12] == 'in_invoice':
                listrow[12] = "AVOIR"
            else:
                listrow[12]= ""
            listrow[8] = str(row[8])
            listrow[9] = str(row[9])
            #listrow[9] = "test09" 
            listrow[13] = ""

#listrow =) [u'01/02/2017', 'None', 'x000002', u'411100', '41110000', 'SAS M. INNOVATION', '0,00', '              53,92', 'BNK1/2017/0009', '01/02/2017', None, '            64', 'None']

            _logger.info("listrow =) " + str(listrow))

            w.writerow([s.encode("utf-8") for s in listrow])
            currentmoveid=moveid

        siren = company.vat[4:13]
        end_date = self.date_to.replace('-', '')
        suffix = '-NONOFFICIAL'
        fecvalue = fecfile.getvalue()
        self.write({
            'fec_data': base64.encodestring(fecvalue),
            'filename': '%sFEC%s%s.csv' % (siren, end_date, suffix),
            })
        fecfile.close()

        action = {
            'name': 'FEC IsaCompta',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=account.fr.fec.isacompta&id=" + str(self.id) + "&filename_field=filename&field=fec_data&download=true&filename=" + self.filename,
            'target': 'self',
            }
        return action
