import spacy
from questions_list import answers_list


class Analysis:
    def __init__(self, text):
        self.text = text
        self.nlp = spacy.load("it_core_news_md")
        self.doc = self.nlp(self.text)

    def get_dependecies(self):
        dict = {}
        for token in self.doc:
            dict[token.text] = token.dep_, token.pos_, token.head.text, token.morph
        return dict

    def check_for_answer(self):
        found = []
        answers_words_list = [answer.split() for answer in answers_list]
        for token in self.doc:
            for answwer_word in answers_words_list:
                if token.text == answwer_word[0]:
                    if len(answwer_word) == 1:
                        found.append(token.text)
                    elif token.i == len(self.doc) - 1 and len(answwer_word) > 1:
                        found.append(None)
                    else:
                        found.append(
                            self.scan_neighbour_tokens(token, answwer_word)
                        )
        found = [x for x in found if x is not None]
        return found

    def scan_neighbour_tokens(self, token, answwer_word):
        for i in range(1, len(answwer_word)):
            if token.i + i == len(self.doc) and len(answwer_word) > 1:
                return None
            if token.nbor(i).text != answwer_word[i]:
                return None
        return " ".join(answwer_word)

    def check_positivity(self):
        self.positivity = True
        for token in self.doc:
            if "Neg" in token.morph.get("Polarity") or token.text == "no":
                self.positivity = False
        return self.positivity

    def number_of_answer(self):
        return len(self.check_for_answer())


if __name__ == "__main__":
    analysis = Analysis("arc standard e eisner sono algoritmi per il parsing delle dipendenze sintattiche")
    print(analysis.text)
    print("\n")
    dependencies = analysis.get_dependecies()
    for key, value in dependencies.items():
        print(f"{key}: {value}")
    print("\n")
    print(f"Found Answers: {analysis.check_for_answer()}")
    print(f"Positivity: {analysis.check_positivity()}")
    print(f"Number of Answers: {analysis.number_of_answer()}")
