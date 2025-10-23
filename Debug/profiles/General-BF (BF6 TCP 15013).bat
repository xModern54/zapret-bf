@echo off
chcp 65001 > nul
:: 65001 - UTF-8

cd /d "%~dp0"
call service.bat status_zapret
call service.bat check_updates
echo:

set "BIN=%~dp0bin\"
set "LISTS=%~dp0lists\"
cd /d %BIN%

start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%BIN%wf-tcp-15013.txt" ^
--filter-tcp=15013 --dpi-desync=fake --dpi-desync-repeats=4 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2

