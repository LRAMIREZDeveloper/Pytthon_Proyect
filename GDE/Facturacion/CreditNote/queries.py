#SQL que valida si tenemos o no ese registro en mi tabla aduana.
SELECT_FACCT = """SELECT 1 FROM api.i_creditnote WHERE folio = %s AND rutemisor = %s LIMIT 1;"""

INSERT_FACCT = """ SELECT * FROM api.add_gde_creditnote(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


#Validacion de facturas que ya se encuentran el Adempiere.
SELECT_VALIDATION_FACCT = """
      SELECT documentno, docstatus, doc_order, neto, ispaid, rut
  FROM api.facct_validation WHERE documentno = %s::text AND rut = %s LIMIT 1
"""

#=========================== Notas de credito ==============================

#SQL que clasifica las NC.
SELECT_RECLASSIFICATION_NC = """SELECT classification FROM api.classification_purchase WHERE documentno = %s LIMIT 1;"""

#SQL para poder revisar las notas de credito.
SELECT_NC = """
      SELECT folio, rutemisor, netoamount, folioref, nc_ref, iva, totalamount, fchemis::date FROM api.i_creditnote WHERE tipodte NOT IN (33,34) AND status IN ('DR', 'RJ')"""


SELECT_FACCT_NC = """
      SELECT folio, rutemisor, folioref, netoamount, totalamount, status, classification_facct, tipodte, fmapago, movementdate::date AS movementdate FROM api.i_facctcontrol WHERE folio = %s AND rutemisor = %s
      """

SELECT_DM_NC = """
      SELECT
            o.c_order_id,
            o.documentno AS documentno_order,
            ol.c_orderline_id,
            mq.m_requisitionline_id,
            ord.devolucion,
            ol.m_product_id
            FROM adempiere.c_order o
             JOIN adempiere.c_bpartner cb ON cb.c_bpartner_id = o.c_bpartner_id
             LEFT JOIN adempiere.c_orderline ol ON ol.c_order_id = o.c_order_id
             LEFT JOIN adempiere.m_requisitionline mq ON mq.m_requisitionline_id = ol.m_requisitionline_id
             LEFT JOIN LATERAL (SELECT o2.documentno AS devolucion
				  FROM adempiere.c_orderline ol2
				  JOIN adempiere.c_order o2 ON ol2.c_order_id = o2.c_order_id
				  WHERE mq.m_requisitionline_id = ol2.m_requisitionline_id
				  AND o2.c_doctypetarget_id = 1000019 LIMIT 1
					) ord ON true
            WHERE o.documentno = %s
            AND CONCAT(cb.value, '-', cb.digito) = %s
             ORDER BY o.c_order_id DESC """
      
UPDATE_FACCT_DATA = """
      SELECT * FROM api.update_facct(%s, %s, %s, %s, %s, %s)
"""

UPDATE_NC = """ SELECT * FROM api.update_nc(%s)
"""

ADD_CREDIT_NOTE = """ SELECT * FROM api.add_creditnote(%s, %s, %s, %s, %s)"""

ADD_CREDIT_NOTE_DM = """ SELECT * FROM api.add_creditnote_dm(%s,%s,%s,%s,%s,%s,%s,%s)"""

QUERY_INSERT = """
    SELECT * FROM api.add_invoice(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_CREDITNOTE = """SELECT * FROM api.update_creditnote_facct(%s,%s,%s,%s,%s)"""