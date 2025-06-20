import questions_list
import analysis
import nlg_simplenlg as nlg
import frame
import random
import math
import pyttsx3
from speech_recognition import Microphone, Recognizer

class DialogManager:
    def __init__(self, can_listen, total_questions=5):
        self.question = random.choice(questions_list.question_list)
        self.frame = frame.Frame(self.question)
        self.target_answers = self.frame.get_target_answer()
        self.wrong_dmanswers = 0
        self.dmquestion_generator = nlg.NLG("questions")
        self.pos_dmanswer_generator = nlg.NLG("positive answers")
        self.neg_dmanswer_generator = nlg.NLG("negative answers")
        self.memory = []
        self.voice_engine = pyttsx3.init()
        self.can_listen = can_listen
        
        # Nuovo sistema di gestione domande
        self.total_questions = total_questions
        self.questions_asked = 0
        self.generated_questions_count = 0
        self.traditional_questions_count = 0
        self.current_generated_question_is_correct = None
        
        # Pre-genera le domande per bilanciare correttamente
        self.question_plan = self.create_question_plan()

    def create_question_plan(self):
        """Crea un piano delle domande bilanciando generate e tradizionali"""
        plan = []
        
        # Calcola quante domande di ogni tipo
        generated_count = self.total_questions // 2
        traditional_count = self.total_questions - generated_count
        
        print(f"[DEBUG] Piano domande: {generated_count} generate + {traditional_count} tradizionali = {self.total_questions} totali")
        
        # Crea lista bilanciata
        for i in range(generated_count):
            plan.append('generated')
        for i in range(traditional_count):
            plan.append('traditional')
        
        # Mescola per varietà
        random.shuffle(plan)
        
        return plan

    def intro(self):
        intro = f"Ciao, sono Lara Croft, archeologa e avventuriera. Ti farò {self.total_questions} domande per verificare quanto conosci il mondo di Tomb Raider e le mie avventure. Preparati ad esplorare i segreti nascosti!"
        print(f"Lara Croft: {intro}")
        self.speak(intro)

    def print_helper(self):
        print(f"\nDomanda {self.questions_asked + 1}/{self.total_questions}")
        print(f"Piano: {self.question_plan[self.questions_asked] if self.questions_asked < len(self.question_plan) else 'completato'}")
        print(f"Generate: {self.generated_questions_count}, Tradizionali: {self.traditional_questions_count}")
        print(f"Errori: {self.wrong_dmanswers}\n")

    def print_helper_topic(self, topic_num, interaction_num=1):
        """Helper per visualizzare info su argomento e interazione"""
        print(f"\nArgomento {topic_num}/{self.total_questions} - Interazione {interaction_num}")
        if hasattr(self, 'frame') and self.frame:
            completed_answers = len(self.frame.get_current_answers())
            total_answers = len(self.target_answers)
            print(f"Frame: {completed_answers}/{total_answers} risposte trovate")
            print(f"Risposte trovate: {list(self.frame.get_current_answers())}")
            remaining = [answer for answer in self.target_answers 
                        if answer.lower() not in [a.lower() for a in self.frame.get_current_answers()]]
            if remaining:
                print(f"Risposte rimanenti: {remaining}")
            print(f"Frame completo: {'✅ SÌ' if self.frame.check_if_complete() else '❌ NO'}")
        print(f"Errori totali: {self.wrong_dmanswers}\n")

    def interview(self):
        self.intro()
        
        # Nuovo sistema con frame completi
        current_topic = 0  # Indice dell'argomento corrente
        
        while current_topic < self.total_questions and self.wrong_dmanswers < 5:
            question_type = self.question_plan[current_topic]
            
            print(f"\n=== ARGOMENTO {current_topic + 1}/{self.total_questions} ===")
            
            if question_type == 'generated':
                # Domande generate: completamento automatico dopo 1 risposta
                dmquestion, n = self.ask_generated_question()
                self.generated_questions_count += 1
                
                self.print_helper_topic(current_topic + 1)
                self.print_dmquestion(dmquestion, current_topic + 1)
                self.user_interaction(dmquestion, n)
                
                # Le domande generate si completano automaticamente
                print(f"[DEBUG] Domanda generata completata automaticamente")
                current_topic += 1
                
            else:  # traditional
                # Domande tradizionali: continua fino al completamento del frame
                dmquestion, n = self.ask_traditional_question()
                self.traditional_questions_count += 1
                
                interaction_count = 0
                max_interactions = 5  # Limite per evitare loop infiniti
                
                while not self.frame.check_if_complete() and interaction_count < max_interactions and self.wrong_dmanswers < 5:
                    interaction_count += 1
                    
                    self.print_helper_topic(current_topic + 1, interaction_count)
                    self.print_dmquestion(dmquestion, current_topic + 1, interaction_count)
                    self.user_interaction(dmquestion, n)
                    
                    if self.frame.check_if_complete():
                        print(f"[DEBUG] Frame completato dopo {interaction_count} interazioni!")
                        feedback = "Perfetto! Hai esplorato completamente questo argomento. Passiamo al prossimo!"
                        print(f"Lara Croft: {feedback}")
                        self.speak(feedback)
                        break
                    else:
                        remaining_answers = [answer for answer in self.target_answers 
                                           if answer.lower() not in [a.lower() for a in self.frame.get_current_answers()]]
                        if len(remaining_answers) > 0:
                            hints = ["Ci sono altri dettagli da scoprire su questo argomento...", 
                                   "Cosa altro sai su questo tema?", 
                                   "Continua l'esplorazione, c'è ancora molto da scoprire!"]
                            hint = random.choice(hints)
                            print(f"Lara Croft: {hint}")
                            self.speak(hint)
                
                current_topic += 1
            
            # Feedback intermedio ogni 2-3 argomenti
            if current_topic % 3 == 0 and current_topic < self.total_questions:
                remaining = self.total_questions - current_topic
                feedback = f"Ottimo progresso! Ancora {remaining} argomenti e avremo esplorato molti segreti insieme."
                print(f"Lara Croft: {feedback}")
                self.speak(feedback)
        
        # Aggiorna il contatore per compatibilità
        self.questions_asked = current_topic
        
        # Decide l'esito finale dell'intervista
        if self.wrong_dmanswers >= 5:
            return self.fail()
        else:
            return self.success()

    def ask_generated_question(self):
        """Genera una domanda usando il sistema NLG avanzato"""
        categories = ['biography', 'characteristics', 'adventures', 'facts']
        category = random.choice(categories)
        
        # 50% probabilità di domanda corretta vs scorretta
        correct = random.choice([True, False])
        
        dmquestion = self.dmquestion_generator.generate_from_knowledge_base(category, correct)
        
        # Memorizza se la domanda è intenzionalmente corretta o sbagliata
        self.current_generated_question_is_correct = correct
        
        print(f"[DEBUG] Domanda generata: '{dmquestion}'")
        print(f"[DEBUG] Intenzionalmente {'CORRETTA' if correct else 'SBAGLIATA'}")
        
        # Le domande generate sono tutte di tipo sì/no (n=3)
        return dmquestion, 3

    def ask_traditional_question(self):
        """Usa il sistema tradizionale con question_list"""
        # Scegli una domanda diversa da quelle già usate
        available_questions = [q for q in questions_list.question_list if q != self.question]
        if available_questions:
            self.question = random.choice(available_questions)
            self.frame = frame.Frame(self.question)
            self.target_answers = self.frame.get_target_answer()
        
        return self.question.get_text() + "?", 2

    def print_dmquestion(self, dmquestion, topic_num=None, interaction_num=None):
        if topic_num and interaction_num:
            print(f"\t\t[Argomento {topic_num}/{self.total_questions} - Domanda {interaction_num}] {dmquestion}")
        elif topic_num:
            print(f"\t\t[Argomento {topic_num}/{self.total_questions}] {dmquestion}")
        else:
            question_num = self.questions_asked + 1
            print(f"\t\t[{question_num}/{self.total_questions}] {dmquestion}")
        self.speak(dmquestion)

    def choose_dmquestion(self):
        """Metodo legacy - non più utilizzato nel nuovo sistema"""
        # Manteniamo per compatibilità, ma ora usiamo ask_generated_question e ask_traditional_question
        rand = random.randint(0, 100)
        if rand < 50:  # 50% generata
            return self.ask_generated_question()
        else:  # 50% tradizionale
            return self.ask_traditional_question()

    def check_not_repeated_dmquestion(self):
        dmquestion = self.dmquestion_generator.generate_question()
        checked_dmquestion = analysis.Analysis(dmquestion)
        if checked_dmquestion.check_for_answer() in self.memory:
            return self.check_not_repeated_dmquestion()
        else:
            self.memory.append(checked_dmquestion.check_for_answer())
            return dmquestion

    def ask_dmquestion(self):
        dmquestions = [
            f"{self.question.get_text()}?",
        ]
        return random.choice(dmquestions)

    def user_interaction(self, dmquestion, n):
        if self.can_listen:
            user_dmanswer = self.listen()
            self.check_user_dmanswer(user_dmanswer, dmquestion, n)
        else:
            user_dmanswer = input(f"Avventuriero: ")
            self.check_user_dmanswer(user_dmanswer, dmquestion, n)

    def check_if_contains_answer(self, dmquestion):
        checked_dmquestion = analysis.Analysis(dmquestion)
        answer = checked_dmquestion.check_for_answer()
        if answer and len(answer) > 0:
            return answer[0] in self.target_answers
        return False

    def check_user_dmanswer(self, user_dmanswer, dmquestion, n):
        if n == 1:
            self.user_replies_answer(
                user_dmanswer, self.check_if_contains_answer(dmquestion)
            )
        elif n == 2:
            self.user_proposes_answer(user_dmanswer)
        elif n == 3:
            # Nuovo tipo: domanda generata sì/no
            self.handle_generated_question_answer(user_dmanswer, dmquestion)

    def handle_generated_question_answer(self, user_answer, dmquestion):
        """Gestisce le risposte alle domande generate (sì/no)"""
        checked_answer = analysis.Analysis(user_answer)
        is_positive_answer = checked_answer.check_positivity()
        
        print(f"[DEBUG] Utente ha risposto: {'sì' if is_positive_answer else 'no'}")
        
        # Usa l'informazione memorizzata sulla correttezza della domanda
        if hasattr(self, 'current_generated_question_is_correct'):
            question_was_correct = self.current_generated_question_is_correct
        else:
            # Fallback alla valutazione tradizionale
            question_was_correct = self.evaluate_generated_question(dmquestion, is_positive_answer)
            
        print(f"[DEBUG] La domanda era: {'CORRETTA' if question_was_correct else 'SBAGLIATA'}")
        
        # La risposta è corretta se:
        # - Domanda corretta e utente dice sì, OPPURE
        # - Domanda sbagliata e utente dice no
        is_correct_answer = (question_was_correct and is_positive_answer) or (not question_was_correct and not is_positive_answer)
        
        print(f"[DEBUG] Risposta dell'utente è: {'CORRETTA' if is_correct_answer else 'SBAGLIATA'}")
        
        if is_correct_answer:
            dmanswer = self.pos_dmanswer_generator.generate_answer()
            print(f"Lara Croft: {dmanswer}")
            self.speak(dmanswer)
        else:
            self.wrong_dmanswers += 1
            dmanswer = self.neg_dmanswer_generator.generate_answer(positive=False)
            print(f"Lara Croft: {dmanswer}")
            self.speak(dmanswer)

    def evaluate_generated_question(self, dmquestion, user_said_yes):
        """Valuta se la risposta a una domanda generata è corretta"""
        # Per una valutazione più precisa, dobbiamo controllare se la domanda 
        # generata era intenzionalmente corretta o scorretta.
        
        # Il nuovo sistema NLG dovrebbe generare domande con informazioni che
        # sanno essere corrette o scorrette, ma per ora usiamo una logica migliorata
        
        print(f"[DEBUG] Valutando domanda: '{dmquestion}'")
        print(f"[DEBUG] Utente ha risposto: {'sì' if user_said_yes else 'no'}")
        
        # Mappatura più precisa di fatti veri vs falsi
        true_statements = {
            "lara croft è nata a wimbledon": True,
            "lara croft è britannica": True,
            "lara croft è inglese": True,
            "lara croft ha i capelli castani": True,
            "lara croft ha gli occhi marroni": True,
            "lara croft è alta 175 cm": True,
            "tomb raider è del 1996": True,
            "toby gard ha creato lara croft": True,
            "angelina jolie ha interpretato lara": True,
            "lara croft usa doppie pistole": True,
            "lord richard croft è il padre di lara": True,
            "lady amelia croft è la madre di lara": True,
        }
        
        # Controlla se la domanda corrisponde a una delle affermazioni note
        question_lower = dmquestion.lower().replace("?", "")
        
        # Verifica affermazioni note
        for statement, is_true in true_statements.items():
            if statement in question_lower:
                print(f"[DEBUG] Trovata corrispondenza: '{statement}' -> {is_true}")
                # La risposta corretta è:
                # - "sì" se l'affermazione è vera
                # - "no" se l'affermazione è falsa
                correct_answer_is_yes = is_true
                is_correct = (user_said_yes == correct_answer_is_yes)
                print(f"[DEBUG] Risposta corretta doveva essere: {'sì' if correct_answer_is_yes else 'no'}")
                print(f"[DEBUG] Risultato: {'CORRETTO' if is_correct else 'SBAGLIATO'}")
                return is_correct
        
        # Se non troviamo corrispondenze specifiche, usiamo la logica originale migliorata
        known_facts = [
            "wimbledon", "britannica", "inglese", "castani", "marroni", "175", 
            "1996", "1997", "1998", "1999", "2000", "2003", "toby gard", 
            "angelina jolie", "doppie pistole", "richard croft", "amelia croft",
            "perù", "grecia", "egitto", "atlantide", "venezia", "tibet"
        ]
        
        # Controlla se la domanda contiene informazioni probabilmente corrette
        fact_matches = sum(1 for fact in known_facts if fact.lower() in question_lower)
        
        # Logica euristica: se ci sono molti fatti noti, probabilmente è vera
        question_seems_true = fact_matches >= 1
        
        print(f"[DEBUG] Fatti trovati: {fact_matches}, domanda sembra vera: {question_seems_true}")
        is_correct = (user_said_yes == question_seems_true)
        print(f"[DEBUG] Risultato finale: {'CORRETTO' if is_correct else 'SBAGLIATO'}")
        return is_correct

    def user_replies_answer(self, user_dmanswer, is_target_answer):
        checked_dmanswer = analysis.Analysis(user_dmanswer)
        is_positive_dmanswer = checked_dmanswer.check_positivity()
        
        # La domanda contiene una risposta corretta
        if is_target_answer:
            if is_positive_dmanswer:  # Utente risponde positivamente (sì) - giusto
                # Aggiungi la risposta al frame senza incrementare wrong_dmanswers
                if len(self.memory) > 0:  # Verifica che la memory abbia elementi
                    self.frame.add_answer(self.memory[-1])
                dmanswer = self.pos_dmanswer_generator.generate_answer()
                print(f"Lara Croft: {dmanswer}")
                self.speak(dmanswer)
            else:  # Utente risponde negativamente (no) - sbagliato
                self.wrong_dmanswers += 1
                dmanswer = self.neg_dmanswer_generator.generate_answer(positive=False)
                print(f"Lara Croft: {dmanswer}")
                self.speak(dmanswer)
        # La domanda contiene una risposta scorretta
        else:
            if is_positive_dmanswer:  # Utente risponde positivamente (sì) - sbagliato
                self.wrong_dmanswers += 1
                dmanswer = self.neg_dmanswer_generator.generate_answer(positive=False)
                print(f"Lara Croft: {dmanswer}")
                self.speak(dmanswer)
            else:  # Utente risponde negativamente (no) - giusto
                dmanswer = self.pos_dmanswer_generator.generate_answer()
                print(f"Lara Croft: {dmanswer}")
                self.speak(dmanswer)

    def user_proposes_answer(self, user_dmanswer):
        # Se la risposta è vuota, trattala come un errore
        if not user_dmanswer.strip():
            self.wrong_dmanswers += 1
            dmanswer = "Devi darmi una risposta! L'esplorazione richiede coraggio e decisione."
            print(f"Lara Croft: {dmanswer}")
            self.speak(dmanswer)
            return
        
        print(f"[DEBUG] Valutando risposta: '{user_dmanswer}'")
        print(f"[DEBUG] Risposte target: {self.target_answers}")
        
        # Semplifichiamo l'algoritmo di riconoscimento delle risposte
        found_correct_answer = False
        user_answer_lower = user_dmanswer.lower().strip()  # Normalizza l'input dell'utente
        
        # Lista di parole "rumore" da ignorare nelle risposte
        noise_words = {'e', 'il', 'la', 'di', 'da', 'in', 'con', 'per', 'su', 'tra', 'fra', 'a', 'the', 'and', 'or', 'pippo', 'pasticcio', 'topolino', 'paperino'}
        
        # Prima controlla se l'intera risposta corrisponde esattamente a una delle risposte target
        for target in self.target_answers:
            target_lower = target.lower().strip()
            
            # Match esatto
            if user_answer_lower == target_lower:
                if not self.check_if_already_said(target):
                    print(f"[DEBUG] Match esatto trovato: {target}")
                    self.frame.add_answer([target])
                    self.memory.append(target)
                    found_correct_answer = True
                else:
                    print(f"Lara Croft: È corretto, ma l'hai già detto. Cerchiamo nuovi reperti da scoprire!")
                    self.speak("È corretto, ma l'hai già detto. Cerchiamo nuovi reperti da scoprire!")
                    return
            
            # Match se target è contenuto nella risposta (per risposte più lunghe)
            elif target_lower in user_answer_lower and len(target_lower) > 5:
                if not self.check_if_already_said(target):
                    print(f"[DEBUG] Match contenuto trovato: {target}")
                    self.frame.add_answer([target])
                    self.memory.append(target)
                    found_correct_answer = True
                else:
                    print(f"Lara Croft: È corretto, ma l'hai già detto. Cerchiamo nuovi reperti da scoprire!")
                    self.speak("È corretto, ma l'hai già detto. Cerchiamo nuovi reperti da scoprire!")
                    return

        # Se non troviamo corrispondenze esatte, proviamo matching intelligente per parole
        if not found_correct_answer:
            # Dividi l'input in parole e rimuovi rumore
            words = [word for word in user_answer_lower.split() if word not in noise_words and len(word) > 2]
            print(f"[DEBUG] Parole pulite dall'input: {words}")
            
            # Controlla ogni parola significativa
            for word in words:
                if len(word) >= 4:  # Solo parole con lunghezza significativa
                    for target in self.target_answers:
                        target_words = [w for w in target.lower().split() if w not in noise_words and len(w) > 2]
                        
                        # Cerca match di parole significative
                        for target_word in target_words:
                            if len(target_word) >= 4 and (word == target_word or target_word in word or word in target_word):
                                if not self.check_if_already_said(target):
                                    print(f"[DEBUG] Match di parola trovato: {target} ('{word}' ≈ '{target_word}')")
                                    self.frame.add_answer([target])
                                    self.memory.append(target)
                                    found_correct_answer = True
                                    break
                        if found_correct_answer:
                            break
                if found_correct_answer:
                    break
        
        # Fornisci il feedback appropriato in base alle risposte trovate
        if found_correct_answer:
            dmanswer = self.pos_dmanswer_generator.generate_answer()
            print(f"Lara Croft: {dmanswer}")
            self.speak(dmanswer)
        else:
            # Nessuna risposta corretta trovata
            print(f"[DEBUG] Nessuna risposta corretta trovata per: '{user_dmanswer}'")
            self.wrong_dmanswers += 1
            dmanswer = self.neg_dmanswer_generator.generate_answer(positive=False)
            print(f"Lara Croft: {dmanswer}")
            self.speak(dmanswer)

    def check_if_already_said(self, answer):
        # Normalizza la risposta corrente e tutte le risposte già date per un confronto equo
        answer_lower = answer.lower()
        current_answers = self.frame.get_current_answers()
        
        # La classe Frame usa un set per memorizzare le risposte correnti
        for a in current_answers:
            if a.lower() == answer_lower:
                return True
        return False

    def fail(self):
        percentage = max(0, 100 - (self.wrong_dmanswers * 20))
        fail = f"La tua prestazione necessita di miglioramenti... Hai completato {self.questions_asked}/{self.total_questions} domande con {self.wrong_dmanswers} errori (punteggio: {percentage}/100). Nelle mie avventure, un archeologo non preparato non sopravvive a lungo! Ti invito ad esplorare meglio il mio mondo e riprovare quando avrai acquisito più esperienza."
        print(f"\t\t Lara Croft: {fail}")
        self.speak(fail)

    def get_rating(self):
        ratings = ["principiante", "notevole", "eccellente", "straordinaria", "leggendaria"]
        # Calcola punteggio basato su domande totali ed errori
        points = max(0, 100 - ((self.wrong_dmanswers / self.total_questions) * 100))
        
        if points >= 90:
            return f"{ratings[4]} ({points:.0f}/100 punti)"
        elif points >= 75:
            return f"{ratings[3]} ({points:.0f}/100 punti)"
        elif points >= 60:
            return f"{ratings[2]} ({points:.0f}/100 punti)"
        elif points >= 45:
            return f"{ratings[1]} ({points:.0f}/100 punti)"
        else:
            return f"{ratings[0]} ({points:.0f}/100 punti)"

    def comment(self):
        points = max(0, 100 - ((self.wrong_dmanswers / self.total_questions) * 100))
        if points >= 90:
            comment = "Straordinario! La tua conoscenza di Tomb Raider rivale quella di un vero archeologo! Saresti un perfetto compagno d'avventura nei templi antichi."
        elif points >= 75:
            comment = "Eccellente! Hai dimostrato una conoscenza notevole delle mie avventure. Con un po' più di allenamento potresti diventare un esploratore formidabile!"
        elif points >= 60:
            comment = "Bel lavoro! Conosci abbastanza bene il mondo di Tomb Raider per sopravvivere alle sfide più comuni."
        elif points >= 45:
            comment = "Hai una conoscenza di base del mondo di Tomb Raider. Potresti superare qualche trappola, ma dovresti studiare meglio prima di avventurarti."
        else:
            comment = "La tua conoscenza di Tomb Raider necessita di miglioramenti... Ti invito ad esplorare meglio il mio mondo e riprovare quando avrai acquisito più esperienza."
        return comment

    def success(self):
        success = f"Impressionante! Hai completato {self.questions_asked}/{self.total_questions} domande con solo {self.wrong_dmanswers} errori! La tua conoscenza del mondo di Tomb Raider è {self.get_rating()}! {self.comment()}"
        print(f"\t\t Lara Croft: {success}")
        self.speak(success)

    def speak(self, text):
        # Usiamo una voce femminile inglese per Lara Croft se disponibile
        try:
            voice_id = "com.apple.voice.compact.en-GB.Serena"
            self.voice_engine.setProperty("voice", voice_id)
        except:
            # Se non disponibile, usa la voce predefinita
            pass
        self.voice_engine.setProperty("rate", 280)  # Velocità più naturale
        self.voice_engine.say(text)
        self.voice_engine.runAndWait()

    def listen(self):
        recognizer = Recognizer()
        with Microphone() as source:
            print("...pronto ad ascoltare...")
            audio = recognizer.listen(source, timeout=10)
            try:
                text = recognizer.recognize_google(audio, language="it-IT")
                print(f"Studente: {text}")
                return text
            except:
                print("Non ho capito")
                return ""


if __name__ == "__main__":
    print("=== COLLOQUIO CON LARA CROFT ===")
    print("Scegli la durata del colloquio:")
    print("1. Colloquio breve (3 domande)")
    print("2. Colloquio medio (5 domande) [default]")
    print("3. Colloquio completo (10 domande)")
    
    choice = input("Inserisci la tua scelta (1-3): ").strip()
    
    if choice == "1":
        total_questions = 3
    elif choice == "3":
        total_questions = 10
    else:
        total_questions = 5  # default
    
    print(f"\nHai scelto un colloquio con {total_questions} domande.")
    print("Metà saranno generate dinamicamente, metà dal database tradizionale.\n")
    
    dialog_manager = DialogManager(can_listen=False, total_questions=total_questions)
    dialog_manager.interview()

# IMPORTANTE
# Per un corretto funzionamento del programma:
# - Modalità con riconoscimento vocale: parlare solamente dopo che viene stampato "...ready to listen..."
# - Modalità standard: scrivere solamente dopo che viene stampato "Student: "
