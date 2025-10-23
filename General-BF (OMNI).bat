@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 > nul
:: 65001 - UTF-8

cd /d "%~dp0"
call service.bat status_zapret
echo:

set "BIN=%~dp0bin\"
set "LISTS=%~dp0lists\"
set "PORT_FILE=%LISTS%port-bf.txt"
set "WF_TMP=%TEMP%\wf_bf_omni_prod.txt"
cd /d %BIN%

:: Read BF port range (e.g. 65530-65535 or 65535)
set "BFPORTS="
for /f "usebackq tokens=1 delims=" %%L in ("%PORT_FILE%") do (
  if not "%%L"=="" (
    set "BFPORTS=%%L"
    goto :have_bf
  )
)
:have_bf
if not defined BFPORTS (
  echo [WARN] lists\port-bf.txt missing or empty. Using default 65530-65535
  set "BFPORTS=65530-65535"
)

set "START_PORT="
set "END_PORT="
if not "!BFPORTS:-=!"=="!BFPORTS!" (
  set "_R=!BFPORTS:-= !"
  for /f "tokens=1,2" %%A in ("!_R!") do (
    set "START_PORT=%%A"
    set "END_PORT=%%B"
  )
) else (
  set "START_PORT=!BFPORTS!"
  set "END_PORT=!BFPORTS!"
)
if not defined START_PORT set "START_PORT=65530"
if not defined END_PORT set "END_PORT=65535"

:: Build unified WinDivert filter: TCP(80,443,2053,2083,2087,2096,8443) OR UDP dst 443 OR UDP src BF range
echo outbound and ((tcp and (tcp.DstPort == 80 or tcp.DstPort == 443 or tcp.DstPort == 2053 or tcp.DstPort == 2083 or tcp.DstPort == 2087 or tcp.DstPort == 2096 or tcp.DstPort == 8443)) or (udp and (udp.DstPort == 443 or (udp.DstPort^>^=19294 and udp.DstPort^<^=19344) or (udp.DstPort^>^=50000 and udp.DstPort^<^=50100) or (udp.SrcPort^>^=!START_PORT! and udp.SrcPort^<^=!END_PORT!))))>"%WF_TMP%"

start "zapret: %~n0" /min "%BIN%winws.exe" --wf-raw=@"%WF_TMP%" ^
--filter-udp=443 --hostlist="%LISTS%list-general.txt" --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic="%BIN%quic_initial_www_google_com.bin" --new ^
--filter-tcp=80 --hostlist="%LISTS%list-general.txt" --dpi-desync=fake,multisplit --dpi-desync-autottl=2 --dpi-desync-fooling=md5sig --new ^
--filter-tcp=2053,2083,2087,2096,8443 --hostlist-domains=discord.media --dpi-desync=fake,multidisorder --dpi-desync-split-pos=midsld --dpi-desync-repeats=8 --dpi-desync-fooling=md5sig,badseq --new ^
--filter-tcp=443 --hostlist="%LISTS%list-general.txt" --dpi-desync=fake,multidisorder --dpi-desync-split-pos=midsld --dpi-desync-repeats=8 --dpi-desync-fooling=md5sig,badseq --new ^
--filter-udp=443 --ipset="%LISTS%ipset-all.txt" --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic="%BIN%quic_initial_www_google_com.bin" --new ^
--filter-tcp=80 --ipset="%LISTS%ipset-all.txt" --dpi-desync=fake,multisplit --dpi-desync-autottl=2 --dpi-desync-fooling=md5sig --new ^
--filter-tcp=443 --ipset="%LISTS%ipset-all.txt" --dpi-desync=fake,multidisorder --dpi-desync-split-pos=midsld --dpi-desync-repeats=6 --dpi-desync-fooling=md5sig,badseq --new ^
:: BF handshake: apply generic UDP desync to any UDP matched by wf-raw (i.e., src BF range or dst 443)
--new ^
--filter-udp=* --dpi-desync=fake --dpi-desync-any-protocol=1 --dpi-desync-autottl=2 --dpi-desync-repeats=9 --dpi-desync-fake-unknown-udp="%BIN%quic_initial_www_google_com.bin" --dpi-desync-cutoff=n2

endlocal
