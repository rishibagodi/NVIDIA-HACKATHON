#!/usr/bin/python3
"""Vigil local speech-to-text (runs entirely inside the sandbox).
Voice language is a user setting (/sandbox/.openclaw/vigil/voice_lang: en | hi), default English.
English uses whisper-base.en (fast, accurate); Hindi uses multilingual whisper-small with a Hindi vocabulary hint.
(Automatic language detection was unreliable on short, Indian-accented clips: 0.39–0.53 confidence for both languages.)
Decodes audio with PyAV directly (faster-whisper 1.2.1's decoder passes an option removed in PyAV 19)."""
import os, sys
import av
import numpy as np
import onnxruntime
onnxruntime.set_default_logger_severity(3)
from faster_whisper import WhisperModel

M = "/sandbox/.openclaw/vigil/models"
SETTING = "/sandbox/.openclaw/vigil/voice_lang"
PROFILES = {
    "en": (f"{M}/whisper-base.en", "College deadlines: viva, lab, internals, CIE, SEE, assignment, submission, hall ticket, semester exam, registration, fee."),
    "hi": (f"{M}/whisper-small", "सोमवार, मंगलवार, बुधवार, गुरुवार, शुक्रवार, शनिवार, रविवार, कल, परसों, सुबह, शाम, बजे, जमा करना, परीक्षा, फीस, वाइवा, लैब।"),
}

def load(path):
    rs = av.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks = []
    with av.open(path) as c:
        for frame in c.decode(audio=0):
            chunks += [f.to_ndarray().reshape(-1) for f in rs.resample(frame)]
    chunks += [f.to_ndarray().reshape(-1) for f in rs.resample(None)]
    return np.concatenate(chunks).astype(np.float32) / 32768.0 if chunks else np.zeros(0, np.float32)

lang = open(SETTING).read().strip() if os.path.exists(SETTING) else "en"
lang = lang if lang in PROFILES else "en"
path, hint = PROFILES[lang]
model = WhisperModel(path, device="cpu", compute_type="int8")
segments, _ = model.transcribe(load(sys.argv[1]), beam_size=1, vad_filter=True, language=lang, initial_prompt=hint)
print(" ".join(s.text.strip() for s in segments))