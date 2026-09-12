# Custom Dashboard für Hargassner Pelletheizung

Diese Anleitung zeigt dir, wie du ein umfassendes Dashboard für deine Hargassner Pelletheizung einrichtest, inklusive Verbrauchsprognosen basierend auf Heizgradtagen (HDD) nach VDI 4710.

![Custom Dashboard](images/Custom_Dashboard.png)

## Übersicht

Das Dashboard bietet folgende Funktionen:

- **Pelletheizung (Übersicht)**: Alle wichtigen Sensoren auf einen Blick
- **Pelletheizung (Statistiken)**: Grafische Darstellung von Betriebszustand, Effizienz, Temperaturen und Pufferspeicher
- **Pelletverbrauch – Kennzahlen**: Tages-, Wochen-, Monats- und Jahresverbrauch sowie intelligente Prognosen
- **Pelletheizung (Alle Sensordaten)**: Komplette Übersicht aller verfügbaren Sensoren

## Voraussetzungen

- Home Assistant mit der Hargassner Integration installiert
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) für erweiterte Diagramme (optional, für die 30-Tage-Übersicht)

## Installation

### Schritt 1: Template-Sensoren einrichten

Die Template-Sensoren berechnen Heizgradtage und Verbrauchsprognosen basierend auf VDI 4710 Normdaten.

Erstelle oder erweitere die Datei `templates.yaml` in deinem Home Assistant Konfigurationsverzeichnis:

