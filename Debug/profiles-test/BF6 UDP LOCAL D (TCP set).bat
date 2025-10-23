@echo off
chcp 65001 > nul
cd /d "%~dp0..\\..\\"
call service.bat status_zapret
call service.bat check_updates
set "BIN_ROOT=%~dp0..\\..\\bin\\"
set "LISTS=%~dp0..\\lists\\"
cd /d %BIN%
start "zapret: %~n0" /min "%BIN_ROOT%winws.exe" --wf-raw=@"%~dp0..\\filters\\wf-bf6-u-local-D.txt" ^
--filter-tcp=443,80,8095,9000,10010,15013,2053,2083,2087,2096,8443 --dpi-desync=fake,split2 --dpi-desync-autottl=2 --dpi-desync-repeats=6 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2 --new ^
--filter-udp=* --dpi-desync=fake --dpi-desync-any-protocol=1 --dpi-desync-autottl=2 --dpi-desync-repeats=10 --dpi-desync-fake-unknown-udp="%BIN_ROOT%quic_initial_www_google_com.bin" --dpi-desync-cutoff=n2


