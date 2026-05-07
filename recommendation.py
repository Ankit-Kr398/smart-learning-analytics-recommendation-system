from datetime import date


# ─────────────────────────────────────────────
# PRIORITY CONSTANTS
# These define recommendation urgency levels.
# Using named constants instead of raw strings
# prevents typos and makes comparisons reliable.
# ─────────────────────────────────────────────

PRIORITY_CRITICAL = 'critical'
PRIORITY_HIGH     = 'high'
PRIORITY_MEDIUM   = 'medium'
PRIORITY_LOW      = 'low'


# ─────────────────────────────────────────────
# HELPER — BUILD ONE RECOMMENDATION OBJECT
# Every recommendation in the system is built
# through this single function. This guarantees
# every recommendation has identical structure,
# making template rendering predictable.
# ─────────────────────────────────────────────

def make_recommendation(priority, category, title, reason, action):
    return {
        'priority': priority,
        'category': category,
        'title': title,
        'reason': reason,
        'action': action
    }


# ─────────────────────────────────────────────
# RULE 1 — NO DATA AT ALL
# A brand new user with zero logs needs a
# different recommendation than an active user.
# ─────────────────────────────────────────────

def recommend_for_new_user():
    return [
        make_recommendation(
            priority=PRIORITY_CRITICAL,
            category='Getting Started',
            title='Log your first study session',
            reason='You have no study data yet. The system cannot analyze or recommend anything without at least one logged session.',
            action='Click "Log Study Session" and record what you studied today — even 15 minutes counts.'
        )
    ]


# ─────────────────────────────────────────────
# RULE 2 — WEAK TOPIC RECOMMENDATIONS
# Topics with health score below 40 are critical.
# Topics between 40 and 60 are high priority.
# ─────────────────────────────────────────────

def recommend_weak_topics(weak_topics):
    recommendations = []

    for topic in weak_topics[:3]:
        score = topic['topic_health_score']
        accuracy = topic['accuracy']
        name = topic['topic_name']
        subject = topic['subject_name']

        if score < 40:
            priority = PRIORITY_CRITICAL
            title = f'Urgent: Revise {name} ({subject})'
            reason = (
                f'Your health score for {name} is critically low at '
                f'{score}% with only {accuracy}% accuracy. '
                f'This topic needs immediate focused attention.'
            )
            action = (
                f'Dedicate at least 45 minutes today to {name}. '
                f'Start from fundamentals, not practice questions. '
                f'Understanding must come before speed.'
            )

        elif score < 60:
            priority = PRIORITY_HIGH
            title = f'Improve: Practice {name} ({subject})'
            reason = (
                f'{name} has a health score of {score}% with '
                f'{accuracy}% accuracy. You know some of it but '
                f'not well enough for placement-level questions.'
            )
            action = (
                f'Attempt 15 medium-difficulty questions on {name} today. '
                f'Focus on understanding wrong answers, not just quantity.'
            )

        else:
            continue

        recommendations.append(
            make_recommendation(priority, 'Weak Topic', title, reason, action)
        )

    return recommendations


# ─────────────────────────────────────────────
# RULE 3 — NEGLECTED TOPIC RECOMMENDATIONS
# Topics not studied for 7+ days are at risk
# of being forgotten due to the forgetting curve.
# ─────────────────────────────────────────────

def recommend_neglected_topics(neglected_topics):
    recommendations = []

    for topic in neglected_topics[:2]:
        days = topic['days_since_studied']
        name = topic['topic_name']
        subject = topic['subject_name']
        accuracy = topic['accuracy']

        if days >= 14:
            priority = PRIORITY_HIGH
            title = f'Revisit {name} — {days} days without practice'
            reason = (
                f'You have not studied {name} in {days} days. '
                f'Research on memory retention shows significant '
                f'decay after 2 weeks without revision, even for '
                f'topics with previously high accuracy.'
            )
            action = (
                f'Spend 20 minutes reviewing {name} today. '
                f'A quick revision session resets the forgetting curve '
                f'and protects your earlier effort.'
            )

        else:
            priority = PRIORITY_MEDIUM
            title = f'Schedule revision for {name} ({subject})'
            reason = (
                f'{name} has not been studied for {days} days. '
                f'Your last accuracy was {accuracy}%. '
                f'Regular spacing improves long-term retention.'
            )
            action = (
                f'Add {name} to your plan for the next 2 days. '
                f'Even 10 practice questions will maintain retention.'
            )

        recommendations.append(
            make_recommendation(
                priority, 'Neglected Topic', title, reason, action
            )
        )

    return recommendations