```yaml
#
# Templates - Pelletverbrauch HG-PK32
#
# Korrigierte Fassung vom 12.09.2026.
#
# WAS GEAENDERT WURDE
#
# 1) Zwei-Komponenten-Modell statt reiner HDD-Skalierung.
#    Vorher wurde der gesamte Verbrauch als wetterabhaengig behandelt. Die
#    Warmwasserbereitung laeuft aber das ganze Jahr und hat mit Heizgradtagen
#    nichts zu tun. Im Sommer geht HDD gegen null, der Verbrauch nicht - damit
#    explodiert kg/HDD und die Hochrechnung mit der Jahres-HDD ebenfalls.
#    Jetzt gilt:  Verbrauch = Grundlast * Tage  +  kg/HDD * HDD
#    Die Grundlast steht in input_number.pelletverbrauch_grundlast_warmwasser
#    (aktuell 5,11 kg/Tag, hergeleitet aus Juli 154 kg + August 163 kg / 62 Tage).
#
# 2) Die Monats-HDD-Tabelle steht weiterhin inline in den vier Sensoren, die
#    sie brauchen. Sauber waere sie einmal als Makro unter
#    config/custom_templates/heizung.jinja - dann muesste sie bei einer
#    Aenderung nur an einer Stelle angefasst werden. Das ist der naechste
#    sinnvolle Schritt, aendert aber nichts an der Rechnung.
#
# 3) Die Jahres-HDD war in Sensor 6 als 2798 hart eingetragen, obwohl es
#    sensor.hdd_norm_jahr gibt. Jetzt durchgaengig ueber den Sensor.
#
# 4) availability statt | float(0).
#    Faellt der Zaehler aus, lieferte float(0) einen negativen Verbrauch, der
#    von "verbrauch > 0" auf 0 gefiltert wurde - alle Prognosen sprangen still
#    auf 0. Jetzt werden die Sensoren unavailable, das sieht man.
#
# 5) hdd_norm_zeitraum: Monatsschleife von 24 auf 130 erweitert. Bei einem
#    Messzeitraum ueber zwei Jahre fielen vorher Monate stillschweigend weg.
#
# 6) Neu: sensor.hdd_norm_bis_heute (Jahres-HDD bis heute) und
#    sensor.pelletverbrauch_heizanteil - beide werden fuer das Modell
#    gebraucht und sind auch fuer sich nuetzlich.
#
# HINWEIS ZUR GRUNDLAST
# Einmal im Jahr nachziehen: Verbrauch Juli + August geteilt durch 62.
# Ueber sensor.hg_pk32_pelletverbrauch_monat in den Statistiken ablesbar.
#

- sensor:

    ###########################################################################
    # 1) Norm-HDD des laufenden Monats
    #    Die Monatstabelle liegt hier als Attribut und ist die einzige Quelle
    #    fuer alle folgenden Sensoren.
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
    # 2) Norm-HDD Jahr (VDI 4710) - Summe der Monatstabelle
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
      state: >
        {% set ts = state_attr('input_datetime.hg_pk32_pelletverbrauch_startzeit','timestamp') %}
        {{ ((now().timestamp() - ts) / 86400) | round(2) }}
      availability: >
        {% set ts = state_attr('input_datetime.hg_pk32_pelletverbrauch_startzeit','timestamp') %}
        {{ ts is not none and ts > 0 and now().timestamp() > ts }}

    ###########################################################################
    # 4) Norm-HDD im Messzeitraum
    #    Start- und Endmonat tagesgenau anteilig, die Monate dazwischen voll.
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
    # 5) Norm-HDD vom 01.01. bis heute
    #    Wird fuer die Restjahr-Rechnung gebraucht und ersetzt den frueheren,
    #    dauerhaft unavailable sensor.hdd_norm_bis_monat.
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
    # 7) Effizienz: kg pro HDD - nur noch der wetterabhaengige Heizanteil
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
    # 8) Jahresprognose = Grundlast * 365 + kg/HDD * Jahres-HDD
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

**Wichtig:** Stelle sicher, dass `templates.yaml` in deiner `configuration.yaml` eingebunden ist:

```yaml
# Templates
template: !include templates.yaml
```

### Schritt 2: Helper erstellen

Für die Verbrauchsprognosen werden **zwei Helper** benötigt:

| Helper | Typ | Zweck |
| --- | --- | --- |
| `hg_pk32_pelletverbrauch_startzeit` | `input_datetime` | Beginn des Messzeitraums |
| `hg_pk32_pelletverbrauch_startwert` | `input_number` | Zählerstand (kg) bei Beginn |

**Option A: Über die UI erstellen (empfohlen)**

1. Gehe zu **Einstellungen** → **Geräte & Dienste** → **Helfer**
2. **Startzeit erstellen:**
   - Klicke auf **+ Helfer erstellen** → **Datum und/oder Uhrzeit**
   - **Name**: `hg_pk32_pelletverbrauch_startzeit`
   - **Hat ein Datum**: ✓ aktiviert
   - **Hat eine Zeit**: ✓ aktiviert
   - Klicke auf **Erstellen**
3. **Startwert erstellen:**
   - Klicke auf **+ Helfer erstellen** → **Zahl**
   - **Name**: `hg_pk32_pelletverbrauch_startwert`
   - **Minimum**: 0
   - **Maximum**: 999999
   - **Schrittweite**: 1
   - **Einheit**: kg
   - Klicke auf **Erstellen**
4. Setze beide Helper auf die Werte zum Zeitpunkt, ab dem du den Verbrauch messen willst:
   - **Startzeit**: Datum/Uhrzeit des Messbeginns
   - **Startwert**: Der Zählerstand von `sensor.hg_pk32_pelletverbrauch` zu diesem Zeitpunkt

**Option B: Per YAML erstellen**

Erstelle oder erweitere die Datei `input_datetime.yaml`:

```yaml
#
# Input DateTime Helpers
#

# Startzeit für Pelletverbrauch-Berechnung
# Setze dieses Datum auf den Zeitpunkt, ab dem der Verbrauch gezählt werden soll
hg_pk32_pelletverbrauch_startzeit:
  name: "Startzeit Pelletverbrauchszähler"
  has_date: true
  has_time: true
```

Erstelle oder erweitere die Datei `input_number.yaml`:

```yaml
#
# Input Number Helpers
#

# Zählerstand bei Beginn des Messzeitraums
# Setze diesen Wert auf den Pelletverbrauch-Zählerstand zum Startzeitpunkt
hg_pk32_pelletverbrauch_startwert:
  name: "Startwert Pelletverbrauchszähler"
  min: 0
  max: 999999
  step: 1
  unit_of_measurement: "kg"
  mode: box
```

Stelle sicher, dass beide Dateien in deiner `configuration.yaml` eingebunden sind:

```yaml
# Input DateTime
input_datetime: !include input_datetime.yaml

