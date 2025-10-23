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

:: TEST STRATEGY: only TLS on TCP:443 for BF6 (handshake stage only)
:: - WFP: outbound tcp.DstPort == 443 only
:: - Strategy: TLS only, short cutoff, moderate repeats
:: - Exclude common anti-cheat/Steam/CDN domains by SNI/Host

start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%~dp0..\filters\wf-bf6-ports-tls.txt" ^
--filter-tcp=443 --filter-l7=tls --hostlist-exclude="%LISTS%exclude-domains.txt" --dpi-desync=fake --dpi-desync-fake-tls-mod=none --dpi-desync-repeats=5 --dpi-desync-fooling=badseq --dpi-desync-badseq-increment=2 --dpi-desync-cutoff=n2

