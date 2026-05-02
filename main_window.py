from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QSlider, QGroupBox, QCheckBox, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from constants import SOLFEGGIO, RING_COLORS, TONAL_CONSTRUCTIONS, DIM_NAMES, DIM_COLORS, PERCEPTION_CHANNELS
from helpers import aggregate_dimensions, aggregate_perception, get_perception_scores, get_brain_wave_activation
from audio_engine import AudioEngine
from widgets_viz import VisualizationWidget, WaveformWidget
from widgets_analysis import PsychRadarWidget, BrainWaveWidget, PerceptionWidget
from widgets_controls import FreqRow

class SonicCalm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio = AudioEngine()
        self.rows: list[FreqRow] = []
        self._active_construction = ""

        self.setWindowTitle("✦ Sonic Calm — Tonal Psychology")
        self.setMinimumSize(1280, 920)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setStyleSheet(self._css())
        self._build()

        # Visualization Timer (60 FPS target)
        self._viz_timer = QTimer(self)
        self._viz_timer.timeout.connect(self._update_viz)
        self._viz_timer.start(16)

        # Analysis Timer (20 FPS)
        self._analysis_timer = QTimer(self)
        self._analysis_timer.timeout.connect(self._update_analysis)
        self._analysis_timer.start(50)

        # Initial State
        self._add_row(432, "Universal")
        self._add_row(528, "Love/Heal")

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header = QVBoxLayout()
        title = QLabel("✦ S O N I C   C A L M ✦")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title)

        sub = QLabel("Tonal Variation • Psychological Effects • Perception & Cognition")
        sub.setObjectName("appSub")
        sub.setAlignment(Qt.AlignCenter)
        header.addWidget(sub)
        main_layout.addLayout(header)

        # Content
        content_row = QHBoxLayout()
        
        # Left: Visualization
        left_col = QVBoxLayout()
        self.viz = VisualizationWidget(self.audio)
        self.viz.setMinimumWidth(400)
        left_col.addWidget(self.viz, 1)
        
        self.wave = WaveformWidget(self.audio)
        left_col.addWidget(self.wave)
        content_row.addLayout(left_col, 3)

        # Right: Controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("mainScroll")

        rpanel = QWidget()
        r_layout = QVBoxLayout(rpanel)
        r_layout.setSpacing(12)

        # Presets
        cg = QGroupBox("TONAL CONSTRUCTION 🔧")
        cgl = QVBoxLayout()
        preset_grid = QGridLayout()
        preset_grid.setSpacing(5)
        
        presets = list(TONAL_CONSTRUCTIONS.items())
        for i, (name, data) in enumerate(presets):
            b = QPushButton(name)
            b.setCursor(Qt.PointingHandCursor)
            b.setToolTip(data["desc"])
            b.clicked.connect(lambda _, n=name: self._apply_construction(n))
            preset_grid.addWidget(b, i // 2, i % 2)
        cgl.addLayout(preset_grid)

        self.const_label = QLabel("Select a preset or build your own.")
        self.const_label.setWordWrap(True)
        self.const_label.setObjectName("infoCard")
        cgl.addWidget(self.const_label)
        cg.setLayout(cgl)
        r_layout.addWidget(cg)

        # Frequencies
        fg = QGroupBox("FREQUENCIES")
        fl = QVBoxLayout()
        self.fbox = QVBoxLayout()
        fl.addLayout(self.fbox)
        
        ab = QPushButton("+ Add Tone")
        ab.setObjectName("addBtn")
        ab.setCursor(Qt.PointingHandCursor)
        ab.clicked.connect(self._add)
        fl.addWidget(ab)
        fg.setLayout(fl)
        r_layout.addWidget(fg)

        # Binaural
        bg = QGroupBox("BINAURAL BEATS 🎧")
        bl = QVBoxLayout()
        self.b_check = QCheckBox("Enable (Headphones Required)")
        self.b_check.toggled.connect(self._bin)
        bl.addWidget(self.b_check)
        
        self.b_slider = QSlider(Qt.Horizontal)
        self.b_slider.setRange(1, 40)
        self.b_slider.setValue(6)
        self.b_slider.setEnabled(False)
        self.b_slider.valueChanged.connect(self._bin)
        bl.addWidget(self.b_slider)
        
        self.b_lbl = QLabel("Δf = 6.0 Hz (Theta — Meditation)")
        self.b_lbl.setObjectName("binLabel")
        bl.addWidget(self.b_lbl)
        bg.setLayout(bl)
        r_layout.addWidget(bg)

        # Volume
        vl = QHBoxLayout()
        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("font-size: 16px;")
        vl.addWidget(vol_icon)
        
        self.vol_s = QSlider(Qt.Horizontal)
        self.vol_s.setRange(0, 100)
        self.vol_s.setValue(50)
        self.vol_s.valueChanged.connect(self._vol)
        vl.addWidget(self.vol_s)
        
        self.vol_v = QLabel("50 %")
        self.vol_v.setObjectName("volVal")
        self.vol_v.setAlignment(Qt.AlignCenter)
        vl.addWidget(self.vol_v)
        r_layout.addLayout(vl)

        # Play Button
        self.play = QPushButton("▶   P L A Y")
        self.play.setObjectName("playBtn")
        self.play.setCursor(Qt.PointingHandCursor)
        self.play.setCheckable(True)
        self.play.clicked.connect(self._toggle)
        r_layout.addWidget(self.play)

        r_layout.addStretch()
        scroll.setWidget(rpanel)
        content_row.addWidget(scroll, 2)
        main_layout.addLayout(content_row)

        # Bottom Analysis
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("hLine")
        main_layout.addWidget(sep)

        bot_row = QHBoxLayout()
        bot_row.setSpacing(12)
        
        self.radar = PsychRadarWidget()
        bot_row.addWidget(self.radar, 2)

        self.brain_wv = BrainWaveWidget()
        bot_row.addWidget(self.brain_wv, 3)

        self.perc_wv = PerceptionWidget()
        bot_row.addWidget(self.perc_wv, 3)

        main_layout.addLayout(bot_row)

    @staticmethod
    def _css():
        return (
            "QMainWindow{background:#0c0c14;}"
            "QWidget{background:transparent;color:#ddd;font-family:'Segoe UI', 'San Francisco', sans-serif;}"
            "QLabel{background:transparent;}"
            
            "#appTitle{font-size:26px;font-weight:300;letter-spacing:12px;color:#00ffc8;}"
            "#appSub{font-size:10px;color:#556;letter-spacing:3px;margin-top:2px;}"
            
            "QPushButton{background:#18182e;color:#ccc;border:1px solid #333;border-radius:8px;padding:8px 14px;font-weight:bold;}"
            "QPushButton:hover{background:#22223a;border-color:#555;}"
            "QPushButton:checked{background:#0d3b3b;border-color:#00ffc8;color:#00ffc8;}"
            
            "#addBtn{background:transparent;border:1px dashed #333;color:#666;border-radius:8px;}"
            "#addBtn:hover{border-color:#00ffc8;color:#00ffc8;}"
            
            "#playBtn{font-size:16px;padding:16px;border-radius:12px;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0d2a2a,stop:1 #1a0d3b);color:#00ffc8;border:2px solid #00ffc8;}"
            "#playBtn:checked{background:#2a0d0d;color:#ff4466;border-color:#ff4466;}"
            
            "QGroupBox{background:#10101a;border:1px solid #222;border-radius:12px;margin-top:20px;padding-top:16px;font-weight:bold;color:#888;}"
            "QGroupBox::title{subcontrol-origin:margin;left:12px;padding:0 8px;background:#10101a;}"
            
            "QCheckBox{color:#aaa;spacing:8px;}"
            "QCheckBox::indicator{width:18px;height:18px;border-radius:5px;border:1px solid #333;background:#111;}"
            "QCheckBox::indicator:checked{background:#00ffc8;border-color:#00ffc8;}"
            
            "QSlider::groove:horizontal{border:none;height:5px;background:#1a1a2a;border-radius:2px;}"
            "QSlider::handle:horizontal{background:#fff;width:16px;height:16px;margin:-5px 0;border-radius:8px;}"
            
            "#infoCard{color:#888;font-size:11px;padding:10px;background:#08081a;border-radius:8px;border:1px solid #1a1a2a;}"
            "#hLine{color:#222;}"
        )

    def _update_viz(self):
        self.wave.refresh()
        self.viz.update() # Trigger paintEvent

    def _add_row(self, freq, label=None):
        idx = len(self.rows)
        c = RING_COLORS[idx % 5]
        if label is None:
            best = min(SOLFEGGIO, key=lambda k: abs(k - freq))
            label = SOLFEGGIO[best] if abs(best - freq) < 20 else f"Tone {idx + 1}"
        
        r = FreqRow(freq, label, c)
        r.changed.connect(self._sync)
        r.remove.connect(lambda row=r: self._del(row))
        self.fbox.addWidget(r)
        self.rows.append(r)
        self._sync()

    def _add(self):
        if len(self.rows) >= 5: return
        used = {int(row.freq()) for row in self.rows}
        d = 432
        for f in SOLFEGGIO:
            if f not in used:
                d = f
                break
        self._add_row(d)

    def _del(self, row):
        if len(self.rows) <= 1: return
        self.rows.remove(row)
        self.fbox.removeWidget(row)
        row.deleteLater()
        self._sync()

    def _sync(self):
        with self.audio._lock:
            self.audio.frequencies = [(r.freq(), 1.0) for r in self.rows]

    def _bin(self):
        on = self.b_check.isChecked()
        self.b_slider.setEnabled(on)
        if on:
            v = float(self.b_slider.value())
            self.audio.binaural_offset = v
            tag = ("Delta" if v < 4 else "Theta" if v < 8 else "Alpha" if v < 13 else "Beta" if v < 30 else "Gamma")
            self.b_lbl.setText(f"Δf = {v:.1f} Hz ({tag})")
        else:
            self.audio.binaural_offset = 0
            self.b_lbl.setText("Δf = 0 Hz (Disabled)")

    def _vol(self, v):
        self.audio.master_volume = v / 100
        self.vol_v.setText(f"{v} %")

    def _toggle(self, on):
        if on:
            self.play.setText("⏹   S T O P")
            self.audio.start()
        else:
            self.play.setText("▶   P L A Y")
            self.audio.stop()

    def _apply_construction(self, name):
        data = TONAL_CONSTRUCTIONS.get(name)
        if not data: return
        self._active_construction = name

        for r in self.rows[:]:
            self.fbox.removeWidget(r)
            r.deleteLater()
        self.rows.clear()

        for f in data["freqs"]:
            best = min(SOLFEGGIO, key=lambda k: abs(k - f))
            label = SOLFEGGIO.get(f, SOLFEGGIO.get(best, f"Custom {f}"))
            self._add_row(f, label)

        if data["binaural"] > 0:
            self.b_check.setChecked(True)
            self.b_slider.setValue(int(data["binaural"]))
        else:
            self.b_check.setChecked(False)

        self.const_label.setText(f"<b style='color:#00ffc8'>{name}</b><br><br>{data['desc']}")
        
        if not self.play.isChecked():
            self.play.click()

    def _update_analysis(self):
        freqs = [f for f, _ in self.audio.frequencies]

        dims = aggregate_dimensions(freqs)
        self.radar.set_dimensions(dims)
        self.radar.tick()

        brain = get_brain_wave_activation(self.audio.binaural_offset, freqs)
        self.brain_wv.set_activations(brain)
        self.brain_wv.tick()

        perc = aggregate_perception(freqs)
        self.perc_wv.set_scores(perc)
        self.perc_wv.tick()

        if not self._active_construction and freqs:
            self._update_auto_construction(freqs)

    def _update_auto_construction(self, freqs):
        lines = ["<b style='color:#9470ff'>Custom Mix</b><br>"]
        for f in freqs:
            name = "Custom"
            for sf, sn in SOLFEGGIO.items():
                if abs(sf - f) < 15: name = sn; break
            lines.append(f"<br>{int(f)} Hz ({name})")
        
        dims = aggregate_dimensions(freqs)
        max_idx = dims.index(max(dims))
        lines.append(f"<br><b style='color:rgb{DIM_COLORS[max_idx]}'>Primary:</b> {DIM_NAMES[max_idx]}")
        
        self.const_label.setText("".join(lines))

    def closeEvent(self, ev):
        self.audio.stop()
        if self.audio.stream:
            try: self.audio.stream.close()
            except: pass
        ev.accept()