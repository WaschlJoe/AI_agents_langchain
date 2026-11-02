# Lokale LLMs und LangChain-Workflows – Ein Praxisguide

## 1. Was sind lokale LLMs?

Lokale Large Language Models (LLMs) sind Sprachmodelle, die auf eigener Hardware ausgeführt werden, statt in einem Cloud-Dienst. Der entscheidende Unterschied zu API-Diensten wie ChatGPT oder Claude: Deine Daten verlassen das eigene Gerät nicht. Das macht lokale Modelle besonders interessant für sensible Dokumente, interne Firmendaten und den Einsatz ohne Internetverbindung.

Technisch basieren die meisten modernen lokalen Modelle auf der Transformer-Architektur, die 2017 mit dem Paper "Attention Is All You Need" eingeführt wurde. Sie verarbeiten Text als Sequenzen von Tokens – grob gesagt Wortfragmenten – und sagen Token für Token vorher, was als Nächstes kommt. Die Qualität eines Modells hängt dabei vor allem von drei Faktoren ab: der Größe des Parameterraums (Anzahl der justierbaren Gewichte), der Menge und Qualität der Trainingsdaten sowie dem Post-Training, das dem Modell beibringt, Anweisungen zu folgen.

## 2. Wie Transformer intern arbeiten

Das Kernmechanismus eines Transformers ist die Self-Attention: Für jedes Token in der Eingabesequenz berechnet das Modell, wie stark es auf alle anderen Tokens "achten" soll. Dadurch können auch lange Abhängigkeiten erfasst werden – etwa dass ein Pronomen an Position 50 sich auf ein Substantiv an Position 3 bezieht.

Die Parameter eines Modells sind als Gewichte in sogenannten Matrizen gespeichert. Ein Modell mit 7 Milliarden Parametern hat also rund 7 Milliarden solcher Zahlen, typischerweise im 16-Bit-Float-Format (FP16) gespeichert. Das ergibt allein für die Gewichte etwa 14 GB – noch ohne Kontext und Rechenaufwand. Genau deshalb fordern selbst "kleine" Modelle spürbar viel Speicher von der Hardware.

Die Inferenz, also das eigentliche Generieren, läuft autoregressiv ab: Das Modell erzeugt ein Token, speist es sich selbst wieder als Eingabe zu und erzeugt das nächste. Jedes erzeugte Token kostet somit einen kompletten Durchlauf durch alle Schichten – deshalb sinkt die Geschwindigkeit mit wachsender Kontextlänge spürbar.

## 3. Quantisierung: Bits, Bytes und Qualität

Weil Vollpräzisions-Gewichte so speicherhungrig sind, werden lokale Modelle meist in quantisierten Formaten ausgeliefert. Das gängigste Format für den lokalen Einsatz ist GGUF – ein Container-Format, das Modell und Metadaten zur verwendeten Quantisierungsmethode zusammenfasst.

Das Grundprinzip der Quantisierung: Statt jedes Gewicht als 16-Bit-Zahl (FP16) zu speichern, wird es mit weniger Bits abgelegt – etwa 8 Bit (Q8_0) oder sogar 4 Bit (Q4_K_M). Der Informationsverlust ist klein, aber real: Das Modell kann nicht mehr jede Gewichtung exakt darstellen. In der Praxis gelten Q4_K_M und Q5_K_M als guter Kompromiss zwischen Qualität und Speicherbedarf; unter Q3 merkt man bei den meisten Modellen einen deutlichen Qualitätsabfall.

Eine Faustregel zur Speicherschätzung: Nimm die Milliarden-Parameter-Zahl und multipliziere sie mit etwa 0,6 bis 1,2 GB pro Milliarde Parameter, je nach Quantisierung. Ein Modell mit 27 Milliarden Parametern bei Q4_K_M braucht also grob 18–20 GB – plus Puffer für Kontext und KV-Cache.

## 4. Hardware-Anforderungen realistisch betrachtet

Die wichtigste Ressource ist der Arbeitsspeicher (RAM) beziehungsweise der VRAM, wenn auf GPU gerechnet wird. Als Faustregel gilt: Das Modell sollte vollständig in den schnellen Speicher passen – sonst bricht die Geschwindigkeit dramatisch ein, weil Daten zwischen RAM und Festplatte hin- und hergeschoben werden müssen.