# Input Number
input_number: !include input_number.yaml
```

Nach dem Neustart von Home Assistant: Gehe zu **Entwicklerwerkzeuge** → **Zustände** und setze beide Helper:

- `input_datetime.hg_pk32_pelletverbrauch_startzeit` → Startdatum (z.B. `2025-11-22 17:51:43`)
- `input_number.hg_pk32_pelletverbrauch_startwert` → Zählerstand bei Start (z.B. `121`)

> **Wichtig**: Ohne diese Helper zeigen alle Prognose-Sensoren "unknown" oder "0" an! Die Effizienz wird aus dem **Verbrauch seit Start** (aktueller Zähler minus Startwert) und den **HDD im Messzeitraum** berechnet.

### Schritt 3: Utility Meters konfigurieren

Die Utility Meters erfassen den Pelletverbrauch in verschiedenen Zeiträumen (Tag, Woche, Monat, Jahr).

Erstelle oder erweitere die Datei `utility_meter.yaml`:

```yaml
#
# Utility Meters
#

###########################################################################
# 1) TAGESVERBRAUCH PELLETS
#    - erzeugt einen täglichen Pelletverbrauch in kg
#    - Grundlage für Heatmaps, Tagesanalysen, Trendlinien
###########################################################################
hg_pk32_pelletverbrauch_tag:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: daily

###########################################################################
# 2) WOCHENVERBRAUCH PELLETS
#    - sauberer 7-Tage-intervallierter Verbrauch
#    - sinnvoll für Wochenberichte oder Effizienzauswertungen
###########################################################################
hg_pk32_pelletverbrauch_woche:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: weekly

###########################################################################
# 3) MONATSVERBRAUCH PELLETS
#    - extrem wichtig für:
#        * kg/HDD-Berechnung (Effizienz)
#        * Monatsprognosen
#        * Jahresprognosen
#    - dieser Wert wird direkt in den Templates weiterverwendet
###########################################################################
hg_pk32_pelletverbrauch_monat:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: monthly

###########################################################################
# 4) JAHRESVERBRAUCH PELLETS
#    - summiert deinen tatsächlichen Pelletverbrauch pro Kalenderjahr
#    - dient als Referenz für Ist-vs.-Prognose-Analysen
###########################################################################
hg_pk32_pelletverbrauch_jahr:
  source: sensor.hg_pk32_pelletverbrauch
  cycle: yearly
