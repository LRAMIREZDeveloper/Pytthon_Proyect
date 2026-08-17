import json
import logging
import psycopg2

from psycopg2.extras import execute_values
from connection import connect_to_api, user_login, call_apis


logging.basicConfig(
    filename='error_assetlocation.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================
# CONEXIÓN A POSTGRESQL
# ============================================================

def connect_to_database():
    return psycopg2.connect(
        host='adempiere.tsm.cl',
        port='5432',
        database='tsm',
        user='pg_api',
        password='8YR53mDRavJlfd6d'
    )


# ============================================================
# OBTENER ASSETS DESDE LA API
# ============================================================

def data_asset():

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # Obtener credenciales para la API
        # ----------------------------------------------------

        USER_NAME, PASSWORD = user_login()

        server, _, _, _, _, context_location, _ = call_apis()

        response = connect_to_api(
            USER_NAME,
            PASSWORD,
            server,
            context_location
        )

        body = response.read().decode('utf-8')

        # ----------------------------------------------------
        # Validar respuesta
        # ----------------------------------------------------

        if response.getcode() != 200:
            print(f'Error API: {response.getcode()}')
            return None

        # ----------------------------------------------------
        # Convertir respuesta a JSON
        # ----------------------------------------------------

        assets = json.loads(body)

        if not assets:
            print('No se encontraron assets para guardar.')
            return []

        print(f'Assets recibidos: {len(assets)}')

        # ----------------------------------------------------
        # Preparar registros para PostgreSQL
        # ----------------------------------------------------

        data_list = []

        for asset in assets:

            data = (

                asset.get('reportId'),
                asset.get('sequentialId'),

                asset.get('reportDate'),
                asset.get('inputDate'),

                asset.get('deviceId'),
                asset.get('holderId'),

                asset.get('assetId'),
                asset.get('assetName'),

                asset.get('eventId'),
                asset.get('eventName'),

                asset.get('gpsValidity'),
                asset.get('gpsSatellites'),
                asset.get('gpsDop'),

                asset.get('latitude'),
                asset.get('longitude'),

                asset.get('location'),

                asset.get('speed'),
                asset.get('heading'),
                asset.get('altitude'),
                asset.get('odometer'),
                asset.get('gpsSpeed'),
                asset.get('cartographyLimitSpeed'),

                asset.get('backupBatteryVoltage'),
                asset.get('batteryVoltage'),
                asset.get('backupBatteryChargePercentage'),

                asset.get('ignition'),
                asset.get('ignitionDate'),

                asset.get('hourmeter'),
                asset.get('totalFuelUsed'),

                asset.get('onboardComputerHourmeter'),
                asset.get('onboardComputerOdometer'),

                asset.get('serviceBrakingOdometer'),
                asset.get('engineBrakingOdometer'),

                asset.get('zoneCode'),

                asset.get('ralentiBandTime'),
                asset.get('yellowBandTime'),
                asset.get('efficientHandlingBandTime'),
                asset.get('redBandTime'),
                asset.get('loadOverSeventyFivePercentBandTime'),
                asset.get('inefficientCruiseControlBandTime'),
                asset.get('engagedGearWhileInertialDrivingTime'),
                asset.get('engineBrakingTime'),

                asset.get('abruptBrakingQuantity'),

                asset.get('ecuTfu'),

                asset.get('engineRunningStatus'),

                asset.get('parameterValue'),
                asset.get('parameterName'),
                asset.get('parameterId'),

                asset.get('driverName'),
                asset.get('driverLastName'),
                asset.get('driverDocumentType'),
                asset.get('driverDocumentNumber'),

                asset.get('areaType'),

                asset.get('deviceHourmeter'),
                asset.get('receivedIcanDataPercentage'),

                asset.get('odometerDate'),

                asset.get('tankFuelVolume'),
                asset.get('tankFuelPercentage'),

                asset.get('onboardComputerFuelLevelVolume'),
                asset.get('onboardComputerFuelLevelPercentage'),

                asset.get('drivingHourmeter'),

                asset.get('errorCode'),
                asset.get('endIdleTime'),
                asset.get('tripidCode'),

                asset.get('associatedEventDate'),

                asset.get('reasonText')
            )

            data_list.append(data)

        # ----------------------------------------------------
        # Conectar a PostgreSQL
        # ----------------------------------------------------

        connection = connect_to_database()

        cursor = connection.cursor()

        # ----------------------------------------------------
        # INSERT masivo
        # ----------------------------------------------------

        query = """
            INSERT INTO api.i_asset_data_location
            (
                report_id,
                sequential_id,
                report_date,
                input_date,
                device_id,
                holder_id,
                asset_id,
                asset_name,
                event_id,
                event_name,
                gps_validity,
                gps_satellites,
                gps_dop,
                latitude,
                longitude,
                location,
                speed,
                heading,
                altitude,
                odometer,
                gps_speed,
                cartography_limit_speed,
                backup_battery_voltage,
                battery_voltage,
                backup_battery_charge_percentage,
                ignition,
                ignition_date,
                hourmeter,
                total_fuel_used,
                onboard_computer_hourmeter,
                onboard_computer_odometer,
                service_braking_odometer,
                engine_braking_odometer,
                zone_code,
                ralenti_band_time,
                yellow_band_time,
                efficient_handling_band_time,
                red_band_time,
                load_over_seventy_five_percent_band_time,
                inefficient_cruise_control_band_time,
                engaged_gear_while_inertial_driving_time,
                engine_braking_time,
                abrupt_braking_quantity,
                ecu_tfu,
                engine_running_status,
                parameter_value,
                parameter_name,
                parameter_id,
                driver_name,
                driver_last_name,
                driver_document_type,
                driver_document_number,
                area_type,
                device_hourmeter,
                received_ican_data_percentage,
                odometer_date,
                tank_fuel_volume,
                tank_fuel_percentage,
                onboard_computer_fuel_level_volume,
                onboard_computer_fuel_level_percentage,
                driving_hourmeter,
                error_code,
                end_idle_time,
                tripid_code,
                associated_event_date,
                reason_text
            )
            VALUES %s
        """

        # ----------------------------------------------------
        # Limpiar tabla antes de cargar datos actualizados
        # ----------------------------------------------------

        print('Eliminando datos anteriores...')

        cursor.execute("""
            TRUNCATE TABLE api.i_asset_data_location
        """)

        print('Datos anteriores eliminados.')


        # ----------------------------------------------------
        # Ejecutar INSERT
        # ----------------------------------------------------

        execute_values(
            cursor,
            query,
            data_list,
            page_size=1000
        )

        connection.commit()

        print('-----------------------------------')
        print('Proceso terminado correctamente')
        print(f'Registros procesados: {len(data_list)}')
        print('-----------------------------------')

        return assets

    except Exception as e:

        if connection:
            connection.rollback()

        logger.error(
            'Error en data_asset: {}'.format(e),
            exc_info=True
        )

        print(f'Error: {e}')

        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    datos = data_asset()