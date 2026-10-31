"""Throwaway spike: how does Whisper behave on our audio, and how fast is it?

    uv run python spike.py "C:\\path\\to\\file.m4a" --model medium --lang auto
    uv run python spike.py FILE --model large-v3 --lang he
    uv run python spike.py FILE --model medium --lang auto --no-multilingual

--lang: auto | he | en.  Results go to spike_out/ and a summary line is printed.
"""

import argparse
import os
import re
import site
import subprocess
import time
from pathlib import Path

import numpy as np
import imageio_ffmpeg

OUT = Path("spike_out")
ARABIC = re.compile(r"[\u0600-\u06FF]")
HEBREW = re.compile(r"[\u0590-\u05FF]")
LATIN = re.compile(r"[A-Za-z]")


def add_cuda_dlls():
    for base in site.getsitepackages():
        for d in (Path(base) / "nvidia").glob("*/bin"):
            os.add_dll_directory(str(d))
            os.environ["PATH"] = str(d) + os.pathsep + os.environ["PATH"]


def load_audio(path):
    raw = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-loglevel", "error", "-i", str(path),
         "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--model", default="medium")
    ap.add_argument("--lang", default="auto", choices=["auto", "he", "en"])
    ap.add_argument("--no-multilingual", action="store_true")
    ap.add_argument("--cpu", action="store_true")
    args = ap.parse_args()

    add_cuda_dlls()
    from faster_whisper import WhisperModel

    audio = load_audio(args.file)
    duration = len(audio) / 16000

    device, ctype = ("cpu", "int8") if args.cpu else ("cuda", "float16")
    t_load = time.time()
    model = WhisperModel(args.model, device=device, compute_type=ctype)
    load_s = time.time() - t_load

    lang = None if args.lang == "auto" else args.lang
    t0 = time.time()
    segments, info = model.transcribe(
        audio,
        language=lang,
        multilingual=(lang is None and not args.no_multilingual),
        vad_filter=True,
        beam_size=5,
        condition_on_previous_text=False,
    )
    texts = []
    for seg in segments:  # generator: decoding happens as we iterate
        texts.append((seg.start, seg.text.strip()))
        print(f"\r{seg.end / duration:5.0%}", end="", flush=True)
    elapsed = time.time() - t0
    print()

    tag = f"{Path(args.file).stem}.{args.model}.{args.lang}{'.nomulti' if args.no_multilingual else ''}"
    OUT.mkdir(exist_ok=True)
    (OUT / f"{tag}.txt").write_text(
        "\n".join(f"[{int(s // 60):02d}:{int(s % 60):02d}] {t}" for s, t in texts) + "\n", encoding="utf-8"
    )

    n = len(texts)
    arabic = sum(1 for _, t in texts if ARABIC.search(t))
    only_latin = sum(1 for _, t in texts if LATIN.search(t) and not HEBREW.search(t))
    print(f"{tag} | device={device} load={load_s:.0f}s | audio={duration / 60:.1f}min "
          f"decode={elapsed:.0f}s RTF={duration / elapsed:.1f}x | "
          f"first-lang={info.language}({info.language_probability:.0%}) | "
          f"segments={n} arabic={arabic} latin-only={only_latin}")


if __name__ == "__main__":
    main()
