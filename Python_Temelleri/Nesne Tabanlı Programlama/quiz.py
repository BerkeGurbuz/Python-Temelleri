#Question
class Question:
    def __init__(self, text, choices, answer):
        self.text = text
        self.choices = choices
        self.answer = answer

    def checkanswer(self,answer):
        return self.answer == answer

#Quiz
class Quiz:
    def __init__(self,question):
        self.question = question
        self.score = 0
        self.questionindex = 0

    def getquestion(self):
        return self.question[self.questionindex]
    
    def displayquestion(self):
        question = self.getquestion()

        print(f'Soru {self.questionindex + 1} : {question.text}')

        for q in question.choices:
            print('-' + q)

        answer = input('cevap: ')
        print(question.checkanswer(answer))
        self.guess(answer)
        self.loadquestion()

    def guess(self,answer):
        question = self.getquestion()

        if question.checkanswer(answer):
            self.score += 1
        self.questionindex += 1

    def loadquestion(self):
        if len(self.question) == self.questionindex:
            self.showscore()

        else:
            self.displayprogress()
            self.displayquestion()

    def showscore(self):
        print('Score: ', self.score)

    def displayprogress(self):
        questionnumber = self.questionindex + 1
        totalquestion = len(self.question)

        if questionnumber <= totalquestion:
            print(f'Question {questionnumber} of {totalquestion}'.center(100,'*'))

        else:
            print('Quiz over.')


q1 = Question('En iyi programlama dili dili hangisidir?', ['C#','python','java','javascript'], 'python')
q2 = Question('En popüler programlama dili dili hangisidir?', ['C#','python','java','javascript'], 'python')  
q3 = Question('En çok kazandıran programlama dili dili hangisidir?', ['C#','python','java','javascript'], 'python')
questions = [q1,q2,q3]

quiz = Quiz(questions)

quiz.loadquestion()



# print(q1.checkanswer('python'))
# print(q3.checkanswer('java'))

