class Question:
    def __init__(self, text, answers):
        self.text = text
        self.answers = answers

    def __str__(self):
        return f'{self.text}\n\tCorrect Answers: {", ".join(self.answers)}'

    def get_text(self):
        return self.text

    def get_answers(self):
        return self.answers


if __name__ == "__main__":
    question = Question(
        "In quali luoghi è ambientato Tomb Raider II?", 
        ["Grande Muraglia Cinese","Venezia","Tibet","Piattaforma Petrolifera"]
    )
    print(question)
    print(question.get_text())
    print(question.get_answers())