from datetime import datetime, timedelta

def calculate_fasting_duration(start_time, fasting_hours):
    return start_time + timedelta(hours=fasting_hours)


def calculate_eating_duration(target_end_time, eating_hours):
    return target_end_time + timedelta(hours=eating_hours)

def fasting_progress(start_time, target_end_time, now=None  ):
    if now is None:
        now = datetime.now()
    total_seconds = (target_end_time - start_time).total_seconds()
    elapsed_seconds = (now - start_time).total_seconds()

    progress = (elapsed_seconds / total_seconds)

    return max(0, min(progress, 1))  # Ensure progress is between 0 and 1

def remaining_time(target_end_time, now=None):
    if now is None:
        now = datetime.now()

    diff = target_end_time - now
    if diff.total_seconds() <= 0:
        return "Ayuno completado"
    
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    return f"{diff.days * 24 + hours}h, {minutes} minutos restantes"