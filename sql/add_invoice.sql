-- Function: api.add_inout(numeric, character varying, numeric, character varying)

-- DROP FUNCTION api.add_inout(numeric, character varying, numeric, character varying);

CREATE OR REPLACE FUNCTION api.add_inout(
    p_order_id numeric,
    p_poreference character varying,
    p_user_id numeric,
    p_line character varying)
  RETURNS json AS
$BODY$
DECLARE
--Variables usadas para M_InOut
    V_ID numeric;
    V_DOCUMENTNO numeric;
    V_BPARTNER_ID numeric;
    V_BPARTNER_LOCATION_ID numeric;
    V_WAREHOUSE_ID numeric;
    V_ORG_ID numeric;
    V_DESCRIPTION character varying;
    V_CHARGEDETAIL numeric;
    V_DOCSTATUS character varying;
    
-- Variables usadas para M_InOutLine
    V_ID_LINE numeric;
    V_C_ORDERLINE_ID numeric;
    V_C_ORDERLINE_PRICE numeric;
    V_DESCRIPTION_LINE character varying;
    V_CREATEASSET character varying; 
    V_CAPVSEXP character varying; 
    V_ASSET_GROUP_ID numeric; 
    V_UOM_ID numeric;
    V_CHARGE_ID numeric;
    V_PRODUCT_ID numeric;
    V_JSON jsonb;
    line_data jsonb;
    
