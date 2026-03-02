from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from bson import ObjectId
from bson.errors import InvalidId
import uuid
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from io import BytesIO
import json

from .models import (
    Event, EventAssessment, AssessmentSubmission, EventSchedule,
    EventRegistration, StudentAnswer, EventFeedback, EventMaterial,
    Question, QuestionOption, NumericalAnswer,
)
from users.models import CustomUser
from users.views import login_required_mongo as login_required


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_404(model, **kwargs):
    """MongoEngine equivalent of get_object_or_404."""
    try:
        obj = model.objects(**kwargs).first()
    except Exception:
        raise Http404()
    if obj is None:
        raise Http404()
    return obj


def _same_user(a, b):
    """Compare two MongoEngine document references by id."""
    return str(getattr(a, 'id', a)) == str(getattr(b, 'id', b))


def _resolve_event(event_id):
    """Look up an Event by its custom event_id string or MongoDB ObjectId."""
    event = Event.objects(event_id=event_id).first()
    if event:
        return event
    try:
        return Event.objects(id=ObjectId(event_id)).first()
    except (InvalidId, Exception):
        return None


def _get_event_or_404(event_id):
    event = _resolve_event(event_id)
    if not event:
        raise Http404()
    return event


def _get_by_id_or_404(model, obj_id):
    """Fetch a document by its MongoDB ObjectId string."""
    try:
        return _get_or_404(model, id=ObjectId(obj_id))
    except (InvalidId, Exception):
        raise Http404()


# ─── Event CRUD ───────────────────────────────────────────────────────────────

@login_required
def create_event(request, event_id=None):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Only event coordinators can create events.')
        return redirect('dashboard')

    event = None
    if event_id:
        event = _get_event_or_404(event_id)
        if not _same_user(event.coordinator, request.user):
            messages.error(request, 'You can only edit your own events.')
            return redirect('my_events')

    if request.method == 'POST':
        try:
            if event:
                event.name = request.POST['event_name']
                event.event_name = request.POST['event_name']
                event.about = request.POST['about']
                event.title = request.POST['title']
                event.date = request.POST['date']
                event.time = request.POST['time']
                event.expected_attendees = int(request.POST['expected_attendees'])
                event.mode = request.POST['mode']
                event.venue = request.POST.get('venue')
                event.meeting_link = request.POST.get('meeting_link')
                event.budget = request.POST['budget']
                event.registration_fee = request.POST['registration_fee']
                event.refreshment = request.POST['refreshment']
                event.renumeration = request.POST['renumeration']
                event.honorarium = request.POST['honorarium']
                event.other_requirements = request.POST.get('other_requirements', '')
            else:
                import datetime, random, string
                current_year = datetime.datetime.now().year
                random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                new_event_id = f'EVT-{current_year}-{random_suffix}'

                event = Event(
                    name=request.POST['event_name'],
                    coordinator=request.user,
                    department=request.user.department,
                    event_name=request.POST['event_name'],
                    about=request.POST['about'],
                    title=request.POST['title'],
                    date=request.POST['date'],
                    time=request.POST['time'],
                    expected_attendees=int(request.POST['expected_attendees']),
                    mode=request.POST['mode'],
                    venue=request.POST.get('venue'),
                    meeting_link=request.POST.get('meeting_link'),
                    budget=request.POST['budget'],
                    registration_fee=request.POST['registration_fee'],
                    refreshment=request.POST['refreshment'],
                    renumeration=request.POST['renumeration'],
                    honorarium=request.POST['honorarium'],
                    other_requirements=request.POST.get('other_requirements', ''),
                    event_id=new_event_id,
                )
            event.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Event updated successfully!' if event_id else 'Event created successfully!',
                    'event_id': event.event_id,
                })

            if event_id:
                messages.success(request, 'Event updated successfully!')
            else:
                messages.success(request, 'Event created successfully! Waiting for approval.')
            return redirect('my_events')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
            messages.error(request, f'Error creating event: {str(e)}')

    context = {'event': event} if event else {}
    return render(request, 'events/create_event.html', context)