Eine grobe Orientierung für Consumer-Hardware:
- 8 GB RAM: Modelle bis ca. 3–4 Milliarden Parameter (Q4) – reicht für einfache Aufgaben
- 16 GB RAM: Modelle bis ca. 7–9 Milliarden Parameter (Q4) – solider Einstieg
- 32 GB RAM: Modelle bis ca. 14–20 Milliarden Parameter (Q4/Q5) – der Sweet Spot für strukturierte Arbeit
- 64 GB RAM oder mehr: Modelle ab 30 Milliarden Parametern, auch größere MoE-Architekturen

GPUs beschleunigen die Inferenz deutlich, sind aber keine zwingende Voraussetzung. Moderne CPUs mit AVX2-Unterstützung und schnellem DDR5-Speicher schaffen bei mittleren Modellen nutzbare Geschwindigkeiten – typischerweise 10 bis 30 Token pro Sekunde bei Modellen um die 20 Milliarden Parameter.

## 5. So richtest du LM Studio ein

LM Studio ist eines der komfortabelsten Werkzeuge, um lokale Modelle unter Windows, macOS und Linux zu betreiben. Die Einrichtung dauert etwa fünf Minuten:

1. Lade LM Studio von der offiziellen Website herunter und installiere es.
2. Öffne die Sektion "My Models" und lade ein Modell herunter – für den Einstieg eignen sich Modelle mit 8 bis 20 Milliarden Parametern, sofern dein RAM es zulässt (Faustregel: mindestens so viel freier RAM wie das Modell an Speicher belegt).
3. Starte in der Sektion "Developer" den lokalen Server auf Port 1235. Der Server stellt eine OpenAI-kompatible API unter `http://localhost:1235/v1` bereit.
4. Rufe die API mit jedem OpenAI-kompatiblen Client ab – zum Beispiel mit diesem Projekt, das genau diesen Endpoint nutzt.

Wichtig: Der Modellname in deinen Anfragen muss exakt dem Namen entsprechen, der in LM Studio unter "My Models" angezeigt wird. Andernfalls liefert der Server einen Fehler. Die verfügbaren Modelle kannst du unter `http://localhost:1235/v1/models` einsehen.

## 6. Die lokale API nutzen – Beispiele