BEGIN
        -- SELECT SEQUENCE AND ID DOCUMENTNO
        SELECT CurrentNext INTO V_ID
        FROM adempiere.AD_Sequence
        WHERE AD_Sequence_ID = 256;

        SELECT CurrentNext INTO V_DOCUMENTNO
        FROM adempiere.AD_Sequence
        WHERE AD_Sequence_ID = 1000021;

    -- OBTENER DATOS DE LA ORDEN
	SELECT
	    o.c_bpartner_id,
	    o.c_bpartner_location_id,
	    o.m_warehouse_id,
	    o.ad_org_id,
	    o.description,
	    MAX(cl.c_charge_id) AS max_charge_id
	INTO
	    V_BPARTNER_ID,
	    V_BPARTNER_LOCATION_ID,
	    V_WAREHOUSE_ID,
	    V_ORG_ID,
	    V_DESCRIPTION,
	    V_CHARGEDETAIL
	FROM
	    adempiere.c_order o
	LEFT JOIN
	    adempiere.c_orderline cl ON o.c_order_id = cl.c_order_id
	WHERE
	    o.c_order_id = P_ORDER_ID
	GROUP BY
	    o.c_bpartner_id,
	    o.c_bpartner_location_id,
	    o.m_warehouse_id,
	    o.ad_org_id,
	    o.description;

        -- INSERTAR EN LA TABLA M_InOut y completamos, ya que la orden corresponde a "cargo"
    INSERT INTO adempiere.M_InOut(m_inout_id,
				ad_client_id, 
				ad_org_id, 
				isactive, 
				created, 
				createdby, 
				updated, 
				updatedby, 
				issotrx, 
				description, 
				documentno, 
				docaction, 
				docstatus, 
				c_doctype_id, 
				c_order_id, 
				movementtype, 
				movementdate, 
				dateacct, 
				c_bpartner_id, 
				c_bpartner_location_id, 
				m_warehouse_id, 
				poreference, 
				deliveryrule, 
				freightcostrule, 
				deliveryviarule, 
				priorityrule, 
				processing, 
				processed,
				createfrom, 
				generateto,
				trackingno,
				createconfirm, 
				createpackage,
				isapproved, 
				volume, 
				weight)
			VALUES ( V_ID ,
				1000000, 
				V_ORG_ID, 
				'Y', 
				now(), 
				P_USER_ID, 
				now(), 
				P_USER_ID, 
				'N', 
				V_DESCRIPTION, 
				V_DOCUMENTNO, 
				CASE WHEN  V_CHARGEDETAIL > 0 THEN 'CL' ELSE 'CO' END, 
				CASE WHEN  V_CHARGEDETAIL > 0 THEN 'CO' ELSE 'DR' END, 
				1000014, 
				P_ORDER_ID, 
				'V+', 
				now()::date, 
				now()::date, 
				V_BPARTNER_ID, 
				V_BPARTNER_LOCATION_ID, 
				V_WAREHOUSE_ID, 
				P_POREFERENCE, 
				'A', 
				'I', 
				'P', 
				'5', 
				'N',
				CASE WHEN V_CHARGEDETAIL > 0 THEN 'Y' ELSE 'N' END, 
				'Y', 
				'N',
				'APP',
				'N', 
				'N',
				CASE WHEN V_CHARGEDETAIL > 0 THEN 'Y' ELSE 'N' END, 
				0, 
				0)
    RETURNING m_inout_id, docstatus INTO V_ID, V_DOCSTATUS;

    ---Se guarda el JSON enviado en la variable a usar
    V_JSON := p_line::jsonb;
    
    -- Iterar a través de los elementos del JSON e insertar en M_InOutLine
    FOR line_data IN SELECT * FROM jsonb_array_elements(V_JSON)
    LOOP

    --Obtener Secuencias asociadas al ID de las lineas
    SELECT CurrentNext INTO V_ID_LINE
    FROM adempiere.AD_Sequence
    WHERE AD_Sequence_ID = 257;

        --Extraer datos de la orderline
	SELECT c_orderline_id, priceentered,description, a_createasset, a_capvsexp, a_asset_group_id, c_uom_id , c_charge_id, m_product_id
	INTO V_C_ORDERLINE_ID, V_C_ORDERLINE_PRICE, V_DESCRIPTION_LINE, V_CREATEASSET, V_CAPVSEXP, V_ASSET_GROUP_ID, V_UOM_ID, V_CHARGE_ID, V_PRODUCT_ID
	FROM adempiere.c_orderline
	WHERE c_order_id = P_ORDER_ID
	AND (line_data->>'line')::numeric = c_orderline.line::numeric;
	

        -- INSERTAR EN LA TABLA M_InOutLine
        INSERT INTO adempiere.M_InOutLine(
            m_inout_id,
            m_inoutline_id, 
            ad_client_id, 
            ad_org_id, 
            isactive, 
            created, 
            createdby, 
            updated, 
            updatedby,
            line,
            description,
            c_orderline_id,
            qtyentered,
            c_uom_id,
            priceactual,
            isinvoiced,
            processed,
            a_createasset,
            a_capvsexp,
            a_asset_group_id,
            c_charge_id,
            m_locator_id,
            movementqty,
            m_product_id
        )
        VALUES (
            V_ID,
            V_ID_LINE,
            1000000,
            V_ORG_ID,
            'Y',
            now(),
            P_USER_ID,
            now(),
            P_USER_ID,
            (line_data->>'line')::numeric,
            V_DESCRIPTION_LINE,
            V_C_ORDERLINE_ID,
            (line_data->>'qtydelivered')::numeric,
            V_UOM_ID,
            V_C_ORDERLINE_PRICE,
            'N',
            CASE WHEN V_CHARGE_ID > 0 THEN 'Y' ELSE 'N' END,
            V_CREATEASSET,
            V_CAPVSEXP,
            V_ASSET_GROUP_ID,
            V_CHARGE_ID,
            CASE WHEN V_CHARGE_ID > 0 THEN 1000006 ELSE null END,
            (line_data->>'qtydelivered')::numeric,
            V_PRODUCT_ID
        );

       --Incrementar el ID de línea
	UPDATE adempiere.AD_Sequence 
	SET CurrentNext = V_ID_LINE + 1
	WHERE AD_Sequence_ID = 257;
	
	-- Modificamos la cantidad en la linea de la order solo si es cargo.
	IF V_CHARGE_ID > 0 THEN
	UPDATE adempiere.c_orderline SET qtydelivered = (line_data->>'qtydelivered')::numeric + qtydelivered::numeric
	WHERE c_order_id = P_ORDER_ID
	AND (line_data->>'line')::numeric = c_orderline.line::numeric;

	END IF;
      
      END LOOP;

    -- Actualizar la secuencia AD_Sequence
    UPDATE adempiere.AD_Sequence 
    SET CurrentNext = V_ID + 1
    WHERE AD_Sequence_ID = 256;

    UPDATE adempiere.AD_Sequence 
    SET CurrentNext = V_DOCUMENTNO + 1
    WHERE AD_Sequence_ID = 1000021;
  
        -- Retornar el resultado como JSON
    RETURN json_build_object('m_inout_id', V_ID, 'docstatus', V_DOCSTATUS);
	
EXCEPTION
   WHEN others THEN
	RAISE EXCEPTION 'Error en la funcion %, line_data es %', SQLERRM, V_JSON;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION api.add_inout(numeric, character varying, numeric, character varying)
  OWNER TO pg_api;
GRANT EXECUTE ON FUNCTION api.add_inout(numeric, character varying, numeric, character varying) TO pg_api;
REVOKE ALL ON FUNCTION api.add_inout(numeric, character varying, numeric, character varying) FROM public;
