@echo off
set LOG=D:\log\adempiere\refresh-petro.log
set ERR=D:\log\adempiere\error-petro.log

REM Sobrescribe el archivo LOG y ERR para comenzar limpio cada vez
echo. > %LOG%
echo. > %ERR%

REM Mide el tiempo de inicio
for /f "tokens=1-4 delims=:.," %%a in ("%time%") do (
    set HOUR=%%a
    set MINUTE=%%b
    set SECOND=%%c
    set MILLISECOND=%%d
)
set /a STARTTIME=(%HOUR%*360000+%MINUTE%*6000+%SECOND%*100+%MILLISECOND%)

REM Agrega la fecha y hora al archivo LOG
echo %date% %time% > %LOG%

REM Define las variables de conexión
set PGUSER=adempiere
set PGHOST=adempiere.petroamerica.cl
set PGDATABASE=petro
set PGPASSWORD=36jwhowHAoJFKO0z9wc8M4nPh2hPHIY1

REM Ejecuta los comandos de PostgreSQL
psql -U %PGUSER% -h %PGHOST% -d %PGDATABASE% -c "refresh materialized view horacio_rvofb_dias_calle_v2;" > %LOG% 2> %ERR%
psql -U %PGUSER% -h %PGHOST% -d %PGDATABASE% -c "refresh materialized view rvofb_dias_calle_v2;" > %LOG% 2> %ERR%

REM Mide el tiempo de finalización
for /f "tokens=1-4 delims=:.," %%a in ("%time%") do (
    set HOUR=%%a
    set MINUTE=%%b
    set SECOND=%%c
    set MILLISECOND=%%d
)
set /a ENDTIME=(%HOUR%*360000+%MINUTE%*6000+%SECOND%*100+%MILLISECOND%)

REM Calcula la diferencia de tiempo
set /a DIFF=%ENDTIME% - %STARTTIME%

REM Convierte la diferencia a segundos
set /a SECONDS=%DIFF% / 100
echo Segundos: %SECONDS% >> %LOG%
echo Segundos: %SECONDS%



