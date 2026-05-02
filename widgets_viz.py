import math
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen, QPainterPath, QFont

from constants import SOLFEGGIO, RING_COLORS, GOLDEN_RATIO
from audio_engine import AudioEngine

class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'decay', 'size')
    def __init__(self, x, y, color, angle, speed):
        self.x, self.y = x, y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 1.0
        self.decay = 0.004 + np.random.random() * 0.012
        self.size = 1.5 + np.random.random() * 4.5

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.992
        self.vy *= 0.992
        self.life -= self.decay

class VisualizationWidget(QWidget):
    def __init__(self, audio: AudioEngine):
        super().__init__()
        self.audio = audio
        self.particles: list[Particle] = []
        self.t = 0.0
        self._pt = 0.0
        self.path = QPainterPath() # Reusable path
        
        # Performance timer
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start(16)

    def _tick(self):
        self.t += 0.016
        self._pt += 0.016
        
        # Particle Generation
        if self.audio.playing and self._pt > 0.04:
            self._pt = 0
            cx, cy = self.width() / 2, self.height() / 2
            with self.audio._lock:
                freqs = list(self.audio.frequencies)
            
            for i, (freq, vol) in enumerate(freqs):
                if np.random.random() < 0.6:
                    a = np.random.random() * 2 * math.pi
                    sp = 0.4 + vol * 2.5
                    self.particles.append(Particle(cx, cy, RING_COLORS[i % 5], a, sp))

        # Particle Update
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        self.update() # Trigger repaint

    def paintEvent(self, _ev):
        P = QPainter(self)
        P.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        # Background
        bg = QRadialGradient(cx, cy, max(w, h) * 0.7)
        bg.setColorAt(0, QColor(15, 15, 35))
        bg.setColorAt(1, QColor(5, 5, 12))
        P.fillRect(self.rect(), bg)

        # Particles
        P.setPen(Qt.NoPen)
        for p in self.particles:
            c = QColor(*p.color)
            c.setAlpha(int(p.life * 180))
            P.setBrush(c)
            P.drawEllipse(QPointF(p.x, p.y), p.size * p.life, p.size * p.life)

        # Frequencies
        with self.audio._lock:
            freqs = list(self.audio.frequencies)
        freqs = [(f, v) for f, v in freqs if f > 0]
        n_freq = len(freqs)
        env = self.audio.envelope
        
        if not freqs:
            # Idle State
            breath = math.sin(self.t * 1.2) * 0.15 + 0.85
            P.setPen(QColor(255, 255, 255, 40))
            P.setFont(QFont("Segoe UI", 14))
            P.drawText(self.rect(), Qt.AlignCenter, "Press PLAY to begin")
            return

        max_r = min(w, h) * 0.38

        # Draw Rings
        for i, (freq, vol) in enumerate(freqs):
            col = QColor(*RING_COLORS[i % 5])
            base_r = (i + 1) * max_r / (n_freq + 1)
            pulse = math.sin(self.t * freq * 0.08) * 15 * vol * env
            radius = base_r + pulse

            # Glow Effect (Optimized with single pass)
            P.setPen(QPen(QColor(col.red(), col.green(), col.blue(), 30), 6))
            P.setBrush(Qt.NoBrush)
            P.drawEllipse(QPointF(cx, cy), radius, radius)
            
            P.setPen(QPen(col, 1.5))
            self.path.clear()
            segs = 100
            for j in range(segs + 1):
                a = j * 2 * math.pi / segs
                d = math.sin(a * (int(freq) % 7 + 3) + self.t * freq * 0.04) * 8 * vol * env
                r = radius + d
                px = cx + r * math.cos(a)
                py = cy + r * math.sin(a)
                (self.path.moveTo if j == 0 else self.path.lineTo)(px, py)
            self.path.closeSubpath()
            P.drawPath(self.path)

            # Label
            P.setPen(col)
            P.setFont(QFont("Consolas", 9, QFont.Bold))
            lx = cx + radius * math.cos(-0.78)
            ly = cy + radius * math.sin(-0.78)
            P.drawText(QPointF(lx + 6, ly - 6), f"{int(freq)} Hz")

        # Center Core
        cg = QRadialGradient(cx, cy, 50)
        cg.setColorAt(0, QColor(200, 255, 240, int(80 * env)))
        cg.setColorAt(1, QColor(200, 255, 240, 0))
        P.setPen(Qt.NoPen)
        P.setBrush(cg)
        P.drawEllipse(QPointF(cx, cy), 50, 50)
        
        P.setBrush(QColor(255, 255, 255, int(200 * env)))
        P.drawEllipse(QPointF(cx, cy), 4, 4)

        # Info
        P.setFont(QFont("Consolas", 9))
        P.setPen(QColor(255, 255, 255, 80))
        fl = [f for f, _ in freqs]
        y0 = h - 16
        if len(fl) >= 2:
            r = fl[1] / fl[0]
            txt = f"Ratio {int(fl[1])}/{int(fl[0])} = {r:.3f}"
            if abs(r - GOLDEN_RATIO) < 0.06: txt += " (Golden Ratio φ)"
            P.drawText(QPointF(10, y0), txt)
        P.end()


class WaveformWidget(QWidget):
    def __init__(self, audio: AudioEngine):
        super().__init__()
        self.audio = audio
        self.data = np.zeros(512)
        self.setFixedHeight(80)
        self.path = QPainterPath()

    def refresh(self):
        self.data = self.audio.snapshot(512)
        self.update()

    def paintEvent(self, _):
        P = QPainter(self)
        P.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        P.fillRect(self.rect(), QColor(10, 10, 20))

        P.setPen(QPen(QColor(30, 30, 50), 1))
        P.drawLine(0, h//2, w, h//2)

        n = len(self.data)
        
        # Draw waveform (optimized)
        self.path.clear()
        self.path.moveTo(0, h/2 - self.data[0] * h * 0.35)
        for i in range(1, n):
            self.path.lineTo(i * w / n, h/2 - self.data[i] * h * 0.35)
        
        # Glow layer
        P.setPen(QPen(QColor(0, 255, 200, 35), 3))
        P.drawPath(self.path)
        # Core layer
        P.setPen(QPen(QColor(0, 255, 200, 200), 1))
        P.drawPath(self.path)
        
        P.end()