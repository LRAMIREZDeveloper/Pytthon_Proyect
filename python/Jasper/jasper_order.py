import subprocess

def compile_jrxml_to_jasper(jrxml_file):
    """
    Compila un archivo JRXML a Jasper (.jasper).
    """
    try:
        jasperstarter_path = 'C:/Program Files (x86)/JasperStarter/bin/jasperstarter.exe'

        command = [jasperstarter_path, 'compile', jrxml_file]
        subprocess.run(command, check=True)
        print(f'Compilación exitosa: {jrxml_file} compilado a Jasper.')
    except subprocess.CalledProcessError as e:
        print(f'Error al compilar {jrxml_file}: {e}')

def generate_pdf_from_jasper(jasper_file, output_pdf, c_order_id, db_params):
    """
    Genera un informe PDF desde un archivo Jasper compilado.
    """
    try:
        jasperstarter_path = 'C:/Program Files (x86)/JasperStarter/bin/jasperstarter.exe'

        command = [
            jasperstarter_path, 'process', jasper_file, 
            '-f', 'pdf', '-o', output_pdf, 
            '-P', f'C_Order_ID={c_order_id}',
            '-t', 'postgres',
            '-H', db_params['host'],
            '-n', db_params['db_name'],
            '-u', db_params['user'],
            '-p', db_params['password'],
            '--jdbc-dir', 'C:/Program Files (x86)/JasperStarter/lib'
        ]
        subprocess.run(command, check=True)
        print(f'Informe PDF generado: {output_pdf}')
    except subprocess.CalledProcessError as e:
        print(f'Error al generar PDF desde {jasper_file}: {e}')

def main():
    # Parámetro C_Order_ID
    c_order_id = 1110227

    # Detalles de conexión a la base de datos
    db_params = {
        'host': 'adempiere.tsm.cl',
        'db_name': 'tsm',
        'user': 'pg_api',
        'password': '8YR53mDRavJlfd6d'
    }

    # Rutas a los archivos JRXML y salida del archivo PDF
    jrxml_file = 'C:/Users/lramirez/Github/Pytthon_Proyect/python/Jasper/jrxml/Order.jrxml'
    output_pdf = 'C:/Users/lramirez/Github/Pytthon_Proyect/extracted_files/order'

    # Compilar JRXML a Jasper
    compile_jrxml_to_jasper(jrxml_file)

    # Generar PDF desde Jasper compilado
    jasper_file = jrxml_file.replace('.jrxml', '.jasper')
    generate_pdf_from_jasper(jasper_file, output_pdf, c_order_id, db_params)


if __name__ == "__main__":
    main()
