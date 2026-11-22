import math
import numpy as np
from constants import SOLFEGGIO_PSYCH, BRAIN_WAVES

def _gauss(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def get_psych_dimensions(freq):
    """Interpolate psychological dimension scores for any frequency."""
    anchors = sorted(SOLFEGGIO_PSYCH.keys())
    if freq <= anchors[0]: return list(SOLFEGGIO_PSYCH[anchors[0]])
    if freq >= anchors[-1]: return list(SOLFEGGIO_PSYCH[anchors[-1]])
    
    for i in range(len(anchors) - 1):
        if anchors[i] <= freq <= anchors[i + 1]:
            t = (freq - anchors[i]) / (anchors[i + 1] - anchors[i])
            d1 = np.array(SOLFEGGIO_PSYCH[anchors[i]])
            d2 = np.array(SOLFEGGIO_PSYCH[anchors[i + 1]])
            return (d1 * (1 - t) + d2 * t).tolist()
    return [0.5] * 8

def get_perception_scores(freq):
    """Perception channel activation via log-frequency Gaussians."""
    lf = math.log(max(freq, 20))
    return [
        _gauss(lf, math.log(80),  0.90),   # Visceral
        _gauss(lf, math.log(450), 1.00),   # Emotional
        _gauss(lf, math.log(650), 0.85),   # Cognitive
        _gauss(lf, math.log(880), 0.75),   # Spiritual
        _gauss(lf, math.log(280), 1.10),   # Somatic
        _gauss(lf, math.log(130), 1.20),   # Subconscious
    ]

def get_brain_wave_activation(binaural_offset, frequencies):
    """Compute brain wave band activation."""
    bo = binaural_offset
    result = []
    
    for name, sym, lo, hi, color, desc in BRAIN_WAVES:
        activation = 0.05
        if bo > 0:
            center = (lo + hi) / 2
            width = (hi - lo) / 2 + 2
            activation = max(0.0, _gauss(bo, center, width))
        
        # Carrier influence
        for f in frequencies:
            lf = math.log(max(f, 20))
            if name == "Delta": activation = max(activation, _gauss(lf, math.log(100), 1.2) * 0.25)
            elif name == "Theta": activation = max(activation, _gauss(lf, math.log(250), 1.0) * 0.25)
            elif name == "Alpha": activation = max(activation, _gauss(lf, math.log(450), 0.9) * 0.25)
            elif name == "Beta": activation = max(activation, _gauss(lf, math.log(700), 0.8) * 0.25)
            elif name == "Gamma": activation = max(activation, _gauss(lf, math.log(900), 0.7) * 0.25)
        result.append(min(activation, 1.0))
    return result

def aggregate_dimensions(frequencies):
    if not frequencies: return [0.0] * 8
    dims = [0.0] * 8
    for f in frequencies:
        scores = get_psych_dimensions(f)
        for i in range(8): dims[i] = max(dims[i], scores[i])
    return dims

def aggregate_perception(frequencies):
    if not frequencies: return [0.0] * 6
    perc = [0.0] * 6
    for f in frequencies:
        scores = get_perception_scores(f)
        for i in range(6): perc[i] = max(perc[i], scores[i])
    return perc