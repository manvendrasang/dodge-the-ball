# pylint: disable=missing-module-docstring, missing-function-docstring, line-too-long, missing-class-docstring, disallowed-name, invalid-name
# pylint: disable=broad-exception-caught, global-statement

import numpy as np
import pygame
import threading

# sample rate for all sounds
SR = 44100

def _make_array(duration, func):
    """Generate mono int16 samples from a lambda(t) -> amplitude -1..1"""
    t   = np.linspace(0, duration, int(SR * duration), endpoint=False)
    arr = np.clip(func(t), -1, 1)
    arr = (arr * 32767).astype(np.int16)
    # pygame needs stereo
    return np.column_stack([arr, arr])

def _adsr(t, a, d, s_level, r, total):
    """Simple ADSR envelope"""
    env = np.zeros_like(t)
    a_end = a
    d_end = a + d
    r_start = total - r
    env[t < a_end]                          = t[t < a_end] / a
    env[(t >= a_end) & (t < d_end)]         = 1.0 - (1.0 - s_level) * (t[(t >= a_end) & (t < d_end)] - a_end) / d
    env[(t >= d_end) & (t < r_start)]       = s_level
    env[t >= r_start]                        = s_level * (1.0 - (t[t >= r_start] - r_start) / r)
    return np.clip(env, 0, 1)

# collect beep: short rising sine chirp
def _make_collect():
    dur = 0.12
    def f(t):
        freq = 440 + 660 * (t / dur)  # 440->1100 Hz sweep
        env  = _adsr(t, 0.005, 0.02, 0.4, 0.07, dur)
        return np.sin(2 * np.pi * freq * t) * env * 0.55
    return _make_array(dur, f)

# powerup chime: two-tone arpeggio
def _make_powerup():
    dur = 0.35
    def f(t):
        f1  = np.sin(2 * np.pi * 660  * t)
        f2  = np.sin(2 * np.pi * 880  * t)
        f3  = np.sin(2 * np.pi * 1100 * t)
        # stagger onsets
        sig = (f1 * (t < 0.12) +
               f2 * ((t >= 0.10) & (t < 0.25)) +
               f3 * (t >= 0.22))
        env = _adsr(t, 0.01, 0.05, 0.5, 0.15, dur)
        return sig * env * 0.45
    return _make_array(dur, f)

# death buzz: low-freq growl with noise burst
def _make_death():
    dur = 0.55
    rng = np.random.default_rng(42)
    def f(t):
        noise = rng.uniform(-1, 1, len(t))
        tone  = np.sin(2 * np.pi * 80 * t) + 0.5 * np.sin(2 * np.pi * 40 * t)
        sig   = tone * 0.6 + noise * 0.4
        env   = _adsr(t, 0.003, 0.05, 0.3, 0.35, dur)
        # pitch drops over time
        drop  = np.sin(2 * np.pi * (120 - 80 * t / dur) * t)
        return (sig * 0.5 + drop * 0.5) * env * 0.7
    return _make_array(dur, f)

# shrink alert: descending two-blip warning
def _make_shrink():
    dur = 0.5
    def f(t):
        blip1 = np.sin(2 * np.pi * 520 * t) * (t < 0.18)
        blip2 = np.sin(2 * np.pi * 380 * t) * ((t >= 0.22) & (t < 0.45))
        env1  = np.exp(-18 * np.clip(t,             0, 0.18))
        env2  = np.exp(-18 * np.clip(t - 0.22,      0, 0.23))
        return (blip1 * env1 + blip2 * env2) * 0.5
    return _make_array(dur, f)


