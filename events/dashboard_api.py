from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Event, EventRegistration, EventAssessment, AssessmentSubmission, EventFeedback
from users.models import CustomUser
from users.views import login_required_mongo as login_required


@login_required
def get_coordinator_dashboard_data(request):
    if request.user.role != 'EVENT_COORDINATOR':
        return JsonResponse({'success': False, 'message': 'Access denied'})

    events = list(Event.objects(coordinator=request.user))
    my_events_count = len(events)
    approved_events_count = sum(1 for e in events if e.status == 'PRINCIPAL_APPROVED')
    pending_events_count = sum(1 for e in events if e.status in ('PENDING', 'HOD_APPROVED'))

    approved_events = [e for e in events if e.status == 'PRINCIPAL_APPROVED'][:5]
    event_participation = {}
    for event in approved_events:
        event_participation[event.event_name] = EventRegistration.objects(event=event).count()

    assessment_completion = {}
    for event in approved_events:
        assessments = list(EventAssessment.objects(event=event))
        if assessments:
            reg_count = EventRegistration.objects(event=event).count()
            total_possible = len(assessments) * reg_count
            if total_possible > 0:
                assessment_ids = [a.id for a in assessments]
                actual = AssessmentSubmission.objects(assessment__in=assessment_ids).count()
                assessment_completion[event.event_name] = round((actual / total_possible) * 100, 1)

    current_year = timezone.now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    event_timeline = [
        {'month': month, 'count': sum(1 for e in events if e.date and e.date.year == current_year and e.date.month == i)}
        for i, month in enumerate(months, 1)
    ]

    feedback_data = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}
    event_ids = [e.id for e in events]
    for fb in EventFeedback.objects(event__in=event_ids):
        if fb.rating >= 4:
            feedback_data['Excellent'] += 1
        elif fb.rating == 3:
            feedback_data['Good'] += 1
        elif fb.rating == 2:
            feedback_data['Average'] += 1
        else:
            feedback_data['Poor'] += 1

    return JsonResponse({
        'success': True,
        'myEvents': my_events_count,
        'approvedEvents': approved_events_count,
        'pendingEvents': pending_events_count,
        'eventParticipation': event_participation,
        'assessmentCompletion': assessment_completion,
        'eventTimeline': event_timeline,
        'eventFeedback': feedback_data,
    })


@login_required
def get_hod_dashboard_data(request):
    if request.user.role != 'HOD':
        return JsonResponse({'success': False, 'message': 'Access denied'})

    events = list(Event.objects(department=request.user.department))
    department_events_count = len(events)
    pending_approvals_count = sum(1 for e in events if e.status == 'PENDING')

    event_ids = [e.id for e in events]
    student_ids = set(
        str(r.student.id)
        for r in EventRegistration.objects(event__in=event_ids)
        if r.student
    )
    student_participation_count = len(student_ids)

    event_status = {
        'Pending': sum(1 for e in events if e.status == 'PENDING'),
        'HOD Approved': sum(1 for e in events if e.status == 'HOD_APPROVED'),
        'Principal Approved': sum(1 for e in events if e.status == 'PRINCIPAL_APPROVED'),
    }

    current_year = timezone.now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_events = [
        {'month': month, 'count': sum(1 for e in events if e.date and e.date.year == current_year and e.date.month == i)}
        for i, month in enumerate(months, 1)
    ]

    assessment_performance = {}
    for event in [e for e in events if e.status == 'PRINCIPAL_APPROVED'][:5]:
        assessment_ids = [a.id for a in EventAssessment.objects(event=event)]
        if assessment_ids:
            subs = list(AssessmentSubmission.objects(assessment__in=assessment_ids))
            if subs:
                scores = [s.score for s in subs if s.score is not None]
                if scores:
                    assessment_performance[event.event_name] = round(sum(scores) / len(scores), 1)

    event_modes = {
        'Online': sum(1 for e in events if e.mode == 'ONLINE'),
        'Offline': sum(1 for e in events if e.mode == 'OFFLINE'),
    }

    return JsonResponse({
        'success': True,
        'departmentEvents': department_events_count,
        'pendingApprovals': pending_approvals_count,
        'studentParticipation': student_participation_count,
        'eventStatus': event_status,
        'monthlyEvents': monthly_events,
        'assessmentPerformance': assessment_performance,
        'eventModes': event_modes,
    })


