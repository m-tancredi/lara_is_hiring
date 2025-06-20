# Changelog

Tutte le modifiche importanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### ✨ Aggiunto
- **Sistema di domande generate dinamicamente** dalla knowledge base JSON
- **Bilanciamento automatico 50/50** tra domande generate e tradizionali
- **Completamento frame intelligente** con loop fino al completamento
- **Scelta flessibile della durata**: 3, 5 o 10 domande
- **Hint progressivi** per guidare l'utente verso le risposte mancanti
- **Sistema di valutazione dinamica** basato su errori/domande totali
- **Debug dettagliato** per trasparenza del sistema
- **Knowledge base JSON strutturata** con 100+ fatti su Tomb Raider
- **Generazione NLG avanzata** con SimpleNLG per domande sì/no
- **Analisi NLP migliorata** per riconoscimento positività e risposte

### 🎯 Frame System
- **Frame tradizionali (tipo 2)**: Continuano fino al completamento totale
- **Frame generati (tipo 3)**: Completamento automatico dopo risposta sì/no
- **Feedback intelligente**: Lara fornisce hint quando il frame è incompleto
- **Tracciamento stato**: Monitoraggio risposte trovate vs. rimanenti

### 🎲 Generazione Dinamica
- **4 categorie**: Biografia, Caratteristiche, Avventure, Fatti
- **Bilanciamento vero/falso**: 50% domande corrette, 50% scorrette
- **Valutazione intelligente**: Logica sì/no basata su knowledge base
- **Varietà garantita**: Ogni colloquio è diverso

### 🎮 Esperienza Utente
- **Menu di scelta durata** all'avvio
- **Feedback di progresso** ogni 3 argomenti
- **Rating dinamico**: Da principiante a leggendaria
- **Risposte contestuali** tematiche di Lara Croft
- **Separazione argomenti**: Chiara divisione tra topic

### 🛠️ Tecnico
- **Architettura modulare** con separazione responsabilità
- **Sistema di testing** per debugging e verifica
- **Gestione errori robusta** con limiti e fallback
- **Documentazione completa** con esempi e diagrammi

### 🐛 Risolto
- **Bug feedback positivi** per risposte sbagliate
- **Problema bilanciamento** domande generate/tradizionali
- **Errori di valutazione** nelle domande sì/no
- **Loop infiniti** nei frame incompleti

---

## Versioni Future Pianificate

### [1.1.0] - Pianificata
- 🌐 Supporto multilingua (inglese)
- 🎨 Interfaccia grafica web
- 📊 Statistiche dettagliate sessioni

### [1.2.0] - Pianificata  
- 🤖 Integrazione AI avanzata
- 🎮 Sistema achievements
- 📱 App mobile

---

**Legenda:**
- ✨ Aggiunto
- 🔄 Modificato  
- 🐛 Risolto
- ❌ Rimosso
- 🔒 Sicurezza 