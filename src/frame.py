from questions_list import *


class Frame:
    def __init__(self, target_question, current_answers=None):
        if current_answers is None:
            current_answers = []
        self.target_question = target_question
        self.current_answer = set(current_answers)
        self.is_completed = False

    def __str__(self):
        return f"{self.target_question}\n\tCurrent answer: {', '.join(self.current_answer)}"

    def get_target_question(self):
        return self.target_question

    def get_target_answer(self):
        answers = self.get_target_question().get_answers()
        result = []
        for answer in answers:
            result.append(answer.lower())
        return result

    def get_current_answers(self):
        return self.current_answer

    def check_if_complete(self):
        if self.current_answer == set(self.get_target_answer()):
            self.is_completed = True
        return self.is_completed

    def add_answer(self, answers):
        answers = set(answers)
        for answer in answers:
            self.check_casefold_and_add(answer)

    def check_casefold_and_add(self, answer):
        found = False
        for target_answer in self.target_question.get_answers():
            if answer.casefold() == target_answer.casefold():
                self.current_answer.add(answer.lower())
                found = True
        if not found:
            print(f"Wrong answer: {answer}")


if __name__ == "__main__":
    frame = Frame(question2)
    print(frame)
    frame.add_answer(["Wimbledon","Londra"])
    print(frame)
    frame.add_answer(["Scozia"])
    print(frame)
    frame.add_answer(["Galles"])
    print(frame)
    frame.add_answer(
        [
            "Inghilterra"
        ]
    )
    print(frame)
    print(f"Is completed: {frame.check_if_complete()}")
