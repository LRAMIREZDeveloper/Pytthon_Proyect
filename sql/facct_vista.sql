 SELECT fcn.folio,
    fcn.fchemis,
    fcn.rutemisor,
    cb.name AS rznsoc,
        CASE
            WHEN fcn.tipodte = 33::numeric THEN fcn.netoamount
            ELSE fcn.totalamount
        END AS netoamount,
    fcn.creditnote,
    fcn.nmbitem,
    fcn.movementdate,
        CASE
            WHEN fcn.tipodte = 33::numeric THEN 'FA - Factura Electronica Afecta'::text
            WHEN fcn.tipodte = 34::numeric THEN 'FA - Factura Electronica Exenta'::text
            WHEN fcn.tipodte = 61::numeric THEN 'NC - Nota de Credito'::text
            WHEN fcn.tipodte = 56::numeric THEN 'ND - Nota de Debito'::text
            ELSE 'Sin datos'::text
        END AS tipo_documento,
    fcn.url,
    COALESCE(fcn.approval_id, apro.user_id) AS user_id,
    apro.user2_id,
    COALESCE(ad2.description, apro.approver) AS approver,
    apro.approver_two,
    apro.detail,
        CASE
            WHEN fcn.status::text = 'DR'::text THEN 'Pendiente'::text
            WHEN fcn.status::text = 'PR'::text THEN 'En Proceso'::text
            WHEN fcn.status::text = 'AJ'::text THEN 'Aprobación Jefe'::text
            WHEN fcn.status::text = 'CO'::text THEN 'Completa'::text
            WHEN fcn.status::text = 'RJ'::text THEN 'Rechazada'::text
            WHEN fcn.status::text = 'VO'::text THEN 'Anulada'::text
            ELSE NULL::text
        END AS estado,
    'now'::text::date - fcn.fchemis::date AS can_days,
    fcn.approval_id,
    ad2.description,
    fcn.tipodte,
    COALESCE(fcn.ad_org_id, apro.ad_org_id) AS ad_org_id,
    COALESCE(fcn.c_charge_id, apro.c_charge_id) AS c_charge_id,
    COALESCE(fcn.m_product_id, apro.m_product_id) AS m_product_id,
    fcn.a_asset_id,
    fcn.status_sb_c,
    fcn.classification,
    fcn.folioref AS oc,
        CASE
            WHEN COALESCE(col.approver_requisition, co.approver_id) = 1001125::numeric THEN 1000843::numeric
            ELSE COALESCE(col.approver_requisition, co.approver_id)
        END AS approver_id_fc,
        CASE
            WHEN COALESCE(col.nombre_aprobador_sc, ad.description)::text = 'Juan Pablo Bowen'::text THEN 'Brenda Gonzalez'::character varying
            ELSE COALESCE(col.nombre_aprobador_sc, ad.description)
        END AS approver_fc,
    fcn.iva,
    fcn.totalamount,
    fcn.classification_facct,
    fcn.detail AS line_json,
    fcn.fmapago,
    ci.documentno AS documentno_invoice,
    fcn.difference,
    nc.folio AS credit_note
   FROM api.i_facctcontrol fcn
     LEFT JOIN c_order co ON fcn.folioref::text = co.documentno::text
     LEFT JOIN ad_user ad ON co.approver_id = ad.ad_user_id
     LEFT JOIN ad_user ad2 ON fcn.approval_id = ad2.ad_user_id
     LEFT JOIN c_bpartner cb ON concat(cb.value, '-', cb.digito) = fcn.rutemisor::text
     LEFT JOIN c_invoice ci ON fcn.folio::text = ci.documentno::text AND ci.c_bpartner_id = cb.c_bpartner_id AND (ci.docstatus = ANY (ARRAY['CO'::bpchar, 'CL'::bpchar]))
     LEFT JOIN api.i_creditnote nc ON nc.folioref::text = fcn.folio::text
     LEFT JOIN LATERAL ( SELECT fm.user_id,
            fm.user2_id,
            fm.approver,
            fm.approver_two,
            fm.detail,
            fm.ad_org_id,
            fm.c_charge_id,
            fm.m_product_id
           FROM facct_matrix fm
          WHERE fm.rut::text = fcn.rutemisor::text AND (fm.number::text = fcn.cdgintrecep::text OR fm.number IS NULL)
          ORDER BY fm.number::text = fcn.cdgintrecep::text DESC NULLS LAST
         LIMIT 1) apro ON true
     LEFT JOIN LATERAL ( SELECT col_1.c_orderline_id,
            col_1.m_requisitionline_id,
            mr.documentno AS documentno_requisiton,
            mr.approver_id AS approver_requisition,
            ad3.description AS nombre_aprobador_sc
           FROM c_orderline col_1
             JOIN m_requisitionline mrl ON mrl.m_requisitionline_id = col_1.m_requisitionline_id
             JOIN m_requisition mr ON mr.m_requisition_id = mrl.m_requisition_id
             JOIN ad_user ad3 ON ad3.ad_user_id = mr.approver_id
          WHERE col_1.c_order_id = co.c_order_id
         LIMIT 1) col ON true
  WHERE ci.documentno IS NULL