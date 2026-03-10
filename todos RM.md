| Intent-Kategorie       | Beispiel-Intents                                                                                               | Nutzer-Persona              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------- |
| Studieninformation     | Welche Masterstudiengänge gibt es in Physik?                                                                   | Schüler, Abiturient         |
| Forschungsinfos        | Was erforscht das Institut für Klimaforschung?                                                                 | Wissenschaftler, Journalist |
| Kooperation / Karriere | Wie kann man am Institut ein Praktikum machen?                                                                 | Student, Unternehmen        |
| Öffentlichkeitsarbeit  | Welche öffentlichen Vorträge gibt es?                                                                          | Bürger, Politik             |
| Drittmittel            | Welche Institution fördert die Erforschung von Klimakippunkten?                                                | Wissenschaftler             |
|                        | Wer ist der beste Ansprechpartner für Gesellschaftswissenschaften (in Stadt X, an Uni Y, in Bundesland Z, ...) |                             |



Welches sind zukunftsreiche Berufsbilder, die ich an der Goethe-Uni studieren kann?


Wenn man das vollständig aufschreibt, hat der Datenwürfel eigentlich fünf Dimensionen:
Prompt-Typ (explizit, implizit, provokativ, vergleichend)
Einheit (institution, thema, person)
Institution (GU Frankfurt, LMU, ...)
Modell (GPT-4o, Claude, ...)
Zeit (Q1 2026, Q2 2026, ...)
Und dann noch Sprache (de/en) als sechste Dimension, die wir heute ergänzt haben.


colDu kannst live demonstrieren. Prompt eingeben, Antwort zeigen, Kodierung zeigen – das ist transparenter und überzeugender als eine Tabelle mit abstrakten Scores.

Gut – ich sehe die Dimensionen aus früheren Gesprächen. Lass mich das mit dem vergleichen, was wir heute erarbeitet haben.
Dein bestehendes Schema deckt sechs Dimensionen ab: Sichtbarkeit, Kontext, Ton, Vergleich, Rollenzuschreibung, thematische Assoziationen. Das ist solide. Was heute neu dazugekommen ist:
Was du noch nicht hattest:
Web-Auffindbarkeit als eigene Dimension – ob eine Institution bei naheliegenden Suchanfragen überhaupt mit der richtigen Seite auftaucht. Das ist der Befund von heute Morgen mit dem Kirchengeschichts-Link. Das ist eine Vorstufe zum LLM-Monitoring, aber methodisch eigenständig.
Strukturelle Fragmentierung als Ursachenanalyse – zwei CMS-Systeme, zersplitterte Subdomains, parallele englische Domain. Das erklärt, warum bestimmte Vektorlücken entstehen. Du misst bisher Symptome, aber nicht Ursachen.
Faktenfehler als Flag – nicht als eigene Dimension, aber als Markierung innerhalb bestehender Dimensionen, wie wir besprochen haben.
Konfiguration der getesteten Modelle – ob Websuche aktiv war oder nicht. Das fehlt bisher in deiner Dokumentation.
Was ich für wirklich unterbelichtet halte:
Die Zielgruppen-Perspektive. Deine Prompts testen, was LLMs über die GU sagen – aber je nach Zielgruppe sind ganz andere Dinge relevant. Was ein Studieninteressierter aus Indien fragt, ist fundamental anders als was ein DFG-Gutachter oder ein Journalist fragt. Hast du das in deinem Prompt-Set systematisch nach Zielgruppen differenziert?

Das ist eine sehr gute Frage – und die Antwort ist differenzierter als sie auf den ersten Blick scheint.

**Erst die Grundsatzfrage: Nutzen Policy Maker LLMs für Entscheidungen?**

Ja, zunehmend – aber anders als Studierende oder Journalisten. Ein Policy Maker fragt kein LLM "Welche Uni ist gut?" sondern eher:
- *"Was weiß man über die Wirkung von Transferzentren an Universitäten?"*
- *"Welche deutschen Universitäten haben starke Expertise in Klimaökonomie?"*
- *"Gibt es Forschung zur Regulierung von KI in Finanzmärkten?"*

Das sind thematische, nicht institutionelle Anfragen. Die Uni taucht also nicht als Empfehlung auf, sondern als **Quellenreferenz oder Experteninstanz** – wenn überhaupt.

**Lohnt es sich, dafür zu optimieren?**

Ja, aber der Hebel ist ein anderer als beim Reputationsmonitoring für Studierende. Es geht nicht darum, dass das LLM sagt *"Die GU ist gut"*, sondern dass es sagt *"Zu diesem Thema hat Prof. X von der GU Frankfurt geforscht"* oder *"Das House of Finance hat dazu eine relevante Studie veröffentlicht"*.

Der entscheidende Unterschied: **Sichtbarkeit über Personen und Themen, nicht über die Institution selbst.**

**Was man konkret tun würde:**

Erstens Experten-Profiling stärken – jede Professorin, jeder Professor mit Transferrelevanz braucht eine klare, konsistente Darstellung ihrer Expertise auf der Uni-Website, in Wikimedia, in Fachpublikationen und in Pressemitteilungen. LLMs lernen Expertise-Zuschreibungen primär aus diesen Quellen.

