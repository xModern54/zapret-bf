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

:: TEST STRATEGY: apply DPI only on BF6 TCP ports (no UDP tamper)
:: - WFP: outbound TCP dst ports {443,80,8095,9000,10010,15013}
:: - Strategy: generic fake/split with short cutoff; no L7 filter to avoid misclassification

start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%~dp0..\filters\wf-bf6-ports-tcp.txt" ^
--filter-tcp=443 --dpi-desync=fake,split2 --dpi-desync-autottl=2 --dpi-desync-repeats=6 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2 --new ^
--filter-tcp=80,8095,9000,10010,15013 --dpi-desync=fake --dpi-desync-repeats=4 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2

