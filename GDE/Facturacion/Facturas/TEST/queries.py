
# Extramos todos los socios de negocios catalogados como servicios basicos o contratos.
DATA_CLIENT_SB_C = """
SELECT value AS rut, classification AS typeclient, status
  FROM api.classification_bpartner;
"""

INSERT_FACCT = """
INSERT INTO api.i_facctcontrol(
    folio, fchemis, fchvenc, rutemisor, 
    folioref, netoamount,tpodocref, fmapago, tipodte, creditnote, cdgintrecep, nmbitem, status, 
    movementdate, url, classification, status_sb_c, iva, totalamount, detail, status_oc,classification_facct, difference
)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

#SQL que valida si tenemos o no ese registro en mi tabla aduana.
SELECT_FACCT = """SELECT 1 FROM api.i_facctcontrol WHERE folio = %s AND rutemisor = %s LIMIT 1;"""

SELECT_FACCT_DATA_REC = """SELECT folio, rutemisor, folioref, netoamount, totalamount FROM api.i_facctcontrol WHERE status = 'DR' """

SELECT_RECLASSIFICATION = """SELECT 1 FROM api.i_facctcontrol WHERE folio = %s AND rutemisor = %s AND status = 'CO' LIMIT 1;"""

#SQL que clasifica las facturas con ordenes de compra.
SELECT_FACCT_OC = """SELECT classification FROM api.classification_purchase WHERE documentno = %s LIMIT 1;"""

#SQL que extrae la data para trabajar las facturas con OC clasificadas como RM
SELECT_FACCT_OC_DETAIL = """
      SELECT ad_org_id, value, documentno_order, documentno_inout, poreference, 
            m_inoutline_id, c_orderline_id, description, m_product_id, c_charge_id, 
            qtyordered, priceentered, qtydelivered, qtydelivered_total, total_order, 
            total_orderline, total_inoutline, total_inout, grandtotal_inout, 
            status
      FROM api.classification_purchase_inout WHERE documentno_order = %s;
"""

##SQL que extrae el monto asociada a la OC, esto con el fin de trabajar las facturas clasificadas como OC
SELECT_FACCT_OC_DETAIL2 = """
      SELECT total_order
  FROM api.api_facct_data_complemets WHERE oc = %s LIMIT 1 ;
"""

#SQL para actualizar la clasificacion de la factura en base al RPA
UPDATE_FACCT_DATA = """
      SELECT * FROM api.update_facct(%s, %s, %s, %s, %s, %s)
"""

#Validacion de facturas que ya se encuentran el Adempiere.
SELECT_VALIDATION_FACCT = """
      SELECT 1 
            FROM adempiere.c_invoice ci
      JOIN adempiere.c_bpartner cb ON cb.c_bpartner_id = ci.c_bpartner_id
      WHERE ci.documentno = %s::text 
      AND CONCAT(cb.value, '-', cb.digito) = %s LIMIT 1
"""

UPDATE_FACCT_EXIST = """
UPDATE api.i_facctcontrol SET status = 'CO' WHERE folio = %s AND rutemisor = %s
"""

# =================== Aprobaciones =========================

QUERY_DATA = """
        SELECT rutemisor, folio, tipodte, movementdate, nmbitem, netoamount, 
       totalamount, oc, ad_org_id, difference_detected, difference, line FROM api.api_facct_receive;
"""

QUERY_INSERT = """
    SELECT * FROM api.add_invoice(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""