@login_required
def my_events(request):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    events = list(Event.objects(coordinator=request.user).order_by('-created_at'))
    context = {
        'events': events,
        'pending_count': sum(1 for e in events if e.status == 'PENDING'),
        'approved_count': sum(1 for e in events if e.status in ('HOD_APPROVED', 'PRINCIPAL_APPROVED')),
        'rejected_count': sum(1 for e in events if e.status in ('HOD_REJECTED', 'PRINCIPAL_REJECTED')),
    }
    return render(request, 'events/my_events.html', context)


@login_required
def event_detail(request, event_id):
    event = _get_event_or_404(event_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'events/event_detail_modal.html', {'event': event})
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def event_detail_api(request, event_id):
    event = _get_event_or_404(event_id)
    return JsonResponse({
        'event_id': event.event_id,
        'event_name': event.event_name,
        'title': event.title,
        'department': event.get_department_display(),
        'coordinator': event.coordinator.username,
        'date': str(event.date),
        'time': str(event.time),
        'mode': event.get_mode_display(),
        'venue': event.venue,
        'expected_attendees': event.expected_attendees,
        'status': event.status,
    })


@login_required
def online_events(request):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    registrations = list(EventRegistration.objects(student=request.user))
    online_regs = [r for r in registrations if r.event and r.event.mode == 'ONLINE']
    return render(request, 'events/online_events.html', {'registered_online_events': online_regs})


# ─── Approval ─────────────────────────────────────────────────────────────────

