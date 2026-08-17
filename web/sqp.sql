SELECT
    m.description AS descripcion_mantencion,
    m.interval AS intervalo,
    md.lastmp AS ultima_mantencion,
    md.nextmp AS proxima_mantencion,
    ot.mp_maintain_id AS mantencion_ot,
    ot.documentno AS documento,
    ot.created AS fecha
FROM adempiere.mp_maintain m
JOIN adempiere.mp_maintaindetail md ON md.mp_maintain_id = m.mp_maintain_id
JOIN adempiere.a_asset a ON a.a_asset_id = md.a_asset_id
LEFT JOIN (
    SELECT ot1.a_asset_id, ot1.mp_maintain_id, ot1.documentno, ot1.created
    FROM adempiere.mp_ot ot1
    WHERE ot1.C_DocType_ID = 1000081
      AND ot1.documentno = (
          SELECT MAX(ot2.documentno)
          FROM adempiere.mp_ot ot2
          WHERE ot2.a_asset_id = ot1.a_asset_id
            AND ot2.mp_maintain_id = ot1.mp_maintain_id
            AND ot2.C_DocType_ID = 1000081
      )
) ot ON ot.a_asset_id = a.a_asset_id AND ot.mp_maintain_id = m.mp_maintain_id
WHERE m.isactive = 'Y'
AND a.value = 'KSCK41'
AND m.interval > 0;
