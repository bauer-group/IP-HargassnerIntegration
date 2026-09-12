# Custom Dashboard für Hargassner Pelletheizung

Diese Anleitung zeigt dir, wie du ein umfassendes Dashboard für deine Hargassner Pelletheizung einrichtest, inklusive Verbrauchsprognosen auf Basis von Heizgradtagen (HDD) nach VDI 4710.

![Custom Dashboard](images/Custom_Dashboard.png)

## Übersicht

Das Dashboard bietet folgende Funktionen:

- **Pelletheizung (Übersicht)**: Alle wichtigen Sensoren auf einen Blick
- **Pelletheizung (Statistiken)**: Grafische Darstellung von Betriebszustand, Effizienz, Temperaturen und Pufferspeicher
- **Pelletverbrauch – Kennzahlen**: Tages-, Wochen-, Monats- und Jahresverbrauch sowie Prognosen
- **Pelletheizung (Alle Sensordaten)**: Komplette Übersicht aller verfügbaren Sensoren

## So rechnet die Prognose

Der Kessel verbraucht Pellets aus zwei Gründen, und die beiden verhalten sich völlig unterschiedlich:

| Anteil | Wovon abhängig | Größenordnung |
| --- | --- | --- |
| **Warmwasser** | vom Wetter unabhängig, läuft das ganze Jahr | konstante kg pro Tag |
| **Heizung** | direkt von der Außentemperatur | kg pro Heizgradtag |

Deshalb rechnet das Modell zweigeteilt:

```
Verbrauch  =  Grundlast × Tage  +  kg/HDD × Heizgradtage
```

Würde man stattdessen den gesamten Verbrauch als wetterabhängig behandeln — also einfach `Verbrauch ÷ HDD` — bekäme man im Sommer eine absurde Kennzahl: die Heizgradtage gehen im Juli gegen null, der Warmwasserverbrauch nicht. Aus 46 kg/HDD statt 1,3 kg/HDD wird bei der Hochrechnung auf ein volles Jahr schnell ein zwanzigfach zu hoher Wert. Die Aufteilung in Grundlast und Heizanteil ist also kein Feinschliff, sondern die Voraussetzung dafür, dass die Prognose ganzjährig brauchbar bleibt.

Die Grundlast steht in einem eigenen Helper und wird einmal jährlich aus den Sommermonaten nachgezogen — siehe [Schritt 2](#schritt-2-helper-erstellen).

## Voraussetzungen

- Home Assistant mit der Hargassner Integration installiert
- `sensor.hg_pk32_pelletverbrauch` liefert Werte und hat `state_class: total_increasing` (Voraussetzung für die Utility Meters)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) für die 30-Tage-Übersicht (optional)

Die Einrichtung umfasst vier Bausteine, die aufeinander aufbauen:

1. **Drei Helper** — Startzeit, Startwert, Grundlast
2. **Vier Utility Meters** — Tag, Woche, Monat, Jahr
3. **Zehn Template-Sensoren** — Heizgradtage, Effizienz, Prognosen
4. **Eine Automatisierung** — hält den Anker bei einem Zählerreset konsistent

## Installation

### Schritt 1: Helper erstellen

Für die Verbrauchsprognosen werden **drei Helper** benötigt:

| Helper | Typ | Zweck |
| --- | --- | --- |
| `hg_pk32_pelletverbrauch_startzeit` | `input_datetime` | Beginn des Messzeitraums |
| `hg_pk32_pelletverbrauch_startwert` | `input_number` | Zählerstand (kg) zu genau diesem Zeitpunkt |
| `pelletverbrauch_grundlast_warmwasser` | `input_number` | Warmwasser-Grundlast in kg pro Tag |

> **Startzeit und Startwert gehören zusammen.** Sie bilden einen gemeinsamen Ankerpunkt: „Am *Startzeit* stand der Zähler auf *Startwert*." Passen die beiden nicht zusammen, rechnet die Prognose mit einem falschen Verbrauch und liefert stillschweigend Unsinn. Das ist der mit Abstand häufigste Fehler bei dieser Einrichtung.

**Option A: Über die UI erstellen (empfohlen)**

1. Gehe zu **Einstellungen** → **Geräte & Dienste** → **Helfer**
2. **Startzeit erstellen:**
   - **+ Helfer erstellen** → **Datum und/oder Uhrzeit**
   - **Name**: `hg_pk32_pelletverbrauch_startzeit`
   - **Hat ein Datum**: ✓ · **Hat eine Zeit**: ✓
3. **Startwert erstellen:**
   - **+ Helfer erstellen** → **Zahl**
   - **Name**: `hg_pk32_pelletverbrauch_startwert`
   - **Minimum**: 0 · **Maximum**: 999999 · **Schrittweite**: 1 · **Einheit**: kg · **Modus**: Eingabefeld
4. **Grundlast erstellen:**
   - **+ Helfer erstellen** → **Zahl**
   - **Name**: `pelletverbrauch_grundlast_warmwasser`
   - **Minimum**: 0 · **Maximum**: 50 · **Schrittweite**: 0.01 · **Einheit**: kg/d · **Modus**: Eingabefeld

**Option B: Per YAML erstellen**

`input_datetime.yaml`:

```yaml
hg_pk32_pelletverbrauch_startzeit:
  name: "Startzeit Pelletverbrauchszähler"
  has_date: true
  has_time: true
```

`input_number.yaml`:

```yaml
hg_pk32_pelletverbrauch_startwert:
  name: "Startwert Pelletverbrauchszähler"
  min: 0
  max: 999999
  step: 1
  unit_of_measurement: "kg"
  mode: box

pelletverbrauch_grundlast_warmwasser:
  name: "Pelletverbrauch Grundlast (Warmwasser)"
  min: 0
  max: 50
  step: 0.01
  unit_of_measurement: "kg/d"
  icon: mdi:water-boiler
  mode: box
```

Einbindung in `configuration.yaml`:

```yaml
input_datetime: !include input_datetime.yaml
input_number: !include input_number.yaml
```

#### Die drei Helper befüllen

Nach dem Neustart unter **Entwicklerwerkzeuge** → **Zustände** setzen:

**Startzeit und Startwert.** Am einfachsten und robustesten ist der Jahresbeginn als Anker:

- `input_datetime.hg_pk32_pelletverbrauch_startzeit` → `2026-01-01 00:00:00`
- `input_number.hg_pk32_pelletverbrauch_startwert` → Zählerstand am 1. Januar

Den Zählerstand am Jahresanfang bekommst du ohne Rätselraten aus dem Jahres-Utility-Meter:

