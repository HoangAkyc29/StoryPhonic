import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from pydub import AudioSegment

def parse_filename(filename: str) -> Tuple[int, int, str]:
    match = re.match(r"chunk_(\d+)_(\d+)_voice-actor_(.+?)\.wav", filename)
    if not match:
        raise ValueError(f"Filename {filename} does not match expected pattern.")
    return int(match.group(1)), int(match.group(2)), match.group(3)

def merge_audio_and_generate_metadata(input_dir: str, output_dir: str) -> Tuple[List[Dict], str]:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    files = [f for f in os.listdir(input_path) if f.endswith(".wav")]

    # Parse and sort files
    parsed_files = []
    for file in files:
        try:
            a, b, va_name = parse_filename(file)
            parsed_files.append((a, b, va_name, file))
        except ValueError:
            continue  # skip files that don't match

    parsed_files.sort(key=lambda x: (x[0], x[1]))  # sort by a then b

    final_audio = AudioSegment.silent(duration=0)
    metadata = []
    current_time_ms = 0
    prev_va_name = None

    for a, b, va_name, file in parsed_files:
        file_path = input_path / file
        chunk_audio = AudioSegment.from_wav(file_path)

        time_start = current_time_ms / 1000  # convert to seconds

        final_audio += chunk_audio
        current_time_ms += len(chunk_audio)

        metadata.append({
            "index_a": a,
            "index_b": b,
            "va_name": va_name,
            "time_start": round(time_start, 3),
            "time_end": round(current_time_ms / 1000, 3)
        })

        # Insert silence between clips
        if va_name == prev_va_name:
            final_audio += AudioSegment.silent(duration=300)  # 0.3s
            current_time_ms += 300
        else:
            if prev_va_name is not None:
                final_audio += AudioSegment.silent(duration=700)  # 0.7s
                current_time_ms += 700

        prev_va_name = va_name

    # Save final audio
    output_audio_path = output_path / "merged_output.wav"
    final_audio.export(output_audio_path, format="wav")

    # Save metadata
    metadata_path = output_path / "merged_output_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return metadata, str(output_audio_path)
