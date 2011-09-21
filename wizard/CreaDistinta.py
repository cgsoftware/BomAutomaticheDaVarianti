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


class crea_distinta(osv.osv_memory):
    _name = 'crea.distinta'
    _description = 'Genera una distinta base partendo daglle varianti'
    _columns = {
         'articolo_id':fields.many2one('product.product', 'Articolo', required=True, ondelete='cascade', select=True),
         'peso_prod_conai': fields.float('Peso di Produzione/conai', required=False, digits=(11, 5)),
         'righe_materiali':fields.one2many('crea.distinta.righe', 'testa', 'Righe Varianti Materie Prime'),
                }
    def onchange_articolo(self, cr, uid, ids, articolo_id):
        #import pdb;pdb.set_trace()
        v = {}
        righe_materiali = []
        vals = {
                'articolo_id':articolo_id,
                }
        # id_art = self.create(cr, uid, vals, {})
        product = self.pool.get('product.product').browse(cr, uid, [articolo_id])[0]
        varianti_product = product.dimension_value_ids
        for riga_var in varianti_product:
            if riga_var.dimension_id.flag_obbl:
                # c'è scritto qualcosa nel flag obbligatorio
                if 'D' in riga_var.dimension_id.flag_obbl:
                    # è obbligatorio che si fermi e chieda la materia prima per questa variante
                    righe_materiali.append ({
                                              'variant_dimension_id':riga_var.dimension_id.id,
                                              'variant_value_id':riga_var.id,
                                            })
        if product.production_conai_peso:
            qta = product.production_conai_peso
        else:
            qta = product.product_tmpl_id.production_peso
        

        v = {'articolo_id':articolo_id, 'righe_materiali':righe_materiali, 'peso_prod_conai':qta}
                
        #Dimension_ids 
        return {'value':v}
    
    def cerca_testa_distinta(self, cr, uid, articolo_id, context=None):
        # import pdb;pdb.set_trace()
        cerca = [('product_id', '=', articolo_id.id), ('bom_id', '=', 0), ('active', '=', True)]
        distinte = self.pool.get('mrp.bom').search(cr, uid, cerca)
        if distinte:
            # ha trovato delle distinte base dell'articolo e a questo punto deve fare aggiornamenti e non aggiunte
            # quindi prende l' id della prima distinta base attiva sull'articolo
            pass
            testa_id = distinte[0]
        else:
            # È DA INSERIRE PRIMA LA TESTATA DELLA DISTINTA BASE
            testa_distinta = {
                               'name':articolo_id.name,
                               'code':articolo_id.default_code,
                               'product_id':articolo_id.id,
                               'bom_id':0,
                               'product_uom': articolo_id.uom_id.id,
                               }
            testa_id = self.pool.get('mrp.bom').create(cr, uid, testa_distinta)

        
        return testa_id
    
    def scrive_componente_distinta(self, cr, uid, righe_comp, rigamat, testa_id, context=None):
            #import pdb;pdb.set_trace()
            if type(rigamat) == type({}):
                product = self.pool.get('product.product').browse(cr, uid, [rigamat['product_id']])[0]
                if righe_comp:
                    # c'è la riga deve fare update
                    riga_distinta = {
                               'name':product.name,
                               'code':'',
                               'product_id':product.id,
                               'bom_id':testa_id,
                               'type':'normal',
                               'product_uom': product.uom_id.id,
                               'product_qty':rigamat['product_qty'],
                               }
                    riga_dist_id = self.pool.get('mrp.bom').write(cr, uid, righe_comp, riga_distinta)
                    return righe_comp

                else:
                    riga_distinta = {
                               'name':product.name,
                               'code':'',
                               'product_id':product.id,
                               'bom_id':testa_id,
                               'type':'normal',
                               'product_uom': product.uom_id.id,
                               'product_qty':rigamat['product_qty'],
                               }
                    riga_dist_id = self.pool.get('mrp.bom').create(cr, uid, riga_distinta)
                    return [riga_dist_id]

                
            else:
                if righe_comp:
                    # c'è la riga deve fare update
                    riga_distinta = {
                               'name':rigamat.product_id.name,
                               'code':'',
                               'product_id':rigamat.product_id.id,
                               'bom_id':testa_id,
                               'type':'normal',
                               'product_uom': rigamat.product_id.uom_id.id,
                               'product_qty':rigamat.product_qty,
                               }
                    riga_dist_id = self.pool.get('mrp.bom').write(cr, uid, righe_comp, riga_distinta)
                    return righe_comp

                else:
                    
                    riga_distinta = {
                               'name':rigamat.product_id.name,
                               'code':'',
                               'product_id':rigamat.product_id.id,
                               'bom_id':testa_id,
                               'type':'normal',
                               'product_uom': rigamat.product_id.uom_id.id,
                               'product_qty':rigamat.product_qty,
                               }
                    riga_dist_id = self.pool.get('mrp.bom').create(cr, uid, riga_distinta)
                    return [riga_dist_id]
        


    def genera(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        param = self.pool.get('crea.distinta').browse(cr, uid, ids)[0]
        articolo_id = param.articolo_id
        testa_id = self.cerca_testa_distinta(cr, uid, articolo_id, context=None)
        # Aggiorna il peso del calcolo
        okk = self.pool.get('product.product').write(cr, uid, [articolo_id.id], {'production_conai_peso':param.peso_prod_conai})
        # per prima cosa cicla sulla distinta base del template se esite
        if articolo_id.product_tmpl_id.bom_template_ids:
            # ci sono materie prime definite a livello di template
            for rigamat in articolo_id.product_tmpl_id.bom_template_ids:
                # cerca in distinta base l'articolo componente  
                cerca = [('bom_id', '=', testa_id), ('active', '=', True), ('product_id', '=', rigamat.product_id.id)]
                righe_comp = self.pool.get('mrp.bom').search(cr, uid, cerca)
                ids_riga = self.scrive_componente_distinta(cr, uid, righe_comp, rigamat, testa_id, context=None)
                # cicla sulle varianti
            # import pdb;pdb.set_trace()
            for variante in articolo_id.dimension_value_ids:   
                    cerca = [('name', '=', variante.dimension_id.name.strip() + "-" + variante.name.strip())]
                    variant_comp_ids = self.pool.get('bom.variant').search(cr, uid, cerca)
                    if variant_comp_ids:
                        # ci sono delle righe di componenti definite per la varaiante
                        testa_variant_comp = self.pool.get('bom.variant').browse(cr, uid, variant_comp_ids)[0]
                        for riga_materie_prime in testa_variant_comp.righe_materie_prime:
                            # verifica e calcola prima la qta
                            if riga_materie_prime.tipo_calcolo == "perc":
                                qta = param.peso_prod_conai * riga_materie_prime.material_qty / 100
                            else:
                                qta = riga_materie_prime.material_qty
                            if  riga_materie_prime.product_material_id:
                                # fa riferimento ad una articolo prodotto diretto materia prima
                                righe_comp = False
                                rigamat = {
                                           'product_id':riga_materie_prime.product_material_id.id,
                                           'product_qty':qta,
                                           }
                                #import pdb;pdb.set_trace()
                                cerca = [('bom_id', '=', testa_id), ('active', '=', True), ('product_id', '=', rigamat['product_id'])]
                                righe_comp = self.pool.get('mrp.bom').search(cr, uid, cerca)
                                ids_riga = self.scrive_componente_distinta(cr, uid, righe_comp, rigamat, testa_id, context=None)
                            else:
                                # la cosa è + complessa qui bisogna associare un template di materia prima con il suo colore 
                                #
                               
                                if riga_materie_prime.material_variant:
                                    righe_comp = False
                                    rigamat = {
                                           'product_id':riga_materie_prime.material_variant.id,
                                           'product_qty':qta,
                                           }
                                    cerca = [('bom_id', '=', testa_id), ('active', '=', True), ('product_id', '=', rigamat['product_id'])]
                                    righe_comp = self.pool.get('mrp.bom').search(cr, uid, cerca)
                                    ids_riga = self.scrive_componente_distinta(cr, uid, righe_comp, rigamat, testa_id, context=None)
            # ORA CICLA SULLE RIGHE MATERIE PRIME DEFINITE A MANO
            for rigamat1 in   param.righe_materiali:
                rigamat = {
                           'product_id':rigamat1.materia_id.id,
                            'product_qty':rigamat1.product_qty,
                                           }
                cerca = [('bom_id', '=', testa_id), ('active', '=', True), ('product_id', '=', rigamat['product_id'])]
                righe_comp = self.pool.get('mrp.bom').search(cr, uid, cerca)
                ids_riga = self.scrive_componente_distinta(cr, uid, righe_comp, rigamat, testa_id, context=None)                       


        context.update({'product_id':articolo_id.id})
        context.update({'active_id':articolo_id.id})
        context.update({'active_ids':[articolo_id.id]})
        return {
            'name': _('Prodotto'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'product.product',
            'res_id':context['product_id'],
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
         }

    def view_init(self, cr, uid, fields_list, context=None):
        #import pdb;pdb.set_trace()
        res = super(crea_distinta, self).view_init(cr, uid, fields_list, context=context)
        # IN ACTIVE_MOVE DEVE METTERE IL CODICE ARTICOLO E QUINDI SETTARLO IN Articolo_id
        #if not context.get('active_ids', []):
         #   raise osv.except_osv(_('Invalid action !'), _('Selezionare l articolo !'))
        return res
    
    
    def  default_get(self, cr, uid, fields, context=None):
        #import pdb;pdb.set_trace()
        active_ids = context and context.get('active_ids', [])
        res = {}
        ids = []
        if active_ids:
            for product in self.pool.get('product.product').browse(cr, uid, active_ids, context=context):
                res = self.onchange_articolo(cr, uid, ids, product.id)
                
        
        return {'articolo_id':product.id}
    

crea_distinta()

class crea_distinta_righe(osv.osv_memory):
        _name = 'crea.distinta.righe'
        _description = 'Genera una distinta base partendo daglle varianti'
        _columns = {
                    'testa':fields.many2one('crea.distinta', 'Testa', required=True, ondelete='cascade', select=True,),
                    'variant_dimension_id':fields.many2one('product.variant.dimension.type', 'Tipo', required=True, ondelete='cascade', select=True, readonly=True),
                    'variant_value_id':fields.many2one('product.variant.dimension.value', 'Variante', required=True, ondelete='cascade', select=True, readonly=True),
                    'materia_id':fields.many2one('product.product', 'Articolo Mat.Prima', required=True, ondelete='cascade', select=True),
                    'product_qty': fields.float('Quantita', required=False, digits=(11, 5)),
  
                    }
        
        _defaults = {  
        'product_qty': 1,
        }
        

    
crea_distinta_righe()    
