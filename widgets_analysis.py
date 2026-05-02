import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QLinearGradient

from constants import DIM_NAMES, DIM_COLORS, BRAIN_WAVES, PERCEPTION_CHANNELS, PERCEPTION_COLORS

class PsychRadarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dims = [0.0] * 8
        self.target_dims = [0.0] * 8
        self.setMinimumSize(220, 240)
        self._pen_grid = QPen(QColor(35, 35, 55), 1)

    def set_dimensions(self, dims): self.target_dims = dims[:8]

    def tick(self):
        changed = False
        for i in range(8):
            diff = self.target_dims[i] - self.dims[i]
            if abs(diff) > 0.005:
                self.dims[i] += diff * 0.12
                changed = True
        if changed: self.update()

    def paintEvent(self, _ev):
        P = QPainter(self)
        P.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2 + 8
        max_r = min(w, h) / 2 - 40

        P.setFont(QFont("Segoe UI", 9, QFont.Bold))
        P.setPen(QColor(100, 100, 130))
        P.drawText(QPointF(8, 14), "PSYCHOLOGICAL DIMENSIONS")

        n, step, start = 8, 2 * math.pi / 8, -math.pi / 2

        # Draw Grid
        for level in (0.25, 0.5, 0.75, 1.0):
            path = QPainterPath()
            for i in range(n):
                a = start + i * step
                px = cx + max_r * level * math.cos(a)
                py = cy + max_r * level * math.sin(a)
                (path.moveTo if i == 0 else path.lineTo)(px, py)
            path.closeSubpath()
            P.setPen(self._pen_grid)
            P.setBrush(Qt.NoBrush)
            P.drawPath(path)

        # Draw Data
        data_pts = []
        for i in range(n):
            a = start + i * step
            r = max_r * max(self.dims[i], 0.02)
            data_pts.append(QPointF(cx + r * math.cos(a), cy + r * math.sin(a)))

        if any(d > 0.01 for d in self.dims):
            path = QPainterPath()
            path.moveTo(data_pts[0])
            for pt in data_pts[1:]: path.lineTo(pt)
            path.closeSubpath()
            
            P.setPen(QPen(QColor(0, 255, 200, 60), 3))
            P.setBrush(QColor(0, 255, 200, 25))
            P.drawPath(path)

        # Labels
        P.setFont(QFont("Segoe UI", 8))
        for i in range(n):
            a = start + i * step
            lx = cx + (max_r + 15) * math.cos(a)
            ly = cy + (max_r + 15) * math.sin(a)
            P.setPen(QColor(*DIM_COLORS[i]))
            P.drawText(QPointF(lx - 20, ly), DIM_NAMES[i])
        P.end()


class BrainWaveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.activations = [0.05] * 5
        self.targets = [0.05] * 5
        self.setMinimumSize(300, 190)

    def set_activations(self, acts): self.targets = acts[:5]

    def tick(self):
        changed = False
        for i in range(5):
            diff = self.targets[i] - self.activations[i]
            if abs(diff) > 0.005:
                self.activations[i] += diff * 0.12
                changed = True
        if changed: self.update()

    def paintEvent(self, _ev):
        P = QPainter(self)
        P.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        
        P.setFont(QFont("Segoe UI", 9, QFont.Bold))
        P.setPen(QColor(100, 100, 130))
        P.drawText(8, 14, "BRAIN WAVE ENTRAINMENT")

        bar_h, spacing = 22, 8
        x_bar, bar_w = 76, w - 76 - 55

        y = 26
        for i, (name, sym, lo, hi, color, desc) in enumerate(BRAIN_WAVES):
            act = self.activations[i]
            
            # Label
            P.setFont(QFont("Segoe UI", 10, QFont.Bold))
            P.setPen(QColor(*color))
            P.drawText(6, y + 15, f"{sym} {name}")

            # Bar BG
            P.setPen(Qt.NoPen)
            P.setBrush(QColor(20, 20, 30))
            P.drawRoundedRect(x_bar, y + 3, bar_w, bar_h, 5, 5)

            # Bar Fill
            fill_w = bar_w * act
            if fill_w > 2:
                grad = QLinearGradient(x_bar, 0, x_bar + fill_w, 0)
                grad.setColorAt(0, QColor(*color).darker(150))
                grad.setColorAt(1, QColor(*color))
                P.setBrush(grad)
                P.drawRoundedRect(x_bar, y + 3, fill_w, bar_h, 5, 5)

            # Text
            P.setFont(QFont("Consolas", 9, QFont.Bold))
            P.setPen(QColor(*color))
            P.drawText(x_bar + bar_w + 6, y + 17, f"{act:.0%}")

            y += bar_h + spacing
        P.end()

class PerceptionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.scores = [0.0] * 6
        self.targets = [0.0] * 6
        self.setMinimumSize(300, 190)

    def set_scores(self, scores): self.targets = scores[:6]

    def tick(self):
        changed = False
        for i in range(6):
            diff = self.targets[i] - self.scores[i]
            if abs(diff) > 0.005:
                self.scores[i] += diff * 0.12
                changed = True
        if changed: self.update()

    def paintEvent(self, _ev):
        P = QPainter(self)
        P.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        
        P.setFont(QFont("Segoe UI", 9, QFont.Bold))
        P.setPen(QColor(100, 100, 130))
        P.drawText(8, 14, "PERCEPTION INFLUENCE")

        bar_h, spacing = 18, 7
        x_bar, bar_w = 88, w - 88 - 55

        y = 26
        for i in range(6):
            sc = self.scores[i]
            col = QColor(*PERCEPTION_COLORS[i])

            P.setFont(QFont("Segoe UI", 9))
            P.setPen(col)
            P.drawText(6, y + 13, PERCEPTION_CHANNELS[i])

            P.setPen(Qt.NoPen)
            P.setBrush(QColor(20, 20, 30))
            P.drawRoundedRect(x_bar, y + 2, bar_w, bar_h, 4, 4)

            fill_w = bar_w * sc
            if fill_w > 2:
                grad = QLinearGradient(x_bar, 0, x_bar + fill_w, 0)
                grad.setColorAt(0, col.darker(150))
                grad.setColorAt(1, col)
                P.setBrush(grad)
                P.drawRoundedRect(x_bar, y + 2, fill_w, bar_h, 4, 4)

            P.setFont(QFont("Consolas", 9, QFont.Bold))
            P.setPen(col)
            P.drawText(x_bar + bar_w + 6, y + 14, f"{sc:.0%}")

            y += bar_h + spacing
        P.end()