from models import db, StudyLog, Topic, Subject, WeeklyReport
from datetime import date, datetime, timedelta
from collections import defaultdict
import math


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_user_logs(user_id):
    return (StudyLog.query
            .filter_by(user_id=user_id)
            .order_by(StudyLog.session_date.asc())
            .all())


def get_difficulty_multiplier(difficulty):
    multipliers = {
        'Easy': 1.0,
        'Medium': 1.3,
        'Hard': 1.6
    }
    return multipliers.get(difficulty, 1.0)


def safe_divide(numerator, denominator, default=0.0):
    if denominator == 0:
        return default
    return round(numerator / denominator, 2)


# ─────────────────────────────────────────────
# TOPIC-LEVEL ANALYTICS
# ─────────────────────────────────────────────

def compute_topic_stats(logs):
    topic_data = defaultdict(lambda: {
        'topic_id': None,
        'topic_name': '',
        'subject_name': '',
        'subject_id': None,
        'total_attempted': 0,
        'total_correct': 0,
        'total_sessions': 0,
        'total_time': 0,
        'last_studied': None,
        'difficulty_scores': []
    })

    for log in logs:
        tid = log.topic_id
        topic_data[tid]['topic_id'] = tid
        topic_data[tid]['topic_name'] = log.topic.name
        topic_data[tid]['subject_name'] = log.topic.subject.name
        topic_data[tid]['subject_id'] = log.topic.subject_id
        topic_data[tid]['total_attempted'] += log.questions_attempted
        topic_data[tid]['total_correct'] += log.correct_answers
        topic_data[tid]['total_sessions'] += 1
        topic_data[tid]['total_time'] += log.study_time_minutes
        topic_data[tid]['difficulty_scores'].append(
            get_difficulty_multiplier(log.difficulty)
        )

        log_date = log.session_date
        if (topic_data[tid]['last_studied'] is None or
                log_date > topic_data[tid]['last_studied']):
            topic_data[tid]['last_studied'] = log_date

    results = []
    today = date.today()

    for tid, data in topic_data.items():
        accuracy = safe_divide(
            data['total_correct'] * 100,
            data['total_attempted']
        )

        frequency = data['total_sessions']
        frequency_score = min(frequency / 10.0, 1.0) * 100

        days_since = (today - data['last_studied']).days if data['last_studied'] else 999
        recency_score = max(0, 100 - (days_since * 10))

        avg_difficulty = safe_divide(
            sum(data['difficulty_scores']),
            len(data['difficulty_scores'])
        )

        topic_health = (
            (accuracy * 0.50) +
            (frequency_score * 0.30) +
            (recency_score * 0.20)
        )

        productivity = round(
            safe_divide(accuracy, 100) *
            math.log(data['total_time'] + 1) *
            avg_difficulty,
            2
        )

        results.append({
            'topic_id': tid,
            'topic_name': data['topic_name'],
            'subject_name': data['subject_name'],
            'subject_id': data['subject_id'],
            'total_attempted': data['total_attempted'],
            'total_correct': data['total_correct'],
            'total_sessions': frequency,
            'total_time_minutes': data['total_time'],
            'last_studied': data['last_studied'].isoformat() if data['last_studied'] else None,
            'days_since_studied': days_since,
            'accuracy': accuracy,
            'frequency_score': round(frequency_score, 2),
            'recency_score': round(recency_score, 2),
            'topic_health_score': round(topic_health, 2),
            'productivity_score': productivity
        })

    results.sort(key=lambda x: x['topic_health_score'])
    return results


# ─────────────────────────────────────────────
# SUBJECT-LEVEL ANALYTICS
# ─────────────────────────────────────────────

