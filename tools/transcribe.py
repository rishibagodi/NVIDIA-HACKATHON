#!/usr/bin/python3
"""Vigil local speech-to-text: transcribes a voice note entirely inside the sandbox (no audio leaves the machine).
Decodes audio with PyAV directly (faster-whisper 1.2.1's decoder passes an option removed in PyAV 19)."""
import sys
import av
import numpy as np
import onnxruntime
onnxruntime.set_default_logger_severity(3)
from faster_whisper import WhisperModel

HINT = "College deadlines: viva, lab, internals, CIE, SEE, assignment, submission, hall ticket, semester exam, registration, fee."

def load(path):
    rs = av.AudioResampler(format="s16", layout="mono", rate=16000)
    chunks = []
    with av.open(path) as c:
        for frame in c.decode(audio=0):
            chunks += [f.to_ndarray().reshape(-1) for f in rs.resample(frame)]
    chunks += [f.to_ndarray().reshape(-1) for f in rs.resample(None)]
    return np.concatenate(chunks).astype(np.float32) / 32768.0 if chunks else np.zeros(0, np.float32)

model = WhisperModel("/sandbox/.openclaw/vigil/models/whisper-base.en", device="cpu", compute_type="int8")
segments, _ = model.transcribe(load(sys.argv[1]), beam_size=1, vad_filter=True, initial_prompt=HINT)
print(" ".join(s.text.strip() for s in segments))