# synthwave loop: bass + pad + arp
# 4-bar loop at 90 BPM = 2.667s per bar, 10.67s total
def _make_synthwave():
    bpm    = 90
    beat   = 60 / bpm          # seconds per beat
    bars   = 4
    dur    = beat * 4 * bars   # 4 beats * 4 bars
    rng    = np.random.default_rng(7)

    t = np.linspace(0, dur, int(SR * dur), endpoint=False)

    # bass line: root notes on beats, heavy low sine + sub octave
    bass_freqs = [55, 55, 41, 46]  # A1 A1 E1 Bb1 (dark minor feel)
    bass = np.zeros(len(t))
    for bar, freq in enumerate(bass_freqs):
        for beat_n in range(4):
            onset = (bar * 4 + beat_n) * beat
            mask  = (t >= onset) & (t < onset + beat * 0.85)
            lo    = t[mask] - onset
            env_b = np.exp(-2.5 * lo)
            bass[mask] += (
                np.sin(2 * np.pi * freq       * lo) * 0.8 +
                np.sin(2 * np.pi * freq * 2   * lo) * 0.3 +
                np.sin(2 * np.pi * freq * 0.5 * lo) * 0.5   # sub
            ) * env_b

    # dark pad: slow attack chord (Am)
    pad_freqs = [220, 261.6, 329.6]  # A3 C4 E4
    pad = np.zeros(len(t))
    for freq in pad_freqs:
        wave = np.sin(2 * np.pi * freq * t)
        # slow tremolo
        trem = 0.85 + 0.15 * np.sin(2 * np.pi * 0.8 * t)
        pad += wave * trem
    pad_env = 0.5 + 0.5 * np.sin(2 * np.pi * (1/(beat*4)) * t - np.pi/2)
    pad *= pad_env * 0.18

    # arp: 16th-note stabs on a minor pentatonic
    arp_notes = [440, 523, 392, 440, 349, 440, 392, 523,
                 440, 392, 349, 392, 440, 523, 440, 392]
    arp = np.zeros(len(t))
    step = beat / 4  # 16th note
    for i, freq in enumerate(arp_notes * bars):
        onset = i * step
        if onset >= dur:
            break
        mask  = (t >= onset) & (t < onset + step * 0.6)
        lo    = t[mask] - onset
        env_a = np.exp(-12 * lo)
        arp[mask] += (
            np.sin(2 * np.pi * freq       * lo) * 0.6 +
            np.sin(2 * np.pi * freq * 2   * lo) * 0.2
        ) * env_a * 0.3

    # kick drum: sine thump + click
    kick = np.zeros(len(t))
    for bar in range(bars):
        for beat_n in [0, 2]:  # beats 1 and 3
            onset = (bar * 4 + beat_n) * beat
            mask  = (t >= onset) & (t < onset + 0.18)
            lo    = t[mask] - onset
            freq_sweep = 180 * np.exp(-30 * lo)
            kick[mask] += np.sin(2 * np.pi * freq_sweep * lo) * np.exp(-20 * lo) * 0.9

    # hi-hat: 8th-note filtered noise bursts
    hat = np.zeros(len(t))
    hat_noise = rng.uniform(-1, 1, len(t))
    for bar in range(bars):
        for beat_n in range(8):
            onset = (bar * 4 + beat_n * 0.5) * beat
            mask  = (t >= onset) & (t < onset + 0.06)
            lo    = t[mask] - onset
            hat[mask] += hat_noise[mask] * np.exp(-40 * lo) * 0.18

    mix = bass * 0.55 + pad + arp + kick * 0.6 + hat
    # soft limiter
    mix = np.tanh(mix * 0.9) * 0.85
    mix = np.clip(mix, -1, 1)
    arr = (mix * 32767).astype(np.int16)
    return np.column_stack([arr, arr])


# button click: ultra-short soft tick with a tiny pitch pop
def _make_click():
    dur = 0.055
    def f(t):
        body = np.sin(2 * np.pi * 900 * t) * 0.5 + np.sin(2 * np.pi * 1400 * t) * 0.25
        env  = np.exp(-55 * t)
        return body * env * 0.45
    return _make_array(dur, f)


class AudioManager:
    def __init__(self):
        self._ready  = False
        self._sounds = {}
        self._music_channel = None
        self._music_arr     = None
        self._music_sound   = None
        self._volume        = 0.7
        self._music_volume  = 0.45
        # build sounds in background thread so startup is instant
        t = threading.Thread(target=self._build, daemon=True)
        t.start()

    def _build(self):
        try:
            pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=512)
            data = {
                "collect": _make_collect(),
                "powerup": _make_powerup(),
                "death":   _make_death(),
                "shrink":  _make_shrink(),
                "click":   _make_click(),
            }
            sounds = {}
            for name, arr in data.items():
                s = pygame.sndarray.make_sound(arr)
                s.set_volume(self._volume)
                sounds[name] = s
            # music as looping Sound on dedicated channel
            music_arr   = _make_synthwave()
            music_sound = pygame.sndarray.make_sound(music_arr)
            music_sound.set_volume(self._music_volume)
            self._sounds       = sounds
            self._music_sound  = music_sound
            self._ready        = True
        except Exception as e:
            print(f"[audio] init failed: {e}")

    def play(self, name):
        if not self._ready:
            return
        s = self._sounds.get(name)
        if s:
            s.play()

    def start_music(self):
        if not self._ready or self._music_sound is None:
            # retry shortly after build finishes
            threading.Timer(1.0, self.start_music).start()
            return
        if self._music_channel and self._music_channel.get_busy():
            return
        self._music_channel = self._music_sound.play(loops=-1)

    def stop_music(self):
        if self._music_channel:
            self._music_channel.stop()

    def set_volume(self, vol):
        self._volume = vol
        for s in self._sounds.values():
            s.set_volume(vol)

    def set_music_volume(self, vol):
        self._music_volume = vol
        if self._music_sound:
            self._music_sound.set_volume(vol)

# singleton
_manager = None

def get_audio() -> AudioManager:
    global _manager
    if _manager is None:
        _manager = AudioManager()
    return _manager
