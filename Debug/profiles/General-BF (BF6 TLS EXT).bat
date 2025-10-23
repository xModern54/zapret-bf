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

:: TEST STRATEGY: TLS on BF6 ports (443 + aux) and QUIC on UDP:443
:: - WFP: outbound tcp.DstPort in {443,8095,9000,10010,15013,8443,80} and udp.DstPort==443
:: - Strategy:
::    * TLS only on listed TCP ports (short cutoff)
::    * QUIC on UDP:443 (short cutoff)
:: - Exclude anti-cheat/Steam/CDN by SNI/Host

start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%~dp0..\filters\wf-bf6-ports-tls-ext.txt" ^
--filter-tcp=443,8095,9000,10010,15013,8443 --filter-l7=tls --hostlist-exclude="%LISTS%exclude-domains.txt" --dpi-desync=fake --dpi-desync-fake-tls-mod=none --dpi-desync-repeats=6 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2 --new ^
--filter-udp=443 --filter-l7=quic --dpi-desync=fake --dpi-desync-repeats=9 --dpi-desync-fake-quic="%BIN%quic_initial_www_google_com.bin" --dpi-desync-cutoff=n2

