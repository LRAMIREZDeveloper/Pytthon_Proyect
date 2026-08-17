
# Extramos todos los socios de negocios catalogados como servicios basicos o contratos.
DATA_CLIENT_SB_C = """
SELECT value AS rut, classification AS typeclient, status
  FROM api.classification_bpartner;
"""

INSERT_FACCT = """
INSERT INTO api.i_facctcontrolnotgde(
    folio, fchemis, fchvenc, rutemisor, 
    folioref, netoamount,tpodocref, fmapago, tipodte, creditnote, cdgintrecep, nmbitem, status, 
    movementdate, url, classification, status_sb_c, iva, totalamount, detail, status_oc,classification_facct, difference
)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

#SQL que valida si tenemos o no ese registro en mi tabla aduana.
SELECT_FACCT = """SELECT 1 FROM api.i_facctcontrolnotgde WHERE folio = %s AND rutemisor = %s LIMIT 1;"""