```
Startwert = sensor.hg_pk32_pelletverbrauch − sensor.hg_pk32_pelletverbrauch_jahr
```

Beide Werte stehen in **Entwicklerwerkzeuge** → **Zustände**. Zur Kontrolle: nach dem Setzen muss `sensor.pelletverbrauch_heizanteil` im Attribut `verbrauch_gesamt` exakt den Jahresverbrauch anzeigen.

Alternativ geht auch jeder andere Zeitpunkt — etwa die letzte Pelletlieferung. Wichtig ist nur, dass der Startwert der Zählerstand **genau zu dieser Startzeit** ist.

**Grundlast.** Nimm den Verbrauch der beiden Hochsommermonate, in denen sicher nicht geheizt wurde:

```
Grundlast = (Verbrauch Juli + Verbrauch August) ÷ 62
```

Die Monatswerte findest du im Verlauf von `sensor.hg_pk32_pelletverbrauch_monat`. Beispiel: 154 kg + 163 kg ergeben 5,11 kg/Tag. Einmal im Jahr nachziehen reicht. Bei einer Solarthermie- oder Wärmepumpenunterstützung für das Warmwasser fällt der Wert deutlich niedriger aus.

### Schritt 2: Utility Meters konfigurieren

Die Utility Meters erfassen den Pelletverbrauch in verschiedenen Zeiträumen. Sie dienen der Anzeige und als Kontrollgröße gegen die Prognose — die Prognose selbst rechnet mit dem Rohzähler und dem Ankerpunkt, nicht mit diesen Zählern.

`utility_meter.yaml`:

```yaml
# Tagesverbrauch - Grundlage für Heatmaps, Tagesanalysen, Trendlinien
hg_pk32_pelletverbrauch_tag:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: daily

# Wochenverbrauch - für Wochenberichte
hg_pk32_pelletverbrauch_woche:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: weekly

# Monatsverbrauch - liefert die Zahlen, aus denen du die Grundlast ableitest
hg_pk32_pelletverbrauch_monat:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: monthly

# Jahresverbrauch - Referenz für Ist-vs.-Prognose und für den Startwert
hg_pk32_pelletverbrauch_jahr:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: yearly
```

Einbindung in `configuration.yaml`:

```yaml
utility_meter: !include utility_meter.yaml
```

### Schritt 3: Template-Sensoren einrichten

Erstelle oder erweitere `templates.yaml`:

