import random

def calculate_credit_score(data):
    score = 300

    # Payment History (35%)
    total_payments = data['on_time_payments'] + data['missed_payments']
    payment_ratio = data['on_time_payments'] / max(1, total_payments)
    score += payment_ratio * 35 * 10  # up to 350 pts

    # Credit Utilization (30%)
    utilization = data['current_balance'] / max(1, data['credit_limit'])
    utilization_score = (1 - utilization) * 30 * 10  # lower is better
    score += max(0, utilization_score)

    # Credit Age (15%)
    score += min(data['credit_age'], 10) * 15  # up to 150 pts

    # Credit Mix (10%)
    score += min(data['loan_types'], 3) * 10  # 3 types max = 30 pts

    # Inquiries (10%)
    score -= data['recent_inquiries'] * 5  # up to -50 pts

    return round(min(score, 850))
