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

:: E: TCP set + UDP 443 (QUIC) + UDP STUN (3478-3481)
start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%~dp0..\filters\wf-bf6-E.txt" ^
--filter-tcp=443,80,8095,9000,10010,15013,2053,2083,2087,2096,8443 --dpi-desync=fake,split2 --dpi-desync-autottl=2 --dpi-desync-repeats=6 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2 --new ^
--filter-udp=443 --filter-l7=quic --dpi-desync=fake --dpi-desync-repeats=9 --dpi-desync-fake-quic="%BIN%quic_initial_www_google_com.bin" --dpi-desync-cutoff=n2 --new ^
--filter-udp=3478-3481 --dpi-desync=fake --dpi-desync-repeats=7 --dpi-desync-cutoff=n2