```yaml
#
# Templates - Pelletverbrauch
#
# Modell:  Verbrauch = Grundlast * Tage + kg/HDD * Heizgradtage
#
# Die Monats-HDD-Tabelle steht in vier Sensoren inline. Wer sie an einer
# Stelle pflegen will, legt sie als Makro unter
# config/custom_templates/heizung.jinja ab und importiert sie.
#

- sensor:

    ###########################################################################
    # 1) Norm-HDD des laufenden Monats (VDI 4710 / DWD 1991-2020)
    ###########################################################################
    - name: "hdd_norm_monat"
      unique_id: hdd_norm_monat
      unit_of_measurement: "HDD"
      state: >
        {% set hdd = {
          1: 496, 2: 413, 3: 341, 4: 232, 5: 118, 6: 34,
          7: 17, 8: 27, 9: 86, 10: 215, 11: 370, 12: 449
        } %}
        {{ hdd[now().month] }}

    ###########################################################################
    # 2) Norm-HDD Jahr - Summe der Monatstabelle, damit beide nicht
    #    auseinanderlaufen koennen
    ###########################################################################
    - name: "hdd_norm_jahr"
      unique_id: hdd_norm_jahr
      unit_of_measurement: "HDD"
      state: >
        {% set hdd = {
          1: 496, 2: 413, 3: 341, 4: 232, 5: 118, 6: 34,
          7: 17, 8: 27, 9: 86, 10: 215, 11: 370, 12: 449
        } %}
        {{ hdd.values() | sum }}

    ###########################################################################
    # 3) Laenge des Messzeitraums in Tagen
    ###########################################################################
    - name: "pelletverbrauch_zeitraum_tage"
      unique_id: pelletverbrauch_zeitraum_tage
      unit_of_measurement: "d"
      availability: >
        {% set ts = state_attr('input_datetime.hg_pk32_pelletverbrauch_startzeit','timestamp') %}
        {{ ts is not none and ts > 0 and now().timestamp() > ts }}
      state: >
        {% set ts = state_attr('input_datetime.hg_pk32_pelletverbrauch_startzeit','timestamp') %}
        {{ ((now().timestamp() - ts) / 86400) | round(2) }}

    ###########################################################################
    # 4) Norm-HDD im Messzeitraum
    #    Start- und Endmonat tagesgenau anteilig, Monate dazwischen voll.
    ###########################################################################
    - name: "hdd_norm_zeitraum"
      unique_id: hdd_norm_zeitraum
      unit_of_measurement: "HDD"
      availability: >
        {% set ts = state_attr('input_datetime.hg_pk32_pelletverbrauch_startzeit','timestamp') %}
        {{ ts is not none and ts > 0 }}
      state: >
        {% set hdd = {
          1: 496, 2: 413, 3: 341, 4: 232, 5: 118, 6: 34,
          7: 17, 8: 27, 9: 86, 10: 215, 11: 370, 12: 449
        } %}
        {% set ts = state_attr('input_datetime.hg_pk32_pelletverbrauch_startzeit','timestamp') %}
        {% set start = ts | as_datetime | as_local %}
        {% set ende = now() %}
        {% set ns = namespace(sum=0.0) %}
        {% set start_em = start.year * 12 + start.month %}
        {% set ende_em = ende.year * 12 + ende.month %}

        {% macro tage_im_monat(j, m) -%}
          {{ 31 if m in [1,3,5,7,8,10,12] else (30 if m != 2 else (29 if (j % 4 == 0 and j % 100 != 0) or j % 400 == 0 else 28)) }}
        {%- endmacro %}

        {% if start_em == ende_em %}
          {% set tim = tage_im_monat(start.year, start.month) | int %}
          {% set ns.sum = hdd[start.month] * ((ende.day - start.day + 1) / tim) %}
        {% else %}
          {% set tim = tage_im_monat(start.year, start.month) | int %}
          {% set ns.sum = ns.sum + hdd[start.month] * ((tim - start.day + 1) / tim) %}

          {% for offset in range(1, 130) %}
            {% set em = start_em + offset %}
            {% if em < ende_em %}
              {% set ns.sum = ns.sum + hdd[((em - 1) % 12) + 1] %}
            {% endif %}
          {% endfor %}

          {% set tim = tage_im_monat(ende.year, ende.month) | int %}
          {% set ns.sum = ns.sum + hdd[ende.month] * (ende.day / tim) %}
        {% endif %}
        {{ ns.sum | round(2) }}

    ###########################################################################
    # 5) Norm-HDD vom 01.01. bis heute - Grundlage der Restjahr-Rechnung
    ###########################################################################
    - name: "hdd_norm_bis_heute"
      unique_id: hdd_norm_bis_heute
      unit_of_measurement: "HDD"
      state: >
        {% set hdd = {
          1: 496, 2: 413, 3: 341, 4: 232, 5: 118, 6: 34,
          7: 17, 8: 27, 9: 86, 10: 215, 11: 370, 12: 449
        } %}
        {% set heute = now() %}
        {% set ns = namespace(sum=0.0) %}
        {% for m in range(1, heute.month) %}
          {% set ns.sum = ns.sum + hdd[m] %}
        {% endfor %}
        {% set m = heute.month %}
        {% set j = heute.year %}
        {% set tim = 31 if m in [1,3,5,7,8,10,12] else (30 if m != 2 else (29 if (j % 4 == 0 and j % 100 != 0) or j % 400 == 0 else 28)) %}
        {{ (ns.sum + hdd[m] * (heute.day / tim)) | round(2) }}

    ###########################################################################
    # 6) Verbrauch im Messzeitraum, aufgeteilt in Grundlast und Heizanteil
    ###########################################################################
    - name: "pelletverbrauch_heizanteil"
      unique_id: pelletverbrauch_heizanteil
      unit_of_measurement: "kg"
      availability: >
        {{ states('sensor.hg_pk32_pelletverbrauch') | is_number
           and states('input_number.hg_pk32_pelletverbrauch_startwert') | is_number
           and states('input_number.pelletverbrauch_grundlast_warmwasser') | is_number
           and states('sensor.pelletverbrauch_zeitraum_tage') | is_number }}
      state: >
        {% set verbrauch = states('sensor.hg_pk32_pelletverbrauch') | float
                         - states('input_number.hg_pk32_pelletverbrauch_startwert') | float %}
        {% set grundlast = states('input_number.pelletverbrauch_grundlast_warmwasser') | float
                         * states('sensor.pelletverbrauch_zeitraum_tage') | float %}
        {{ [verbrauch - grundlast, 0] | max | round(1) }}
      attributes:
        verbrauch_gesamt: >
          {{ (states('sensor.hg_pk32_pelletverbrauch') | float
              - states('input_number.hg_pk32_pelletverbrauch_startwert') | float) | round(1) }}
        grundlast_anteil: >
          {{ (states('input_number.pelletverbrauch_grundlast_warmwasser') | float
              * states('sensor.pelletverbrauch_zeitraum_tage') | float) | round(1) }}

    ###########################################################################
    # 7) Effizienz: kg pro HDD - nur der wetterabhaengige Heizanteil
    ###########################################################################
    - name: "pellets_pro_hdd_norm"
      unique_id: pellets_pro_hdd_norm
      unit_of_measurement: "kg/HDD"
      availability: >
        {{ states('sensor.pelletverbrauch_heizanteil') | is_number
           and states('sensor.hdd_norm_zeitraum') | is_number
           and states('sensor.hdd_norm_zeitraum') | float > 0 }}
      state: >
        {{ (states('sensor.pelletverbrauch_heizanteil') | float
            / states('sensor.hdd_norm_zeitraum') | float) | round(3) }}

    ###########################################################################
    # 8) Jahresprognose = Grundlast * Tage im Jahr + kg/HDD * Jahres-HDD
    ###########################################################################
    - name: "pelletverbrauch_prognose_jahr_hdd_norm"
      unique_id: pelletverbrauch_prognose_jahr_hdd_norm
      unit_of_measurement: "kg"
      availability: >
        {{ states('sensor.pellets_pro_hdd_norm') | is_number
           and states('sensor.hdd_norm_jahr') | is_number
           and states('input_number.pelletverbrauch_grundlast_warmwasser') | is_number }}
      state: >
        {% set jahr = now().year %}
        {% set tage = 366 if (jahr % 4 == 0 and jahr % 100 != 0) or jahr % 400 == 0 else 365 %}
        {{ (states('input_number.pelletverbrauch_grundlast_warmwasser') | float * tage
            + states('sensor.pellets_pro_hdd_norm') | float
              * states('sensor.hdd_norm_jahr') | float) | round(1) }}

    ###########################################################################
    # 9) Monatsprognose = Grundlast * Tage im Monat + kg/HDD * Monats-HDD
    ###########################################################################
    - name: "pelletverbrauch_prognose_monat_hdd_norm"
      unique_id: pelletverbrauch_prognose_monat_hdd_norm
      unit_of_measurement: "kg"
      availability: >
        {{ states('sensor.pellets_pro_hdd_norm') | is_number
           and states('sensor.hdd_norm_monat') | is_number
           and states('input_number.pelletverbrauch_grundlast_warmwasser') | is_number }}
      state: >
        {% set m = now().month %}
        {% set j = now().year %}
        {% set tim = 31 if m in [1,3,5,7,8,10,12] else (30 if m != 2 else (29 if (j % 4 == 0 and j % 100 != 0) or j % 400 == 0 else 28)) %}
        {{ (states('input_number.pelletverbrauch_grundlast_warmwasser') | float * tim
            + states('sensor.pellets_pro_hdd_norm') | float
              * states('sensor.hdd_norm_monat') | float) | round(1) }}

    ###########################################################################
    # 10) Restjahr = Grundlast * Resttage + kg/HDD * (Jahres-HDD - HDD bis heute)
    ###########################################################################
    - name: "pelletverbrauch_restjahr_hdd_norm"
      unique_id: pelletverbrauch_restjahr_hdd_norm
      unit_of_measurement: "kg"
      availability: >
        {{ states('sensor.pellets_pro_hdd_norm') | is_number
           and states('sensor.hdd_norm_jahr') | is_number
           and states('sensor.hdd_norm_bis_heute') | is_number
           and states('input_number.pelletverbrauch_grundlast_warmwasser') | is_number }}
      state: >
        {% set jahr = now().year %}
        {% set tage_jahr = 366 if (jahr % 4 == 0 and jahr % 100 != 0) or jahr % 400 == 0 else 365 %}
        {% set resttage = tage_jahr - now().timetuple().tm_yday %}
        {% set hdd_rest = [states('sensor.hdd_norm_jahr') | float
                           - states('sensor.hdd_norm_bis_heute') | float, 0] | max %}
        {{ (states('input_number.pelletverbrauch_grundlast_warmwasser') | float * resttage
            + states('sensor.pellets_pro_hdd_norm') | float * hdd_rest) | round(1) }}
```