@login_required
def event_approval_list(request):
    if request.user.role not in ('HOD', 'PRINCIPAL'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    if request.user.role == 'HOD':
        return redirect('hod_pending_events')
    return redirect('principal_pending_events')


@login_required
@require_http_methods(['POST'])
def approve_event(request, event_id):
    if request.user.role not in ('HOD', 'PRINCIPAL'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Access denied.'})
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    event = _get_event_or_404(event_id)
    success, message = False, ''

    if request.user.role == 'HOD':
        if event.status != 'PENDING':
            message = 'This event cannot be approved.'
        else:
            event.status = 'HOD_APPROVED'
            event.hod_approval_date = timezone.now()
            event.save()
            success, message = True, 'Event approved and sent to Principal.'
    elif request.user.role == 'PRINCIPAL':
        if event.status != 'HOD_APPROVED':
            message = 'This event cannot be approved.'
        else:
            event.status = 'PRINCIPAL_APPROVED'
            event.principal_approval_date = timezone.now()
            event.save()
            success, message = True, 'Event approved successfully.'

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': success, 'message': message})

    return redirect('hod_pending_events' if request.user.role == 'HOD' else 'principal_pending_events')


@login_required
@require_http_methods(['POST'])
def reject_event(request, event_id):
    if request.user.role not in ('HOD', 'PRINCIPAL'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Access denied.'})
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    event = _get_event_or_404(event_id)
    success, message = False, ''

    if request.user.role == 'HOD':
        if event.status != 'PENDING':
            message = 'This event cannot be rejected.'
        else:
            event.status = 'HOD_REJECTED'
            event.save()
            success, message = True, 'Event has been rejected.'
    elif request.user.role == 'PRINCIPAL':
        if event.status != 'HOD_APPROVED':
            message = 'This event cannot be rejected.'
        else:
            event.status = 'PRINCIPAL_REJECTED'
            event.save()
            success, message = True, 'Event has been rejected.'

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': success, 'message': message})

    return redirect('hod_pending_events' if request.user.role == 'HOD' else 'principal_pending_events')


# ─── Analytics ────────────────────────────────────────────────────────────────

@login_required
def get_event_analytics(request, event_id):
    if request.user.role not in ('HOD', 'PRINCIPAL'):
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    event = _get_event_or_404(event_id)
    historical_events = list(Event.objects(
        status='PRINCIPAL_APPROVED',
        department=event.department,
        event_id__ne=event.event_id,
    ))

    if not historical_events:
        return JsonResponse({
            'success': True,
            'prediction': 'Not enough historical data',
            'message': 'Unable to make prediction due to insufficient historical data.',
        })

    try:
        from .utils import analyze_event_budget_name
        analysis_result = analyze_event_budget_name(
            event_name=event.event_name,
            event_budget=float(event.budget),
            historical_events=historical_events,
        )
        return JsonResponse({
            'success': True,
            'prediction': analysis_result['recommendation'],
            'confidence': analysis_result['confidence'],
            'name_similarity': analysis_result['name_similarity'],
            'budget_analysis': analysis_result['budget_analysis'],
            'message': 'Analysis based on event name and budget similarity.',
        })
    except Exception as e:
        try:
            limited = historical_events[:50]
            data = [{
                'budget': float(e.budget),
                'expected_attendees': e.expected_attendees,
                'registration_fee': float(e.registration_fee),
                'success': True,
            } for e in limited]
            df = pd.DataFrame(data)
            X = df[['budget', 'expected_attendees', 'registration_fee']]
            y = df['success']
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model = RandomForestClassifier(n_estimators=50)
            model.fit(X_scaled, y)
            current_data = np.array([[float(event.budget), event.expected_attendees, float(event.registration_fee)]])
            prediction = model.predict_proba(scaler.transform(current_data))[0]
            prob = prediction[1] * 100 if len(prediction) > 1 else prediction[0] * 100
            budgets = [float(e.budget) for e in limited]
            avg_budget = sum(budgets) / len(budgets) if budgets else 0
            recommendation = (
                'Strongly Recommended' if prob > 85 else
                'Recommended' if prob > 70 else
                'Needs Review' if prob > 50 else
                'Not Recommended'
            )
            return JsonResponse({
                'success': True,
                'prediction': recommendation,
                'confidence': prob,
                'avg_budget': avg_budget,
                'current_budget': float(event.budget),
                'message': 'Fallback analytics model.',
            })
        except Exception as fallback_err:
            return JsonResponse({'success': False, 'message': str(fallback_err)})


# ─── Assessments ──────────────────────────────────────────────────────────────

@login_required
def create_assessment(request):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Only event coordinators can create assessments.')
        return redirect('dashboard')

    events = list(Event.objects(coordinator=request.user, status='PRINCIPAL_APPROVED'))

    if request.method == 'POST':
        try:
            event = _get_by_id_or_404(Event, request.POST['event'])
            title = request.POST['title']
            description = request.POST['description']
            due_date = request.POST['due_date']
            is_ai_generated = 'is_ai_generated' in request.POST

            if is_ai_generated:
                from .ai_assessment import generate_ai_assessment
                assessment = generate_ai_assessment(event, title, description, due_date)
                messages.success(request, 'AI Assessment with 10 questions created successfully!')
            else:
                passing_score = int(request.POST.get('passing_score', 3))
                assessment = EventAssessment(
                    event=event,
                    title=title,
                    description=description,
                    due_date=due_date,
                    total_marks=10,
                    passing_score=passing_score,
                )
                assessment.save()

                for i in range(10):
                    question_text = request.POST.get(f'question_text_{i}')
                    question_type = request.POST.get(f'question_type_{i}')
                    if question_text and question_type:
                        question = Question(
                            assessment=assessment,
                            question_text=question_text,
                            question_type=question_type,
                            marks=1,
                        )
                        question.save()

                        if question_type in ('MCQ', 'MSQ'):
                            if question_type == 'MCQ':
                                correct_options = [request.POST.get(f'correct_option_{i}', '')]
                            else:
                                correct_options = request.POST.getlist(f'correct_options_{i}')

                            for j in range(4):
                                opt_text = request.POST.get(f'option_text_{i}_{j}')
                                if opt_text:
                                    QuestionOption(
                                        question=question,
                                        option_text=opt_text,
                                        is_correct=str(j) in correct_options,
                                    ).save()
                        elif question_type == 'NAT':
                            correct_answer = request.POST.get(f'correct_answer_{i}')
                            tolerance = request.POST.get(f'tolerance_{i}', 0.1)
                            if correct_answer:
                                NumericalAnswer(
                                    question=question,
                                    correct_answer=float(correct_answer),
                                    tolerance=float(tolerance),
                                ).save()

                messages.success(request, 'Assessment created successfully!')

            return redirect('assessment_list')
        except Exception as e:
            messages.error(request, f'Error creating assessment: {str(e)}')

    return render(request, 'events/create_assessment.html', {'events': events})


@login_required
def assessment_list(request):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    coord_events = Event.objects(coordinator=request.user)
    event_ids = [e.id for e in coord_events]
    assessments = list(EventAssessment.objects(event__in=event_ids))
    return render(request, 'events/assessment_list.html', {'assessments': assessments})


@login_required
def student_assessment_list(request):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    reg_event_ids = [r.event.id for r in EventRegistration.objects(student=request.user) if r.event]
    assessments = list(EventAssessment.objects(event__in=reg_event_ids))
    now = timezone.now()
    return render(request, 'events/student_assessment_list.html', {
        'assessments': assessments,
        'now': now,
    })


@login_required
def submit_assessment(request, assessment_id):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    assessment = _get_by_id_or_404(EventAssessment, assessment_id)

    if assessment.due_date < timezone.now():
        messages.error(request, 'Assessment submission deadline has passed.')
        return redirect('student_assessment_list')

    questions = list(Question.objects(assessment=assessment))
    has_questions = len(questions) > 0

    if request.method == 'POST':
        try:
            existing = AssessmentSubmission.objects(
                assessment=assessment, student=request.user
            ).first()

            if existing:
                submission = existing
                if not has_questions and request.FILES.get('submission_file'):
                    submission.submission_file = str(request.FILES['submission_file'])
                    submission.save()
            else:
                submission = AssessmentSubmission(
                    assessment=assessment,
                    student=request.user,
                )
                if not has_questions and request.FILES.get('submission_file'):
                    submission.submission_file = str(request.FILES['submission_file'])
                submission.save()

            if has_questions:
                StudentAnswer.objects(submission=submission).delete()

                for question in questions:
                    answer = StudentAnswer(submission=submission, question=question)

                    if question.question_type == 'MCQ':
                        option_id = request.POST.get(f'question_{str(question.id)}')
                        if option_id:
                            try:
                                opt = QuestionOption.objects(id=ObjectId(option_id)).first()
                                if opt:
                                    answer.selected_option_ids = [opt.id]
                            except Exception:
                                pass

                    elif question.question_type == 'MSQ':
                        option_ids = request.POST.getlist(f'question_{str(question.id)}')
                        valid_ids = []
                        for oid in option_ids:
                            try:
                                opt = QuestionOption.objects(id=ObjectId(oid)).first()
                                if opt:
                                    valid_ids.append(opt.id)
                            except Exception:
                                pass
                        answer.selected_option_ids = valid_ids

                    elif question.question_type == 'NAT':
                        val = request.POST.get(f'question_{str(question.id)}')
                        if val:
                            try:
                                answer.numerical_value = float(val)
                            except ValueError:
                                pass

                    answer.save()

                from .ai_assessment import evaluate_student_submission
                score = evaluate_student_submission(submission)
                passed = score >= assessment.passing_score

                if passed:
                    from .utils import check_and_generate_certificates
                    check_and_generate_certificates(assessment.event)

                return redirect('assessment_result', submission_id=str(submission.id))
            else:
                messages.success(request, 'Assessment submitted successfully!')
                return redirect('student_assessment_list')

        except Exception as e:
            messages.error(request, f'Error submitting assessment: {str(e)}')

    return render(request, 'events/submit_assessment.html', {
        'assessment': assessment,
        'has_questions': has_questions,
        'questions': questions,
    })


@login_required
def assessment_result(request, submission_id):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    submission = _get_by_id_or_404(AssessmentSubmission, submission_id)
    assessment = submission.assessment

    if not _same_user(submission.student, request.user):
        messages.error(request, 'Access denied.')
        return redirect('student_assessment_list')

    passed = (submission.score or 0) >= assessment.passing_score
    has_certificate = EventRegistration.objects(
        event=assessment.event, student=request.user, certificate_generated=True
    ).first() is not None

    questions = list(Question.objects(assessment=assessment))
    answers = {}
    for question in questions:
        ans = StudentAnswer.objects(submission=submission, question=question).first()
        if ans:
            answers[str(question.id)] = ans

    context = {
        'submission': submission,
        'assessment': assessment,
        'passed': passed,
        'has_certificate': has_certificate,
        'questions': questions,
        'answers': answers,
    }
    return render(request, 'events/assessment_result.html', context)


@login_required
def grade_assessment(request, submission_id):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Only event coordinators can grade assessments.')
        return redirect('dashboard')

    submission = _get_by_id_or_404(AssessmentSubmission, submission_id)

    if not _same_user(submission.assessment.event.coordinator, request.user):
        messages.error(request, 'You can only grade assessments for your events.')
        return redirect('assessment_list')

    if request.method == 'POST':
        try:
            submission.score = int(request.POST['score'])
            submission.save()
            messages.success(request, 'Assessment graded successfully!')
            from .utils import check_and_generate_certificates
            check_and_generate_certificates(submission.assessment.event)
            return redirect('assessment_submissions', assessment_id=str(submission.assessment.id))
        except Exception as e:
            messages.error(request, f'Error grading assessment: {str(e)}')

    return render(request, 'events/grade_assessment.html', {'submission': submission})


@login_required
def assessment_detail(request, assessment_id):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    assessment = _get_by_id_or_404(EventAssessment, assessment_id)
    if not _same_user(assessment.event.coordinator, request.user):
        messages.error(request, 'You can only view assessments for your events.')
        return redirect('assessment_list')

    return render(request, 'events/assessment_detail.html', {'assessment': assessment})


@login_required
def assessment_submissions(request, assessment_id):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    assessment = _get_by_id_or_404(EventAssessment, assessment_id)
    if not _same_user(assessment.event.coordinator, request.user):
        messages.error(request, 'You can only view submissions for your assessments.')
        return redirect('assessment_list')

    submissions = list(AssessmentSubmission.objects(assessment=assessment).order_by('-submitted_at'))
    return render(request, 'events/assessment_submissions.html', {
        'assessment': assessment,
        'submissions': submissions,
    })


@login_required
def edit_assessment(request, assessment_id):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    assessment = _get_by_id_or_404(EventAssessment, assessment_id)
    if not _same_user(assessment.event.coordinator, request.user):
        messages.error(request, 'You can only edit assessments for your events.')
        return redirect('assessment_list')

    events = list(Event.objects(coordinator=request.user, status='PRINCIPAL_APPROVED'))

    if request.method == 'POST':
        try:
            assessment.title = request.POST['title']
            assessment.description = request.POST['description']
            assessment.due_date = request.POST['due_date']
            assessment.total_marks = int(request.POST['total_marks'])
            assessment.save()
            messages.success(request, 'Assessment updated successfully!')
            return redirect('assessment_list')
        except Exception as e:
            messages.error(request, f'Error updating assessment: {str(e)}')

    return render(request, 'events/edit_assessment.html', {'assessment': assessment, 'events': events})


@login_required
def delete_assessment(request, assessment_id):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    assessment = _get_by_id_or_404(EventAssessment, assessment_id)
    if not _same_user(assessment.event.coordinator, request.user):
        messages.error(request, 'You can only delete assessments for your events.')
        return redirect('assessment_list')

    if request.method == 'POST':
        try:
            assessment.delete()
            messages.success(request, 'Assessment deleted successfully!')
            return redirect('assessment_list')
        except Exception as e:
            messages.error(request, f'Error deleting assessment: {str(e)}')

    return render(request, 'events/delete_assessment.html', {'assessment': assessment})


# ─── Students ─────────────────────────────────────────────────────────────────

@login_required
def available_events(request):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    today = timezone.now().date()
    events = list(Event.objects(status='PRINCIPAL_APPROVED', date__gte=today).order_by('date'))

    reg_event_ids = set(
        str(r.event.id)
        for r in EventRegistration.objects(student=request.user)
        if r.event
    )
    registered_events = [e for e in events if str(e.id) in reg_event_ids]

    return render(request, 'events/available_events.html', {
        'events': events,
        'registered_events': registered_events,
    })


@login_required
def register_event(request, event_id):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Only students can register for events.')
        return redirect('dashboard')

    event = _get_event_or_404(event_id)

    if event.status != 'PRINCIPAL_APPROVED':
        messages.error(request, 'This event is not available for registration.')
        return redirect('available_events')

    if EventRegistration.objects(event=event, student=request.user).first():
        messages.info(request, 'You are already registered for this event.')
        return redirect('available_events')

    try:
        EventRegistration(event=event, student=request.user).save()
        messages.success(request, f'Successfully registered for {event.event_name}!')
    except Exception as e:
        messages.error(request, f'Error registering for event: {str(e)}')

    return redirect('available_events')


@login_required
def certificates(request):
    if request.user.role == 'EVENT_COORDINATOR':
        events = list(Event.objects(coordinator=request.user, status='PRINCIPAL_APPROVED').order_by('-date'))
        return render(request, 'events/certificates.html', {'events': events})
    elif request.user.role == 'STUDENT':
        reg_event_ids = [r.event.id for r in EventRegistration.objects(student=request.user) if r.event]
        events = list(Event.objects(id__in=reg_event_ids, status='PRINCIPAL_APPROVED').order_by('-date'))
        return render(request, 'events/certificates.html', {'events': events})
    messages.error(request, 'Access denied.')
    return redirect('dashboard')


# ─── Feedback ─────────────────────────────────────────────────────────────────

@login_required
def submit_feedback(request, event_id):
    if request.user.role != 'STUDENT':
        messages.error(request, 'Only students can submit feedback.')
        return redirect('dashboard')

    event = _get_by_id_or_404(Event, event_id)
    registration = EventRegistration.objects(event=event, student=request.user).first()
    if not registration:
        raise Http404()

    if not registration.certificate_generated:
        messages.error(request, 'You can only provide feedback after receiving a certificate.')
        return redirect('certificates')

    if EventFeedback.objects(event=event, student=request.user).first():
        messages.info(request, 'You have already submitted feedback for this event.')
        return redirect('certificates')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
            feedback_text = request.POST.get('feedback_text', '').strip()
            if not rating or not feedback_text:
                messages.error(request, 'Please provide both rating and feedback.')
                return render(request, 'events/submit_feedback.html', {'event': event})
            EventFeedback(event=event, student=request.user, rating=rating, feedback_text=feedback_text).save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('certificates')
        except Exception as e:
            messages.error(request, f'Error submitting feedback: {str(e)}')

    return render(request, 'events/submit_feedback.html', {'event': event})


@login_required
def event_feedback_report(request, event_id):
    if request.user.role not in ('EVENT_COORDINATOR', 'HOD'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    event = _get_by_id_or_404(Event, event_id)

    if request.user.role == 'EVENT_COORDINATOR' and not _same_user(event.coordinator, request.user):
        messages.error(request, 'You can only view feedback for your events.')
        return redirect('my_events')

    if request.user.role == 'HOD' and event.department != request.user.department:
        messages.error(request, 'You can only view feedback for events in your department.')
        return redirect('dashboard')

    feedbacks = list(EventFeedback.objects(event=event).order_by('-submitted_date'))
    feedback_count = len(feedbacks)
    avg_rating = (sum(f.rating for f in feedbacks) / feedback_count) if feedback_count else 0
    total_participants = EventRegistration.objects(event=event).count()
    feedback_rate = (feedback_count / total_participants * 100) if total_participants else 0

    def _cnt(rating):
        return sum(1 for f in feedbacks if f.rating == rating)

    counts = {r: _cnt(r) for r in range(1, 6)}
    percents = {r: (counts[r] / feedback_count * 100) if feedback_count else 0 for r in range(1, 6)}

    context = {
        'event': event,
        'feedbacks': feedbacks,
        'feedback_count': feedback_count,
        'avg_rating': round(avg_rating, 1),
        'feedback_rate': round(feedback_rate, 1),
        **{f'rating_{r}_count': counts[r] for r in range(1, 6)},
        **{f'rating_{r}_percent': round(percents[r], 1) for r in range(1, 6)},
    }
    return render(request, 'events/feedback_report.html', context)


# ─── HOD views ────────────────────────────────────────────────────────────────

@login_required
def hod_pending_events(request):
    if request.user.role != 'HOD':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    pending_events = list(Event.objects(department=request.user.department, status='PENDING').order_by('-created_at'))
    return render(request, 'events/hod_pending_events.html', {'pending_events': pending_events})


@login_required
def hod_approved_events(request):
    if request.user.role != 'HOD':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    approved_events = list(Event.objects(department=request.user.department, status='HOD_APPROVED').order_by('-created_at'))
    return render(request, 'events/hod_approved_events.html', {'approved_events': approved_events})


@login_required
def hod_rejected_events(request):
    if request.user.role != 'HOD':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    rejected_events = list(Event.objects(department=request.user.department, status='HOD_REJECTED').order_by('-created_at'))
    return render(request, 'events/hod_rejected_events.html', {'rejected_events': rejected_events})


# ─── Principal views ──────────────────────────────────────────────────────────

@login_required
def principal_pending_events(request):
    if request.user.role != 'PRINCIPAL':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    pending_events = list(Event.objects(status='HOD_APPROVED').order_by('-created_at'))
    return render(request, 'events/principal_pending_events.html', {'pending_events': pending_events})


@login_required
def principal_approved_events(request):
    if request.user.role != 'PRINCIPAL':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    approved_events = list(Event.objects(status='PRINCIPAL_APPROVED').order_by('-created_at'))
    return render(request, 'events/principal_approved_events.html', {'approved_events': approved_events})


@login_required
def principal_rejected_events(request):
    if request.user.role != 'PRINCIPAL':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    rejected_events = list(Event.objects(status='PRINCIPAL_REJECTED').order_by('-created_at'))
    return render(request, 'events/principal_rejected_events.html', {'rejected_events': rejected_events})


# ─── Analytics page ───────────────────────────────────────────────────────────

@login_required
def analytics(request):
    if request.user.role not in ('HOD', 'PRINCIPAL'):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.user.role == 'HOD':
        events = list(Event.objects(department=request.user.department))
    else:
        events = list(Event.objects())

    total_events = len(events)
    approved_events_count = sum(1 for e in events if e.status == 'PRINCIPAL_APPROVED')
    pending_events_count = sum(1 for e in events if e.status == 'PENDING')
    total_budget = sum(float(e.budget or 0) for e in events)

    from collections import defaultdict
    dept_event_count = defaultdict(int)
    dept_attendees = defaultdict(list)
    for e in events:
        dept_event_count[e.department] += 1
        if e.expected_attendees:
            dept_attendees[e.department].append(e.expected_attendees)

    dept_stats = [
        {
            'name': dict(CustomUser.DEPARTMENT_CHOICES).get(dept, dept) or 'Unknown',
            'count': cnt,
        }
        for dept, cnt in dept_event_count.items()
    ]

    event_ids = [e.id for e in events]
    assessments = list(EventAssessment.objects(event__in=event_ids))
    total_assessments = len(assessments)
    assessment_ids = [a.id for a in assessments]
    submissions = list(AssessmentSubmission.objects(assessment__in=assessment_ids))
    submission_rate = (len(submissions) / total_assessments * 100) if total_assessments else 0
    scores = [s.score for s in submissions if s.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    context = {
        'total_events': total_events,
        'approved_events': approved_events_count,
        'pending_events': pending_events_count,
        'total_budget': total_budget,
        'dept_stats': dept_stats,
        'dept_stats_json': json.dumps(dept_stats),
        'total_assessments': total_assessments,
        'submission_rate': round(submission_rate, 2),
        'avg_score': round(avg_score, 2),
    }
    return render(request, 'events/analytics.html', context)


# ─── Scheduler ────────────────────────────────────────────────────────────────

@login_required
def event_scheduler(request):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Only event coordinators can schedule events.')
        return redirect('dashboard')

    events = list(Event.objects(coordinator=request.user, status='PRINCIPAL_APPROVED', mode='ONLINE').order_by('-date'))
    event_ids = [e.id for e in events]
    event_schedules = list(EventSchedule.objects(event__in=event_ids).order_by('start_time'))

    if request.method == 'POST':
        try:
            event_pk = request.POST.get('event')
            event = _get_by_id_or_404(Event, event_pk)
            if not _same_user(event.coordinator, request.user) or event.mode != 'ONLINE':
                raise Http404()

            session_names = request.POST.getlist('session_name[]')
            start_times = request.POST.getlist('start_time[]')
            end_times = request.POST.getlist('end_time[]')
            meeting_link = request.POST.get('meeting_link')

            if meeting_link:
                event.meeting_link = meeting_link
                event.save()

            for i in range(len(session_names)):
                EventSchedule(
                    event=event,
                    session_name=session_names[i],
                    start_time=start_times[i],
                    end_time=end_times[i],
                ).save()

            messages.success(request, 'Online event schedule created successfully!')
            return redirect('event_scheduler')
        except Exception as e:
            messages.error(request, f'Error creating schedule: {str(e)}')

    return render(request, 'events/event_scheduler.html', {
        'events': events,
        'event_schedules': event_schedules,
    })


@login_required
@require_http_methods(['POST'])
def delete_schedule(request, schedule_id):
    if request.user.role != 'EVENT_COORDINATOR':
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    schedule = _get_by_id_or_404(EventSchedule, schedule_id)
    if not _same_user(schedule.event.coordinator, request.user):
        return JsonResponse({'success': False, 'message': 'You can only delete schedules for your events.'})

    try:
        schedule.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ─── Certificates & Participants ─────────────────────────────────────────────

@login_required
def event_participants(request, event_id):
    if request.user.role != 'EVENT_COORDINATOR':
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    event = _get_by_id_or_404(Event, event_id)
    if not _same_user(event.coordinator, request.user):
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    registrations = list(EventRegistration.objects(event=event))
    participants = [{
        'student_id': r.student.username,
        'name': r.student.get_full_name(),
        'email': r.student.email,
        'certificate_generated': r.certificate_generated,
    } for r in registrations]

    return JsonResponse({'success': True, 'participants': participants})


@login_required
@require_http_methods(['POST'])
def generate_certificates(request, event_id):
    if request.user.role != 'EVENT_COORDINATOR':
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    event = _get_by_id_or_404(Event, event_id)
    if not _same_user(event.coordinator, request.user):
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    registrations = list(EventRegistration.objects(event=event))
    if not registrations:
        return JsonResponse({'success': False, 'message': 'No participants found for this event.'})

    try:
        from .utils import generate_certificate
        count = 0
        for registration in registrations:
            if not registration.certificate_generated:
                certificate_url, _ = generate_certificate(event, registration.student)
                registration.certificate_url = certificate_url
                registration.certificate_generated = True
                registration.save()
                count += 1
        return JsonResponse({'success': True, 'message': f'Generated {count} certificates.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


# ─── Materials ────────────────────────────────────────────────────────────────

@login_required
def upload_material(request):
    if request.user.role != 'EVENT_COORDINATOR':
        messages.error(request, 'Only event coordinators can upload study materials.')
        return redirect('dashboard')

    events = list(Event.objects(coordinator=request.user, status='PRINCIPAL_APPROVED').order_by('-date'))

    if request.method == 'POST':
        try:
            event_pk = request.POST.get('event')
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            material_file = request.FILES.get('material_file')

            if not all([event_pk, title, material_file]):
                messages.error(request, 'Please fill all required fields.')
                return render(request, 'events/upload_material.html', {'events': events})

            event = _get_by_id_or_404(Event, event_pk)
            if not _same_user(event.coordinator, request.user):
                raise Http404()

            EventMaterial(
                event=event,
                title=title,
                description=description,
                file=str(material_file),
            ).save()

            messages.success(request, 'Study material uploaded successfully!')
            return redirect('upload_material')
        except Http404:
            raise
        except Exception as e:
            messages.error(request, f'Error uploading material: {str(e)}')

    return render(request, 'events/upload_material.html', {'events': events})


@login_required
def view_materials(request):
    if request.user.role == 'STUDENT':
        reg_event_ids = [r.event.id for r in EventRegistration.objects(student=request.user) if r.event]
        events = list(Event.objects(id__in=reg_event_ids, status='PRINCIPAL_APPROVED').order_by('-date'))
        for event in events:
            event._materials = list(EventMaterial.objects(event=event))
        return render(request, 'events/view_materials.html', {'registered_events': events})
    elif request.user.role == 'EVENT_COORDINATOR':
        events = list(Event.objects(coordinator=request.user, status='PRINCIPAL_APPROVED').order_by('-date'))
        for event in events:
            event._materials = list(EventMaterial.objects(event=event))
        return render(request, 'events/view_materials.html', {'registered_events': events})
    messages.error(request, 'Access denied.')
    return redirect('dashboard')