# ─────────────────────────────────────────────
# RULE 4 — SUBJECT BALANCE RECOMMENDATIONS
# If a high-weight subject like DSA has very
# low health, the placement score is being
# dragged down significantly.
# ─────────────────────────────────────────────

def recommend_subject_balance(subject_stats):
    recommendations = []

    high_weight_subjects = [
        s for s in subject_stats
        if s['weight'] >= 0.20 and s['subject_health_score'] < 50
    ]

    high_weight_subjects.sort(
        key=lambda x: x['weight'] * (50 - x['subject_health_score']),
        reverse=True
    )

    for subject in high_weight_subjects[:2]:
        name = subject['subject_name']
        score = subject['subject_health_score']
        weight = int(subject['weight'] * 100)

        recommendations.append(
            make_recommendation(
                priority=PRIORITY_HIGH,
                category='Subject Balance',
                title=f'Boost {name} — High placement impact',
                reason=(
                    f'{name} carries {weight}% weight in your placement '
                    f'readiness score but currently scores only {score}%. '
                    f'Improving this subject has the highest return on '
                    f'your overall placement readiness.'
                ),
                action=(
                    f'Allocate at least 1 hour to {name} today. '
                    f'Focus on its lowest-scoring topics first — '
                    f'they are already highlighted in your weak topics list.'
                )
            )
        )

    return recommendations


# ─────────────────────────────────────────────
# RULE 5 — CONSISTENCY RECOMMENDATIONS
# If the student is not studying regularly,
# consistency gets flagged regardless of scores.
# ─────────────────────────────────────────────

def recommend_consistency(consistency_score, streak):
    recommendations = []

    if consistency_score < 30:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_CRITICAL,
                category='Consistency',
                title='Study consistency is critically low',
                reason=(
                    f'You have only studied on {consistency_score}% of '
                    f'days in the last 30 days. Placement preparation '
                    f'requires consistent daily effort. Sporadic '
                    f'marathon sessions are significantly less effective '
                    f'than short daily practice.'
                ),
                action=(
                    'Commit to one 30-minute session every day this week. '
                    'Set a phone alarm. Log even short sessions. '
                    'Building the habit is the first goal.'
                )
            )
        )

    elif consistency_score < 60:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_MEDIUM,
                category='Consistency',
                title='Improve your study regularity',
                reason=(
                    f'You studied on {consistency_score}% of days recently. '
                    f'This is developing but needs improvement. '
                    f'Students with 70%+ consistency outperform others '
                    f'in placement results regardless of total hours.'
                ),
                action=(
                    'Try to study at least 5 days per week. '
                    'Even 20 minutes on busy days maintains momentum '
                    'and keeps your streak alive.'
                )
            )
        )

    if streak >= 7:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_LOW,
                category='Streak',
                title=f'Protect your {streak}-day streak',
                reason=(
                    f'You have studied consistently for {streak} days. '
                    f'This is a strong habit signal. Protecting this '
                    f'streak maintains psychological momentum and '
                    f'your recency scores across all topics.'
                ),
                action=(
                    'Log at least one short session today to keep your '
                    'streak alive. Minimum 15 minutes on any topic counts.'
                )
            )
        )

    return recommendations


# ─────────────────────────────────────────────
# RULE 6 — ACCURACY DROP DETECTION
# If overall accuracy has dropped below a
# threshold, the student may be rushing or
# attempting too-hard questions prematurely.
# ─────────────────────────────────────────────

def recommend_accuracy_improvement(overall_accuracy, total_sessions):
    recommendations = []

    if total_sessions < 3:
        return recommendations

    if overall_accuracy < 40:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_HIGH,
                category='Accuracy',
                title='Overall accuracy needs significant improvement',
                reason=(
                    f'Your overall accuracy across all sessions is '
                    f'{overall_accuracy}%. Attempting difficult questions '
                    f'before mastering fundamentals creates false familiarity '
                    f'and slows real progress.'
                ),
                action=(
                    'Switch to Easy difficulty questions for the next week. '
                    'Focus on understanding solutions fully before moving on. '
                    'Speed and difficulty can increase once accuracy crosses 60%.'
                )
            )
        )

    elif overall_accuracy < 60:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_MEDIUM,
                category='Accuracy',
                title='Work on improving answer accuracy',
                reason=(
                    f'Your overall accuracy is {overall_accuracy}%. '
                    f'This indicates you are attempting questions at '
                    f'the right pace but need more conceptual clarity '
                    f'on several topics.'
                ),
                action=(
                    'After every wrong answer, spend 5 minutes understanding '
                    'the correct approach before moving to the next question. '
                    'Quality of review matters more than question quantity.'
                )
            )
        )

    return recommendations