Einbindung in `configuration.yaml`:

```yaml
template: !include templates.yaml
```

Übernehmen mit **Entwicklerwerkzeuge** → **YAML** → **Konfiguration prüfen**, danach **Vorlagen neu laden**. Ein Neustart ist nicht nötig. Den Prüfschritt nicht überspringen: bei einem YAML-Fehler lädt der gesamte `template:`-Block nicht und alle zehn Sensoren verschwinden statt nur einem.

### Schritt 4: Automatisierung für den Zählerreset

Wird der Pelletzähler am Kessel zurückgesetzt, stimmt der Ankerpunkt nicht mehr: der Startwert zeigt auf einen Zählerstand, den es nicht mehr gibt. Ohne Korrektur rechnet die Prognose ab diesem Moment mit einem viel zu hohen Verbrauch weiter — ohne jede Fehlermeldung.

Diese Automatisierung setzt bei einem echten Reset **beide** Ankerwerte gemeinsam neu:

```yaml
- id: pelletverbrauch_reset_anker
  alias: "Pelletverbrauch: Anker aktualisieren bei Zählerreset"
  description: >
    Als Reset gilt nur ein Rückgang um mindestens 100 kg auf höchstens die
    Hälfte. Ein einzelner Ausreißer oder ein Ausfall des Zählers löst nichts aus.
  mode: single
  max_exceeded: silent
  triggers:
    - trigger: state
      entity_id: sensor.hg_pk32_pelletverbrauch
  conditions:
    - condition: template
      value_template: >
        {{ trigger.from_state is not none
           and trigger.to_state is not none
           and trigger.from_state.state | is_number
           and trigger.to_state.state | is_number
           and (trigger.from_state.state | float - trigger.to_state.state | float) >= 100
           and trigger.to_state.state | float <= (trigger.from_state.state | float * 0.5) }}
  actions:
    - action: input_number.set_value
      target:
        entity_id: input_number.hg_pk32_pelletverbrauch_startwert
      data:
        value: "{{ trigger.to_state.state | float }}"
    - action: input_datetime.set_datetime
      target:
        entity_id: input_datetime.hg_pk32_pelletverbrauch_startzeit
      data:
        date: "{{ now().strftime('%Y-%m-%d') }}"
        time: "{{ now().strftime('%H:%M:%S') }}"
    - action: logbook.log
      data:
        name: "Pelletverbrauch - Anker"
        message: >
          Zählerreset erkannt ({{ trigger.from_state.state }} ->
          {{ trigger.to_state.state }} kg). Anker neu gesetzt.
        entity_id: sensor.hg_pk32_pelletverbrauch
```

> **Warum die Bedingung so umständlich aussieht.** Naheliegend wäre
> `{{ to_state.state | float(0) < from_state.state | float(0) }}`. Das ist eine Falle:
> `float(0)` greift auch bei `unavailable`, also zählt jeder Ausfall des Zählers als
> Reset und verstellt den Anker. Deshalb die explizite Prüfung auf Zahlen plus ein
> Mindestrückgang.

Nach einem Reset braucht die Prognose einige Wochen, bis der Messzeitraum wieder lang genug für eine belastbare Effizienzkennzahl ist.

### Schritt 5: ApexCharts Card installieren (optional)

Für die 30-Tage-Übersicht wird die ApexCharts Card benötigt. Installation via HACS:

1. Öffne **HACS** → **Frontend**
2. Suche nach "ApexCharts Card"
3. Klicke auf **Download**
4. Starte Home Assistant neu

### Schritt 6: Dashboard erstellen

1. Gehe zu **Einstellungen** → **Dashboards**
2. Öffne ein bestehendes Dashboard oder lege ein neues an
3. Wechsle in den **Bearbeitungsmodus** (Stift oben rechts)
4. Öffne über das Dreipunktmenü den **Raw-Konfigurationseditor**
5. Füge den folgenden YAML-Block als neue Ansicht unter `views:` ein

Der Block bringt Pfad, Titel, Icon und Typ bereits mit — die Ansicht muss nicht vorher von Hand angelegt werden.

