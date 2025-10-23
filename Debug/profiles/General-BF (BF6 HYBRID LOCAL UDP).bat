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

:: HYBRID: TCP set + UDP local observed ranges + UDP 443/3478-3481/3659
start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%~dp0..\filters\wf-bf6-hybrid.txt" ^
--filter-tcp=443,80,8095,9000,10010,15013,2053,2083,2087,2096,8443 --dpi-desync=fake,split2 --dpi-desync-autottl=2 --dpi-desync-repeats=8 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=10000000 --dpi-desync-cutoff=n2 --new ^
--filter-udp=* --dpi-desync=fake --dpi-desync-any-protocol=1 --dpi-desync-autottl=2 --dpi-desync-repeats=10 --dpi-desync-fake-unknown-udp="%BIN%quic_initial_www_google_com.bin" --dpi-desync-cutoff=n2

