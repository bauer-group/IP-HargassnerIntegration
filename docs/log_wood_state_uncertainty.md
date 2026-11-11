# Log wood (HV) ZK states: what's confirmed and what isn't

The `ZK` (Zustand Kessel) state names in `boiler_profiles.py` for the log wood
profile are inferred from DAQ log analysis, not read off a boiler display or
confirmed by Hargassner. This table lists every value where that inference is
shaky, so it can be dropped into a PR and the community can fill the gaps.

Evidence is from ten `.DAQ` archive files sampled across ~5 years and three
firmware versions (V10.2d1, V10.2l3, V10.2HAR.n2) from one HV20 installation,
three days of live telnet capture from the same boiler, and - as of 12 Oct
2026 - a live burn watched both via telnet capture and the boiler's own
"Zustand" field on web.hargassner.at.

| ZK | Current name (en/de) | Confidence | Evidence | Open question |
|----|----|----|----|----|
| 4 | Ignition / Zündung | **confirmed** | Read directly off the boiler's own display during a live burn (12 Oct 2026): Zustand showed "Zündung" while TK/TRG/Leistung matched ZK 4 in the telnet log. Originally guessed as "Heat-up"/"Anheizen" - that guess was wrong. | None - this one's settled. |
| 5 | *(none, shows as "ZK 5")* | none | Never observed in any sample. | What is it, and when does it occur? |
| 6 | Full burn / Leistungsbrand | **confirmed** | Read directly off the boiler's own display during the same live burn: Zustand showed "Leistungsbrand" while TK/TRG/Leistung matched ZK 6 in the telnet log. | None - this one's settled. |
| 7 | Full firing / Vollbrand | low | O2 drops to 2.5-6.6 % (lower than during ZK 6), flue gas 199-238 °C. Cycles 6 → 7 → 8 → 6 → 7 → 8 → 9 within a single burn. | Is this really a distinct "peak output" phase, or just a measurement artifact of the O2 sensor during the same burn as 6? Still not seen on the display directly - the live burn on 12 Oct didn't reach it before this was written. |
| 8 | Ember preservation / Gluterhaltung | low | Flue gas 127-233 °C, primary air 12-40 %, consistently bridges from 6/7 toward burn-out (9). | Does it only ever follow 6/7, or can it occur independently? |
| 9 | Burn-out / Ausbrand | **confirmed** | Read directly off the boiler's own display during the same 12 Oct 2026 burn: Zustand showed "Ausbrand". (The local telnet capture had stopped logging by this point - see note below - so this wasn't cross-checked against the per-second log the way 4 and 6 were, but the display text is a direct read regardless.) Duration (number of consecutive samples in the archive) differs between the oldest firmware (V10.2d1) and the newer ones - not yet explained. | Is the firmware-era duration difference a real behaviour change, or just batch-size/wood-load dependent? |
| 11 | Residual heat / Restwärme | **confirmed** | Read directly off the boiler's own display during the same 12 Oct 2026 burn (16:28 local): Zustand showed "Restwärme" with Leistung 0 %, flue gas falling (65 °C), fan off - matching ZK 11 in the telnet log. Originally guessed as "Cool-down"/"Nachlauf" - that guess was wrong on the name, though the behaviour (cooling after burn-out) matches. Present in every archive sample, always follows 9. The original 3-day analysis described this as "exactly 360 min" - that does **not** hold up against the wider archive; duration varies. | What actually ends this state - a timer, a temperature threshold, or a demand signal? |
| 12 | *(none, shows as "ZK 12")* | very low | Seen exactly once (one sample) in one file, nested *inside* a full-burn run: `...6 → 12 → 6 → 9...`, co-occurring with fault 24 ("Rücklaufanhebung Temperatur nicht erreicht" / return-temperature boost not reached). Hargassner's own changelog for the V10.2HAR.p update (received from support, 12 Oct 2026) lists "Berechnung des Temperatur Rücklaufs verbessert" (return-temperature calculation improved) as a fix in that release - independent support for this being a return-temp calculation glitch rather than a distinct boiler phase. | Is this a named state at all, or just a one-tick side effect of the return-temperature fault? |
| 14 | *(none, shows as "ZK 14")* | very low | Seen exactly once (one sample) in one file, between "door open" (13) and "ignition preparation" (3): `...13 → 14 → 3 → 2 → 3 → 4...`. | Same question as 12 - real state or a one-tick transition blip? |

