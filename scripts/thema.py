#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/neuro.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "neuro-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
    '(("Brain Diseases"[Majr:noexp] OR "Parkinson Disease"[Majr] OR '
    '"Multiple Sclerosis"[Majr] OR "Epilepsy"[Majr] OR "Migraine '
    'Disorders"[Majr] OR "Amyotrophic Lateral Sclerosis"[Majr] OR '
    '"Stroke"[Majr] OR "Dementia"[Majr:noexp] OR "Headache '
    'Disorders"[Majr] OR "Movement Disorders"[Majr:noexp]) NOT '
    '("Artificial Intelligence"[Majr] OR "Machine Learning"[Majr] OR '
    '"Deep Learning"[Majr] OR "Telemedicine"[Majr] OR "Medical '
    'Informatics"[Majr] OR "Nursing"[Majr] OR "Nursing Care"[Majr] OR '
    '"Long-Term Care"[Majr] OR "Nursing Homes"[Majr] OR "Aging"[Majr] '
    'OR "Longevity"[Majr] OR "Frailty"[Majr] OR "Geriatrics"[Majr] OR '
    '"Health Literacy"[Majr] OR "Patient Education as Topic"[Majr] OR '
    '"Climate Change"[Majr] OR "Air Pollution"[Majr] OR '
    '"Vaccination"[Majr] OR "Vaccines"[Majr] OR "Multimorbidity"[Majr] '
    'OR "Patient Safety"[Majr] OR "Medical Errors"[Majr] OR "Cross '
    'Infection"[Majr] OR "Mental Health Services"[Majr] OR "Mental '
    'Disorders"[Majr:noexp] OR "Obesity"[Majr] OR "Bariatric '
    'Surgery"[Majr] OR "Diabetes Mellitus"[Majr] OR "Eye '
    'Diseases"[Majr] OR "Ophthalmology"[Majr] OR "Musculoskeletal '
    'Diseases"[Majr:noexp] OR "Osteoarthritis"[Majr] OR "Arthritis, '
    'Rheumatoid"[Majr] OR "Osteoporosis"[Majr] OR "Back Pain"[Majr]))'
)
_KONTEXT = (
    '(hasabstract NOT (Comment[Publication Type] OR '
    'Editorial[Publication Type] OR Letter[Publication Type] OR '
    'News[Publication Type] OR "Published Erratum"[Publication Type] '
    'OR "Retraction of Publication"[Publication Type] OR "Case '
    'Reports"[Publication Type]))'
)
# OHNE "Humans"[MeSH]: Dieses Portal zeigt bewusst auch Grundlagenforschung.
# Tier- und Laborarbeiten kommen damit in den Pool - der Prompt muss sie ordnen.
# Zweiter Grund, den Filter hier wegzulassen: Frisch in PubMed aufgenommene
# Datensaetze sind noch nicht verschlagwortet. In der Woche vom 29.08.2026 trugen
# nur 37 bis 40 Prozent der neuen Datensaetze ueberhaupt "Humans"[MeSH] - ueber
# das ganze Jahr sind es 56 bis 67. Der Filter siebt also auch nach
# Bearbeitungsstand der NLM, nicht nur nach Inhalt.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}))',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 12
POOL_ALLGEMEIN = 43
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 1
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer Neurologie. "
    "Aus einer Liste von PubMed-Abstracts waehlst du die relevantesten "
    "aktuellen Studien aus und fasst sie praezise auf Deutsch zusammen. "
    "Deine Leserschaft arbeitet im deutschen Gesundheitswesen: "
    "neurologische Praxen und Kliniken, Stroke Units, "
    "Rehabilitationseinrichtungen, Kostentraeger, Selbstverwaltung, "
    "Selbsthilfe und Gesundheitspolitik. "
    "Sie erwartet beides - was die Forschung ueber das Nervensystem "
    "herausfindet und was davon bei den Behandelten ankommt."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) Diagnostik, Therapie, Rehabilitation oder Versorgung bei neurologischen Erkrankungen betreffen - oder die Grundlagen, auf denen sie beruhen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
  1. Praxisveraendernde Evidenz: randomisierte Studien, Metaanalysen,
     Leitlinien, Nutzenbewertungen, Registerauswertungen mit grosser
     Fallzahl.
  2. Harte Endpunkte: Sterblichkeit, bleibende Behinderung, funktionelle
     Unabhaengigkeit, Pflegebeduerftigkeit, Rezidiv, Lebensqualitaet.
     Was daran etwas aendert, wiegt schwerer als ein Skalenwert.
  3. Versorgung und Ergebnis: Zeit bis zur Behandlung, Erreichbarkeit
     einer Stroke Unit, Nachsorge, Rehabilitation, Teilhabe, Uebergang
     in die Pflege - gemessen an Folgen fuer die Behandelten.
  4. Grundlagenforschung mit erkennbarem Weg in die Klinik: Mechanismus,
     Zielstruktur, Biomarker, Modell - wenn die Arbeit selbst sagt,
     wohin es fuehrt.