# ─────────────────────────────────────────────
# RULE 7 — POSITIVE REINFORCEMENT
# When a student is performing well, the system
# should acknowledge it and suggest next steps
# rather than staying silent.
# ─────────────────────────────────────────────

def recommend_next_level(placement_score, overall_accuracy):
    recommendations = []

    if placement_score >= 75 and overall_accuracy >= 70:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_LOW,
                category='Next Level',
                title='Strong performance — time for mock tests',
                reason=(
                    f'Your placement readiness score is {placement_score}% '
                    f'with {overall_accuracy}% overall accuracy. '
                    f'You have covered strong fundamentals. The next '
                    f'growth lever is timed practice under exam conditions.'
                ),
                action=(
                    'Attempt one full-length mock aptitude or DSA test this week. '
                    'Time yourself strictly. Identify which question types '
                    'cause the most time loss and target those next.'
                )
            )
        )

    elif placement_score >= 60:
        recommendations.append(
            make_recommendation(
                priority=PRIORITY_LOW,
                category='Progress',
                title='Good progress — push for consistency in weak areas',
                reason=(
                    f'Your placement readiness is at {placement_score}%. '
                    f'You are on the right track. The remaining gap is '
                    f'likely concentrated in 2 or 3 specific weak topics.'
                ),
                action=(
                    'Review your weak topics list and schedule one dedicated '
                    'session for each this week. Targeted effort now will '
                    'have outsized impact on your final readiness score.'
                )
            )
        )

    return recommendations


# ─────────────────────────────────────────────
# PRIORITY SORTER
# Ensures recommendations always appear in
# critical → high → medium → low order
# regardless of which rules fired.
# ─────────────────────────────────────────────

PRIORITY_ORDER = {
    PRIORITY_CRITICAL: 0,
    PRIORITY_HIGH: 1,
    PRIORITY_MEDIUM: 2,
    PRIORITY_LOW: 3
}

def sort_by_priority(recommendations):
    return sorted(
        recommendations,
        key=lambda r: PRIORITY_ORDER.get(r['priority'], 99)
    )


# ─────────────────────────────────────────────
# DEDUPLICATION
# Prevents showing two recommendations with
# identical titles if multiple rules fire
# for the same topic.
# ─────────────────────────────────────────────

def deduplicate(recommendations):
    seen_titles = set()
    unique = []
    for rec in recommendations:
        if rec['title'] not in seen_titles:
            seen_titles.add(rec['title'])
            unique.append(rec)
    return unique


# ─────────────────────────────────────────────
# MASTER RECOMMENDATION FUNCTION
# Called by the dashboard route and the
# /recommendations API route.
# Receives the full analytics dictionary and
# returns a clean prioritized list.
# ─────────────────────────────────────────────

def generate_recommendations(analytics_data):

    if not analytics_data.get('has_data', False):
        return recommend_for_new_user()

    topic_stats      = analytics_data.get('topic_stats', [])
    subject_stats    = analytics_data.get('subject_stats', [])
    weak_topics      = analytics_data.get('weak_topics', [])
    neglected_topics = analytics_data.get('neglected_topics', [])
    placement_score  = analytics_data.get('placement_score', 0.0)
    consistency      = analytics_data.get('consistency_score', 0.0)
    streak           = analytics_data.get('streak', 0)
    overall_accuracy = analytics_data.get('overall_accuracy', 0.0)
    total_sessions   = analytics_data.get('total_sessions', 0)

    all_recommendations = []

    all_recommendations += recommend_weak_topics(weak_topics)
    all_recommendations += recommend_neglected_topics(neglected_topics)
    all_recommendations += recommend_subject_balance(subject_stats)
    all_recommendations += recommend_consistency(consistency, streak)
    all_recommendations += recommend_accuracy_improvement(
                               overall_accuracy, total_sessions)
    all_recommendations += recommend_next_level(
                               placement_score, overall_accuracy)

    all_recommendations = deduplicate(all_recommendations)
    all_recommendations = sort_by_priority(all_recommendations)

    if len(all_recommendations) > 6:
        all_recommendations = all_recommendations[:6]

    if not all_recommendations:
        all_recommendations.append(
            make_recommendation(
                priority=PRIORITY_LOW,
                category='Maintenance',
                title='Keep up your current study pace',
                reason=(
                    'All tracked topics and subjects are currently '
                    'in a healthy state. No immediate action items detected.'
                ),
                action=(
                    'Continue your current routine. '
                    'Log sessions regularly to maintain accurate tracking. '
                    'Check back after a few more sessions for updated insights.'
                )
            )
        )

    return all_recommendations