```yaml
type: masonry
path: heating
icon: mdi:heating-coil
title: Heizung
cards:
  - square: false
    type: grid
    cards:
      - type: entities
        icon: mdi:heating-coil
        title: Pelletheizung (Übersicht)
        entities:
          - type: section
            label: System & Status
          - entity: sensor.hg_pk32_verbindung
            name:
              type: entity
            icon: mdi:link
          - entity: sensor.hg_pk32_betriebsstatus
            name:
              type: entity
            icon: mdi:factory
          - entity: sensor.hg_pk32_kesselzustand
            name:
              type: entity
          - type: section
            label: Verbrauch & Wärmerzeugung
          - entity: sensor.hg_pk32_warmemenge
            name:
              type: entity
          - entity: sensor.hg_pk32_pelletverbrauch
            name:
              type: entity
            icon: mdi:chart-bar
          - type: section
            label: Kessel & Verbrennung
          - entity: sensor.hg_pk32_ausgangsleistung
            icon: mdi:gauge
            name:
              type: entity
          - entity: sensor.hg_pk32_wirkungsgrad
            name:
              type: entity
            icon: mdi:speedometer
          - entity: sensor.hg_pk32_kesseltemperatur
            name:
              type: entity
          - entity: sensor.hg_pk32_kessel_solltemperatur
            name:
              type: entity
            icon: mdi:thermometer-lines
          - entity: sensor.hg_pk32_brennraumtemperatur
            icon: mdi:fire
            name:
              type: entity
          - entity: sensor.hg_pk32_rauchgastemperatur
            name:
              type: entity
            icon: mdi:smoke
          - entity: sensor.hg_pk32_o2_gehalt
            name:
              type: entity
            icon: mdi:chart-line
          - entity: sensor.hg_pk32_saugzug_ist
            name:
              type: entity
            icon: mdi:fan
          - type: section
            label: Puffer & Speicher
          - entity: sensor.hg_pk32_pufferfullgrad
            name: Pufferfüllgrad
            icon: mdi:battery-medium
          - entity: sensor.hg_pk32_puffer_oben
            name: Puffer Oben
            icon: mdi:thermometer
          - entity: sensor.hg_pk32_puffer_mitte
            name: Puffer Mitte
            icon: mdi:thermometer
          - entity: sensor.hg_pk32_puffer_unten
            name: Puffer Unten
            icon: mdi:thermometer
          - entity: sensor.hg_pk32_puffer_sollwert_unten
            name: Maximum Sollwert
            icon: mdi:thermometer-plus
          - entity: sensor.hg_pk32_puffer_sollwert_oben
            name: Minimum Sollwert
            icon: mdi:thermometer-minus
          - type: section
            label: Heizkreise
          - entity: sensor.hg_pk32_vorlauf_hk_1
            name: Vorlauf HK 1
            icon: mdi:thermometer
          - entity: sensor.hg_pk32_vorlauf_soll_hk_1
            name: Ziel HK 1
            icon: mdi:target
          - type: section
            label: Warmwasser
          - entity: sensor.hg_pk32_warmwasser_1
            name: Warmwasser 1
            icon: mdi:water-boiler
          - entity: sensor.hg_pk32_warmwasser_b
            name: Warmwasser Soll 1
            icon: mdi:target
          - type: section
            label: Außentemperaturen
          - entity: sensor.hg_pk32_aussentemperatur
            name: Außentemperatur
        state_color: true
        show_header_toggle: false
    columns: 1

  # Diese Karte zeigt einen Raumfühler im Heizraum. Passe die beiden
  # Entitäten an deine Installation an oder entferne die Karte.
  - square: false
    type: grid
    cards:
      - type: entities
        entities: []
        title: Heizraum - Temperaturen
        icon: mdi:heat-pump-outline
      - square: false
        type: grid
        cards:
          - graph: line
            type: sensor
            entity: sensor.thd_005_temperature
            detail: 1
            name:
              type: entity
          - graph: line
            type: sensor
            entity: sensor.thd_005_humidity
            detail: 1
            name:
              type: entity
        columns: 2
    columns: 1

  - square: false
    type: grid
    cards:
      - type: entities
        entities: []
        title: Pelletheizung (Statistiken)
        icon: mdi:heating-coil
      - type: history-graph
        entities:
          - entity: sensor.hg_pk32_kesselzustand
            name: Status
        hours_to_show: 24
        title: Betriebszustand
      - square: false
        type: grid
        cards:
          - chart_type: line
            period: 5minute
            type: statistics-graph
            entities:
              - entity: sensor.hg_pk32_ausgangsleistung
                name: Leistung (%)
              - entity: sensor.hg_pk32_wirkungsgrad
                name: Wirkungsgrad (%)
            stat_types:
              - mean
            hide_legend: false
            logarithmic_scale: false
            days_to_show: 1
            title: Effizienz
        columns: 1
      - square: false
        type: grid
        cards:
          - chart_type: line
            period: 5minute
            type: statistics-graph
            entities:
              - entity: sensor.hg_pk32_kesseltemperatur
                name: Kesseltemperatur (°C)
              - entity: sensor.hg_pk32_kessel_solltemperatur
                name: Kesselsolltemperatur (°C)
              - entity: sensor.hg_pk32_brennraumtemperatur
                name: Brennraumtemperatur (°C)
              - entity: sensor.hg_pk32_rauchgastemperatur
                name: Rauchgastemperatur (°C)
            stat_types:
              - mean
            hide_legend: false
            logarithmic_scale: false
            days_to_show: 1
            title: Temperaturen
        columns: 1
      - chart_type: line
        period: 5minute
        type: statistics-graph
        entities:
          - sensor.hg_pk32_pufferfullgrad
        stat_types:
          - mean
          - min
          - max
        hide_legend: true
        logarithmic_scale: false
        days_to_show: 1
        title: Pufferfüllgrad
      - chart_type: line
        period: 5minute
        type: statistics-graph
        entities:
          - entity: sensor.hg_pk32_puffer_oben
            name: Oben
          - entity: sensor.hg_pk32_puffer_mitte
            name: Mitte
          - entity: sensor.hg_pk32_puffer_unten
            name: Unten
        stat_types:
          - mean
        hide_legend: false
        logarithmic_scale: false
        days_to_show: 1
        title: Pufferspeichertemperaturen
      - chart_type: line
        period: 5minute
        type: statistics-graph
        entities:
          - entity: sensor.hg_pk32_vorlauf_hk_1
            name: Vorlauf HK1 (Ist)
          - entity: sensor.hg_pk32_vorlauf_soll_hk_1
            name: Vorlauf HK1 (Soll)
          - entity: sensor.hg_pk32_warmwasser_1
            name: Warmwasser (Ist)
          - entity: sensor.hg_pk32_warmwasser_b
            name: Warmwasser (Soll)
        stat_types:
          - mean
        hide_legend: false
        logarithmic_scale: false
        days_to_show: 1
        title: Heizkreis & Warmwasser
      - chart_type: line
        period: 5minute
        type: statistics-graph
        entities:
          - entity: sensor.hg_pk32_aussentemperatur
            name: Außentemperatur
        stat_types:
          - mean
          - max
          - min
        hide_legend: true
        logarithmic_scale: false
        days_to_show: 1
        title: Außentemperatur
    columns: 1

  - type: vertical-stack
    cards:
      - type: entities
        title: Pelletverbrauch – Kennzahlen
        icon: mdi:fire
        entities:
          - entity: sensor.hg_pk32_pelletverbrauch_tag
            name: Tagesverbrauch (Ist)
            icon: mdi:calendar-today
          - entity: sensor.hg_pk32_pelletverbrauch_woche
            name: Wochenverbrauch (Ist)
            icon: mdi:calendar-week
          - entity: sensor.hg_pk32_pelletverbrauch_monat
            name: Monatsverbrauch (Ist)
            icon: mdi:calendar-month
          - entity: sensor.hg_pk32_pelletverbrauch_jahr
            name: Jahresverbrauch (Ist)
            icon: mdi:calendar-range
          - type: section
            label: Verbrauchsprognosen (HDD/VDI 4710)
          - entity: sensor.pelletverbrauch_prognose_monat_hdd_norm
            name: Monatsprognose
            icon: mdi:chart-line
          - entity: sensor.pelletverbrauch_prognose_jahr_hdd_norm
            name: Jahresprognose
            icon: mdi:chart-areaspline
          - entity: sensor.pelletverbrauch_restjahr_hdd_norm
            name: Restjahr-Prognose
            icon: mdi:calendar-clock
          - type: section
            label: Rechengrundlagen
          - entity: input_number.pelletverbrauch_grundlast_warmwasser
            name: Grundlast Warmwasser
            icon: mdi:water-boiler
          - entity: sensor.pelletverbrauch_heizanteil
            name: Heizanteil im Messzeitraum
            icon: mdi:radiator
          - entity: sensor.pellets_pro_hdd_norm
            name: Effizienz (nur Heizanteil)
            icon: mdi:speedometer
          - type: section
            label: Messzeitraum
          - entity: input_datetime.hg_pk32_pelletverbrauch_startzeit
            name: Startzeit
            icon: mdi:calendar-start
          - entity: input_number.hg_pk32_pelletverbrauch_startwert
            name: Startwert
            icon: mdi:counter
          - entity: sensor.pelletverbrauch_zeitraum_tage
            name: Länge
            icon: mdi:calendar-expand-horizontal
          - type: section
            label: Heizgradtage (VDI 4710 / DWD 1991–2020)
          - entity: sensor.hdd_norm_monat
            name: HDD Norm Monat
            icon: mdi:thermometer
          - entity: sensor.hdd_norm_jahr
            name: HDD Norm Jahr
            icon: mdi:thermometer-lines
          - entity: sensor.hdd_norm_bis_heute
            name: HDD Norm bis heute
            icon: mdi:thermometer-chevron-up
          - entity: sensor.hdd_norm_zeitraum
            name: HDD Norm im Messzeitraum
            icon: mdi:chart-timeline-variant
          - type: section
            label: Pelletverbrauch – 30 Tage Übersicht
          - type: custom:apexcharts-card
            header:
              title: Pelletverbrauch – 30 Tage Übersicht
              show: false
            graph_span: 30d
            span:
              end: day
            series:
              - entity: sensor.hg_pk32_pelletverbrauch_tag
                name: Tagesverbrauch
                type: column
                yaxis_id: main
                group_by:
                  duration: 1d
                  func: max
                transform: "return x === 0 ? null : x;"
                color: "#1e88e5"
            yaxis:
              - id: main
                decimals: 0
                min: 0
            apex_config:
              chart:
                height: 260
              plotOptions:
                bar:
                  columnWidth: 75%
              xaxis:
                axisBorder:
                  show: false
                axisTicks:
                  show: false
              yaxis:
                - axisBorder:
                    show: false
                  axisTicks:
                    show: false
              grid:
                yaxis:
                  lines:
                    show: false

  - type: entities
    title: Pelletheizung (Alle Sensordaten)
    icon: mdi:fire-circle
    entities:
      - type: section
        label: System & Status
      - entity: sensor.hg_pk32_verbindung
        name: Verbindung
        icon: mdi:link
      - entity: sensor.hg_pk32_betriebsstatus
        name: Betriebsstatus
        icon: mdi:factory
      - entity: sensor.hg_pk32_kesselzustand
        name:
          type: entity
      - entity: sensor.hg_pk32_storung
        name: Störung
        icon: mdi:alert-circle
      - entity: sensor.hg_pk32_storungsnummer
        name: Störungsnummer
        icon: mdi:numeric
      - entity: sensor.hg_pk32_programm_2
        name: Programm
        icon: mdi:clipboard-list
      - type: section
        label: Kessel & Verbrennung
      - entity: sensor.hg_pk32_warmemenge
        name:
          type: entity
      - entity: sensor.hg_pk32_ausgangsleistung
        name: Ausgangsleistung
        icon: mdi:gauge
      - entity: sensor.hg_pk32_wirkungsgrad
        name: Wirkungsgrad
        icon: mdi:speedometer
      - entity: sensor.hg_pk32_kesseltemperatur
        name: Kesseltemperatur
        icon: mdi:thermometer-water
      - entity: sensor.hg_pk32_kessel_solltemperatur
        name: Kessel Solltemperatur
        icon: mdi:target
      - entity: sensor.hg_pk32_brennraumtemperatur
        name: Brennraumtemperatur
        icon: mdi:fire
      - entity: sensor.hg_pk32_rauchgastemperatur
        name: Rauchgastemperatur
        icon: mdi:smoke
      - entity: sensor.hg_pk32_saugzug_ist
        name: Saugzug Ist
        icon: mdi:fan
      - entity: sensor.hg_pk32_saugzug_soll
        name: Saugzug Soll
        icon: mdi:fan-chevron-up
      - entity: sensor.hg_pk32_o2_gehalt
        name: O2-Gehalt
        icon: mdi:chart-line
      - entity: sensor.hg_pk32_o2_sollwert
        name: O2-Sollwert
        icon: mdi:target
      - entity: sensor.hg_pk32_lambda_heizleistung
        name: Lambda Heizleistung
        icon: mdi:lambda
      - entity: sensor.hg_pk32_lambda_spannung
        name: Lambda Spannung
        icon: mdi:flash
      - entity: sensor.hg_pk32_lambda_heizspannung
        name: Lambda Heizspannung
        icon: mdi:flash-outline
      - entity: sensor.hg_pk32_lambda_heizstrom
        name: Lambda Heizstrom
        icon: mdi:current-ac
      - entity: sensor.hg_pk32_temperaturspreizung
        name: Temperaturspreizung
        icon: mdi:thermometer-chevron-up
      - type: section
        label: Pellets & Förderung
      - entity: sensor.hg_pk32_pelletverbrauch
        name: Pelletverbrauch
        icon: mdi:chart-bar
      - entity: sensor.hg_pk32_pelletvorrat
        name: Pelletvorrat
        icon: mdi:warehouse
      - entity: sensor.hg_pk32_fullstand
        name: Füllstand
        icon: mdi:bucket
      - entity: sensor.hg_pk32_lagerraum_2
        name: Lagerraum
        icon: mdi:warehouse
      - entity: sensor.hg_pk32_laufzeit_seit_fullung
        name: Laufzeit seit Füllung
        icon: mdi:clock-outline
      - entity: sensor.hg_pk32_bldc_einschubschnecke_ist
        name: BLDC Einschubschnecke Ist
        icon: mdi:rotate-right
      - entity: sensor.hg_pk32_bldc_einschubschnecke_soll
        name: BLDC Einschubschnecke Soll
        icon: mdi:rotate-left
      - entity: sensor.hg_pk32_einschubschnecke_lauft
        name: Einschubschnecke Läuft
        icon: mdi:cog-transfer
      - entity: sensor.hg_pk32_einschubschnecke_richtung
        name: Einschubschnecke Richtung
        icon: mdi:arrow-left-right
      - type: section
        label: Puffer & Speicher
      - entity: sensor.hg_pk32_pufferfullgrad
        name: Pufferfüllgrad
        icon: mdi:battery-medium
      - entity: sensor.hg_pk32_puffer_oben
        name: Puffer Oben
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_puffer_mitte
        name: Puffer Mitte
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_puffer_unten
        name: Puffer Unten
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_pufferzustand
        name: Pufferzustand
        icon: mdi:information
      - entity: sensor.hg_pk32_puffer_sollwert_oben
        name: Sollwert Oben
        icon: mdi:target
      - entity: sensor.hg_pk32_puffer_sollwert_unten
        name: Sollwert Unten
        icon: mdi:target
      - type: section
        label: Heizkreise
      - entity: sensor.hg_pk32_heizkreis_anforderung
        name: Gesamtanforderung HK
        icon: mdi:radiator
      - entity: sensor.hg_pk32_vorlauftemperatur_gesamt
        name: Vorlauftemperatur Gesamt
        icon: mdi:thermometer-high
      - entity: sensor.hg_pk32_vorlauf_hk_1
        name: Vorlauf HK 1
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_rucklauf_hk_1
        name: Rücklauf HK 1
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_vorlauf_soll_hk_1
        name: Ziel HK 1
        icon: mdi:target
      - entity: sensor.hg_pk32_vorlauf_hk_2
        name: Vorlauf HK 2
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_rucklauf_hk_2
        name: Rücklauf HK 2
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_vorlauf_soll_hk_2
        name: Ziel HK 2
        icon: mdi:target
      - entity: sensor.hg_pk32_vorlauftemperatur_2
        name: Vorlauftemperatur 2
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_mischer_1_auf
        name: Mischer 1 Auf
        icon: mdi:arrow-up-bold
      - entity: sensor.hg_pk32_mischer_1_zu
        name: Mischer 1 Zu
        icon: mdi:arrow-down-bold
      - entity: sensor.hg_pk32_mischer_2_auf
        name: Mischer 2 Auf
        icon: mdi:arrow-up-bold
      - entity: sensor.hg_pk32_mischer_2_zu
        name: Mischer 2 Zu
        icon: mdi:arrow-down-bold
      - type: section
        label: Warmwasser & Frischwasser
      - entity: sensor.hg_pk32_frischwasser_freigabe
        name: Frischwasser Freigabe
        icon: mdi:water-check
      - entity: sensor.hg_pk32_frischwassertemperatur
        name: Frischwassertemperatur
        icon: mdi:water-thermometer
      - entity: sensor.hg_pk32_warmwasser_1
        name: Warmwasser 1
        icon: mdi:water-boiler
      - entity: sensor.hg_pk32_warmwasser_b
        name: Warmwasser Soll 1
        icon: mdi:target
      - entity: sensor.hg_pk32_boilerpumpe_1
        name: Boilerpumpe 1
        icon: mdi:pump
      - type: section
        label: Außentemperaturen
      - entity: sensor.hg_pk32_aussentemperatur
        name: Außentemperatur
        icon: mdi:thermometer
      - entity: sensor.hg_pk32_aussentemperatur_gemittelt
        name: Außentemperatur Gemittelt
        icon: mdi:thermometer-lines
      - entity: sensor.hg_pk32_aussentemperatur_warmepumpe
        name: Außentemperatur Wärmepumpe
        icon: mdi:heat-pump
      - type: section
        label: Reinigung & Entaschung
      - entity: sensor.hg_pk32_entaschung_gesperrt
        name: Entaschung Gesperrt
        icon: mdi:block-helper
      - entity: sensor.hg_pk32_aschenschnecke_lauft
        name: Aschenschnecke Läuft
        icon: mdi:cog
      - entity: sensor.hg_pk32_aschenschnecke_richtung
        name: Aschenschnecke Richtung
        icon: mdi:arrow-left-right
      - entity: sensor.hg_pk32_asche_saugen
        name: Asche Saugen
        icon: mdi:vacuum
      - entity: sensor.hg_pk32_reinigung_aktiviert
        name: Reinigung Aktiv
        icon: mdi:broom
      - entity: sensor.hg_pk32_reinigung_lauft
        name: Reinigung Läuft
        icon: mdi:progress-wrench
      - entity: sensor.hg_pk32_anzahl_entaschungen
        name: Anzahl Entaschungen
        icon: mdi:counter
      - entity: sensor.hg_pk32_anzahl_schurerbewegungen
        name: Anzahl Schürerbewegungen
        icon: mdi:counter
      - entity: sensor.hg_pk32_aschebox_2
        name: Aschebox
        icon: mdi:alert-box
      - type: section
        label: Kaskadenbetrieb
      - entity: sensor.hg_pk32_kaskade_1_ok
        name: Kaskade 1 OK
        icon: mdi:check-decagram
      - entity: sensor.hg_pk32_kaskade_1_lauft
        name: Kaskade 1 Läuft
        icon: mdi:engine
      - entity: sensor.hg_pk32_kaskade_1_maximalleistung
        name: Max Leistung 1
        icon: mdi:gauge-full
      - entity: sensor.hg_pk32_kaskade_1_minimalleistung
        name: Min Leistung 1
        icon: mdi:gauge-empty
      - type: section
        label: Elektrik & Sensorik
      - entity: sensor.hg_pk32_netzteil_spannung
        name: Netzteil-Spannung
        icon: mdi:flash
      - entity: sensor.hg_pk32_platinentemperatur
        name: Platinentemperatur
        icon: mdi:chip
      - entity: sensor.hg_pk32_netzrelais_2
        name: Netzrelais
        icon: mdi:toggle-switch
```

