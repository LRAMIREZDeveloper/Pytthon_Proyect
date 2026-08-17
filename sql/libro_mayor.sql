 SELECT foo.indice,
    foo.c_period_id,
    foo.periodo,
    foo.c_elementvalue_id,
    foo.value,
    foo.name,
    foo.ad_table_id,
    foo.des_tabla,
    foo.record_id,
    foo.dateacct,
    foo.description,
    foo.amtacctdr,
    foo.amtacctcr,
   FROM ( SELECT 'A'::text AS indice,
            fa.c_period_id,
            p.name AS periodo,
            ce.c_elementvalue_id,
            ce.value,
            ce.name,
            fa.ad_table_id,
            t.name AS des_tabla,
            fa.record_id,
            fa.dateacct,
                CASE
                    WHEN (( SELECT max(pa.documentno::text) AS max
                       FROM c_cashline cl
                         JOIN c_cash c ON cl.c_cash_id = c.c_cash_id
                         JOIN c_payment pa ON pa.c_payment_id = cl.c_payment_id
                      WHERE c.c_cash_id = fa.record_id)) <> NULL::text AND fa.ad_table_id = 407::numeric THEN (((( SELECT max(pa.documentno::text) AS max
                       FROM c_cashline cl
                         JOIN c_cash c ON cl.c_cash_id = c.c_cash_id
                         JOIN c_payment pa ON pa.c_payment_id = cl.c_payment_id
                      WHERE c.c_cash_id = fa.record_id)) || '-'::text) || fa.description::text)::character varying
                    WHEN fa.ad_table_id = 321::numeric THEN (( SELECT concat(i.documentno::text, '#', p_1.value, ' ', p_1.name) AS concat
                       FROM m_inventoryline il
                         JOIN m_inventory i ON il.m_inventory_id = i.m_inventory_id
                         LEFT JOIN m_product p_1 ON p_1.m_product_id = il.m_product_id
                      WHERE il.m_inventoryline_id = fa.line_id))::character varying
                    WHEN fa.ad_table_id = 224::numeric THEN (( SELECT concat('#', jb.documentno, '# (', jl.description, ')') AS concat
                       FROM gl_journalbatch jb
                         JOIN gl_journal j ON j.gl_journalbatch_id = jb.gl_journalbatch_id
                         JOIN gl_journalline jl ON jl.gl_journal_id = j.gl_journal_id
                      WHERE jl.gl_journalline_id = fa.line_id
                     LIMIT 1))::character varying
                    WHEN fa.ad_table_id = 735::numeric THEN (( SELECT concat(a.documentno, ' #0 (', i.documentno, ')') AS concat
                       FROM c_allocationhdr a
                         JOIN c_allocationline al ON al.c_allocationhdr_id = a.c_allocationhdr_id
                         JOIN c_invoice i ON i.c_invoice_id = al.c_invoice_id
                      WHERE a.c_allocationhdr_id = fa.record_id AND al.c_allocationline_id = fa.line_id))::character varying
                    WHEN fa.ad_table_id = 392::numeric THEN (( SELECT concat(p_1.documentno, ' | ', fa.description) AS concat
                       FROM c_bankstatement b
                         JOIN c_bankstatementline bl ON bl.c_bankstatement_id = b.c_bankstatement_id
                         JOIN c_payment p_1 ON p_1.c_payment_id = bl.c_payment_id
                      WHERE b.c_bankstatement_id = fa.record_id AND bl.c_bankstatementline_id = fa.line_id))::character varying
                    ELSE fa.description
                END AS description,
            fa.amtacctdr,
            fa.amtacctcr,
            0 AS saldo,
            ( SELECT org.value
                   FROM ad_org org
                  WHERE org.ad_org_id = fa.ad_org_id) AS centro_costo,
            COALESCE(( SELECT COALESCE(sum(rf.amtacctdr), 0::numeric) + COALESCE(sum(rf.amtacctcr), 0::numeric)
                   FROM rv_fact_acct rf
                  WHERE rf.ad_client_id = 1000000::numeric AND (rf.amtacctdr > 0::numeric OR rf.amtacctcr > 0::numeric)), 1::numeric) AS saldo_inicio,
            ce.ad_client_id,
            ce.ad_org_id,
            ce.created,
            ce.createdby,
            ce.updated,
            ce.updatedby,
            ce.isactive,
            fa.account_id,
                CASE
                    WHEN fa.ad_table_id = 318::numeric THEN ( SELECT a3.value
                       FROM c_invoice ci
                         JOIN c_invoiceline cil ON ci.c_invoice_id = cil.c_invoice_id
                         LEFT JOIN c_order o ON o.c_order_id = ci.c_order_id
                         LEFT JOIN c_orderline ol ON ol.c_orderline_id = cil.c_orderline_id
                         LEFT JOIN a_asset a3 ON a3.a_asset_id = ol.a_asset_id2::numeric
                         LEFT JOIN m_requisitionline rl ON rl.m_requisitionline_id = ol.m_requisitionline_id
                         LEFT JOIN m_requisition sc ON sc.m_requisition_id = rl.m_requisition_id
                      WHERE cil.c_invoiceline_id = fa.line_id)
                    ELSE NULL::character varying
                END AS a_asset_oc,
                CASE
                    WHEN fa.ad_table_id = 318::numeric THEN ( SELECT a2.value
                       FROM c_invoice ci
                         JOIN c_invoiceline cil ON ci.c_invoice_id = cil.c_invoice_id
                         LEFT JOIN c_order o ON o.c_order_id = ci.c_order_id
                         LEFT JOIN c_orderline ol ON ol.c_orderline_id = cil.c_orderline_id
                         LEFT JOIN m_requisitionline rl ON rl.m_requisitionline_id = ol.m_requisitionline_id
                         LEFT JOIN m_requisition sc ON sc.m_requisition_id = rl.m_requisition_id
                         LEFT JOIN a_asset a2 ON a2.a_asset_id = sc.a_asset_id
                      WHERE cil.c_invoiceline_id = fa.line_id)
                    ELSE NULL::character varying
                END AS a_asset_sc,
                CASE
                    WHEN fa.ad_table_id = 318::numeric THEN ( SELECT il.a_asset2_id
                       FROM c_invoiceline il
                      WHERE fa.line_id = il.c_invoiceline_id)
                    WHEN fa.ad_table_id = 224::numeric THEN ( SELECT jl.a_asset_id
                       FROM gl_journal j
                         JOIN gl_journalline jl ON jl.gl_journal_id = j.gl_journal_id
                      WHERE fa.line_id = jl.gl_journalline_id)
                    WHEN fa.ad_table_id = 407::numeric THEN ( SELECT cl.a_asset_id
                       FROM c_cash c
                         JOIN c_cashline cl ON cl.c_cash_id = c.c_cash_id
                      WHERE fa.line_id = cl.c_cashline_id)
                    WHEN fa.ad_table_id = 321::numeric THEN ( SELECT il.a_asset_id
                       FROM m_inventoryline il
                      WHERE fa.line_id = il.m_inventoryline_id)
                    ELSE NULL::numeric
                END AS a_asset_id,
            ( SELECT a4.value
                   FROM a_asset a4
                  WHERE a4.a_asset_id = (( SELECT max(mr.a_asset_id) AS max
                           FROM c_invoice ci
                             JOIN c_invoiceline cil ON ci.c_invoice_id = cil.c_invoice_id
                             LEFT JOIN c_order o ON o.c_order_id = ci.c_order_id
                             LEFT JOIN c_orderline col ON col.c_orderline_id = cil.c_orderline_id
                             JOIN m_requisitionline mrl ON col.m_requisitionline_id = mrl.m_requisitionline_id
                             JOIN m_requisition mr ON mrl.m_requisition_id = mr.m_requisition_id
                          WHERE fa.line_id = cil.c_invoiceline_id))) AS a_asset_occ,
            vcc.itemeerr,
            vcc.groupeerr,
            vcc.clasificationeerr,
            vcc.accounteerr,
            vcc.isaccounteerr,
                CASE
                    WHEN fa.ad_table_id = 321::numeric THEN ( SELECT max(rll.a_asset_id) AS max
                       FROM m_requisitionline rll,
                        m_requisition rr,
                        m_inventory ii,
                        m_inventoryline ill
                      WHERE rll.m_requisition_id = rr.m_requisition_id AND rr.m_inventory_id = ii.m_inventory_id AND ill.m_inventory_id = ii.m_inventory_id AND ill.line = rll.line AND fa.line_id = ill.m_inventoryline_id
                     LIMIT 1)
                    ELSE NULL::numeric
                END AS a_asset_il,
                CASE
                    WHEN fa.c_bpartner_id IS NULL OR fa.ad_table_id = 407::numeric THEN
                    CASE
                        WHEN fa.ad_table_id = 407::numeric AND fa.account_id <> 1000122::numeric THEN ( SELECT ccl.c_bpartner_id
                           FROM c_cash ccc
                             JOIN c_cashline ccl ON ccc.c_cash_id = ccl.c_cash_id
                          WHERE ccc.c_cash_id = fa.record_id AND ccl.c_cashline_id = fa.line_id
                         LIMIT 1)
                        WHEN fa.ad_table_id = 407::numeric AND fa.account_id = 1000122::numeric THEN ( SELECT COALESCE(cll.c_bpartner_id, ccl.c_bpartner_id) AS "coalesce"
                           FROM c_cash ccc
                             JOIN c_cashbook ccl ON ccc.c_cashbook_id = ccl.c_cashbook_id
                             LEFT JOIN c_cashline cll ON cll.c_cash_id = ccc.c_cash_id AND cll.c_cashline_id = fa.line_id
                          WHERE ccc.c_cash_id = fa.record_id
                         LIMIT 1)
                        WHEN fa.ad_table_id = 335::numeric THEN ( SELECT cbb.c_bpartner_id
                           FROM c_payment p_1
                             JOIN c_bpartner cbb ON cbb.c_bpartner_id = p_1.c_bpartner_id
                          WHERE p_1.c_payment_id = fa.record_id
                         LIMIT 1)
                        WHEN fa.ad_table_id = 318::numeric THEN ( SELECT cbb.c_bpartner_id
                           FROM c_invoice i
                             JOIN c_bpartner cbb ON cbb.c_bpartner_id = i.c_bpartner_id
                          WHERE i.c_invoice_id = fa.record_id
                         LIMIT 1)
                        WHEN fa.ad_table_id = 224::numeric THEN ( SELECT cbb.c_bpartner_id
                           FROM gl_journal j
                             JOIN gl_journalline jl ON jl.gl_journal_id = j.gl_journal_id
                             JOIN c_bpartner cbb ON cbb.c_bpartner_id = jl.c_bpartner_id
                          WHERE j.gl_journal_id = fa.record_id AND jl.gl_journalline_id = fa.line_id
                         LIMIT 1)
                        WHEN fa.ad_table_id = 735::numeric THEN ( SELECT cbb.c_bpartner_id
                           FROM c_allocationline al
                             JOIN c_bpartner cbb ON cbb.c_bpartner_id = al.c_bpartner_id
                          WHERE al.c_allocationhdr_id = fa.record_id AND al.c_allocationline_id = fa.line_id)
                        ELSE NULL::numeric
                    END
                    ELSE fa.c_bpartner_id
                END AS c_bpartner,
                CASE
                    WHEN fa.ad_table_id = 335::numeric THEN COALESCE(( SELECT pr.c_paymentrequest_id
                       FROM c_paymentrequest pr
                      WHERE pr.c_payment_id = fa.record_id
                     LIMIT 1), ( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                      WHERE prl.c_payment_id = fa.record_id
                     LIMIT 1))
                    WHEN fa.ad_table_id = 318::numeric THEN ( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                      WHERE prl.c_invoice_id = fa.record_id
                     LIMIT 1)
                    WHEN fa.ad_table_id = 224::numeric AND (( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                      WHERE prl.gl_journal_id = fa.record_id
                     LIMIT 1)) IS NOT NULL THEN ( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                      WHERE prl.gl_journal_id = fa.record_id
                     LIMIT 1)
                    WHEN fa.ad_table_id = 407::numeric THEN ( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                         JOIN dm_document d ON d.dm_document_id = prl.dm_document_id
                      WHERE d.c_cash_id = fa.record_id
                     LIMIT 1)
                    WHEN fa.ad_table_id = 224::numeric AND (( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                      WHERE prl.gl_journal_id = fa.record_id
                     LIMIT 1)) IS NULL THEN ( SELECT prl.c_paymentrequest_id
                       FROM c_paymentrequestline prl
                         JOIN dm_document d ON d.dm_document_id = prl.dm_document_id
                         JOIN tp_refundheader rh ON rh.tp_refundheader_id = d.tp_refundheader_id
                         JOIN gl_journal j ON j.gl_journalbatch_id = rh.gl_journalbatch_id
                      WHERE j.gl_journal_id = fa.record_id
                     LIMIT 1)
                    ELSE NULL::numeric
                END AS c_paymentrequest_id,
                CASE
                    WHEN fa.ad_table_id = 407::numeric THEN ( SELECT ccl.c_bpartner_id
                       FROM c_cash ccc
                         JOIN c_cashbook ccl ON ccc.c_cashbook_id = ccl.c_cashbook_id
                      WHERE ccc.c_cash_id = fa.record_id
                     LIMIT 1)
                    ELSE NULL::numeric
                END AS c_bpartner2_id
           FROM c_elementvalue ce
             LEFT JOIN c_validcombination vcc ON vcc.account_id = ce.c_elementvalue_id AND vcc.isactive = 'Y'::bpchar
             JOIN fact_acct fa ON ce.c_elementvalue_id = fa.account_id
             JOIN c_period p ON fa.c_period_id = p.c_period_id
             JOIN ad_table_trl t ON fa.ad_table_id = t.ad_table_id) foo
  ORDER BY foo.value, foo.indice, foo.c_period_id, foo.dateacct, foo.ad_table_id, foo.record_id;