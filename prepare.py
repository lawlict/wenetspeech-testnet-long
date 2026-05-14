#!/usr/bin/env python3
"""
Prepare WenetSpeech test_net long-form audio dataset.

Given the original WenetSpeech test_net raw audio directory and
WenetSpeech_testnet_long.json (which describes how adjacent segments
were merged into longer chunks), this script slices the source opus
files into individual WAV segments and produces a text file.

Usage:
    python prepare.py \
        --src-dir /path/to/WenetSpeech_test_raw_untar \
        --output-dir /path/to/output \
        [--num-workers 8] \
        [--sample-rate 16000]

Output:
    output_dir/
    ├── wavs/          # 7385 wav files
    └── text           # 7385 lines: sid<TAB>text
"""

import argparse
import json
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path


def slice_segment(args):
    src_audio, sid, begin_time, duration, output_path, sample_rate = args
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{begin_time:.3f}",
        "-i", src_audio,
        "-t", f"{duration:.3f}",
        "-ac", "1",
        "-ar", str(sample_rate),
        output_path,
    ]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sid, r.returncode


def main():
    parser = argparse.ArgumentParser(description="Prepare WenetSpeech test_net long-form dataset")
    parser.add_argument("--src-dir", required=True, help="Path to WenetSpeech_test_raw_untar")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--num-workers", type=int, default=8, help="Parallel ffmpeg workers")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Output sample rate")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    json_path = script_dir / "WenetSpeech_testnet_long.json"

    print(f"Loading {json_path} ...")
    with open(json_path) as f:
        data = json.load(f)

    src_dir = Path(args.src_dir)
    wav_dir = Path(args.output_dir) / "wavs"
    wav_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    text_lines = []

    for audio in data["audios"]:
        src_audio = str(src_dir / audio["path"])
        if not os.path.isfile(src_audio):
            print(f"WARNING: source audio not found: {src_audio}", file=sys.stderr)
            continue
        for seg in audio["segments"]:
            sid = seg["sid"]
            begin = seg["begin_time"]
            duration = seg["end_time"] - seg["begin_time"]
            out_path = str(wav_dir / f"{sid}.wav")
            tasks.append((src_audio, sid, begin, duration, out_path, args.sample_rate))
            text_lines.append(f"{sid}\t{seg['text']}")

    print(f"Slicing {len(tasks)} segments with {args.num_workers} workers ...")

    failed = 0
    done = 0
    with Pool(args.num_workers) as pool:
        for sid, retcode in pool.imap_unordered(slice_segment, tasks, chunksize=32):
            done += 1
            if retcode != 0:
                failed += 1
                print(f"  FAILED: {sid}", file=sys.stderr)
            if done % 500 == 0 or done == len(tasks):
                print(f"  progress: {done}/{len(tasks)}")

    text_path = Path(args.output_dir) / "text"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write("\n".join(text_lines) + "\n")

    print(f"\nDone.")
    print(f"  WAVs:   {wav_dir}  ({done - failed} ok, {failed} failed)")
    print(f"  Text:   {text_path}  ({len(text_lines)} lines)")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