## Erklärung der Sensoren

### Heizgradtage

| Sensor | Bedeutung |
| --- | --- |
| `hdd_norm_monat` | Norm-Heizgradtage des laufenden Monats (VDI 4710 / DWD 1991–2020) |
| `hdd_norm_jahr` | Norm-Heizgradtage eines vollen Jahres, als Summe der Monatstabelle — 2798 HDD im deutschen Mittel |
| `hdd_norm_bis_heute` | Norm-HDD vom 1. Januar bis heute, tagesgenau im laufenden Monat |
| `hdd_norm_zeitraum` | Norm-HDD im Messzeitraum, also ab der gesetzten Startzeit |

### Messzeitraum und Aufteilung

| Sensor | Bedeutung |
| --- | --- |
| `pelletverbrauch_zeitraum_tage` | Länge des Messzeitraums in Tagen |
| `pelletverbrauch_heizanteil` | Verbrauch im Messzeitraum abzüglich Grundlast — also der Teil, der tatsächlich aufs Heizen entfällt. Die Attribute `verbrauch_gesamt` und `grundlast_anteil` zeigen die Aufteilung |

### Effizienz

| Sensor | Bedeutung |
| --- | --- |
| `pellets_pro_hdd_norm` | kg Pellets pro Heizgradtag, berechnet **nur aus dem Heizanteil**. Typische Größenordnung für ein Einfamilienhaus: 1 bis 2 kg/HDD. Werte über 5 deuten auf einen falsch gesetzten Ankerpunkt oder eine zu niedrige Grundlast hin |