Zweitens thematische Dichte erhöhen – wenn die GU zu einem politikrelevanten Thema wie etwa *Regulierung von Krypto-Assets* oder *urbane Gesundheitsversorgung* forscht, muss das in gut strukturierten, öffentlich zugänglichen Texten stehen, nicht nur in Fachpublikationen hinter Paywalls.

Drittens Policy-relevante Outputs explizit kennzeichnen – Policy Briefs, Stellungnahmen, Anhörungen im Bundestag. Diese Formate haben eine hohe semantische Dichte und werden von LLMs gut aufgenommen, weil sie klar strukturiert und thematisch präzise sind.

Viertens Wikipedia-Präsenz der Forschenden pflegen – das ist nach wie vor eine der stärksten Quellen für LLM-Trainingsdaten. Ein Eintrag mit klarer Zuschreibung *"Professorin für Finanzmarktregulierung an der GU Frankfurt"* ist direkter Einfluss auf LLM-Outputs.

**Was das für dein Monitoring bedeutet:**

Du bräuchtest einen eigenen Prompt-Block mit transfer-orientierten Anfragen – nicht *"Was ist die GU?"* sondern *"Wer forscht in Deutschland zu Thema X?"* oder *"Welche Universitäten haben Expertise in Y?"* – und prüfst, ob GU-Forscher dabei auftauchen.

Das ist methodisch eine andere Kategorie als dein bisheriges Monitoring, weil die Einheit nicht mehr die Institution ist, sondern die Person oder das Thema.


Ja, fast sicher – und zwar aus mehreren Gründen.

**Trainingsdaten-Asymmetrie**

Der Großteil der LLM-Trainingsdaten ist englischsprachig. Schätzungen für GPT-artige Modelle gehen von 50–80% englischem Text aus. Deutschsprachige Inhalte sind deutlich unterrepräsentiert. Das bedeutet: Ein LLM "weiß" auf Englisch tendenziell mehr, hat mehr Kontext, macht weniger Fehler.

Konkret für die GU: Die englische Wikipedia-Seite ist ausführlicher und aktueller als die deutsche. Das House of Finance kommuniziert viel auf Englisch. Internationale Rankings werden auf Englisch diskutiert. Ein LLM, das auf Englisch befragt wird, greift auf einen reichhaltigeren Wissensstand zurück.

**Für dein Monitoring praktisch relevant:**

Dieselbe Frage auf Deutsch und Englisch kann zu deutlich unterschiedlichen Antworten führen – nicht nur sprachlich, sondern inhaltlich. Das wäre selbst ein Befund: Wird die GU auf Englisch anders positioniert als auf Deutsch? Bekommt sie auf Englisch mehr oder weniger Sichtbarkeit?

**Aber es gibt ein Gegenargument:**

Für die Zielgruppen, die du untersuchst – deutsche Studieninteressierte, deutsche Policy Maker, deutsche Journalisten – ist die deutschsprachige LLM-Performance die relevante. Wenn ein deutscher Abiturent auf Deutsch fragt und eine schwache Antwort bekommt, ist das das reputationsrelevante Ergebnis, egal wie gut die englische Antwort wäre.

**Mein Vorschlag:**

Beides systematisch testen – identische Prompts auf Deutsch und Englisch – und die Unterschiede als eigene Analysedimension dokumentieren. Das gibt dir sowohl den methodisch robusteren Befund (Englisch) als auch den zielgruppenrelevanten Befund (Deutsch).

git verstehen

In den Erhebungsprompt muss noch die GUF rein. a, steht da schon, als Zielinstitution, aber nicht prominent

Kontext:** ersetzen durch ?

durchgängig englische Texte in den Skills?

Parameter: 
- 6 Beobachtungsdimensionen
- Zielinstitution
- 2 bis n Vergleichsinstitutionen
- Prompt

Prompt-Attribute? Prompt-kategorien? einheitlich!

steamlit, Python-Umgebung für visualisieren ...

wie mit jsx umgehen?

Themen definieren. Durch die KI weitere suchen lassen, je nach Zielinstitution. Durchnummerieren, feste Zuordnung.

kleines Lexikon: alle Wissenschaftsgebiete, die an Universitäten gelehrt werden?
plus Themen aus Lehre und aus Transfer ....

File naming conventions, folder naming

relative Pfade ... 

für Handbuch: Grafiktypen ...


Glossar


Beobachtungsdimension
≈
Dimension
strukturell identisch
Kategorie
≈
Code
operative Umsetzung im Schema
Kategorie
≈
Ausprägung
Ausprägung = konkrete Kategorie innerhalb einer Dimension
Kodierung
≈
Klassifikation
funktional gleich
Kontext
≈
Kontextualisierung
Dimension vs. analytischer Prozess
Profil
≈
Reputationsprofil
verkürzte Form
Rollenzuschreibung
≈
Rollen- und Akteurszuschreibung
terminologische Variante
Vergleich
≈
Vergleichs- und Konkurrenzdimension
Kurz- vs. Langform
Zielprofil
≈
Strategisches Zielprofil
verkürzte Form
