### Report Tecnico e Guida Strategica: Il Capstone Project in Era "Vibe Coding"

##### 1\. Visione del Progetto: Dallo Sviluppo Sintattico all'Ingegneria degli Intenti

Il panorama dello sviluppo software sta vivendo la sua trasformazione più radicale dall'invenzione dei linguaggi di alto livello. Siamo passati dall'era della sintassi — dove il programmatore era un "posatore di mattoni" impegnato a scrivere manualmente ogni riga di codice — all'era dell' **Agentic Engineering** . In questo nuovo paradigma, il "Vibe Coding" (la prototipazione rapida guidata dal linguaggio naturale) rappresenta solo il punto di ingresso. Il Capstone Project non riguarda più la semplice scrittura di codice, ma l' **Ingegneria degli Intenti** : la capacità di definire obiettivi, gestire il giudizio umano e orchestrare sistemi autonomi.I dati di settore per il 2026 riflettono questa realtà competitiva: l' **85% dei professionisti**  utilizza regolarmente strumenti di AI e circa il  **41% del nuovo codice**  è interamente generato da macchine. In questo scenario, l'essere umano evolve da esecutore a "architetto degli intenti". La qualità dell'output finale non è più una funzione della potenza del modello linguistico, ma dipende interamente dalla robustezza dell'ambiente costruito attorno ad esso.

##### 2\. Architettura Obbligatoria: Il Modello "Agent \= Model \+ Harness"