@login_required
def get_principal_dashboard_data(request):
    if request.user.role != 'PRINCIPAL':
        return JsonResponse({'success': False, 'message': 'Access denied'})

    events = list(Event.objects())
    total_events_count = len(events)
    pending_approvals_count = sum(1 for e in events if e.status == 'HOD_APPROVED')
    approved_events_count = sum(1 for e in events if e.status == 'PRINCIPAL_APPROVED')

    from collections import defaultdict
    dept_counts = defaultdict(int)
    for e in events:
        dept_counts[e.department] += 1
    dept_labels = dict(CustomUser.DEPARTMENT_CHOICES)
    department_events = {dept_labels.get(dept, dept): cnt for dept, cnt in dept_counts.items()}

    dept_budgets = defaultdict(float)
    for e in events:
        if e.status == 'PRINCIPAL_APPROVED':
            dept_budgets[e.department] += float(e.budget or 0)
    budget_by_department = {dept_labels.get(dept, dept): total for dept, total in dept_budgets.items()}

    current_year = timezone.now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_events = [
        {'month': month, 'count': sum(1 for e in events if e.date and e.date.year == current_year and e.date.month == i)}
        for i, month in enumerate(months, 1)
    ]

    event_modes = {
        'Online': sum(1 for e in events if e.mode == 'ONLINE'),
        'Offline': sum(1 for e in events if e.mode == 'OFFLINE'),
    }

    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_events_data = [
        {
            'name': e.event_name,
            'department': dept_labels.get(e.department, e.department or ''),
            'date': e.date.strftime('%d %b %Y') if e.date else '',
            'status': dict(Event.STATUS_CHOICES).get(e.status, e.status),
        }
        for e in sorted(
            [e for e in events if e.date and e.date >= thirty_days_ago],
            key=lambda x: x.date,
            reverse=True,
        )[:5]
    ]

    return JsonResponse({
        'success': True,
        'totalEvents': total_events_count,
        'pendingApprovals': pending_approvals_count,
        'approvedEvents': approved_events_count,
        'departmentEvents': department_events,
        'budgetByDepartment': budget_by_department,
        'monthlyEvents': monthly_events,
        'eventModes': event_modes,
        'recentEvents': recent_events_data,
    })


@login_required
def get_student_dashboard_data(request):
    if request.user.role != 'STUDENT':
        return JsonResponse({'success': False, 'message': 'Access denied'})

    registrations = list(EventRegistration.objects(student=request.user))
    registered_events_count = len(registrations)

    today = timezone.now().date()
    upcoming = sorted(
        [r for r in registrations if r.event and r.event.date and r.event.date >= today],
        key=lambda r: r.event.date,
    )[:5]

    upcoming_events_data = [{
        'name': r.event.event_name,
        'date': r.event.date.strftime('%d %b %Y'),
        'time': str(r.event.time),
        'mode': dict(Event.MODE_CHOICES).get(r.event.mode, r.event.mode),
        'venue': r.event.venue if r.event.venue else 'Online',
    } for r in upcoming]

    pending_assessments = []
    now = timezone.now()
    for reg in registrations:
        if not reg.event:
            continue
        for assessment in EventAssessment.objects(event=reg.event, due_date__gte=now):
            if not AssessmentSubmission.objects(assessment=assessment, student=request.user).first():
                pending_assessments.append({
                    'title': assessment.title,
                    'event': assessment.event.event_name,
                    'due_date': assessment.due_date.strftime('%d %b %Y, %I:%M %p'),
                    'id': str(assessment.id),
                })

    certificates = sum(1 for r in registrations if r.certificate_generated)

    submissions = list(AssessmentSubmission.objects(student=request.user))
    scores = [s.score for s in submissions if s.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0

    current_year = timezone.now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_participation = [
        {'month': month, 'count': sum(
            1 for r in registrations
            if r.event and r.event.date and r.event.date.year == current_year and r.event.date.month == i
        )}
        for i, month in enumerate(months, 1)
    ]

    feedback_given = EventFeedback.objects(student=request.user).count()

    return JsonResponse({
        'success': True,
        'registeredEvents': registered_events_count,
        'upcomingEvents': upcoming_events_data,
        'pendingAssessments': pending_assessments,
        'certificates': certificates,
        'avgScore': round(avg_score, 1),
        'monthlyParticipation': monthly_participation,
        'feedbackGiven': feedback_given,
    })