```

**Wichtig:** Stelle sicher, dass `utility_meter.yaml` in deiner `configuration.yaml` eingebunden ist:

```yaml
# Utility Meters
utility_meter: !include utility_meter.yaml
```

### Schritt 4: Dashboard erstellen

Erstelle ein neues Dashboard in Home Assistant oder füge eine neue Ansicht hinzu:

1. Gehe zu **Einstellungen** → **Dashboards**
2. Klicke auf **Dashboard hinzufügen** oder öffne ein bestehendes Dashboard
3. Füge eine neue Ansicht hinzu mit folgenden Einstellungen:
   - **Pfad**: `heating`
   - **Icon**: `mdi:heating-coil`
   - **Titel**: Heizung
   - **Typ**: Masonry

4. Wechsle in den **Bearbeitungsmodus** (drei Punkte oben rechts → **Bearbeiten**)
5. Kopiere den folgenden YAML-Code und füge ihn in die Ansicht ein:

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
            name: Monatsprognose (HDD/VDI 4710)
            icon: mdi:chart-line
          - entity: sensor.pelletverbrauch_prognose_jahr_hdd_norm
            name: Jahresprognose (HDD/VDI 4710)
            icon: mdi:chart-areaspline
          - entity: sensor.pelletverbrauch_restjahr_hdd_norm
            name: Restjahr-Prognose (HDD/VDI 4710)
            icon: mdi:calendar-clock
          - type: section
            label: Effizienzdaten
          - entity: sensor.pellets_pro_hdd_norm
            name: Effizienz
            icon: mdi:speedometer
          - type: section
            label: Heizgradtage (Norm via VDI 4710 / DWD 1991–2020)
          - entity: sensor.hdd_norm_monat
            name: HDD Norm Monat
            icon: mdi:thermometer
          - entity: sensor.hdd_norm_jahr
            name: HDD Norm Jahr
            icon: mdi:thermometer-lines
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

### Schritt 5: ApexCharts Card installieren (optional)

Für die 30-Tage-Übersicht wird die ApexCharts Card benötigt. Installation via HACS:

1. Öffne **HACS** → **Frontend**
2. Suche nach "ApexCharts Card"
3. Klicke auf **Download**
4. Starte Home Assistant neu

## Erklärung der Sensoren

### Template-Sensoren

#### Heizgradtage (HDD)

- **hdd_norm_monat**: Monatliche Norm-Heizgradtage basierend auf VDI 4710 / DWD (1991-2020)
- **hdd_norm_jahr**: Jährliche Norm-Heizgradtage (2798 HDD für Deutschland Mittel)

#### Effizienz

- **pellets_pro_hdd_norm**: Berechnet die Effizienz in kg Pellets pro Heizgradtag

#### Prognosen

- **pelletverbrauch_prognose_monat_hdd_norm**: Monatsprognose basierend auf HDD
- **pelletverbrauch_prognose_jahr_hdd_norm**: Jahresprognose basierend auf HDD
- **pelletverbrauch_restjahr_hdd_norm**: Restjahresprognose (verbleibende Monate)

### Utility Meters

- **hg_pk32_pelletverbrauch_tag**: Täglicher Pelletverbrauch
- **hg_pk32_pelletverbrauch_woche**: Wöchentlicher Pelletverbrauch
- **hg_pk32_pelletverbrauch_monat**: Monatlicher Pelletverbrauch (wichtig für HDD-Berechnung)
- **hg_pk32_pelletverbrauch_jahr**: Jährlicher Pelletverbrauch

## Anpassungen

### Heizgradtage für deine Region

Die Norm-Heizgradtage basieren auf dem deutschen Mittelwert. Du kannst diese Werte für deine Region anpassen:

1. Besuche die [DWD Climate Data Center](https://cdc.dwd.de/portal/) Seite
2. Suche nach den Heizgradtagen für deine Region
3. Passe die Werte in den Templates entsprechend an

### Sensor-Namen

Falls deine Hargassner-Installation andere Sensor-Namen verwendet (z.B. `hg_hsk25` statt `hg_pk32`), musst du diese in allen YAML-Dateien anpassen.

## Troubleshooting

### Sensoren zeigen "unknown" oder "unavailable"

- Stelle sicher, dass die Hargassner Integration korrekt installiert und konfiguriert ist
- Überprüfe, ob die Utility Meters korrekt in `configuration.yaml` eingebunden sind
- Starte Home Assistant neu nach Änderungen an den Konfigurationsdateien

### Prognose-Sensoren zeigen "0" oder "unknown"

- **Häufigste Ursache**: Der `input_datetime.hg_pk32_pelletverbrauch_startzeit` Helper wurde nicht erstellt oder nicht konfiguriert
- Erstelle den Helper wie in **Schritt 2** beschrieben
- Setze das Datum auf einen sinnvollen Startzeitpunkt (z.B. Beginn der Heizperiode oder letztes Pellet-Auffüllen)
- Überprüfe in **Entwicklerwerkzeuge** → **Zustände**, ob der Helper existiert und einen gültigen Zeitstempel hat

### ApexCharts Card wird nicht angezeigt

- Stelle sicher, dass ApexCharts Card via HACS installiert ist
- Lösche den Browser-Cache und lade die Seite neu
- Überprüfe die Browser-Konsole auf Fehler

### Prognosen sind ungenau

- Die Prognosen basieren auf Norm-Heizgradtagen und können von der Realität abweichen
- Für präzisere Prognosen kannst du echte Heizgradtage von einem Wetterdienst verwenden
- Die Genauigkeit verbessert sich im Laufe der Heizperiode

## Support

Bei Fragen oder Problemen:
- Öffne ein [Issue auf GitHub](https://github.com/yourusername/yourrepo/issues)
- Besuche das [Home Assistant Forum](https://community.home-assistant.io/)

## Lizenz

Dieses Dashboard ist unter der MIT-Lizenz lizenziert.
