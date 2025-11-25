"""Firmware templates for Hargassner pellet boilers.

This module contains XML templates (DAQPRJ format) that define the parameter
structure for different firmware versions of Hargassner boilers.
"""

from __future__ import annotations

from typing import Final

# Firmware Templates
#
# XML templates in DAQPRJ format from Hargassner DAQ files.
# These define the structure and order of telnet message parameters
#
# To add support for a new firmware version:
# 1. Use tools/daq_parser.py to extract the DAQPRJ template from a DAQ file
# 2. Add it here with a descriptive version key (e.g., "NANO_V15X")
# 3. Update FIRMWARE_VERSIONS in const.py

FIRMWARE_TEMPLATES: Final[dict[str, str]] = {
    "V14_1HAR_q1": """<DAQPRJ><ANALOG><CHANNEL id='0' name='ZK' dop='0'/><CHANNEL id='1' name='O2' unit='%'/><CHANNEL id='2' name='O2soll' unit='%'/><CHANNEL id='3' name='TK' unit='°C'/><CHANNEL id='4' name='TKsoll' unit='°C'/><CHANNEL id='5' name='TRL' unit='°C'/><CHANNEL id='6' name='TRLsoll' unit='°C' dop='0'/><CHANNEL id='7' name='Spreizung' unit='°C'/><CHANNEL id='8' name='TRG' unit='°C'/><CHANNEL id='9' name='SZist' unit='%' dop='0'/><CHANNEL id='10' name='SZsoll' unit='%'/><CHANNEL id='11' name='TPo' unit='°C'/><CHANNEL id='12' name='TPm' unit='°C'/><CHANNEL id='13' name='TPu' unit='°C'/><CHANNEL id='14' name='Puff Füllgrad' unit='%' dop='0'/><CHANNEL id='15' name='Puffer_soll oben' unit='°C' dop='0'/><CHANNEL id='16' name='Puffer_soll unten' unit='°C' dop='0'/><CHANNEL id='17' name='PuffZustand' dop='0'/><CHANNEL id='18' name='Max Anf Kessel' dop='0'/><CHANNEL id='19' name='TFW' unit='°C' dop='0'/><CHANNEL id='20' name='Leistung' unit='%' dop='0'/><CHANNEL id='21' name='ESsoll' unit='%'/><CHANNEL id='22' name='min.Leist.TRG' unit='%'/><CHANNEL id='23' name='max.Leist.TRG' unit='%'/><CHANNEL id='24' name='max.Leist.Fuell' unit='%'/><CHANNEL id='25' name='max.Leist.TPO' unit='%'/><CHANNEL id='26' name='ESRegler' unit='%' dop='0'/><CHANNEL id='27' name='Regler K'/><CHANNEL id='28' name='KeBrstScale' unit='%' dop='0'/><CHANNEL id='29' name='Programm' dop='0'/><CHANNEL id='30' name='Störungs Nr' dop='0'/><CHANNEL id='31' name='Max Anf ZenPuf' unit='°C' dop='0'/><CHANNEL id='32' name='I Es' unit='mA' dop='0'/><CHANNEL id='33' name='I Ra' unit='mA' dop='0'/><CHANNEL id='34' name='I Aa' unit='mA' dop='0'/><CHANNEL id='35' name='I Sr' unit='mA' dop='0'/><CHANNEL id='36' name='I Rein' unit='mA' dop='0'/><CHANNEL id='37' name='BLDC_ES ist' unit='rpm' dop='0'/><CHANNEL id='38' name='BLDC_ES soll' unit='rpm' dop='0'/><CHANNEL id='39' name='LZ ES seit Füll.' unit='Min' dop='0'/><CHANNEL id='40' name='LZ ES seit Ent.' unit='Min' dop='0'/><CHANNEL id='41' name='Anzahl Entasch.' dop='0'/><CHANNEL id='42' name='Anzahl SR Beweg.' dop='0'/><CHANNEL id='43' name='Lagerstand' unit='kg' dop='0'/><CHANNEL id='44' name='Verbrauchszähler' unit='kg' dop='0'/><CHANNEL id='45' name='Heiz P Lambda' unit='W' dop='2'/><CHANNEL id='46' name='Heiz U Lambda' unit='V' dop='2'/><CHANNEL id='47' name='Heiz I Lambda' unit='mA' dop='0'/><CHANNEL id='48' name='U_Lambda' unit='mV'/><CHANNEL id='49' name='U Netzteil' unit='mV' dop='0'/><CHANNEL id='50' name='T Spülung' unit='°C'/><CHANNEL id='51' name='BRT' unit='°C'/><CHANNEL id='52' name='Tplat' unit='°C' dop='0'/><CHANNEL id='53' name='TVG' unit='°C'/><CHANNEL id='54' name='TVG2' unit='°C'/><CHANNEL id='55' name='AIN17' unit='V'/><CHANNEL id='56' name='Taus' unit='°C'/><CHANNEL id='57' name='TA Gem.' unit='°C'/><CHANNEL id='58' name='Effizienz' unit='%'/><CHANNEL id='59' name='ExtHK Solltmp.' unit='°C' dop='0'/><CHANNEL id='61' name='TVL_A' unit='°C'/><CHANNEL id='62' name='TVLs_A' unit='°C' dop='0'/><CHANNEL id='60' name='TRA_A' unit='°C'/><CHANNEL id='63' name='TRs_A' unit='°C'/><CHANNEL id='64' name='HKZustand_A' dop='0'/><CHANNEL id='65' name='FRA Zustand' dop='0'/><CHANNEL id='66' name='HKPA Status' dop='0'/><CHANNEL id='68' name='TVL_1' unit='°C'/><CHANNEL id='69' name='TVLs_1' unit='°C' dop='0'/><CHANNEL id='67' name='TRA_1' unit='°C'/><CHANNEL id='70' name='TRs_1' unit='°C'/><CHANNEL id='71' name='HKZustand_1' dop='0'/><CHANNEL id='72' name='FR1 Zustand' dop='0'/><CHANNEL id='73' name='HKP1 Status' dop='0'/><CHANNEL id='75' name='TVL_2' unit='°C'/><CHANNEL id='76' name='TVLs_2' unit='°C' dop='0'/><CHANNEL id='74' name='TRA_2' unit='°C'/><CHANNEL id='77' name='TRs_2' unit='°C'/><CHANNEL id='78' name='HKZustand_2' dop='0'/><CHANNEL id='79' name='FR2 Zustand' dop='0'/><CHANNEL id='80' name='HKP2 Status' dop='0'/><CHANNEL id='82' name='TVL_B' unit='°C'/><CHANNEL id='83' name='TVLs_B' unit='°C' dop='0'/><CHANNEL id='81' name='TRA_B' unit='°C'/><CHANNEL id='84' name='TRs_B' unit='°C'/><CHANNEL id='85' name='HKZustand_B' dop='0'/><CHANNEL id='86' name='FRB Zustand' dop='0'/><CHANNEL id='87' name='HKPB Status' dop='0'/><CHANNEL id='88' name='TBA' unit='°C'/><CHANNEL id='89' name='TBs_A' unit='°C' dop='0'/><CHANNEL id='90' name='TB1' unit='°C'/><CHANNEL id='91' name='TBs_1' unit='°C' dop='0'/><CHANNEL id='92' name='TBB' unit='°C'/><CHANNEL id='93' name='TBs_B' unit='°C' dop='0'/><CHANNEL id='94' name='HKR Anf' unit='°C'/><CHANNEL id='95' name='Anf. HKR0' unit='°C' dop='0'/><CHANNEL id='96' name='Anf. HKR1' unit='°C' dop='0'/><CHANNEL id='97' name='Anf. HKR2' unit='°C' dop='0'/><CHANNEL id='98' name='Anf. HKR3' unit='°C' dop='0'/><CHANNEL id='99' name='Anf. HKR4' unit='°C' dop='0'/><CHANNEL id='100' name='Anf. HKR5' unit='°C' dop='0'/><CHANNEL id='101' name='Anf. HKR6' unit='°C' dop='0'/><CHANNEL id='102' name='Anf. HKR7' unit='°C' dop='0'/><CHANNEL id='103' name='Anf. HKR8' unit='°C' dop='0'/><CHANNEL id='104' name='Anf. HKR9' unit='°C' dop='0'/><CHANNEL id='105' name='Anf. HKR10' unit='°C' dop='0'/><CHANNEL id='106' name='Anf. HKR11' unit='°C' dop='0'/><CHANNEL id='107' name='Anf. HKR12' unit='°C' dop='0'/><CHANNEL id='108' name='Anf. HKR13' unit='°C' dop='0'/><CHANNEL id='109' name='Anf. HKR14' unit='°C' dop='0'/><CHANNEL id='110' name='Anf. HKR15' unit='°C' dop='0'/><CHANNEL id='111' name='Wasserdruck' unit='bar' dop='2'/></ANALOG><DIGITAL><CHANNEL id='0' bit='0' name='Störung'/><CHANNEL id='0' bit='1' name='Stb'/><CHANNEL id='0' bit='2' name='Fuellstand'/><CHANNEL id='0' bit='3' name='RLP/PuffP'/><CHANNEL id='0' bit='4' name='RLm_auf'/><CHANNEL id='0' bit='5' name='RLm_zu'/><CHANNEL id='0' bit='10' name='WS freig.'/><CHANNEL id='0' bit='11' name='Akt. Code'/><CHANNEL id='0' bit='14' name='FW Freig.'/><CHANNEL id='0' bit='15' name='gFlP'/><CHANNEL id='0' bit='16' name='gFlM auf'/><CHANNEL id='0' bit='17' name='gFlM zu'/><CHANNEL id='0' bit='18' name='gFl2P'/><CHANNEL id='0' bit='19' name='gFl2M auf'/><CHANNEL id='0' bit='20' name='gFl2M zu'/><CHANNEL id='1' bit='0' name='L Heiz.'/><CHANNEL id='1' bit='1' name='Z Heiz.'/><CHANNEL id='1' bit='2' name='Z Geb.'/><CHANNEL id='1' bit='3' name='AA Run'/><CHANNEL id='1' bit='4' name='AA Dir'/><CHANNEL id='1' bit='5' name='ES Run'/><CHANNEL id='1' bit='6' name='ES Dir'/><CHANNEL id='1' bit='7' name='AS Saug'/><CHANNEL id='1' bit='8' name='AS RA Run'/><CHANNEL id='1' bit='9' name='AS RA Dir'/><CHANNEL id='1' bit='10' name='Rein En'/><CHANNEL id='1' bit='11' name='Rein Run'/><CHANNEL id='1' bit='12' name='Es Rein Endl'/><CHANNEL id='1' bit='13' name='sAS Anf Füll'/><CHANNEL id='2' bit='0' name='HKPA'/><CHANNEL id='2' bit='1' name='MAA'/><CHANNEL id='2' bit='2' name='MAZ'/><CHANNEL id='2' bit='3' name='HKP1'/><CHANNEL id='2' bit='4' name='M1A'/><CHANNEL id='2' bit='5' name='M1Z'/><CHANNEL id='2' bit='6' name='HKP2'/><CHANNEL id='2' bit='7' name='M2A'/><CHANNEL id='2' bit='8' name='M2Z'/><CHANNEL id='2' bit='9' name='HKP3'/><CHANNEL id='2' bit='10' name='M3A'/><CHANNEL id='2' bit='11' name='M3Z'/><CHANNEL id='2' bit='12' name='HKP4'/><CHANNEL id='2' bit='13' name='M4A'/><CHANNEL id='2' bit='14' name='M4Z'/><CHANNEL id='2' bit='15' name='HKP5'/><CHANNEL id='2' bit='16' name='M5A'/><CHANNEL id='2' bit='17' name='M5Z'/><CHANNEL id='2' bit='18' name='HKP6'/><CHANNEL id='2' bit='19' name='M6A'/><CHANNEL id='2' bit='20' name='M6Z'/><CHANNEL id='2' bit='21' name='HKPB'/><CHANNEL id='2' bit='22' name='MBA'/><CHANNEL id='2' bit='23' name='MBZ'/><CHANNEL id='2' bit='24' name='HK-P Poolp'/><CHANNEL id='2' bit='25' name='HK-P Primp'/><CHANNEL id='2' bit='26' name='HK-P MA'/><CHANNEL id='2' bit='27' name='HK-P MZ'/><CHANNEL id='3' bit='0' name='BPA'/><CHANNEL id='3' bit='1' name='BP1'/><CHANNEL id='3' bit='2' name='BP2'/><CHANNEL id='3' bit='3' name='BP3'/><CHANNEL id='3' bit='4' name='BPB'/><CHANNEL id='3' bit='5' name='BZPA'/><CHANNEL id='3' bit='6' name='BZP1'/><CHANNEL id='3' bit='7' name='BZP2'/><CHANNEL id='3' bit='8' name='BZP3'/><CHANNEL id='3' bit='9' name='BZPB'/><CHANNEL id='4' bit='0' name='Aschebox'/><CHANNEL id='4' bit='1' name='Netztrafo'/><CHANNEL id='4' bit='2' name='Netzrelais'/><CHANNEL id='4' bit='4' name='Lagerraum'/><CHANNEL id='4' bit='6' name='FLP'/><CHANNEL id='4' bit='8' name='ATW'/><CHANNEL id='4' bit='9' name='Entasch gesp.'/><CHANNEL id='4' bit='13' name='HKV'/><CHANNEL id='4' bit='14' name='Spülung Aktiv'/><CHANNEL id='4' bit='15' name='ExtHK vorh'/><CHANNEL id='4' bit='16' name='ExtHK_2 vorh'/><CHANNEL id='4' bit='17' name='ExtHK_3 vorh'/><CHANNEL id='5' bit='0' name='Reserved_5'/><CHANNEL id='6' bit='0' name='ExtHK Anf'/><CHANNEL id='6' bit='2' name='ExtHK_2 Anf'/><CHANNEL id='6' bit='3' name='ExtHK_3 Anf'/><CHANNEL id='6' bit='4' name='ExtHK Pumpe'/><CHANNEL id='6' bit='6' name='ExtHK_2 Pumpe'/><CHANNEL id='6' bit='7' name='ExtHK_3 Pumpe'/><CHANNEL id='6' bit='8' name='KASK1 MinLeist'/><CHANNEL id='6' bit='9' name='KASK2 MinLeist'/><CHANNEL id='6' bit='10' name='KASK3 MinLeist'/><CHANNEL id='6' bit='11' name='KASK4 MinLeist'/><CHANNEL id='6' bit='12' name='KASK1 MaxLeist'/><CHANNEL id='6' bit='13' name='KASK2 MaxLeist'/><CHANNEL id='6' bit='14' name='KASK3 MaxLeist'/><CHANNEL id='6' bit='15' name='KASK4 MaxLeist'/><CHANNEL id='6' bit='16' name='KASK1 Run'/><CHANNEL id='6' bit='17' name='KASK2 Run'/><CHANNEL id='6' bit='18' name='KASK3 Run'/><CHANNEL id='6' bit='19' name='KASK4 Run'/><CHANNEL id='6' bit='20' name='KASK1 OK'/><CHANNEL id='6' bit='21' name='KASK2 OK'/><CHANNEL id='6' bit='22' name='KASK3 OK'/><CHANNEL id='6' bit='23' name='KASK4 OK'/><CHANNEL id='6' bit='24' name='Kask KWK Out'/><CHANNEL id='6' bit='25' name='Kask FW Out'/><CHANNEL id='6' bit='26' name='KASK KWK OK'/><CHANNEL id='6' bit='27' name='KASK FW OK'/><CHANNEL id='7' bit='0' name='DReg P2'/><CHANNEL id='7' bit='1' name='DReg P3'/><CHANNEL id='7' bit='2' name='DReg Mi auf'/><CHANNEL id='7' bit='3' name='DReg Mi zu'/><CHANNEL id='7' bit='5' name='DReg2 P2'/><CHANNEL id='7' bit='6' name='DReg2 Mi auf'/><CHANNEL id='7' bit='7' name='DReg2 Mi zu'/><CHANNEL id='7' bit='9' name='DReg3 P2'/><CHANNEL id='7' bit='10' name='DReg3 P3'/><CHANNEL id='7' bit='11' name='DReg3 Mi auf'/><CHANNEL id='7' bit='12' name='DReg3 Mi zu'/><CHANNEL id='8' bit='0' name='Reserved_8'/></DIGITAL></DAQPRJ>""",
    "V14_0HAR_q" : """<DAQPRJ><ANALOG><CHANNEL id='0' name='ZK' dop='0'/><CHANNEL id='1' name='O2' unit='%'/><CHANNEL id='2' name='O2soll' unit='%'/><CHANNEL id='3' name='TK' unit='°C'/><CHANNEL id='4' name='TKsoll' unit='°C'/><CHANNEL id='5' name='TRL' unit='°C'/><CHANNEL id='6' name='TRLsoll' unit='°C' dop='0'/><CHANNEL id='7' name='Spreizung' unit='°C'/><CHANNEL id='8' name='TRG' unit='°C'/><CHANNEL id='9' name='SZist' unit='%' dop='0'/><CHANNEL id='10' name='SZsoll' unit='%'/><CHANNEL id='11' name='TPo' unit='°C'/><CHANNEL id='12' name='TPm' unit='°C'/><CHANNEL id='13' name='TPu' unit='°C'/><CHANNEL id='14' name='Puff Füllgrad' unit='%' dop='0'/><CHANNEL id='15' name='Puffer_soll oben' unit='°C' dop='0'/><CHANNEL id='16' name='Puffer_soll unten' unit='°C' dop='0'/><CHANNEL id='17' name='PuffZustand' dop='0'/><CHANNEL id='18' name='Max Anf Kessel' dop='0'/><CHANNEL id='19' name='TFW' unit='°C' dop='0'/><CHANNEL id='20' name='Leistung' unit='%' dop='0'/><CHANNEL id='21' name='ESsoll' unit='%'/><CHANNEL id='22' name='min.Leist.TRG' unit='%'/><CHANNEL id='23' name='max.Leist.TRG' unit='%'/><CHANNEL id='24' name='max.Leist.Fuell' unit='%'/><CHANNEL id='25' name='max.Leist.TPO' unit='%'/><CHANNEL id='26' name='ESRegler' unit='%' dop='0'/><CHANNEL id='27' name='Regler K'/><CHANNEL id='28' name='KeBrstScale' unit='%' dop='0'/><CHANNEL id='29' name='Programm' dop='0'/><CHANNEL id='30' name='Störungs Nr' dop='0'/><CHANNEL id='31' name='Max Anf ZenPuf' unit='°C' dop='0'/><CHANNEL id='32' name='I Es' unit='mA' dop='0'/><CHANNEL id='33' name='I Ra' unit='mA' dop='0'/><CHANNEL id='34' name='I Aa' unit='mA' dop='0'/><CHANNEL id='35' name='I Sr' unit='mA' dop='0'/><CHANNEL id='36' name='I Rein' unit='mA' dop='0'/><CHANNEL id='37' name='LZ ES seit F°ll.' unit='Min' dop='0'/><CHANNEL id='38' name='LZ ES seit Ent.' unit='Min' dop='0'/><CHANNEL id='39' name='Anzahl Entasch.' dop='0'/><CHANNEL id='40' name='Anzahl SR Beweg.' dop='0'/><CHANNEL id='41' name='Lagerstand' unit='kg' dop='0'/><CHANNEL id='42' name='Verbrauchsz°hler' unit='kg' dop='0'/><CHANNEL id='43' name='Heiz P Lambda' unit='W' dop='2'/><CHANNEL id='44' name='Heiz U Lambda' unit='V' dop='2'/><CHANNEL id='45' name='Heiz I Lambda' unit='mA' dop='0'/><CHANNEL id='46' name='U_Lambda' unit='mV'/><CHANNEL id='47' name='U Netzteil' unit='mV' dop='0'/><CHANNEL id='48' name='T Spülung' unit='°C'/><CHANNEL id='49' name='BRT' unit='°C'/><CHANNEL id='50' name='Tplat' unit='°C' dop='0'/><CHANNEL id='51' name='TVG' unit='°C'/><CHANNEL id='52' name='TVG2' unit='°C'/><CHANNEL id='53' name='AIN17' unit='V'/><CHANNEL id='54' name='Taus' unit='°C'/><CHANNEL id='55' name='TA Gem.' unit='°C'/><CHANNEL id='56' name='Effizienz' unit='%'/><CHANNEL id='57' name='ExtHK Solltmp.' unit='°C' dop='0'/><CHANNEL id='58' name='TVL_A' unit='°C'/><CHANNEL id='59' name='TVLs_A' unit='°C' dop='0'/><CHANNEL id='60' name='TRA_A' unit='°C'/><CHANNEL id='61' name='TRs_A' unit='°C'/><CHANNEL id='62' name='HKZustand_A' dop='0'/><CHANNEL id='63' name='FRA Zustand' dop='0'/><CHANNEL id='64' name='HKPA Status' dop='0'/><CHANNEL id='65' name='TVL_1' unit='°C'/><CHANNEL id='66' name='TVLs_1' unit='°C' dop='0'/><CHANNEL id='67' name='TRA_1' unit='°C'/><CHANNEL id='68' name='TRs_1' unit='°C'/><CHANNEL id='69' name='HKZustand_1' dop='0'/><CHANNEL id='70' name='FR1 Zustand' dop='0'/><CHANNEL id='71' name='HKP1 Status' dop='0'/><CHANNEL id='72' name='TVL_2' unit='°C'/><CHANNEL id='73' name='TVLs_2' unit='°C' dop='0'/><CHANNEL id='74' name='TRA_2' unit='°C'/><CHANNEL id='75' name='TRs_2' unit='°C'/><CHANNEL id='76' name='HKZustand_2' dop='0'/><CHANNEL id='77' name='FR2 Zustand' dop='0'/><CHANNEL id='78' name='HKP2 Status' dop='0'/><CHANNEL id='79' name='TVL_B' unit='°C'/><CHANNEL id='80' name='TVLs_B' unit='°C' dop='0'/><CHANNEL id='81' name='TRA_B' unit='°C'/><CHANNEL id='82' name='TRs_B' unit='°C'/><CHANNEL id='83' name='HKZustand_B' dop='0'/><CHANNEL id='84' name='FRB Zustand' dop='0'/><CHANNEL id='85' name='HKPB Status' dop='0'/><CHANNEL id='86' name='TBA' unit='°C'/><CHANNEL id='87' name='TBs_A' unit='°C' dop='0'/><CHANNEL id='88' name='TB1' unit='°C'/><CHANNEL id='89' name='TBs_1' unit='°C' dop='0'/><CHANNEL id='90' name='BoiZustand_1' dop='0'/><CHANNEL id='91' name='TBB' unit='°C'/><CHANNEL id='92' name='TBs_B' unit='°C' dop='0'/><CHANNEL id='93' name='HKR Anf' unit='°C'/><CHANNEL id='94' name='Anf. HKR0' unit='°C' dop='0'/><CHANNEL id='95' name='Anf. HKR1' unit='°C' dop='0'/><CHANNEL id='96' name='Anf. HKR2' unit='°C' dop='0'/><CHANNEL id='97' name='Anf. HKR3' unit='°C' dop='0'/><CHANNEL id='98' name='Anf. HKR4' unit='°C' dop='0'/><CHANNEL id='99' name='Anf. HKR5' unit='°C' dop='0'/><CHANNEL id='100' name='Anf. HKR6' unit='°C' dop='0'/><CHANNEL id='101' name='Anf. HKR7' unit='°C' dop='0'/><CHANNEL id='102' name='Anf. HKR8' unit='°C' dop='0'/><CHANNEL id='103' name='Anf. HKR9' unit='°C' dop='0'/><CHANNEL id='104' name='Anf. HKR10' unit='°C' dop='0'/><CHANNEL id='105' name='Anf. HKR11' unit='°C' dop='0'/><CHANNEL id='106' name='Anf. HKR12' unit='°C' dop='0'/><CHANNEL id='107' name='Anf. HKR13' unit='°C' dop='0'/><CHANNEL id='108' name='Anf. HKR14' unit='°C' dop='0'/><CHANNEL id='109' name='Anf. HKR15' unit='°C' dop='0'/><CHANNEL id='110' name='Wasserdruck' unit='bar' dop='2'/></ANALOG><DIGITAL><CHANNEL id='0' bit='0' name='Störung'/><CHANNEL id='0' bit='1' name='Stb'/><CHANNEL id='0' bit='2' name='Fuellstand'/><CHANNEL id='0' bit='3' name='RLP/PuffP'/><CHANNEL id='0' bit='4' name='RLm_auf'/><CHANNEL id='0' bit='5' name='RLm_zu'/><CHANNEL id='0' bit='10' name='WS freig.'/><CHANNEL id='0' bit='11' name='Akt. Code'/><CHANNEL id='0' bit='14' name='FW Freig.'/><CHANNEL id='0' bit='15' name='gFlP'/><CHANNEL id='0' bit='16' name='gFlM auf'/><CHANNEL id='0' bit='17' name='gFlM zu'/><CHANNEL id='0' bit='18' name='gFl2P'/><CHANNEL id='0' bit='19' name='gFl2M auf'/><CHANNEL id='0' bit='20' name='gFl2M zu'/><CHANNEL id='1' bit='0' name='L Heiz.'/><CHANNEL id='1' bit='1' name='Z Heiz.'/><CHANNEL id='1' bit='2' name='Z Geb.'/><CHANNEL id='1' bit='3' name='AA Run'/><CHANNEL id='1' bit='4' name='AA Dir'/><CHANNEL id='1' bit='5' name='ES Run'/><CHANNEL id='1' bit='6' name='ES Dir'/><CHANNEL id='1' bit='7' name='AS Saug'/><CHANNEL id='1' bit='8' name='AS RA Run'/><CHANNEL id='1' bit='9' name='AS RA Dir'/><CHANNEL id='1' bit='10' name='Rein En'/><CHANNEL id='1' bit='11' name='Rein Run'/><CHANNEL id='1' bit='12' name='Es Rein Endl'/><CHANNEL id='1' bit='13' name='sAS Anf F°ll'/><CHANNEL id='2' bit='0' name='HKPA'/><CHANNEL id='2' bit='1' name='MAA'/><CHANNEL id='2' bit='2' name='MAZ'/><CHANNEL id='2' bit='3' name='HKP1'/><CHANNEL id='2' bit='4' name='M1A'/><CHANNEL id='2' bit='5' name='M1Z'/><CHANNEL id='2' bit='6' name='HKP2'/><CHANNEL id='2' bit='7' name='M2A'/><CHANNEL id='2' bit='8' name='M2Z'/><CHANNEL id='2' bit='9' name='HKP3'/><CHANNEL id='2' bit='10' name='M3A'/><CHANNEL id='2' bit='11' name='M3Z'/><CHANNEL id='2' bit='12' name='HKP4'/><CHANNEL id='2' bit='13' name='M4A'/><CHANNEL id='2' bit='14' name='M4Z'/><CHANNEL id='2' bit='15' name='HKP5'/><CHANNEL id='2' bit='16' name='M5A'/><CHANNEL id='2' bit='17' name='M5Z'/><CHANNEL id='2' bit='18' name='HKP6'/><CHANNEL id='2' bit='19' name='M6A'/><CHANNEL id='2' bit='20' name='M6Z'/><CHANNEL id='2' bit='21' name='HKPB'/><CHANNEL id='2' bit='22' name='MBA'/><CHANNEL id='2' bit='23' name='MBZ'/><CHANNEL id='2' bit='24' name='HK-P Poolp'/><CHANNEL id='2' bit='25' name='HK-P Primp'/><CHANNEL id='2' bit='26' name='HK-P MA'/><CHANNEL id='2' bit='27' name='HK-P MZ'/><CHANNEL id='3' bit='0' name='BPA'/><CHANNEL id='3' bit='1' name='BP1'/><CHANNEL id='3' bit='2' name='BP2'/><CHANNEL id='3' bit='3' name='BP3'/><CHANNEL id='3' bit='4' name='BPB'/><CHANNEL id='3' bit='5' name='BZPA'/><CHANNEL id='3' bit='6' name='BZP1'/><CHANNEL id='3' bit='7' name='BZP2'/><CHANNEL id='3' bit='8' name='BZP3'/><CHANNEL id='3' bit='9' name='BZPB'/><CHANNEL id='4' bit='0' name='Aschebox'/><CHANNEL id='4' bit='1' name='Netztrafo'/><CHANNEL id='4' bit='2' name='Netzrelais'/><CHANNEL id='4' bit='4' name='Lagerraum'/><CHANNEL id='4' bit='6' name='FLP'/><CHANNEL id='4' bit='8' name='ATW'/><CHANNEL id='4' bit='9' name='Entasch gesp.'/><CHANNEL id='4' bit='13' name='HKV'/><CHANNEL id='4' bit='14' name='Sp°lung Aktiv'/><CHANNEL id='4' bit='15' name='ExtHK vorh'/><CHANNEL id='4' bit='16' name='ExtHK_2 vorh'/><CHANNEL id='4' bit='17' name='ExtHK_3 vorh'/><CHANNEL id='6' bit='0' name='ExtHK Anf'/><CHANNEL id='6' bit='2' name='ExtHK_2 Anf'/><CHANNEL id='6' bit='3' name='ExtHK_3 Anf'/><CHANNEL id='6' bit='4' name='ExtHK Pumpe'/><CHANNEL id='6' bit='6' name='ExtHK_2 Pumpe'/><CHANNEL id='6' bit='7' name='ExtHK_3 Pumpe'/><CHANNEL id='6' bit='8' name='KASK1 MinLeist'/><CHANNEL id='6' bit='9' name='KASK2 MinLeist'/><CHANNEL id='6' bit='10' name='KASK3 MinLeist'/><CHANNEL id='6' bit='11' name='KASK4 MinLeist'/><CHANNEL id='6' bit='12' name='KASK1 MaxLeist'/><CHANNEL id='6' bit='13' name='KASK2 MaxLeist'/><CHANNEL id='6' bit='14' name='KASK3 MaxLeist'/><CHANNEL id='6' bit='15' name='KASK4 MaxLeist'/><CHANNEL id='6' bit='16' name='KASK1 Run'/><CHANNEL id='6' bit='17' name='KASK2 Run'/><CHANNEL id='6' bit='18' name='KASK3 Run'/><CHANNEL id='6' bit='19' name='KASK4 Run'/><CHANNEL id='6' bit='20' name='KASK1 OK'/><CHANNEL id='6' bit='21' name='KASK2 OK'/><CHANNEL id='6' bit='22' name='KASK3 OK'/><CHANNEL id='6' bit='23' name='KASK4 OK'/><CHANNEL id='6' bit='24' name='Kask KWK Out'/><CHANNEL id='6' bit='25' name='Kask FW Out'/><CHANNEL id='6' bit='26' name='KASK KWK OK'/><CHANNEL id='6' bit='27' name='KASK FW OK'/><CHANNEL id='7' bit='0' name='DReg P2'/><CHANNEL id='7' bit='1' name='DReg P3'/><CHANNEL id='7' bit='2' name='DReg Mi auf'/><CHANNEL id='7' bit='3' name='DReg Mi zu'/><CHANNEL id='7' bit='5' name='DReg2 P2'/><CHANNEL id='7' bit='6' name='DReg2 Mi auf'/><CHANNEL id='7' bit='7' name='DReg2 Mi zu'/><CHANNEL id='7' bit='9' name='DReg3 P2'/><CHANNEL id='7' bit='10' name='DReg3 P3'/><CHANNEL id='7' bit='11' name='DReg3 Mi auf'/><CHANNEL id='7' bit='12' name='DReg3 Mi zu'/></DIGITAL></DAQPRJ>""",    
}

