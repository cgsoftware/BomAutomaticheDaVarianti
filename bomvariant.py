# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv
from osv.osv import except_osv
import time
from tools.translate import _
import decimal_precision as dp


class  bom_template(osv.osv):
    _description = 'Materie prime definite a livello di template'
    pass
    _name = "bom.template"
    _columns = {
                'template_id': fields.many2one('product.template', 'Template', ondelete='set null', select=True, required=True),
                'product_id': fields.many2one('product.product', 'Articolo', required=True, ondelete='cascade', select=True),
                'product_qty': fields.float('Product Qty', required=False, digits=(11, 5)),
                }
    
    
bom_template()


class  bom_variant(osv.osv):
    _description = 'Materie prime definite a livello di singola variante '
    _name = "bom.variant"
    _columns = {
                'name': fields.char('Nome Variante', size=64, required=True, select=True, help="deve essere la somma dellla dimensione + il valore es:COL-ROSSO"),
                'template_material_id': fields.many2one('product.template', 'Template Mat.Prima', required=False, ondelete='cascade', select=True),
                'template_material_qty': fields.float('Qty', required=False, digits=(11, 5)),
                'righe_materie_prime': fields.one2many('bom.variant.line', 'bom_variant_id', 'Righe Materie Prime'),
                }
    
bom_variant()


def _TipoCalcolo(self, cr, uid, context={}):
    return [("peso", "Peso Diretto"), ('perc', '% del peso di Template')]


class  bom_variant_line(osv.osv):
    pass
    _name = "bom.variant.line"
    _columns = {
                'bom_variant_id': fields.many2one('bom.variant', 'Testa Variante', required=True, ondelete='cascade', select=True, readonly=True),
                
                'product_material_id': fields.many2one('product.product', 'Materia Prima', required=False, ondelete='cascade', select=True),
                'tipo_calcolo':fields.selection(_TipoCalcolo, 'Tipo Calcolo'),
                'material_variant': fields.many2one('product.product', 'Variante Materia Prima', required=False, ondelete='cascade', select=True),
                'material_qty': fields.float('Qty', required=True, digits=(11, 5)),

                }

    
bom_variant_line()



class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
                
        'production_peso': fields.float('Peso di Produzione', required=False, digits=(11, 5)),
        'bom_template_ids':fields.one2many('bom.template', 'template_id', 'Distinta Materie Prime'),
        'pz_x_collo': fields.integer('Pezzi Per Collo', required=False),
        'routing_id': fields.many2one('mrp.routing', 'Routing', reqired=True, help="TLinea di Produzione"),
    }
    
product_template()    

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'production_conai_peso': fields.float('Peso di Produzione/conai', required=False, digits=(11, 5)),
        'pz_x_collo': fields.integer('Pezzi Per Collo', required=False),
         }
    
product_product() 

class mrp_bom(osv.osv):
    """
    Defines bills of material for a product.
    """
    _inherit = 'mrp.bom'
    _columns = {

        'product_qty': fields.float('Product Qty', digits=(11, 5), required=True),
        'product_uos_qty': fields.float('Product UOS Qty', digits=(11, 5)),
            }
mrp_bom()
