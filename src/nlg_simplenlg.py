from simplenlg import NLGFactory, Realiser, DocumentElement
from simplenlg import Lexicon
from simplenlg import Feature, Tense, Form, Person, NumberAgreement, InterrogativeType
from simplenlg import NPPhraseSpec, VPPhraseSpec, SPhraseSpec
from analysis import Analysis
import spacy
import random
import json
import os

nlp = spacy.load("it_core_news_md")

class NLG:
    def __init__(self, corpus_type="questions", language="italian"):

        self.corpus_type = corpus_type
        self.language = language
        
        # Initialize SimpleNLG components
        self.lexicon = Lexicon.getDefaultLexicon()
        self.factory = NLGFactory(self.lexicon)
        self.realiser = Realiser(self.lexicon)
        
        # Load corpus templates
        self.templates = self.load_templates(corpus_type)
        
        # Load knowledge base
        self.kb = self.load_knowledge_base()
    
    def load_templates(self, corpus_type):
        templates = []
        
        if corpus_type == "questions":
            file_path = "../corpus/questions.txt"
        elif corpus_type == "positive answers":
            file_path = "../corpus/positive_answers.txt"
        elif corpus_type == "negative answers":
            file_path = "../corpus/negative_answers.txt"
        else:
            return templates
            
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                templates = [line.strip() for line in f if line.strip()]
                
        return templates
    
    def load_knowledge_base(self):
        kb = {}
        kb_path = "../knowledge.json"
        
        if os.path.exists(kb_path):
            try:
                with open(kb_path, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
            except json.JSONDecodeError:
                print("Error loading knowledge base JSON")
        
        return kb
    
    def generate_question(self, topic=None):

        if not self.templates:
            return self.create_simple_question(topic)
        
        question = random.choice(self.templates)
        
        test = Analysis(question)
        attempts = 0
        
        while (test.number_of_answer() >= 2 or test.number_of_answer() == 0) and attempts < 5:
            question = random.choice(self.templates)
            test = Analysis(question)
            attempts += 1
            
        return question
    
    def analyze_question_patterns(self):
        """Analizza i pattern delle domande esistenti in questions.txt"""
        patterns = {
            'biography': {
                'birth_year': ['è nata nel', 'è nata negli anni'],
                'birth_place': ['è nata a', 'è nata in'],
                'parents': ['Il padre di', 'La madre di', 'si chiama'],
                'education': ['ha studiato', 'è andata a scuola'],
                'residence': ['vive a', 'abita a'],
                'occupation': ['è un\'', 'lavora come'],
                'nationality': ['è britannica', 'è americana']
            },
            'characteristics': {
                'physical': ['è alta', 'ha gli occhi', 'ha i capelli'],
                'skills': ['possiede abilità', 'è abile nell\'', 'sa', 'conosce', 'è esperta'],
                'weapons': ['usa tipicamente', 'utilizza', 'porta con sé', 'usa principalmente'],
                'personality': ['è determinata', 'è coraggiosa', 'è intelligente', 'è ingegnosa']
            },
            'adventures': {
                'game_years': ['è stato pubblicato nel'],
                'locations': ['è una location', 'è visitato', 'è in'],
                'artifacts': ['è l\'artefatto', 'è un artefatto'],
                'villains': ['è l\'antagonista', 'è un antagonista'],
                'exploration': ['esplora', 'visita']
            },
            'facts': {
                'creation': ['è stata creata da', 'ha creato'],
                'records': ['detiene un', 'ha mai vinto'],
                'names': ['doveva essere', 'si chiamava'],
                'movies': ['ha interpretato'],
                'sales': ['ha venduto'],
                'quotes': ['dice', 'ha detto']
            }
        }
        return patterns

    def generate_from_knowledge_base(self, category=None, correct=True):
        """Genera domande basate sulla knowledge base usando template diretti"""
        if not self.kb:
            return self.create_simple_question()
        
        categories = ['biography', 'characteristics', 'adventures', 'facts']
        if not category:
            category = random.choice(categories)
        
        # Uso template diretti invece di SimpleNLG per evitare problemi di localizzazione
        if category == 'biography' and 'biography' in self.kb:
            bio = self.kb['biography']
            question_type = random.choice(['birth_year', 'birth_place', 'parents', 'nationality'])
            
            if question_type == 'birth_year':
                if correct:
                    year = bio['birth_year']
                    return f"Lara Croft è nata nel {year}?"
                else:
                    year = random.choice([1965, 1970, 1972, 1975])
                    return f"Lara Croft è nata nel {year}?"
                    
            elif question_type == 'birth_place':
                if correct:
                    place = random.choice(['Wimbledon', 'Londra', 'Inghilterra'])
                    return f"Lara Croft è nata a {place}?" if place != 'Inghilterra' else f"Lara Croft è nata in {place}?"
                else:
                    place = random.choice(['Manchester', 'Parigi', 'New York', 'Tokyo'])
                    return f"Lara Croft è nata a {place}?"
                    
            elif question_type == 'parents':
                parent_type = random.choice(['father', 'mother'])
                if parent_type == 'father':
                    if correct:
                        name = bio['parents']['father']
                    else:
                        name = random.choice(['Lord William Croft', 'Lord James Croft', 'Sir Thomas Croft'])
                    return f"Il padre di Lara Croft si chiama {name}?"
                else:
                    if correct:
                        name = bio['parents']['mother']
                    else:
                        name = random.choice(['Lady Elizabeth Croft', 'Lady Victoria Croft', 'Lady Margaret Croft'])
                    return f"La madre di Lara Croft si chiama {name}?"
                    
            elif question_type == 'nationality':
                if correct:
                    return "Lara Croft è britannica?"
                else:
                    nationality = random.choice(['americana', 'francese', 'tedesca', 'italiana'])
                    return f"Lara Croft è {nationality}?"
                
        elif category == 'characteristics' and 'characteristics' in self.kb:
            char = self.kb['characteristics']
            question_type = random.choice(['height', 'eyes', 'hair', 'skills', 'weapons'])
            
            if question_type == 'height':
                if correct:
                    height = char['height']
                    return f"Lara Croft è alta {height}?"
                else:
                    height = random.choice(['160 cm', '165 cm', '180 cm', '170 cm'])
                    return f"Lara Croft è alta {height}?"
                    
            elif question_type == 'eyes':
                if correct:
                    return "Lara Croft ha gli occhi marroni?"
                else:
                    color = random.choice(['blu', 'verdi', 'neri', 'azzurri'])
                    return f"Lara Croft ha gli occhi {color}?"
                    
            elif question_type == 'hair':
                if correct:
                    return "Lara Croft ha i capelli castani?"
                else:
                    color = random.choice(['biondi', 'neri', 'rossi', 'grigi'])
                    return f"Lara Croft ha i capelli {color}?"
                    
            elif question_type == 'skills':
                if correct:
                    skill = random.choice(char['skills_it'])
                    if skill == 'acrobatica':
                        return "Lara Croft possiede abilità acrobatiche?"
                    elif skill == 'arrampicata':
                        return "Lara Croft è abile nell'arrampicata?"
                    elif skill == 'arti marziali':
                        return "Lara Croft conosce le arti marziali?"
                    else:
                        return f"Lara Croft è esperta in {skill}?"
                else:
                    fake_skill = random.choice(['danza', 'cucina', 'pittura', 'musica'])
                    return f"Lara Croft è esperta in {fake_skill}?"
                    
            elif question_type == 'weapons':
                if correct:
                    weapon = random.choice(char['weapons_it'])
                    return f"Lara Croft usa {weapon}?"
                else:
                    fake_weapon = random.choice(['spade laser', 'granate', 'cannone', 'mazza'])
                    return f"Lara Croft usa {fake_weapon}?"
                     
        elif category == 'adventures' and 'adventures' in self.kb:
            games = list(self.kb['adventures'].keys())
            game = random.choice(games)
            game_data = self.kb['adventures'][game]
            question_type = random.choice(['year', 'location', 'artifact', 'villain'])
            
            if question_type == 'year':
                if correct:
                    year = game_data['year']
                    return f"{game} è stato pubblicato nel {year}?"
                else:
                    year = game_data['year'] + random.choice([-2, -1, 1, 2, 3])
                    return f"{game} è stato pubblicato nel {year}?"
                    
            elif question_type == 'location':
                if correct:
                    location = random.choice(game_data['locations_it'])
                    return f"{location} è una location di {game}?"
                else:
                    fake_locations = ['Tokyo', 'Australia', 'Brasile', 'Canada', 'Messico', 'Germania']
                    location = random.choice(fake_locations)
                    return f"{location} è una location di {game}?"
                    
            elif question_type == 'artifact':
                if correct and game_data['artifacts_it']:
                    artifact = random.choice(game_data['artifacts_it'])
                    return f"{artifact} è l'artefatto di {game}?"
                else:
                    fake_artifacts = ['Spada di Excalibur', 'Corona del Re', 'Tesoro dei Pirati', 'Calice del Sangue']
                    artifact = random.choice(fake_artifacts)
                    return f"{artifact} è l'artefatto di {game}?"
                    
            elif question_type == 'villain':
                if correct and game_data['villains']:
                    villain = random.choice(game_data['villains'])
                    return f"{villain} è l'antagonista di {game}?"
                else:
                    fake_villains = ['Dr. Evil', 'Amanda Evert', 'Pierre Dupont', 'Count Dracula']
                    villain = random.choice(fake_villains)
                    return f"{villain} è l'antagonista di {game}?"
        
        elif category == 'facts' and 'facts' in self.kb:
            fact = random.choice(self.kb['facts'])
            if correct:
                return self.fact_to_question(fact['fact_it'], True)
            else:
                return self.fact_to_question(fact['fact_it'], False)
        
        # Fallback
        return self.create_simple_question(category)
    
    def fact_to_question(self, fact, correct):
        """Converte un fatto in una domanda"""
        if 'è stata creata da Toby Gard' in fact:
            if correct:
                return "Lara Croft è stata creata da Toby Gard?"
            else:
                creator = random.choice(['John Carmack', 'Hideo Kojima', 'Shigeru Miyamoto'])
                return f"Lara Croft è stata creata da {creator}?"
        elif 'pubblicato nel 1996' in fact:
            if correct:
                return "Il primo Tomb Raider è stato pubblicato nel 1996?"
            else:
                year = random.choice([1995, 1997, 1998])
                return f"Il primo Tomb Raider è stato pubblicato nel {year}?"
        elif 'Guinness World Record' in fact:
            if correct:
                return "Lara Croft detiene un Guinness World Record?"
            else:
                return "Lara Croft non ha mai vinto premi?"
        elif 'Laura Cruz' in fact:
            if correct:
                return "Il nome originale di Lara doveva essere Laura Cruz?"
            else:
                name = random.choice(['Sarah Mitchell', 'Emma Stone', 'Lisa Parker'])
                return f"Il nome originale di Lara doveva essere {name}?"
        elif 'Angelina Jolie e Alicia Vikander' in fact:
            if correct:
                actress = random.choice(['Angelina Jolie', 'Alicia Vikander'])
                return f"{actress} ha interpretato Lara Croft nei film?"
            else:
                actress = random.choice(['Scarlett Johansson', 'Jennifer Lawrence', 'Charlize Theron'])
                return f"{actress} ha interpretato Lara Croft nei film?"
        else:
            return "Lara Croft è un personaggio interessante?"

    def create_simple_question(self, topic=None):
        """Genera domande semplici usando SimpleNLG con pattern migliorati"""
        patterns = self.analyze_question_patterns()
        
        if not topic:
            topics = ['biography', 'characteristics', 'adventures', 'facts']
            topic = random.choice(topics)
        
        # 50% probabilità di generare domanda corretta o sbagliata
        correct = random.choice([True, False])
        
        # Usa la knowledge base se disponibile
        if self.kb:
            return self.generate_from_knowledge_base(topic, correct)
        
        # Fallback al sistema originale migliorato
        document = self.factory.createDocument()
        sentence = self.factory.createClause()
        
        if topic == 'biography':
            sentence.setSubject('Lara Croft')
            bio_questions = [
                ('nascere', 'nel 1968' if correct else 'nel 1970'),
                ('nascere', 'a Wimbledon' if correct else 'a Manchester'),
                ('essere', 'britannica' if correct else 'americana'),
                ('vivere', 'a Croft Manor' if correct else 'in un appartamento a Londra')
            ]
            verb, complement = random.choice(bio_questions)
            sentence.setVerb(verb)
            sentence.addComplement(complement)
            sentence.setFeature(Feature.TENSE, Tense.PRESENT if verb != 'nascere' else Tense.PAST)
                
        elif topic == 'characteristics':
            sentence.setSubject('Lara Croft')
            if correct:
                char_questions = [
                    ('possedere', 'abilità acrobatiche'),
                    ('essere', 'abile nell\'arrampicata'),
                    ('conoscere', 'le arti marziali'),
                    ('usare', 'tipicamente doppie pistole')
                ]
            else:
                char_questions = [
                    ('avere paura', 'delle armi'),
                    ('odiare', 'i puzzle'),
                    ('essere', 'pigra'),
                    ('usare', 'principalmente granate')
                ]
            verb, obj = random.choice(char_questions)
            sentence.setVerb(verb.split()[0])
            if len(verb.split()) > 1:
                sentence.addComplement(verb.split()[1])
            sentence.setObject(obj)
            sentence.setFeature(Feature.TENSE, Tense.PRESENT)
            
        elif topic == 'adventures':
            game_questions = [
                ('Il primo Tomb Raider', 'essere stato pubblicato', 'nel 1996' if correct else 'nel 1995'),
                ('Tomb Raider II', 'essere stato pubblicato', 'nel 1997' if correct else 'nel 1999'),
                ('Venezia', 'essere', 'una location di Tomb Raider II' if correct else 'una location di Tomb Raider III')
            ]
            subj, verb, complement = random.choice(game_questions)
            sentence.setSubject(subj)
            sentence.setVerb(verb.split()[0])
            sentence.addComplement(complement)
            sentence.setFeature(Feature.TENSE, Tense.PRESENT)
        
        sentence.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.YES_NO)
        document.addComponent(sentence)
        
        realized_text = self.realiser.realise(document).getRealisation()
        return realized_text
    
    def generate_answer(self, positive=True, question=None):

        corpus_type = "positive answers" if positive else "negative answers"
        
        if self.corpus_type != corpus_type:
            self.corpus_type = corpus_type  # AGGIORNA IL TIPO!
            self.templates = self.load_templates(corpus_type)
        
        if not self.templates:
            return self.create_simple_answer(positive)
            
        answer = random.choice(self.templates)
        
        return answer
    
    def create_simple_answer(self, positive=True):
        document = self.factory.createDocument()
        
        if positive:
            sentence = self.factory.createClause()
            
            structures = [
                ("Esatto", "essere", "la risposta corretta"),
                ("Bravo", "avere", "ragione"),
                ("Perfetto", "sapere", "la risposta")
            ]
            
            structure = random.choice(structures)
            
            if structure[0] == "Esatto":
                interjection = self.factory.createClause()
                interjection.setSubject(structure[0])
                document.addComponent(interjection)
                
                sentence.setVerb(structure[1])
                sentence.setObject(structure[2])
                sentence.setFeature(Feature.TENSE, Tense.PRESENT)
                
            elif structure[0] == "Bravo":
                interjection = self.factory.createClause()
                interjection.setSubject(structure[0])
                document.addComponent(interjection)
                
                sentence.setSubject("tu")
                sentence.setVerb(structure[1])
                sentence.setObject(structure[2])
                sentence.setFeature(Feature.TENSE, Tense.PRESENT)
                
            else:
                interjection = self.factory.createClause()
                interjection.setSubject(structure[0])
                document.addComponent(interjection)
                
                sentence.setSubject("tu")
                sentence.setVerb(structure[1])
                sentence.setObject(structure[2])
                sentence.setFeature(Feature.TENSE, Tense.PRESENT)
            
        else:
            sentence = self.factory.createClause()
            
            structures = [
                ("No", "essere", "sbagliato"),
                ("Purtroppo", "sbagliare", ""),
                ("Mi dispiace", "essere", "non corretto")
            ]
            
            structure = random.choice(structures)
            
            if structure[0] == "No":
                interjection = self.factory.createClause()
                interjection.setSubject(structure[0])
                document.addComponent(interjection)
                
                sentence.setVerb(structure[1])
                sentence.setObject(structure[2])
                sentence.setFeature(Feature.TENSE, Tense.PRESENT)
                
            elif structure[0] == "Purtroppo":
                sentence.addPreModifier(structure[0])
                
                sentence.setSubject("tu")
                sentence.setVerb(structure[1])
                sentence.setFeature(Feature.TENSE, Tense.PAST)
                
            else:
                interjection = self.factory.createClause()
                interjection.setSubject(structure[0])
                document.addComponent(interjection)
                
                sentence.setVerb(structure[1])
                sentence.setObject(structure[2])
                sentence.setFeature(Feature.TENSE, Tense.PRESENT)
                sentence.setFeature(Feature.NEGATED, True)
        
        document.addComponent(sentence)
        
        realized_text = self.realiser.realise(document).getRealisation()
        
        return realized_text


if __name__ == "__main__":
    nlg = NLG("questions")
    
    print("\n=== DOMANDE DA TEMPLATE (questions.txt) ===")
    for i in range(5):
        print(f"{i+1}. {nlg.generate_question()}")
    
    print("\n=== DOMANDE GENERATE CON SIMPLENLG (Knowledge Base) ===")
    categories = ['biography', 'characteristics', 'adventures', 'facts']
    for category in categories:
        print(f"\n--- Categoria: {category.upper()} ---")
        for i in range(3):
            question = nlg.generate_from_knowledge_base(category, correct=True)
            print(f"✅ {question}")
            question = nlg.generate_from_knowledge_base(category, correct=False)
            print(f"❌ {question}")
    
    print("\n=== DOMANDE CASUALI MISTE ===")
    for i in range(10):
        question = nlg.create_simple_question()
        print(f"{i+1}. {question}")
    
    print("\n=== RISPOSTE POSITIVE ===")
    for i in range(3):
        print(f"{i+1}. {nlg.generate_answer(positive=True)}")
    
    print("\n=== RISPOSTE NEGATIVE ===")
    for i in range(3):
        print(f"{i+1}. {nlg.generate_answer(positive=False)}")