def compute_subject_stats(topic_stats):
    subject_data = defaultdict(lambda: {
        'subject_name': '',
        'subject_id': None,
        'topic_healths': [],
        'total_attempted': 0,
        'total_correct': 0,
        'total_time': 0,
        'total_sessions': 0
    })

    for topic in topic_stats:
        sid = topic['subject_id']
        subject_data[sid]['subject_name'] = topic['subject_name']
        subject_data[sid]['subject_id'] = sid
        subject_data[sid]['topic_healths'].append(topic['topic_health_score'])
        subject_data[sid]['total_attempted'] += topic['total_attempted']
        subject_data[sid]['total_correct'] += topic['total_correct']
        subject_data[sid]['total_time'] += topic['total_time_minutes']
        subject_data[sid]['total_sessions'] += topic['total_sessions']

    subject_results = []

    for sid, data in subject_data.items():
        avg_health = safe_divide(
            sum(data['topic_healths']),
            len(data['topic_healths'])
        )
        overall_accuracy = safe_divide(
            data['total_correct'] * 100,
            data['total_attempted']
        )

        subject = Subject.query.get(sid)
        weight = subject.weight if subject else 1.0

        subject_results.append({
            'subject_id': sid,
            'subject_name': data['subject_name'],
            'subject_health_score': round(avg_health, 2),
            'overall_accuracy': overall_accuracy,
            'total_time_minutes': data['total_time'],
            'total_sessions': data['total_sessions'],
            'weight': weight
        })

    subject_results.sort(key=lambda x: x['subject_health_score'])
    return subject_results


# ─────────────────────────────────────────────
# PLACEMENT READINESS SCORE
# ─────────────────────────────────────────────

def compute_placement_score(subject_stats):
    if not subject_stats:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for subject in subject_stats:
        w = subject['weight']
        score = subject['subject_health_score']
        weighted_sum += score * w
        total_weight += w

    if total_weight == 0:
        return 0.0

    placement_score = round(weighted_sum / total_weight, 2)
    return placement_score


# ─────────────────────────────────────────────
# CONSISTENCY SCORE
# ─────────────────────────────────────────────

def compute_consistency_score(logs, days=30):
    if not logs:
        return 0.0

    today = date.today()
    cutoff = today - timedelta(days=days)

    recent_logs = [
        log for log in logs
        if log.session_date >= cutoff
    ]

    if not recent_logs:
        return 0.0

    active_days = len(set(log.session_date for log in recent_logs))
    consistency = round((active_days / days) * 100, 2)
    return min(consistency, 100.0)


# ─────────────────────────────────────────────
# STREAK CALCULATION
# ─────────────────────────────────────────────

def compute_streak(logs):
    if not logs:
        return 0

    study_dates = sorted(set(log.session_date for log in logs), reverse=True)
    today = date.today()
    yesterday = today - timedelta(days=1)

    if study_dates[0] not in [today, yesterday]:
        return 0

    streak = 1
    for i in range(1, len(study_dates)):
        expected = study_dates[i - 1] - timedelta(days=1)
        if study_dates[i] == expected:
            streak += 1
        else:
            break

    return streak


# ─────────────────────────────────────────────
# OVERALL LEARNING SCORE
# ─────────────────────────────────────────────

def compute_overall_score(placement_score, consistency_score, streak):
    streak_bonus = min(streak * 0.5, 10.0)
    overall = (
        (placement_score * 0.70) +
        (consistency_score * 0.25) +
        streak_bonus
    )
    return round(min(overall, 100.0), 2)


# ─────────────────────────────────────────────
# WEAK TOPICS DETECTION
# ─────────────────────────────────────────────

def get_weak_topics(topic_stats, threshold=50.0):
    weak = [
        t for t in topic_stats
        if t['topic_health_score'] < threshold
    ]
    return weak[:5]


def get_neglected_topics(topic_stats, days_threshold=7):
    neglected = [
        t for t in topic_stats
        if t['days_since_studied'] >= days_threshold
    ]
    neglected.sort(key=lambda x: x['days_since_studied'], reverse=True)
    return neglected[:5]


# ─────────────────────────────────────────────
# MASTER ANALYTICS FUNCTION
# ─────────────────────────────────────────────