# Complete parameter descriptions for all parameters in DAQPRJ templates
# Format: {"parameter_name": {"en": "English description", "de": "Deutsche Beschreibung"}}
PARAMETER_DESCRIPTIONS: Final[dict[str, dict[str, str]]] = {
    # ===== ANALOG PARAMETERS (0-111) =====

    # Boiler core (0-10)
    "ZK": {"en": "Boiler State", "de": "Kesselzustand"},
    "O2": {"en": "O2 Level", "de": "O2-Gehalt"},
    "O2soll": {"en": "O2 Setpoint", "de": "O2-Sollwert"},
    "TK": {"en": "Boiler Temperature", "de": "Kesseltemperatur"},
    "TKsoll": {"en": "Boiler Setpoint", "de": "Kessel-Solltemperatur"},
    "TRL": {"en": "Return Temperature", "de": "Rücklauftemperatur"},
    "TRLsoll": {"en": "Return Setpoint", "de": "Rücklauf-Solltemperatur"},
    "Spreizung": {"en": "Temperature Spread", "de": "Temperaturspreizung"},
    "TRG": {"en": "Flue Gas Temperature", "de": "Rauchgastemperatur"},
    "SZist": {"en": "Draft Actual", "de": "Saugzug Ist"},
    "SZsoll": {"en": "Draft Setpoint", "de": "Saugzug Soll"},

    # Buffer (11-19)
    "TPo": {"en": "Buffer Top", "de": "Puffer Oben"},
    "TPm": {"en": "Buffer Middle", "de": "Puffer Mitte"},
    "TPu": {"en": "Buffer Bottom", "de": "Puffer Unten"},
    "Puff Füllgrad": {"en": "Buffer Fill Level", "de": "Pufferfüllgrad"},
    "Puffer_soll oben": {"en": "Buffer Setpoint Top", "de": "Puffer Sollwert Oben"},
    "Puffer_soll unten": {"en": "Buffer Setpoint Bottom", "de": "Puffer Sollwert Unten"},
    "PuffZustand": {"en": "Buffer State", "de": "Pufferzustand"},
    "Max Anf Kessel": {"en": "Max Boiler Demand", "de": "Max Kesselanforderung"},
    "TFW": {"en": "Fresh Water Temperature", "de": "Frischwassertemperatur"},

    # Power & Control (20-29)
    "Leistung": {"en": "Output Power", "de": "Ausgangsleistung"},
    "ESsoll": {"en": "Auger Setpoint", "de": "Einschubschnecke Soll"},
    "min.Leist.TRG": {"en": "Min Power Flue Gas", "de": "Min Leistung Rauchgas"},
    "max.Leist.TRG": {"en": "Max Power Flue Gas", "de": "Max Leistung Rauchgas"},
    "max.Leist.Fuell": {"en": "Max Power Fill", "de": "Max Leistung Füllung"},
    "max.Leist.TPO": {"en": "Max Power Buffer Top", "de": "Max Leistung Puffer Oben"},
    "ESRegler": {"en": "Auger Controller", "de": "Einschubschnecken-Regler"},
    "Regler K": {"en": "Controller K", "de": "Regler K"},
    "KeBrstScale": {"en": "Boiler Burner Scale", "de": "Kessel-Brenner-Skalierung"},
    "Programm": {"en": "Program", "de": "Programm"},

    # Error & System (30-42)
    "Störungs Nr": {"en": "Error Code", "de": "Störungsnummer"},
    "Max Anf ZenPuf": {"en": "Max Central Buffer Demand", "de": "Max Zentralpuffer-Anforderung"},
    "I Es": {"en": "Current Auger", "de": "Strom Einschubschnecke"},
    "I Ra": {"en": "Current Grate", "de": "Strom Rost"},
    "I Aa": {"en": "Current Ash Auger", "de": "Strom Aschenschnecke"},
    "I Sr": {"en": "Current Stoker", "de": "Strom Schürer"},
    "I Rein": {"en": "Current Cleaning", "de": "Strom Reinigung"},
    "BLDC_ES ist": {"en": "BLDC Auger Actual", "de": "BLDC Einschubschnecke Ist"},
    "BLDC_ES soll": {"en": "BLDC Auger Setpoint", "de": "BLDC Einschubschnecke Soll"},
    "LZ ES seit Füll.": {"en": "Runtime Since Fill", "de": "Laufzeit seit Füllung"},
    "LZ ES seit Ent.": {"en": "Runtime Since Ash", "de": "Laufzeit seit Entaschung"},
    "Anzahl Entasch.": {"en": "Ash Removal Count", "de": "Anzahl Entaschungen"},
    "Anzahl SR Beweg.": {"en": "Stoker Movement Count", "de": "Anzahl Schürerbewegungen"},

    # Pellets (43-44)
    "Lagerstand": {"en": "Pellet Stock", "de": "Pelletvorrat"},
    "Verbrauchszähler": {"en": "Pellet Consumption", "de": "Pelletverbrauch"},

    # Lambda Probe (45-49)
    "Heiz P Lambda": {"en": "Lambda Heating Power", "de": "Lambda Heizleistung"},
    "Heiz U Lambda": {"en": "Lambda Heating Voltage", "de": "Lambda Heizspannung"},
    "Heiz I Lambda": {"en": "Lambda Heating Current", "de": "Lambda Heizstrom"},
    "U_Lambda": {"en": "Lambda Voltage", "de": "Lambda Spannung"},
    "U Netzteil": {"en": "Power Supply Voltage", "de": "Netzteil-Spannung"},

    # Temperatures (50-58)
    "T Spülung": {"en": "Flushing Temperature", "de": "Spültemperatur"},
    "BRT": {"en": "Burner Temperature", "de": "Brennraumtemperatur"},
    "Tplat": {"en": "Board Temperature", "de": "Platinentemperatur"},
    "TVG": {"en": "Pre-Flow Temperature", "de": "Vorlauftemperatur Gesamt"},
    "TVG2": {"en": "Pre-Flow Temperature 2", "de": "Vorlauftemperatur 2"},
    "AIN17": {"en": "Analog Input 17", "de": "Analogeingang 17"},
    "Taus": {"en": "Outside Temperature", "de": "Außentemperatur"},
    "TA Gem.": {"en": "Average Outside Temperature", "de": "Außentemperatur Gemittelt"},
    "Effizienz": {"en": "Efficiency", "de": "Wirkungsgrad"},

    # External Heating Circuit (59-66)
    "ExtHK Solltmp.": {"en": "Ext. HC Setpoint", "de": "Ext. Heizkreis Solltemperatur"},
    "TVL_A": {"en": "Flow HC A", "de": "Vorlauf HK A"},
    "TVLs_A": {"en": "Flow Setpoint HC A", "de": "Vorlauf Soll HK A"},
    "TRA_A": {"en": "Return HC A", "de": "Rücklauf HK A"},
    "TRs_A": {"en": "Return Setpoint HC A", "de": "Rücklauf Soll HK A"},
    "HKZustand_A": {"en": "State HC A", "de": "Zustand HK A"},
    "FRA Zustand": {"en": "Room Thermostat A State", "de": "Raumthermostat A Zustand"},
    "HKPA Status": {"en": "Pump A Status", "de": "Heizkreispumpe A Status"},

    # Heating Circuit 1 (67-73)
    "TVL_1": {"en": "Flow HC 1", "de": "Vorlauf HK 1"},
    "TVLs_1": {"en": "Flow Setpoint HC 1", "de": "Vorlauf Soll HK 1"},
    "TRA_1": {"en": "Return HC 1", "de": "Rücklauf HK 1"},
    "TRs_1": {"en": "Return Setpoint HC 1", "de": "Rücklauf Soll HK 1"},
    "HKZustand_1": {"en": "State HC 1", "de": "Zustand HK 1"},
    "FR1 Zustand": {"en": "Room Thermostat 1 State", "de": "Raumthermostat 1 Zustand"},
    "HKP1 Status": {"en": "Pump 1 Status", "de": "Heizkreispumpe 1 Status"},

    # Heating Circuit 2 (74-80)
    "TVL_2": {"en": "Flow HC 2", "de": "Vorlauf HK 2"},
    "TVLs_2": {"en": "Flow Setpoint HC 2", "de": "Vorlauf Soll HK 2"},
    "TRA_2": {"en": "Return HC 2", "de": "Rücklauf HK 2"},
    "TRs_2": {"en": "Return Setpoint HC 2", "de": "Rücklauf Soll HK 2"},
    "HKZustand_2": {"en": "State HC 2", "de": "Zustand HK 2"},
    "FR2 Zustand": {"en": "Room Thermostat 2 State", "de": "Raumthermostat 2 Zustand"},
    "HKP2 Status": {"en": "Pump 2 Status", "de": "Heizkreispumpe 2 Status"},

    # Heating Circuit B (81-87)
    "TVL_B": {"en": "Flow HC B", "de": "Vorlauf HK B"},
    "TVLs_B": {"en": "Flow Setpoint HC B", "de": "Vorlauf Soll HK B"},
    "TRA_B": {"en": "Return HC B", "de": "Rücklauf HK B"},
    "TRs_B": {"en": "Return Setpoint HC B", "de": "Rücklauf Soll HK B"},
    "HKZustand_B": {"en": "State HC B", "de": "Zustand HK B"},
    "FRB Zustand": {"en": "Room Thermostat B State", "de": "Raumthermostat B Zustand"},
    "HKPB Status": {"en": "Pump B Status", "de": "Heizkreispumpe B Status"},

    # Hot Water (88-93)
    "TBA": {"en": "Hot Water A", "de": "Warmwasser A"},
    "TBs_A": {"en": "Hot Water Setpoint A", "de": "Warmwasser Soll A"},
    "TB1": {"en": "Hot Water 1", "de": "Warmwasser 1"},
    "TBs_1": {"en": "Hot Water Setpoint 1", "de": "Warmwasser Soll 1"},
    "TBB": {"en": "Hot Water B", "de": "Warmwasser B"},
    "TBs_B": {"en": "Hot Water Setpoint B", "de": "Warmwasser Soll B"},

    # Heating Circuit Demands (94-110)
    "HKR Anf": {"en": "HC Demand", "de": "Heizkreis-Anforderung"},
    "Anf. HKR0": {"en": "Demand HC 0", "de": "Anforderung HK 0"},
    "Anf. HKR1": {"en": "Demand HC 1", "de": "Anforderung HK 1"},
    "Anf. HKR2": {"en": "Demand HC 2", "de": "Anforderung HK 2"},
    "Anf. HKR3": {"en": "Demand HC 3", "de": "Anforderung HK 3"},
    "Anf. HKR4": {"en": "Demand HC 4", "de": "Anforderung HK 4"},
    "Anf. HKR5": {"en": "Demand HC 5", "de": "Anforderung HK 5"},
    "Anf. HKR6": {"en": "Demand HC 6", "de": "Anforderung HK 6"},
    "Anf. HKR7": {"en": "Demand HC 7", "de": "Anforderung HK 7"},
    "Anf. HKR8": {"en": "Demand HC 8", "de": "Anforderung HK 8"},
    "Anf. HKR9": {"en": "Demand HC 9", "de": "Anforderung HK 9"},
    "Anf. HKR10": {"en": "Demand HC 10", "de": "Anforderung HK 10"},
    "Anf. HKR11": {"en": "Demand HC 11", "de": "Anforderung HK 11"},
    "Anf. HKR12": {"en": "Demand HC 12", "de": "Anforderung HK 12"},
    "Anf. HKR13": {"en": "Demand HC 13", "de": "Anforderung HK 13"},
    "Anf. HKR14": {"en": "Demand HC 14", "de": "Anforderung HK 14"},
    "Anf. HKR15": {"en": "Demand HC 15", "de": "Anforderung HK 15"},

    # Water Pressure (111)
    "Wasserdruck": {"en": "Water Pressure", "de": "Wasserdruck"},

    # ===== DIGITAL PARAMETERS =====

    # Digital 0 - System Status
    "Störung": {"en": "Error", "de": "Störung"},
    "Stb": {"en": "Standby", "de": "Standby"},
    "Fuellstand": {"en": "Fill Level", "de": "Füllstand"},
    "RLP/PuffP": {"en": "Return Pump/Buffer Pump", "de": "Rücklaufpumpe/Pufferpumpe"},
    "RLm_auf": {"en": "Return Mixer Open", "de": "Rücklaufmischer Auf"},
    "RLm_zu": {"en": "Return Mixer Close", "de": "Rücklaufmischer Zu"},
    "WS freig.": {"en": "Water Protection Release", "de": "Wasserschutz Freigabe"},
    "Akt. Code": {"en": "Active Code", "de": "Aktiver Code"},
    "FW Freig.": {"en": "Fresh Water Release", "de": "Frischwasser Freigabe"},
    "gFlP": {"en": "Floorheating Pump", "de": "Fußbodenheizung Pumpe"},
    "gFlM auf": {"en": "Floorheating Mixer Open", "de": "Fußbodenheizung Mischer Auf"},
    "gFlM zu": {"en": "Floorheating Mixer Close", "de": "Fußbodenheizung Mischer Zu"},
    "gFl2P": {"en": "Floorheating 2 Pump", "de": "Fußbodenheizung 2 Pumpe"},
    "gFl2M auf": {"en": "Floorheating 2 Mixer Open", "de": "Fußbodenheizung 2 Mischer Auf"},
    "gFl2M zu": {"en": "Floorheating 2 Mixer Close", "de": "Fußbodenheizung 2 Mischer Zu"},

    # Digital 1 - Burner & Motors
    "L Heiz.": {"en": "Load Heating", "de": "Ladung Heizung"},
    "Z Heiz.": {"en": "Ignition Heating", "de": "Zündung Heizung"},
    "Z Geb.": {"en": "Ignition Blower", "de": "Zündgebläse"},
    "AA Run": {"en": "Ash Auger Run", "de": "Aschenschnecke Läuft"},
    "AA Dir": {"en": "Ash Auger Direction", "de": "Aschenschnecke Richtung"},
    "ES Run": {"en": "Auger Run", "de": "Einschubschnecke Läuft"},
    "ES Dir": {"en": "Auger Direction", "de": "Einschubschnecke Richtung"},
    "AS Saug": {"en": "Ash Suction", "de": "Asche Saugen"},
    "AS RA Run": {"en": "Ash Grate Run", "de": "Asche Rost Läuft"},
    "AS RA Dir": {"en": "Ash Grate Direction", "de": "Asche Rost Richtung"},
    "Rein En": {"en": "Cleaning Enable", "de": "Reinigung Aktiviert"},
    "Rein Run": {"en": "Cleaning Run", "de": "Reinigung Läuft"},
    "Es Rein Endl": {"en": "Auger Cleaning Endpoint", "de": "Einschubschnecke Reinigung Endlage"},
    "sAS Anf Füll": {"en": "Ash Auger Fill Request", "de": "Aschenschnecke Anforderung Füllung"},

    # Digital 2 - Heating Circuit Pumps & Mixers
    "HKPA": {"en": "HC Pump A", "de": "Heizkreispumpe A"},
    "MAA": {"en": "Mixer A Open", "de": "Mischer A Auf"},
    "MAZ": {"en": "Mixer A Close", "de": "Mischer A Zu"},
    "HKP1": {"en": "HC Pump 1", "de": "Heizkreispumpe 1"},
    "M1A": {"en": "Mixer 1 Open", "de": "Mischer 1 Auf"},
    "M1Z": {"en": "Mixer 1 Close", "de": "Mischer 1 Zu"},
    "HKP2": {"en": "HC Pump 2", "de": "Heizkreispumpe 2"},
    "M2A": {"en": "Mixer 2 Open", "de": "Mischer 2 Auf"},
    "M2Z": {"en": "Mixer 2 Close", "de": "Mischer 2 Zu"},
    "HKP3": {"en": "HC Pump 3", "de": "Heizkreispumpe 3"},
    "M3A": {"en": "Mixer 3 Open", "de": "Mischer 3 Auf"},
    "M3Z": {"en": "Mixer 3 Close", "de": "Mischer 3 Zu"},
    "HKP4": {"en": "HC Pump 4", "de": "Heizkreispumpe 4"},
    "M4A": {"en": "Mixer 4 Open", "de": "Mischer 4 Auf"},
    "M4Z": {"en": "Mixer 4 Close", "de": "Mischer 4 Zu"},
    "HKP5": {"en": "HC Pump 5", "de": "Heizkreispumpe 5"},
    "M5A": {"en": "Mixer 5 Open", "de": "Mischer 5 Auf"},
    "M5Z": {"en": "Mixer 5 Close", "de": "Mischer 5 Zu"},
    "HKP6": {"en": "HC Pump 6", "de": "Heizkreispumpe 6"},
    "M6A": {"en": "Mixer 6 Open", "de": "Mischer 6 Auf"},
    "M6Z": {"en": "Mixer 6 Close", "de": "Mischer 6 Zu"},
    "HKPB": {"en": "HC Pump B", "de": "Heizkreispumpe B"},
    "MBA": {"en": "Mixer B Open", "de": "Mischer B Auf"},
    "MBZ": {"en": "Mixer B Close", "de": "Mischer B Zu"},
    "HK-P Poolp": {"en": "HC Pool Pump", "de": "Heizkreis Poolpumpe"},
    "HK-P Primp": {"en": "HC Primary Pump", "de": "Heizkreis Primärpumpe"},
    "HK-P MA": {"en": "HC Mixer Open", "de": "Heizkreis Mischer Auf"},
    "HK-P MZ": {"en": "HC Mixer Close", "de": "Heizkreis Mischer Zu"},

    # Digital 3 - Boiler Pumps
    "BPA": {"en": "Boiler Pump A", "de": "Boilerpumpe A"},
    "BP1": {"en": "Boiler Pump 1", "de": "Boilerpumpe 1"},
    "BP2": {"en": "Boiler Pump 2", "de": "Boilerpumpe 2"},
    "BP3": {"en": "Boiler Pump 3", "de": "Boilerpumpe 3"},
    "BPB": {"en": "Boiler Pump B", "de": "Boilerpumpe B"},
    "BZPA": {"en": "Circulation Pump A", "de": "Zirkulationspumpe A"},
    "BZP1": {"en": "Circulation Pump 1", "de": "Zirkulationspumpe 1"},
    "BZP2": {"en": "Circulation Pump 2", "de": "Zirkulationspumpe 2"},
    "BZP3": {"en": "Circulation Pump 3", "de": "Zirkulationspumpe 3"},
    "BZPB": {"en": "Circulation Pump B", "de": "Zirkulationspumpe B"},

    # Digital 4 - System Components
    "Aschebox": {"en": "Ash Box", "de": "Aschebox"},
    "Netztrafo": {"en": "Power Transformer", "de": "Netztrafo"},
    "Netzrelais": {"en": "Power Relay", "de": "Netzrelais"},
    "Lagerraum": {"en": "Storage Room", "de": "Lagerraum"},
    "FLP": {"en": "Floorheating Pump", "de": "Fußbodenheizungspumpe"},
    "ATW": {"en": "Heat Pump", "de": "Außentemperatur-Wärmepumpe"},
    "Entasch gesp.": {"en": "Ash Removal Locked", "de": "Entaschung Gesperrt"},
    "HKV": {"en": "HC Distribution", "de": "Heizkreisverteiler"},
    "Spülung Aktiv": {"en": "Flushing Active", "de": "Spülung Aktiv"},
    "ExtHK vorh": {"en": "Ext HC Present", "de": "Ext Heizkreis Vorhanden"},
    "ExtHK_2 vorh": {"en": "Ext HC 2 Present", "de": "Ext Heizkreis 2 Vorhanden"},
    "ExtHK_3 vorh": {"en": "Ext HC 3 Present", "de": "Ext Heizkreis 3 Vorhanden"},

    # Digital 6 - External HC & Cascades
    "ExtHK Anf": {"en": "Ext HC Request", "de": "Ext Heizkreis Anforderung"},
    "ExtHK_2 Anf": {"en": "Ext HC 2 Request", "de": "Ext Heizkreis 2 Anforderung"},
    "ExtHK_3 Anf": {"en": "Ext HC 3 Request", "de": "Ext Heizkreis 3 Anforderung"},
    "ExtHK Pumpe": {"en": "Ext HC Pump", "de": "Ext Heizkreis Pumpe"},
    "ExtHK_2 Pumpe": {"en": "Ext HC 2 Pump", "de": "Ext Heizkreis 2 Pumpe"},
    "ExtHK_3 Pumpe": {"en": "Ext HC 3 Pump", "de": "Ext Heizkreis 3 Pumpe"},
    "KASK1 MinLeist": {"en": "Cascade 1 Min Power", "de": "Kaskade 1 Minimalleistung"},
    "KASK2 MinLeist": {"en": "Cascade 2 Min Power", "de": "Kaskade 2 Minimalleistung"},
    "KASK3 MinLeist": {"en": "Cascade 3 Min Power", "de": "Kaskade 3 Minimalleistung"},
    "KASK4 MinLeist": {"en": "Cascade 4 Min Power", "de": "Kaskade 4 Minimalleistung"},
    "KASK1 MaxLeist": {"en": "Cascade 1 Max Power", "de": "Kaskade 1 Maximalleistung"},
    "KASK2 MaxLeist": {"en": "Cascade 2 Max Power", "de": "Kaskade 2 Maximalleistung"},
    "KASK3 MaxLeist": {"en": "Cascade 3 Max Power", "de": "Kaskade 3 Maximalleistung"},
    "KASK4 MaxLeist": {"en": "Cascade 4 Max Power", "de": "Kaskade 4 Maximalleistung"},
    "KASK1 Run": {"en": "Cascade 1 Running", "de": "Kaskade 1 Läuft"},
    "KASK2 Run": {"en": "Cascade 2 Running", "de": "Kaskade 2 Läuft"},
    "KASK3 Run": {"en": "Cascade 3 Running", "de": "Kaskade 3 Läuft"},
    "KASK4 Run": {"en": "Cascade 4 Running", "de": "Kaskade 4 Läuft"},
    "KASK1 OK": {"en": "Cascade 1 OK", "de": "Kaskade 1 OK"},
    "KASK2 OK": {"en": "Cascade 2 OK", "de": "Kaskade 2 OK"},
    "KASK3 OK": {"en": "Cascade 3 OK", "de": "Kaskade 3 OK"},
    "KASK4 OK": {"en": "Cascade 4 OK", "de": "Kaskade 4 OK"},
    "Kask KWK Out": {"en": "Cascade CHP Output", "de": "Kaskade KWK Ausgang"},
    "Kask FW Out": {"en": "Cascade FW Output", "de": "Kaskade FW Ausgang"},
    "KASK KWK OK": {"en": "Cascade CHP OK", "de": "Kaskade KWK OK"},
    "KASK FW OK": {"en": "Cascade FW OK", "de": "Kaskade FW OK"},

    # Digital 5 - Reserved
    "Reserved_5": {"en": "Reserved Digital 5", "de": "Reserviert Digital 5"},

    # Digital 7 - Pressure Controllers
    "DReg P2": {"en": "Pressure Ctrl Pump 2", "de": "Druckregler Pumpe 2"},
    "DReg P3": {"en": "Pressure Ctrl Pump 3", "de": "Druckregler Pumpe 3"},
    "DReg Mi auf": {"en": "Pressure Ctrl Mixer Open", "de": "Druckregler Mischer Auf"},
    "DReg Mi zu": {"en": "Pressure Ctrl Mixer Close", "de": "Druckregler Mischer Zu"},
    "DReg2 P2": {"en": "Pressure Ctrl 2 Pump 2", "de": "Druckregler 2 Pumpe 2"},
    "DReg2 Mi auf": {"en": "Pressure Ctrl 2 Mixer Open", "de": "Druckregler 2 Mischer Auf"},
    "DReg2 Mi zu": {"en": "Pressure Ctrl 2 Mixer Close", "de": "Druckregler 2 Mischer Zu"},
    "DReg3 P2": {"en": "Pressure Ctrl 3 Pump 2", "de": "Druckregler 3 Pumpe 2"},
    "DReg3 P3": {"en": "Pressure Ctrl 3 Pump 3", "de": "Druckregler 3 Pumpe 3"},
    "DReg3 Mi auf": {"en": "Pressure Ctrl 3 Mixer Open", "de": "Druckregler 3 Mischer Auf"},
    "DReg3 Mi zu": {"en": "Pressure Ctrl 3 Mixer Close", "de": "Druckregler 3 Mischer Zu"},

    # Digital 8 - Reserved
    "Reserved_8": {"en": "Reserved Digital 8", "de": "Reserviert Digital 8"},
}
