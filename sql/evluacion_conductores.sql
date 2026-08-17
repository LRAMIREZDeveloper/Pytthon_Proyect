 SELECT ( SELECT bp.name
           FROM c_bpartner bp
          WHERE bp.c_bpartner_id = el.c_bpartner_id) AS conductor,
    ( SELECT bp.value
           FROM c_bpartner bp
          WHERE bp.c_bpartner_id = el.c_bpartner_id) AS rut,
    ( SELECT bp.digito
           FROM c_bpartner bp
          WHERE bp.c_bpartner_id = el.c_bpartner_id) AS dv,
    eh.created::date AS fecha,
    ( SELECT f.name
           FROM ad_org o
             JOIN c_projectofb f ON f.c_projectofb_id = o.c_projectofb_id
          WHERE o.ad_org_id = eh.ad_orgref_id) AS flota,
    ( SELECT u1.description
           FROM ad_user u1
          WHERE u1.ad_user_id = eh.createdby) AS supervisor,
    ( SELECT trl.name
           FROM ad_ref_list rl
             JOIN ad_ref_list_trl trl ON trl.ad_ref_list_id = rl.ad_ref_list_id
          WHERE eh.docstatus = rl.value::bpchar AND rl.ad_reference_id = 131::numeric) AS estado,
    COALESCE(el.description, cr.description) AS descripcion,
    concat(el.question1_drive, ' (', to_char(eg.answer1, '99'::text), ' Puntos)') AS q1,
    concat(el.question2_drive, ' (', to_char(eg.answer2, '99'::text), ' Puntos)') AS q2,
    concat(el.question3_drive, ' (', to_char(eg.answer3, '99'::text), ' Puntos)') AS q3,
    concat(el.question4_drive, ' (', to_char(eg.answer4, '99'::text), ' Puntos)') AS q4,
    concat(el.question5_drive, ' (', to_char(eg.answer5, '99'::text), ' Puntos)') AS q5,
    concat(el.question6_drive, ' (', to_char(eg.answer6, '99'::text), ' Puntos)') AS q6,
    concat(el.question7_drive, ' (', to_char(eg.answer7, '99'::text), ' Puntos)') AS q7,
    concat(el.question8_drive, ' (', to_char(eg.answer8, '99'::text), ' Puntos)') AS q8,
    el.rh_evaluationline_id,
        CASE
            WHEN el.answer1 = eg.expectedresult1 THEN eg.answer1
            ELSE 0::numeric
        END AS p1,
        CASE
            WHEN el.answer2 = eg.expectedresult2 THEN eg.answer2
            ELSE 0::numeric
        END AS p2,
        CASE
            WHEN el.answer3 = eg.expectedresult3 THEN eg.answer3
            ELSE 0::numeric
        END AS p3,
        CASE
            WHEN el.answer4 = eg.expectedresult4 THEN eg.answer4
            ELSE 0::numeric
        END AS p4,
        CASE
            WHEN el.answer5 = eg.expectedresult5 THEN eg.answer5
            ELSE 0::numeric
        END AS p5,
        CASE
            WHEN el.answer6 = eg.expectedresult6 THEN eg.answer6
            ELSE 0::numeric
        END AS p6,
        CASE
            WHEN el.answer7 = eg.expectedresult7 THEN eg.answer7
            ELSE 0::numeric
        END AS p7,
        CASE
            WHEN el.answer8 = eg.expectedresult8 THEN eg.answer8
            ELSE 0::numeric
        END AS p8,
        CASE
            WHEN el.answer9 = eg.expectedresult9 THEN eg.answer9
            ELSE 0::numeric
        END AS p9,
        CASE
            WHEN el.answer10 = eg.expectedresult10 THEN eg.answer10
            ELSE 0::numeric
        END AS p10,
    concat(el.question9_drive, ' (', to_char(eg.answer9, '99'::text), ' Puntos)') AS q9,
    concat(el.question10_drive, ' (', to_char(eg.answer1, '99'::text), ' Puntos)') AS q10,
    (( SELECT COALESCE(bp.bonusamount, 0::numeric) AS "coalesce"
           FROM c_bpartner bp
          WHERE bp.c_bpartner_id = el.c_bpartner_id)) - COALESCE(cr.share, 0::numeric) AS monto,
    NULL::text AS gerente,
    eh.c_period_id,
    eh.ad_orgref_id,
    ( SELECT bp.record_card
           FROM c_bpartner bp
          WHERE bp.c_bpartner_id = el.c_bpartner_id
         LIMIT 1) AS ficha,
        CASE
            WHEN el.result = 100::numeric THEN '02'::text
            ELSE '01'::text
        END AS result
   FROM rh_evaluationheader eh
     JOIN rh_evaluationline el ON eh.rh_evaluationheader_id = el.rh_evaluationheader_id
     JOIN rh_evaluationguide eg ON eg.rh_evaluationguide_id = eh.rh_evaluationguide_id
     JOIN c_period p ON p.c_period_id = eh.c_period_id
     LEFT JOIN c_committee_resolution cr ON cr.c_bpartner_id = el.c_bpartner_id AND p.startdate::date >= first_date(cr.startdate) AND p.startdate::date <= first_date(cr.enddate)
  WHERE eh.docstatus = 'CO'::bpchar;