### Prognosen

| Sensor | Rechnung |
| --- | --- |
| `pelletverbrauch_prognose_monat_hdd_norm` | Grundlast × Tage im Monat + kg/HDD × Monats-HDD |
| `pelletverbrauch_prognose_jahr_hdd_norm` | Grundlast × Tage im Jahr + kg/HDD × Jahres-HDD |
| `pelletverbrauch_restjahr_hdd_norm` | Grundlast × Resttage + kg/HDD × (Jahres-HDD − HDD bis heute) |

**Plausibilitätsprüfung:** Jahresverbrauch (Ist) plus Restjahr-Prognose muss ungefähr die Jahresprognose ergeben. Weichen die beiden stark voneinander ab, stimmt etwas mit dem Ankerpunkt nicht.

### Utility Meters

| Sensor | Bedeutung |
| --- | --- |
| `hg_pk32_pelletverbrauch_tag` | Tagesverbrauch, speist die 30-Tage-Grafik |
| `hg_pk32_pelletverbrauch_woche` | Wochenverbrauch |
| `hg_pk32_pelletverbrauch_monat` | Monatsverbrauch — daraus leitest du die Grundlast ab |
| `hg_pk32_pelletverbrauch_jahr` | Jahresverbrauch — Referenz für Ist-vs.-Prognose und zur Bestimmung des Startwerts |