Also unconfirmed, not state-related:
- **dummy1/dummy2 ordering** in the firmware channel template - not yet resolved; needs a live telnet capture around the moment the hot water tank reaches 59 °C while firing.
- States 1, 2, 3, 11, 13 are still inferred from timing and sensor values only, not yet confirmed against the boiler's own display text (4, 6 and 9 now are - see above). 7 and 8 weren't reached by name on the display during the 12 Oct burn either - the local telnet log (see below) dropped out before they could be correlated.
- **The local telnet capture (`tools/burn_2026-10-12.log`) stopped updating twice during the 12 Oct burn** - first at 13:09:41 (stuck on ZK 6), resumed, then stopped again at 14:06:45 (stuck on ZK 9). Both times the web dashboard had already moved past where the log was stuck by the time of the next check, so the log alone can't be trusted as a continuous record for this day - cross-check against the dashboard, or treat gaps as missing rather than "boiler stayed in that state".
- **By the 14:25 check, a second burn cycle was already under way** (Zustand back to "Zündung"/ZK 4, Reinigung-in countdown reset to 31h, Puffer still ~48%) - meaning the cool-down (11) and off (1) states from the *first* burn were missed entirely in this window; still nothing confirmed for 7, 8 or 11.
- **Three new fault codes appeared, all firing once in the same minute (12 Oct 2026, 14:13)**, not previously seen in the archive or the error-code table - now added to `LOG_WOOD_ERROR_CODES`:
  - **4** - "Rauchgasfühler falsch angeschlossen" (flue gas sensor wrongly connected)
  - **6** - "Kesselfühler Kurzschluss" (boiler sensor short circuit)
  - **16** - "Rücklauffühler Kurzschluss" (return sensor short circuit)
  **Resolved**: Hargassner pushed a firmware update that day - the boiler's Info page shows "Letzter Bootzeitpunkt" (last boot) of 12.10.2026 14:11, software version moving from V10.2HAR.n2 to V10.2HAR.p, which lines up exactly with these three faults and the second telnet-capture gap. Not a wiring problem - boot-time noise from the update. Checked the live Home Assistant sensors afterward (Kesseltemperatur, Rauchgastemperatur, O2-Gehalt, Ausgangsleistung, buffer temps) and all are still fresh and physically coherent, so V10.2HAR.p appears to keep the same channel layout as V10.2HAR.n2 - at least for this one data point. Worth re-checking if Hargassner pushes a larger update later.
  **Official changelog received** (via Hargassner support, 12 Oct 2026) for V10.2HAR.p lists three changes: induced-draft fan ("Saugzug") speed tolerance adjusted; RSC (room-sensor-control remote) added as a selectable option; and return-temperature calculation improved (see the ZK 12 row above - this is likely why). None of the three describe a DAQ channel or message-format change, consistent with the live sensor check above.
- **Three event/fault codes the web portal's own history table couldn't resolve to a message**, shown there only as a date instead of text, so they're missing from `LOG_WOOD_ERROR_CODES` entirely:
  - **308** - 2 occurrences, first 2021-09-27, last 2022-10-20
  - **14** - 70 occurrences, first 2020-10-11, last 2022-06-06
  - **87** - 1 occurrence, 2021-09-27 only
  (Every other code in `LOG_WOOD_ERROR_CODES` matches the portal's history table exactly, confirmed 12 Oct 2026 against web.hargassner.at's Ereignisse page.)

If anyone from the community has a Hargassner HV/Neo-HV service manual, firmware
documentation, or has simply watched these ZK numbers scroll past on their own
boiler's display, a correction here would be very welcome.
