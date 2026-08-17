
# Consulta para extraer el dato de los lideres operacionales para el envio de la notificacion
user_data = """
                SELECT ad.description, mb.phonenumber
                FROM adempiere.ad_user ad
                    JOIN adempiere.TI_MobileCtrl_Allocated ma ON ma.c_bpartner_id = ad.c_bpartner_id
                    JOIN adempiere.TI_MobileCtrl mb ON mb.TI_MobileCtrl_ID = ma.TI_MobileCtrl_ID
                    JOIN adempiere.c_bpartner cb ON ad.c_bpartner_id = cb.c_bpartner_id 
                WHERE ad.recruitmentaproval IN ('LO','GG','G')
                AND mb.description = 'LABORAL'
                ORDER BY ad.description LIMIT 1
"""

# PPU con FC vencidas en circulacion
ppu_data = """
                    SELECT DISTINCT value, NOW()::date AS fecha, 
                        STRING_AGG(concept_name, ', ') AS conceptos 
                    FROM bi.criticaldate_asset_expired 
                    GROUP BY value, fecha;
                """