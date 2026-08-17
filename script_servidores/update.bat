@echo off
set LOG=D:\log\adempiere\update-petro.log
set ERR=D:\log\adempiere\error-petro.log

REM Mide el tiempo de inicio
for /f "tokens=1-4 delims=:.," %%a in ("%time%") do (
    set HOUR=%%a
    set MINUTE=%%b
    set SECOND=%%c
    set MILLISECOND=%%d
)
set /a STARTTIME=(%HOUR%*360000+%MINUTE%*6000+%SECOND%*100+%MILLISECOND%)

REM Agrega la fecha y hora al archivo LOG
echo %date% %time% >> %LOG%

REM Define las variables de conexión
set PGUSER=adempiere
set PGHOST=adempiere.petroamerica.cl
set PGDATABASE=petro
set PGPASSWORD=36jwhowHAoJFKO0z9wc8M4nPh2hPHIY1

REM Ejecuta los comandos de PostgreSQL
psql -U %PGUSER% -h %PGHOST% -d %PGDATABASE% -c "update c_bpartner set totalopenbalanceofb=coalesce(owncreditlimit,0)+coalesce(externalcreditlimit,0),so_creditusedofb=0 where iscustomer='Y';" >> %LOG% 2>> %ERR%
psql -U %PGUSER% -h %PGHOST% -d %PGDATABASE% -c "update c_bpartner cbp set so_creditusedofb=Coalesce(( SELECT sum(t.dueamt) AS sum FROM ( SELECT coalesce(dc.dueamt,0) AS dueamt FROM rvofb_dias_calle_v2 dc WHERE dc.c_bpartner_id = cbp.c_bpartner_id and (dc.dueamt not between -5 and 5 or  dc.option=1) and dc.option2=1) t),0) + coalesce((select sum(co.grandtotal) from c_order co where co.c_bpartner_id=cbp.c_bpartner_id and co.c_order_id in (select c_order_id from rvofb_guias_pendientes)),0) where cbp.iscustomer='Y';" >> %LOG% 2>> %ERR%
psql -U %PGUSER% -h %PGHOST% -d %PGDATABASE% -c "update c_bpartner set totalopenbalanceofb=(coalesce(owncreditlimit,0)+coalesce(externalcreditlimit,0))-so_creditusedofb where iscustomer='Y';" >> %LOG% 2>> %ERR%
psql -U %PGUSER% -h %PGHOST% -d %PGDATABASE% -c "update c_bpartner set totalopenbalanceofb=coalesce(owncreditlimit,0)+coalesce(externalcreditlimit,0),so_creditusedofb=0 where iscustomer='N';" >> %LOG% 2>> %ERR%

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