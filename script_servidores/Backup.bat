@echo off
for /f "tokens=1-3 delims=/ " %%i in ("%date%") do (
    set day=%%i
    set month=%%j
    set year=%%k
) 
set datestr=%day%_%month%_%year%
echo datestr is %datestr%
set BACKUP_FILE=D:/Backup/Adempiere.backup
SET PGPASSWORD=36jwhowHAoJFKO0z9wc8M4nPh2hPHIY1

echo on
pg_dump -i -h localhost -p 5432 -U adempiere -Fc -b -v -f %BACKUP_FILE% -d tsm

SET PGPASSWORD=36jwhowHAoJFKO0z9wc8M4nPh2hPHIY1

pause