def compute_user_analytics(user_id):
    logs = get_user_logs(user_id)

    if not logs:
        return {
            'has_data': False,
            'message': 'No study sessions logged yet. Start by logging your first session!',
            'topic_stats': [],
            'subject_stats': [],
            'placement_score': 0.0,
            'consistency_score': 0.0,
            'overall_score': 0.0,
            'streak': 0,
            'total_sessions': 0,
            'total_time_minutes': 0,
            'total_questions': 0,
            'overall_accuracy': 0.0,
            'weak_topics': [],
            'neglected_topics': []
        }

    topic_stats = compute_topic_stats(logs)
    subject_stats = compute_subject_stats(topic_stats)
    placement_score = compute_placement_score(subject_stats)
    consistency_score = compute_consistency_score(logs)
    streak = compute_streak(logs)
    overall_score = compute_overall_score(
        placement_score, consistency_score, streak
    )
    weak_topics = get_weak_topics(topic_stats)
    neglected_topics = get_neglected_topics(topic_stats)

    total_sessions = len(logs)
    total_time = sum(log.study_time_minutes for log in logs)
    total_attempted = sum(log.questions_attempted for log in logs)
    total_correct = sum(log.correct_answers for log in logs)
    overall_accuracy = safe_divide(total_correct * 100, total_attempted)

    return {
        'has_data': True,
        'topic_stats': topic_stats,
        'subject_stats': subject_stats,
        'placement_score': placement_score,
        'consistency_score': consistency_score,
        'overall_score': overall_score,
        'streak': streak,
        'total_sessions': total_sessions,
        'total_time_minutes': total_time,
        'total_questions': total_attempted,
        'overall_accuracy': overall_accuracy,
        'weak_topics': weak_topics,
        'neglected_topics': neglected_topics
    }


# ─────────────────────────────────────────────
# WEEKLY REPORT COMPUTATION
# ─────────────────────────────────────────────

def compute_weekly_report(user_id):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    logs = (StudyLog.query
            .filter_by(user_id=user_id)
            .filter(StudyLog.session_date >= week_start)
            .filter(StudyLog.session_date <= week_end)
            .order_by(StudyLog.session_date.asc())
            .all())

    daily_breakdown = defaultdict(lambda: {
        'sessions': 0,
        'time': 0,
        'attempted': 0,
        'correct': 0
    })

    for log in logs:
        day_key = log.session_date.strftime('%A')
        daily_breakdown[day_key]['sessions'] += 1
        daily_breakdown[day_key]['time'] += log.study_time_minutes
        daily_breakdown[day_key]['attempted'] += log.questions_attempted
        daily_breakdown[day_key]['correct'] += log.correct_answers

    days_order = ['Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday', 'Sunday']

    daily_data = []
    for day in days_order:
        d = daily_breakdown[day]
        daily_data.append({
            'day': day,
            'sessions': d['sessions'],
            'time_minutes': d['time'],
            'accuracy': safe_divide(d['correct'] * 100, d['attempted'])
        })

    total_time = sum(log.study_time_minutes for log in logs)
    total_attempted = sum(log.questions_attempted for log in logs)
    total_correct = sum(log.correct_answers for log in logs)

    return {
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'total_sessions': len(logs),
        'total_time_minutes': total_time,
        'overall_accuracy': safe_divide(total_correct * 100, total_attempted),
        'daily_breakdown': daily_data,
        'logs': logs
    }


# ─────────────────────────────────────────────
# MONTHLY REPORT COMPUTATION
# ─────────────────────────────────────────────

def compute_monthly_report(user_id):
    today = date.today()
    month_start = today.replace(day=1)

    logs = (StudyLog.query
            .filter_by(user_id=user_id)
            .filter(StudyLog.session_date >= month_start)
            .filter(StudyLog.session_date <= today)
            .order_by(StudyLog.session_date.asc())
            .all())

    weekly_breakdown = defaultdict(lambda: {
        'sessions': 0,
        'time': 0,
        'attempted': 0,
        'correct': 0
    })

    for log in logs:
        week_num = log.session_date.isocalendar()[1]
        weekly_breakdown[week_num]['sessions'] += 1
        weekly_breakdown[week_num]['time'] += log.study_time_minutes
        weekly_breakdown[week_num]['attempted'] += log.questions_attempted
        weekly_breakdown[week_num]['correct'] += log.correct_answers

    weekly_data = []
    for week_num, data in sorted(weekly_breakdown.items()):
        weekly_data.append({
            'week': f'Week {week_num}',
            'sessions': data['sessions'],
            'time_minutes': data['time'],
            'accuracy': safe_divide(data['correct'] * 100, data['attempted'])
        })

    total_time = sum(log.study_time_minutes for log in logs)
    total_attempted = sum(log.questions_attempted for log in logs)
    total_correct = sum(log.correct_answers for log in logs)

    return {
        'month': today.strftime('%B %Y'),
        'total_sessions': len(logs),
        'total_time_minutes': total_time,
        'overall_accuracy': safe_divide(total_correct * 100, total_attempted),
        'weekly_breakdown': weekly_data,
        'logs': logs
    }