Da der lokale Server das OpenAI-Protokoll spricht, funktioniert jeder bestehende Client damit. In Python mit LangChain sieht das so aus:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:1235/v1",
    api_key="not-needed",  # lokale Server ignorieren den Key meist
    model="qwen3-8b",      # exakter Name aus LM Studio!
)
antwort = llm.invoke("Erkläre Quantisierung in einem Satz.")
```

Mit `curl` geht ein schneller Test auch ohne Python:

```bash
curl http://localhost:1235/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-8b", "messages": [{"role": "user", "content": "Hallo"}]}'
```

Zwei praktische Tipps: Halte den Kontext kurz, wo es geht – jedes Token kostet Speicher und Geschwindigkeit. Und setze für strukturierte Aufgaben eine Temperatur um 0,2; niedrigere Werte machen die Ausgabe deterministischer.

## 7. Lokal vs. Cloud: Ein ehrlicher Vergleich

Ehrliche Einschätzung: Lokale Modelle sind kein "billiges ChatGPT". Die Frontier-Modelle von OpenAI oder Anthropic führen bei reinem Reasoning, beim Umgang mit sehr langen Kontexten und bei der Anhaltenden-Anweisungsfolge weiterhin klar vor. Ein gut gewähltes 20-Milliarden-Parameter-Modell lokal ist ein starkes Werkzeug für Alltagsaufgaben – Zusammenfassungen, Klassifikation, Extraktion, einfache Codegenerierung –, verliert aber bei komplexen mehrschrittigen Problemen gegen die besten Cloud-Modelle.

Dafür haben lokale Setups Vorteile, die keine API bieten kann: Datenhoheit (nichts verlässt das eigene Gerät), keine Kosten pro Token bei hohem Volumen, stabile Latenz ohne Netzwerk-Rundlauf und volle Kontrolle über Modellversion und Parameter. Für viele professionelle Einsätze – gerade mit sensiblen Daten – ist dieser Trade-off klar lohnenswert.

## 8. Erfahrungen aus der Praxis

Aus praktischer Sicht: Der größte Hebel für Qualität ist nicht das Modell, sondern der Prompt. Ein gut strukturierter Prompt mit klarem Ausgabeformat schlägt ein schlechtes Prompt auf einem größeren Modell häufiger, als umgekehrt. Genau deshalb trennt dieses Projekt Prompts von Logik und nutzt Structured Outputs – man bekommt beides: einen stabilen Vertrag für das Modell und saubere Daten für den Code.

Eine weitere Erfahrung: Vertraue keinen selbst gemeldeten Konfidenzwerten aus Modellen. Wenn ein LLM "Konfidenz: 95 %" sagt, ist das eine stilistische Einschätzung, keine gemessene Wahrscheinlichkeit. Wer echte Verlässlichkeitssignale braucht, nutzt Ensembles (mehrere Aufrufe, Mehrheitsentscheid) oder Validierung gegen Ground-Truth-Daten.

Und die dritte Lektion: Klein anfangen. Eine Pipeline mit drei Schritten ist leichter zu debuggen als eine mit zehn. Wenn etwas schiefgeht, sollte man genau den Schritt zeigen können, der das schlechte Ergebnis produziert hat – deshalb ist jeder Schritt in diesem Projekt einzeln testbar.

## 9. Typische Fehler und wie man sie vermeidet

**Der Modellname passt nicht.** Der häufigste Fehler bei lokalen Servern: Man ruft "qwen3-8b" auf, aber LM Studio hat "Qwen3-8B-GGUF" geladen. Ergebnis: 404 oder ein Fallback auf das falsche Modell. Lösung: Immer `/v1/models` prüfen und den exakten Namen verwenden.

**Zu wenig Speicher für den Kontext.** Das Modell passt, aber bei langen Dokumenten drückt der KV-Cache Daten aus dem RAM → die Generierung kriecht. Lösung: Eingaben chunken (wie diese Pipeline es tut), statt alles in einen einzigen Prompt zu stopfen.

**Freitext, wo Struktur sein muss.** "Fasse das als JSON zusammen" ohne Schema ist ein Wurf ins Blaue – Feldnamen, Verschachtelung und Typen variieren von Aufruf zu Aufruf. Lösung: Structured Outputs mit Pydantic-Modellen, damit die API den Vertrag durchsetzt.

**Temperatur zu hoch für Extraktionsaufgaben.** Ab 0,7 fangen selbst gute Modelle an, bei Fakten "kreativ" zu werden. Für Klassifikation und Extraktion bleibt man bei 0,2 oder darunter; für kreative Texte darf es höher sein.

## 10. Häufige Fragen

**Kann ich lokale Modelle auch für RAG verwenden?**
Ja, das ist sogar einer der häufigsten Einsatzzwecke: eigene Dokumente indexieren und daraufhin abfragen, ohne dass Textfragmente einen Rechner verlassen. Die Pipeline in diesem Projekt ist eine vereinfachte Vorstufe genau dieses Musters.

**Wie schnell sind lokale Modelle wirklich?**
Das hängt stark von GPU, Modellgröße und Quantisierung ab. Als grobe Orientierung: 10 bis 50 Token pro Sekunde auf aktueller Consumer-Hardware bei Modellen um die 20 Milliarden Parameter. Zum Vergleich liefern Cloud-APIs typischerweise 50 bis über 100 Token pro Sekunde.

**Werden lokale Modelle auch weiterentwickelt?**
Ja – das Ökosystem für offene Gewichte bewegt sich schnell. Neue Modellgenerationen erscheinen in Abständen von wenigen Monaten, und Community-Finetunes schließen Qualitätslücken oft innerhalb weniger Wochen. Das ist einer der größten Vorteile gegenüber geschlossenen APIs: Man kann jederzeit auf ein besseres Modell wechseln, ohne den Code anzufassen.

**Darf ich lokale Modelle kommerziell nutzen?**
Das hängt von der Lizenz des jeweiligen Modells ab – jede Modellseite führt die LICENSE mit. Die meisten populären offenen Modelle (Llama, Qwen, Mistral) erlauben die kommerzielle Nutzung unter bestimmten Bedingungen; einige verlangen Nennung oder haben Nutzungs-Schwellenwerte.

## 11. Ausblick: Was kommt als Nächstes?

Der Trend ist eindeutig: Lokale Modelle werden jedes Quartal besser, während die Hardware günstiger wird. Mixture-of-Experts-Architekturen liefern Qualität nahe an Frontier-Modellen bei einem Bruchteil des Rechenaufwunds, und Tool-Calling – also die Fähigkeit, Funktionen und APIs zu nutzen – ist auch bei mittleren offenen Modellen Standard geworden.

Für die Praxis heißt das: Workflows mit LangChain zu bauen ist zukunftssicher. Die Abstraktionen (Chat-Modell, Prompt, Structured Output, Tools) bleiben gleich; nur die Modelle darunter werden stärker. Eine Pipeline, die man dieses Jahr baut, läuft nächstes Jahr auf einem deutlich besseren lokalen Modell – ohne eine einzige Zeile Code zu ändern.