Nel Capstone Project, l'equazione fondamentale da seguire è:  **Agente \= Modello \+ Harness** . È un errore comune trattare il modello (LLM) come il sistema completo; in realtà, il modello fornisce solo circa il  **10% della capacità ragionativa**  (il motore grezzo), mentre l' **Harness**  (l'imbracatura) costituisce il restante  **90%** . L'Harness è ciò che trasforma un "giocattolo AI" in un sistema di produzione, fornendo stato, esecuzione degli strumenti e cicli di feedback.Le componenti essenziali del Harness che il progetto deve implementare sono:

* **Sandboxes:**  Ambienti isolati (come terminali sicuri) per l'esecuzione del codice, che permettono all'agente di testare le proprie soluzioni senza rischi per l'infrastruttura.  
* **Orchestration Logic:**  Il "cervello" che gestisce il routing tra sub-agenti specializzati e decide quando un'attività è completata.  
* **Observability:**  Implementazione di log, tracce di esecuzione e monitoraggio dei costi dei token. Senza osservabilità, l'agente soffre di "Agent Drift", perdendo di vista l'obiettivo.**Il Livello "So What?":**  Un Harness correttamente configurato è il vero differenziatore competitivo. Nei benchmark come  **Terminal Bench 2.0** , l'ottimizzazione del Harness (senza cambiare il modello di base) ha permesso di elevare agenti dalla top 30 alla  **top 5 mondiale** . Ricordate: i fallimenti degli agenti sono quasi sempre fallimenti di configurazione del Harness, non limiti del modello.

##### 3\. Requisiti di Context Engineering: I 6 Pilastri del Progetto

Il  **Context Engineering**  è l'evoluzione del prompt engineering: un agente di successo richiede una "dieta" strutturata di informazioni per operare con precisione. Fornire troppo contesto statico causa il "Context Rot" (deterioramento del contesto), dove il rumore diluisce il segnale e degrada l'intelligenza del modello.Il progetto deve implementare i 6 pilastri del contesto:| Pilastro | Descrizione || \------ | \------ || **Instructions** | Confini core, persona e obiettivi primari (il "chi siamo"). || **Knowledge** | Documentazione, API docs e diagrammi caricati nel sistema. || **Memory** | Log di sessione a breve termine e stato del progetto a lungo termine. || **Examples** | Pattern "few-shot" che mostrano all'agente come risolvere problemi simili. || **Tools** | Definizioni precise di API e filesystem che l'agente può invocare. || **Guardrails** | Intercettori di sicurezza che bloccano azioni pericolose o non autorizzate. |  
Per massimizzare l'efficienza, il progetto deve distinguere tra  **Contesto Statico**  (regole immutabili caricate in file come AGENTS.md) e  **Contesto Dinamico**  (informazioni e "Agent Skills" caricate on-demand tramite RAG).

##### 4\. Il Ciclo di Vita del Progetto (New SDLC)

L'AI trasforma il Software Development Life Cycle (SDLC) nel cosiddetto  **Factory Model** : l'output dello sviluppatore non è più il codice, ma il  *sistema*  che produce il codice.

* **Pianificazione:**  Passaggio da documenti statici a prototipi interattivi generati in 10 minuti tramite Google AI Studio, permettendo una validazione immediata dell'intento.  
* **Implementazione:**  Gestione del  **"Problema dell'80%"** . L'AI gestisce l'80% del lavoro (boilerplate e logica standard), mentre l'umano si concentra sul 20% critico: logica di business complessa e casi limite.  
* **Testing:**  Obbligo di  **Trajectory Evaluation** . Non basta verificare se l'output è corretto; bisogna "valutare i calcoli dell'agente, non solo il risultato finale". L'agente ha seguito i protocolli? Ha verificato i permessi? Una soluzione corretta raggiunta tramite un percorso insicuro è un fallimento.

##### 5\. Protocolli e Interoperabilità: MCP, A2A e A2UI

Per evitare il debito tecnico strutturale, il progetto deve adottare standard aperti che garantiscano l'interoperabilità tra sistemi diversi.

* **MCP (Model Context Protocol):**  L' "USB-C" dell'AI. Permette di collegare l'agente a BigQuery, Drive o Slack tramite un handshake standardizzato (JSON-RPC 2.0), eliminando la necessità di scrivere wrapper personalizzati.  
* **A2A (Agent-to-Agent):**  La  **"Radio di Fabbrica"** . Definisce come agenti specializzati (es. un esperto di billing e uno di database) possano negoziare e delegare compiti tra loro.  
* **A2UI (Agent-to-User Interface):**  La  **"Vetrina Generativa"** . evolve l'output da JSON a interfacce dichiarative sicure, dove l'agente descrive la UI e il client la renderizza nativamente.

##### 6\. Guida Passo Passo: Partecipazione ed Ottenimento del Badge Kaggle

La partecipazione al Capstone Project richiede rigore tecnico. Seguite questa procedura operativa per validare il vostro "Factory Model":

* **Prototipazione in Google AI Studio:**  Accedete ad AI Studio, descrivete l'applicazione e rifinitela tramite linguaggio naturale. Questo è il vostro punto di partenza "Vibe Coding".  
* **Configurazione del Progetto Google Cloud:**  Prima di procedere, accedete alla Console Google Cloud e  **abilitate la Developer Knowledge API** . Generate quindi una Chiave API dedicata.  
* **Configurazione di Antigravity:**  Installate la CLI di Antigravity (comando agy). Configurate il file \~/.gemini/config/mcp\_config.json inserendo la vostra Chiave API per connettere il server google-developer-knowledge. Questo permetterà all'agente di accedere in tempo reale alla documentazione ufficiale Google.  
* **Deployment su Cloud Run:**  Utilizzate la funzione  **Publish**  di AI Studio per distribuire l'applicazione su infrastruttura serverless.  
* *Nota:*  Il  **Google Cloud Starter Tier**  permette fino a due deployment full-stack senza costi iniziali.  
* **Sottomissione su Kaggle:**  Caricate l' **App URL**  fornito da Cloud Run sulla pagina della competizione. È obbligatorio includere il file AGENTS.md (il contratto del vostro agente) e una documentazione che descriva l'architettura del Harness e le Trajectory Evals utilizzate.  
* **Ottenimento del Badge:**  Il badge verrà assegnato in base alla capacità del sistema di operare autonomamente rispettando i protocolli MCP e la robustezza del Harness presentato.**Nota Finale:**  In questa nuova era, la generazione del codice è un problema risolto. Il vero artigianato risiede nella direzione, nella verifica e nel giudizio architettonico.

