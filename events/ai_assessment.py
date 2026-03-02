import random
import numpy as np
from .models import EventAssessment, Question, QuestionOption, NumericalAnswer, StudentAnswer


def generate_ai_assessment(event, title, description, due_date):
    assessment = EventAssessment(
        event=event,
        title=title,
        description=description,
        due_date=due_date,
        total_marks=10,
        is_ai_generated=True,
        passing_score=3,
    )
    assessment.save()

    keywords = extract_keywords(event)
    create_mcq_questions(assessment, keywords, count=6)
    create_msq_questions(assessment, keywords, count=2)
    create_nat_questions(assessment, keywords, count=2)

    return assessment


def extract_keywords(event):
    event_text = f"{event.event_name} {event.title} {event.about}"
    common_words = {'and', 'the', 'is', 'in', 'to', 'of', 'for', 'a', 'an', 'on', 'with'}
    words = event_text.lower().split()
    keywords = [w for w in words if w not in common_words and len(w) > 3]
    return list(set(keywords)) or ['event', 'technology', 'learning']


def create_mcq_questions(assessment, keywords, count=6):
    templates = [
        "What is the main focus of {keyword}?",
        "Which of the following best describes {keyword}?",
        "What is the primary purpose of {keyword}?",
        "Which concept is most closely related to {keyword}?",
        "In the context of this event, what does {keyword} refer to?",
        "What is the significance of {keyword} in this event?",
        "Which of these is a characteristic of {keyword}?",
        "How does {keyword} contribute to the event's objectives?",
    ]

    for i in range(count):
        keyword = random.choice(keywords)
        question_text = random.choice(templates).format(keyword=keyword)
        question = Question(
            assessment=assessment,
            question_text=question_text,
            question_type='MCQ',
            marks=1,
        )
        question.save()

        QuestionOption(question=question, option_text=f"The correct definition of {keyword}", is_correct=True).save()
        for j in range(3):
            QuestionOption(question=question, option_text=f"Incorrect definition {j+1} of {keyword}", is_correct=False).save()


def create_msq_questions(assessment, keywords, count=2):
    templates = [
        "Which of the following are related to {keyword}? (Select all that apply)",
        "Select all concepts that are associated with {keyword}.",
        "Which of these characteristics apply to {keyword}? (Select all that apply)",
        "Identify all elements that are part of {keyword}.",
    ]

    for i in range(count):
        keyword = random.choice(keywords)
        question_text = random.choice(templates).format(keyword=keyword)
        question = Question(
            assessment=assessment,
            question_text=question_text,
            question_type='MSQ',
            marks=1,
        )
        question.save()

        num_correct = random.randint(2, 3)
        for j in range(num_correct):
            QuestionOption(question=question, option_text=f"Correct aspect {j+1} of {keyword}", is_correct=True).save()
        for j in range(5 - num_correct):
            QuestionOption(question=question, option_text=f"Incorrect aspect {j+1} of {keyword}", is_correct=False).save()


def create_nat_questions(assessment, keywords, count=2):
    templates = [
        "How many key components are there in {keyword}?",
        "What is the numerical value associated with {keyword}?",
        "What is the approximate percentage of {keyword} in the event?",
        "If {keyword} has a value of X, what is X/2?",
    ]

    for i in range(count):
        keyword = random.choice(keywords)
        question_text = random.choice(templates).format(keyword=keyword)
        question = Question(
            assessment=assessment,
            question_text=question_text,
            question_type='NAT',
            marks=1,
        )
        question.save()

        correct_answer = round(random.uniform(1, 10), 1)
        NumericalAnswer(question=question, correct_answer=correct_answer, tolerance=0.1).save()


def evaluate_student_submission(submission):
    assessment = submission.assessment
    questions = list(Question.objects(assessment=assessment))
    total_score = 0

    for question in questions:
        student_answer = StudentAnswer.objects(submission=submission, question=question).first()
        if not student_answer:
            continue

        is_correct = False

        if question.question_type == 'MCQ':
            selected = list(QuestionOption.objects(id__in=student_answer.selected_option_ids))
            if len(selected) == 1 and selected[0].is_correct:
                is_correct = True
                total_score += question.marks

        elif question.question_type == 'MSQ':
            selected = list(QuestionOption.objects(id__in=student_answer.selected_option_ids))
            correct_opts = list(QuestionOption.objects(question=question, is_correct=True))
            if (len(selected) == len(correct_opts) and all(o.is_correct for o in selected)):
                is_correct = True
                total_score += question.marks

        elif question.question_type == 'NAT':
            if student_answer.numerical_value is not None:
                num_ans = NumericalAnswer.objects(question=question).first()
                if num_ans and abs(student_answer.numerical_value - num_ans.correct_answer) <= num_ans.tolerance:
                    is_correct = True
                    total_score += question.marks

        student_answer.is_correct = is_correct
        student_answer.save()

    submission.score = total_score
    submission.is_ai_graded = True
    submission.save()
    return total_score
