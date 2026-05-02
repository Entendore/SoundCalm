import math
import numpy as np
import threading
from PySide6.QtCore import QTimer

try:
    import sounddevice as sd
except ImportError:
    print("Error: 'sounddevice' library missing.\nInstall with: pip install sounddevice")
    exit(1)

from constants import SAMPLE_RATE, BLOCK_SIZE

class AudioEngine:
    def __init__(self):
        self.frequencies: list[tuple[float, float]] = []
        self.binaural_offset = 0.0
        self.master_volume = 0.5
        self.playing = False
        
        # Phase accumulators to prevent clicks/pops between chunks
        self.phase_l: dict[float, float] = {}
        self.phase_r: dict[float, float] = {}
        
        # Smooth envelope (attack/release)
        self.envelope = 0.0
        self._target_env = 0.0
        
        # Thread safety lock
        self._lock = threading.Lock()
        
        self.stream = None
        
        # Pre-calculate time array for vectorization (optimization)
        self._t = np.arange(BLOCK_SIZE) / SAMPLE_RATE

    def start(self):
        if self.stream is None:
            try:
                self.stream = sd.OutputStream(
                    samplerate=SAMPLE_RATE, 
                    blocksize=BLOCK_SIZE,
                    channels=2, 
                    dtype='float32', 
                    callback=self._cb
                )
                self.stream.start()
            except Exception as e:
                print(f"Audio Initialization Error: {e}")
                return

        self._target_env = 1.0
        self.playing = True

    def stop(self):
        self._target_env = 0.0
        self.playing = False
        # Delayed stream closure to allow fade-out
        QTimer.singleShot(600, self._kill_stream)

    def _kill_stream(self):
        if self.stream and not self.playing:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception: pass
            self.stream = None
            # Reset phases to prevent old phase data affecting next start
            self.phase_l.clear()
            self.phase_r.clear()
            self.envelope = 0.0

    def _cb(self, outdata, frames, _time, _status):
        # 1. Ramp envelope (linear interpolation for smooth volume changes)
        ramp_speed = 0.004
        if self.envelope < self._target_env:
            self.envelope = min(self.envelope + ramp_speed, self._target_env)
        else:
            self.envelope = max(self.envelope - ramp_speed, self._target_env)

        # 2. Prepare output buffer (Zero allocation: write directly to outdata)
        # outdata is provided by the driver, pre-shaped (frames, 2)
        outdata.fill(0)

        if self.envelope < 0.001:
            return

        # 3. Thread-safe snapshot of current settings
        with self._lock:
            freqs_snapshot = list(self.frequencies)
            offset = self.binaural_offset
            
        if not freqs_snapshot:
            return

        n_freq = len(freqs_snapshot)
        
        # 4. Generate Audio (Vectorized)
        # We iterate through frequencies and accumulate directly into outdata
        for freq, vol in freqs_snapshot:
            if freq <= 0: continue

            # --- Left Channel ---
            # Retrieve current phase or start at 0
            p_l = self.phase_l.get(freq, 0.0)
            
            # Generate wave segment: sin(2*pi*f*t + phase)
            # Using t array is faster than arange in loop
            wave_l = np.sin(2.0 * np.pi * freq * self._t + p_l)
            
            # Update phase for next chunk. 
            # Modulo 2pi keeps the float value small and precise
            self.phase_l[freq] = (p_l + 2.0 * np.pi * freq * (frames / SAMPLE_RATE)) % (2.0 * np.pi)

            # --- Right Channel (Binaural) ---
            freq_r = freq + offset
            p_r = self.phase_r.get(freq, 0.0)
            
            wave_r = np.sin(2.0 * np.pi * freq_r * self._t + p_r)
            self.phase_r[freq] = (p_r + 2.0 * np.pi * freq_r * (frames / SAMPLE_RATE)) % (2.0 * np.pi)

            # --- Mix ---
            # Calculate amplitude scalar
            amp = vol * self.master_volume * self.envelope / n_freq
            
            # Accumulate directly into the memory view
            outdata[:, 0] += wave_l * amp
            outdata[:, 1] += wave_r * amp

    def snapshot(self, n=512):
        """Generate a visualization snapshot (Waveform data)"""
        with self._lock:
            freqs_snapshot = list(self.frequencies)
            
        if not freqs_snapshot:
            return np.zeros(n)
        
        t = np.arange(n) / SAMPLE_RATE
        w = sum(np.sin(2 * np.pi * f * t) * v for f, v in freqs_snapshot)
        return w / len(freqs_snapshot) * self.envelope