NICHT in die Auswahl gehoeren:
Reine Tiermodelle und Zellversuche ohne erkennbaren Bezug zum Menschen (die Neurowissenschaft publiziert davon besonders viel), tiermedizinische Arbeiten, Phase-I-Studien, Bioaequivalenzstudien, Fallberichte und Fallserien unter zehn Behandelten, bibliometrische Arbeiten, Editorials und Kommentare, sowie reine Bildgebungsmethodik ohne klinische Fragestellung.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
  1. MINDESTENS 2 der sechs Studien muessen aus Europa stammen oder
     ein europaeisches Gesundheitssystem betreffen. Der Europa-Anteil
     liegt hier bei 13 Prozent und damit hoeher als bei den uebrigen
     Indikations-Hubs.
  2. HOECHSTENS ZWEI der sechs duerfen reine Grundlagenarbeiten sein
     (Zellsystem, Tiermodell, molekularer Mechanismus).
  3. HOECHSTENS EINE darf eine digitale Anwendung oder ein Verfahren des
     maschinellen Lernens im Mittelpunkt haben. Sie gehoeren nach
     ki.m-vf.de. Die Bildauswertung des Gehirns ist eines der groessten
     Anwendungsgebiete dort - ohne diese Quote bestuende die Ausgabe aus
     Algorithmen.
  4. HOECHSTENS EINE darf die Pflege und Betreuung bei Demenz im
     Mittelpunkt haben. Dieses Gebiet gehoert fachlich in beide Portale
     und ist bewusst nicht ausgeschlossen, aber Pflege ist mit 3,5
     Prozent der groesste Nachbar. Steht die neurologische Erkrankung im
     Mittelpunkt, gehoert die Arbeit hierher; steht die Betreuung im
     Mittelpunkt, nach pflege.m-vf.de.
  5. HOECHSTENS EINE darf eine rein psychiatrische Fragestellung im
     Mittelpunkt haben (Depression, Angst, Psychose). Sie gehoert nach
     mental.m-vf.de. Gemeint ist nicht die Depression NACH einem
     Schlaganfall - die ist neurologische Folge und gehoert hierher.
  6. HOECHSTENS ZWEI der sechs duerfen ausschliesslich einen Skalenwert
     berichten (mRS, NIHSS, EDSS, MMSE, UPDRS) ohne einen Endpunkt, den
     die Behandelten merken. Diese Arbeiten sagen, dass sich eine Zahl
     bewegt, nicht, dass jemand wieder gehen oder sprechen kann.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Zwischen Studienlage und Versorgung steht in Deutschland vor allem die Erreichbarkeit. Beim Schlaganfall entscheidet die Zeit bis zur Behandlung, und die haengt am Netz der zertifizierten Stroke Units und an der Verlegung in ein Zentrum mit Thrombektomie - eine Frage der Logistik, nicht der Evidenz. Bei der Demenz entscheidet die Schnittstelle zur Pflegeversicherung, bei der MS die Verordnungsfaehigkeit der verlaufsmodifizierenden Therapien, bei der Epilepsie die Zahl der spezialisierten Ambulanzen. Dazu kommt die Neurorehabilitation mit ihren Phasen A bis F, eine deutsche Besonderheit ohne direkte Entsprechung in anderen Systemen - Studien zur Rehabilitation aus dem Ausland sind deshalb nur eingeschraenkt uebertragbar, und das gehoert gesagt. Nenne bei internationalen Arbeiten das Gesundheitssystem, in dem sie entstanden sind.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
  **Er MUSS das Ergebnis nennen, nicht nur die Massnahme.** Und er darf
  sich NICHT auf einen Skalenwert beschraenken: Ein Punkt auf der
  modified Rankin Scale ist der Zwischenschritt, nicht das Ziel. Wo eine
  Arbeit einen Endpunkt berichtet, den die Behandelten merken - gehen,
  sprechen, schlucken, allein wohnen, zurueck in den Beruf,
  Pflegebeduerftigkeit, Sterblichkeit -, gehoert dieser in den Titel.
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Englisch bleiben: Stroke Unit, Outcome, Baseline, Setting, Follow-up, Hazard Ratio, Odds Ratio, Screening, mRS, NIHSS, Real-World-Evidenz. Deutsch: Thrombektomie, Thrombolyse, Hirninfarkt, Anfallsleiden, Schluckstoerung, Spastik, Neurorehabilitation, Pflegebeduerftigkeit. Uebersetze alles, wofuer es einen eingefuehrten deutschen Ausdruck gibt.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""

# ------------------------------------------------- Newsfeed
# Wonach dieser Hub im MVF-Archiv sucht (scripts/newsfeed.py). Deutsche,
# versorgungsnahe Begriffe - das Archiv ist deutsch, englische Begriffe
# treffen dort hoechstens zufaellig.
#
# Warum eine eigene Liste und nicht die Schnellwahlbegriffe der Seite: Chips
# sind fuer Datenbankabfragen gemacht. Am 29.08.2026 im Gender-Hub gemessen -
# dort stehen "Herzinfarkt" und "Arzneimittelsicherheit" als Chips, weil deren
# geschlechtsspezifische Seite das Thema ist; im Archiv holten dieselben
# Woerter allgemeine Herz- und Arzneimittelmeldungen. Fehlt NEWS_SUCHE, faellt
# newsfeed.py auf die Chips zurueck - das geht, ist aber die schlechtere Wahl.
#
# Neue Begriffe VOR dem Eintragen messen:
#     py scripts/newsfeed.py --probe
NEWS_SUCHE = [
    "Neurologie",
    "Schlaganfall",
    "Stroke Unit",
    "Demenz",
    "Alzheimer",
    "Parkinson",
    "Multiple Sklerose",
    "Epilepsie",
    "Neurorehabilitation",
]

# Der Ausschreibungsradar steht NICHT mehr hier. Er laeuft seit dem 28.08.2026
# einmal zentral im Versorgungsforschungs-Portal; die zwoelf Themengebiete,
# ihre Auswahlregeln und Suchbegriffe stehen dort in scripts/radar_themen.py.
# Dieser Hub holt sich mit scripts/radar_hinweis.py nur die Zahl seines
# Gebiets.
