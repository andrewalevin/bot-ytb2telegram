

def get_splitting_parts(audio_length, duration, delta):
    if duration < 60:
        duration = 60
    elif duration > 241*60:
        duration = 241*60

    if delta < 0:
        delta = 0
    if delta > 299:
        delta = 299

    parts = []
    time = 0
    while time < audio_length:
        if time == 0:
            parts.append([time, time + duration + delta])
        elif time + duration > audio_length:
            # Golden ration
            if duration / (audio_length - time + delta) > 1.618:
                parts[-1][1] = audio_length
            else:
                # Add one second to add all
                parts.append([time - delta, audio_length+1])
        else:
            parts.append([time - delta, time + duration + delta])
        time += duration

    return parts