## Anpassungen

### Heizgradtage für deine Region

Die Norm-Heizgradtage entsprechen dem deutschen Mittelwert. Für deine Region anpassen:

1. Besuche das [DWD Climate Data Center](https://cdc.dwd.de/portal/)
2. Suche die Heizgradtage für deine Region
3. Passe die Monatstabelle an — sie steht in vier Sensoren (`hdd_norm_monat`, `hdd_norm_jahr`, `hdd_norm_zeitraum`, `hdd_norm_bis_heute`) und muss überall gleich sein

Wer die Tabelle nur an einer Stelle pflegen will, legt sie als Makro unter `config/custom_templates/heizung.jinja` ab und importiert sie in den vier Sensoren.

### Sensor-Namen

Falls deine Installation ein anderes Präfix verwendet (z.B. `hg_hsk25` statt `hg_pk32`), musst du dieses in allen YAML-Dateien anpassen.

### Raumfühler im Heizraum

Die Karte „Heizraum - Temperaturen" verweist auf `sensor.thd_005_temperature` und `sensor.thd_005_humidity`. Das sind installationsspezifische Fühler — ersetze sie durch deine eigenen oder entferne die Karte.

## Troubleshooting

### Prognose-Sensoren zeigen `unavailable`

Das ist gewollt und zeigt an, dass eine Eingangsgröße fehlt. Die Kette von unten nach oben durchgehen — der erste Sensor, der `unavailable` ist, hat die Ursache:

```
input_datetime.hg_pk32_pelletverbrauch_startzeit   gesetzt?
input_number.hg_pk32_pelletverbrauch_startwert     gesetzt?
input_number.pelletverbrauch_grundlast_warmwasser  gesetzt?   ← wird gern vergessen
        ↓
sensor.pelletverbrauch_zeitraum_tage
sensor.hdd_norm_zeitraum
        ↓
sensor.pelletverbrauch_heizanteil
        ↓
sensor.pellets_pro_hdd_norm
        ↓
die drei Prognose-Sensoren
```

Am häufigsten fehlt die **Grundlast**: der Helper existiert nach dem Anlegen zwar, hat aber noch keinen Wert. Ohne ihn bleiben `pelletverbrauch_heizanteil` und damit alles darüber `unavailable`.

### Die Jahresprognose ist absurd hoch

Typisch sind Werte im Bereich des Zehn- bis Dreißigfachen des realistischen Verbrauchs. Zwei Ursachen kommen in Frage, beide beim Ankerpunkt:

**Startwert passt nicht zur Startzeit.** Prüfe das Attribut `verbrauch_gesamt` von `sensor.pelletverbrauch_heizanteil` — es zeigt, mit welchem Verbrauch gerechnet wird. Ist der Wert größer als dein Jahresverbrauch, obwohl die Startzeit im laufenden Jahr liegt, stimmt der Anker nicht. Setze beide Werte nach der Anleitung in Schritt 1 neu.

**Messzeitraum liegt im Sommer.** Beginnt der Messzeitraum im Juni und endet im September, sind die Norm-HDD in diesem Fenster sehr klein. Selbst eine korrekt abgezogene Grundlast lässt dann wenig Heizanteil übrig, und die Kennzahl wird instabil. Für belastbare Prognosen sollte der Messzeitraum mindestens ein paar Wochen Heizperiode enthalten — deshalb ist der Jahresbeginn als Anker die beste Wahl.

### Die Prognose ist zu hoch, aber nicht absurd

Meist ist die Grundlast zu niedrig angesetzt. Prüfe sie gegen die Sommermonate: `sensor.hg_pk32_pelletverbrauch_monat` im Juli und August sollte ungefähr Grundlast × 31 entsprechen.

### Sensoren zeigen `unknown` oder `unavailable`

- Prüfe, ob die Hargassner Integration korrekt installiert und verbunden ist
- Prüfe, ob `templates.yaml`, `utility_meter.yaml`, `input_number.yaml` und `input_datetime.yaml` in `configuration.yaml` eingebunden sind
- Nach Änderungen an den Konfigurationsdateien Home Assistant neu starten

### ApexCharts Card wird nicht angezeigt

- Prüfe, ob ApexCharts Card via HACS installiert ist
- Browser-Cache leeren und Seite neu laden
- Browser-Konsole auf Fehler prüfen

### Prognosen weichen von der Realität ab

- Die Rechnung arbeitet mit **Norm**-Heizgradtagen, nicht mit dem tatsächlichen Wetter. Ein milder oder strenger Winter weicht entsprechend ab
- Die Genauigkeit steigt mit der Länge des Messzeitraums, deutlich sichtbar ab der zweiten Heizperiode
- Für präzisere Ergebnisse lassen sich echte Heizgradtage aus einem Wetterdienst einsetzen statt der Normtabelle

## Support

Bei Fragen oder Problemen:

- Öffne ein [Issue auf GitHub](https://github.com/yourusername/yourrepo/issues)
- Besuche das [Home Assistant Forum](https://community.home-assistant.io/)

## Lizenz

Dieses Dashboard ist unter der MIT-Lizenz lizenziert.
