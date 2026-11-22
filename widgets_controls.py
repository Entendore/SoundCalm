from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSlider
from PySide6.QtCore import Qt, Signal

class FreqRow(QWidget):
    changed = Signal(float)
    remove = Signal()

    def __init__(self, freq: float, label: str, color: tuple):
        super().__init__()
        self.color = color
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)

        dot = QLabel("●")
        dot.setStyleSheet(f"color:rgb{color};font-size:16px;")
        lay.addWidget(dot)

        nl = QLabel(label)
        nl.setStyleSheet("color:#888;font-size:11px;min-width:85px;")
        lay.addWidget(nl)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(20, 2000)
        self.slider.setValue(int(freq))
        self.slider.setStyleSheet(self._ss())
        self.slider.valueChanged.connect(self._on)
        lay.addWidget(self.slider, 1)

        self.vl = QLabel(f"{int(freq)} Hz")
        self.vl.setStyleSheet(f"color:rgb{color};font-size:13px;font-weight:bold;min-width:70px;")
        lay.addWidget(self.vl)

        rb = QPushButton("×")
        rb.setCursor(Qt.PointingHandCursor)
        rb.setStyleSheet("QPushButton{color:#555;background:transparent;border:none;font-size:18px;padding:0 5px;}QPushButton:hover{color:#ff4444;}")
        rb.clicked.connect(self.remove.emit)
        lay.addWidget(rb)

    def _ss(self):
        c = f"rgb{self.color}"
        return (f"QSlider::groove:horizontal{{border:none;height:5px;background:#1a1a2a;border-radius:2px;}}"
                f"QSlider::handle:horizontal{{background:{c};width:16px;height:16px;margin:-5px 0;border-radius:8px;}}"
                f"QSlider::sub-page:horizontal{{background:{c};border-radius:2px;}}")

    def _on(self, v):
        self.vl.setText(f"{v} Hz")
        self.changed.emit(float(v))

    def freq(self) -> float: return float(self.slider.value())