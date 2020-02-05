def generate_progress_bar(curr, max, n_characters):
    """Returns an ascii progress bar"""
    phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    n_phases = len(phases)
    progress = (curr / max) * n_characters
    progress_bar = ""

    for i in range(n_characters):
        if progress > 1:
            phase = phases[-1]
        elif 0 <= progress < 1:
            index = int(round(progress * n_phases))
            phase = phases[index if index < len(phases) else -1]
        else:
            phase = phases[0]
        progress -= 1
        progress_bar += phase

    return progress_bar
