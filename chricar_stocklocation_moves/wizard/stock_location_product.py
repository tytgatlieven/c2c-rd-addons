# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from datetime import datetime, date, time
import logging
import tools
import pytz

class stock_location_product(osv.osv_memory):
    _inherit = "stock.location.product"
    _logger = logging.getLogger(__name__)

    def action_open_window_col(self, cr, uid, ids, context=None): 
        res = super(stock_location_product, self).action_open_window(cr, uid, ids, context)
        return res

    def action_open_report_col(self, cr, uid, ids, context=None):
        res = super(stock_location_product, self).action_open_report(cr, uid, ids, context)
        res['report_name'] =  'report.product.col'
        self._logger.debug('_action_open_report_col %s', res)
        
        d = res['context']['local_to_date2']
        e =  "','YYYY-MM-DD HH24:MI:SS')"
        date_begin = "to_date('" + d + e
        d = res['context']['local_to_date1']
        date_end = "to_date('" + d + e
        where_company = ''        
        where_location_ids = ''
        location_id = res['context']['location']
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_id)])
        where_location_ids = ' and location_id in (' + ','.join([str(id) for id in location_ids])    + ') '
        self._logger.debug('FGF %s %s' %(date_begin,date_end))
        sql = """select product_id,
        sum(case when date < %s then product_qty else 0 end) as qty_begin,
        sum(case when date >= %s then qty_plus else 0 end) as qty_plus,
        sum(case when date >= %s then qty_minus else 0 end) as qty_minus,
        sum(case when date >= %s then qty_inventory else 0 end) as qty_inventory,
        sum(product_qty) as qty_end,
        sum(case when date < %s then move_value_cost else 0 end) as value_begin,
        sum(case when date >= %s then cost_plus else 0 end) as value_plus,
        sum(case when date >= %s then cost_minus else 0 end) as value_minus,
        sum(case when date >= %s then cost_inventory else 0 end) as value_inventory,
        sum(move_value_cost) as value_end
            from chricar_location_move_col
          where date < %s
            %s  -- where company
            %s  -- where location_id
          group by product_id
          order by product_id""" % (date_begin,date_begin,date_begin,date_begin, date_begin,date_begin,date_begin,date_begin, date_end, where_company, where_location_ids )
        self._logger.debug('_action_open_report_col products %s', sql)
        cr.execute(sql)
        rows = cr.dictfetchall()
        #self._logger.debug('_action_open_report_col rows %s', rows)
        products = {}
        for r in rows:
            products[r['product_id']] = r
        self._logger.debug('_action_open_report_col products %s', products)    
        res['context']['products'] = products    
        return res


stock_location_product()
