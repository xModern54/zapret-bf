Test profiles to isolate the minimal UDP subset that fixes BF6 matchmaking handshake.

How to use
- From root: service.bat → Install Service → pick one profile at a time.
- Before switching, stop/remove the previous service to avoid overlaps.

Order to test
1) BF6 UDP LOCAL A (TCP set)   → UDP src 54356–54380
2) BF6 UDP LOCAL B (TCP set)   → UDP src 60517–60518
3) BF6 UDP LOCAL C (TCP set)   → UDP src 52833,55528,58360,60050
4) BF6 UDP LOCAL D (TCP set)   → UDP src 64682,65108,65370,65535

If none of A–D work, fallback to the working HYBRID profiles in root to reconfirm.

TCP set in all profiles
- 443, 80, 8095, 9000, 10010, 15013, 2053, 2083, 2087, 2096, 8443
- Desync: fake,split2 + autottl=2 + repeats=6 + cutoff=n2
