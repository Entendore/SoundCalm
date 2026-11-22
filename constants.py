import math

# Audio Configuration
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024  # Lower latency, still safe
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

SOLFEGGIO = {
    174: "Pain Relief", 285: "Tissue Heal", 396: "Liberation",
    417: "Change", 432: "Universal", 528: "Love/Heal",
    639: "Connection", 741: "Expression", 852: "Intuition", 963: "Crown"
}

RING_COLORS = [
    (0, 255, 200), (147, 112, 255), (255, 100, 200),
    (100, 200, 255), (255, 200, 100),
]

# Psychological dimensions per solfeggio frequency
# [Relaxation, Focus, Creativity, Emotion, Spiritual, Healing, Intuition, Clarity]
SOLFEGGIO_PSYCH = {
    174: [0.85, 0.15, 0.20, 0.50, 0.15, 0.95, 0.20, 0.20],
    285: [0.75, 0.15, 0.15, 0.35, 0.15, 0.90, 0.15, 0.25],
    396: [0.80, 0.30, 0.35, 0.92, 0.30, 0.35, 0.35, 0.50],
    417: [0.50, 0.60, 0.70, 0.80, 0.40, 0.40, 0.45, 0.60],
    432: [0.92, 0.50, 0.70, 0.70, 0.60, 0.55, 0.55, 0.70],
    528: [0.80, 0.40, 0.65, 0.92, 0.70, 0.88, 0.50, 0.60],
    639: [0.70, 0.40, 0.50, 0.92, 0.50, 0.40, 0.60, 0.50],
    741: [0.40, 0.85, 0.88, 0.50, 0.60, 0.30, 0.70, 0.90],
    852: [0.60, 0.50, 0.70, 0.50, 0.92, 0.30, 0.95, 0.70],
    963: [0.50, 0.30, 0.55, 0.40, 0.95, 0.20, 0.92, 0.55],
}

DIM_NAMES = ["Relaxation", "Focus", "Creativity", "Emotion", "Spiritual", "Healing", "Intuition", "Clarity"]
DIM_COLORS = [(0, 210, 180), (255, 210, 50), (200, 100, 255), (255, 100, 150), (170, 120, 255), (100, 255, 150), (140, 175, 255), (255, 220, 100)]

PERCEPTION_CHANNELS = ["Visceral", "Emotional", "Cognitive", "Spiritual", "Somatic", "Subconscious"]
PERCEPTION_COLORS = [(255, 80, 80), (255, 120, 180), (100, 180, 255), (170, 120, 255), (100, 255, 180), (140, 140, 180)]

BRAIN_WAVES = [
    ("Delta", "δ", 0.5, 4,  (90, 70, 200),  "Deep Sleep"),
    ("Theta", "θ", 4,   8,  (60, 150, 230), "Meditation"),
    ("Alpha", "α", 8,   13, (60, 210, 150), "Relaxation"),
    ("Beta",  "β", 13,  30, (230, 190, 60), "Focus"),
    ("Gamma", "γ", 30,  100, (230, 80, 80), "Insight"),
]

TONAL_CONSTRUCTIONS = {
    "Anxiety Relief": {
        "freqs": [396, 528], "binaural": 10,
        "desc": "CARRIER: 396 Hz dissolves fear → 528 Hz fills with love\nBINAURAL: Alpha (10 Hz) — Calm alertness",
    },
    "Deep Sleep": {
        "freqs": [174, 285], "binaural": 2,
        "desc": "CARRIER: 174 Hz tension release → 285 Hz tissue heal\nBINAURAL: Delta (2 Hz) — Deep restoration",
    },
    "Meditation": {
        "freqs": [432, 852], "binaural": 6,
        "desc": "CARRIER: 432 Hz harmony → 852 Hz intuition\nBINAURAL: Theta (6 Hz) — Inner awareness",
    },
    "Focus Flow": {
        "freqs": [741, 417], "binaural": 18,
        "desc": "CARRIER: 741 Hz expression → 417 Hz change\nBINAURAL: Beta (18 Hz) — Active concentration",
    },
    "Heart Opening": {
        "freqs": [528, 639], "binaural": 8,
        "desc": "CARRIER: 528 Hz love → 639 Hz connection\nBINAURAL: Alpha (8 Hz) — Heart-brain coherence",
    },
    "Spiritual Growth": {
        "freqs": [852, 963], "binaural": 7,
        "desc": "CARRIER: 852 Hz intuition → 963 Hz crown\nBINAURAL: Theta (7 Hz) — Transcendence",
    },
    "Creative Break": {
        "freqs": [417, 741], "binaural": 8,
        "desc": "CARRIER: 417 Hz unblocks → 741 Hz sparks\nBINAURAL: Alpha (8 Hz) — Flow state",
    },
    "Pain Release": {
        "freqs": [174, 528], "binaural": 4,
        "desc": "CARRIER: 174 Hz relief → 528 Hz repair\nBINAURAL: Theta (4 Hz) — Endorphin release",
    },
}