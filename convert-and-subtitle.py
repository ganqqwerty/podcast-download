import os
import argparse
import subprocess
import time
import sys

def format_duration(seconds):
    """Formats a time duration into a string of the form HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def estimate_time_left(files_sizes, bytes_processed, start_time):
    current_time = time.time()
    elapsed_time = current_time - start_time
    bytes_per_second = bytes_processed / elapsed_time

    remaining_bytes = sum(files_sizes) - bytes_processed
    estimated_time_left_seconds = remaining_bytes / bytes_per_second if bytes_per_second != 0 else 0

    return format_duration(estimated_time_left_seconds)


def convert_mp3_to_wav(mp3_filepath, wav_filepath):
    # Check if the WAV file already exists and is not empty
    if os.path.exists(wav_filepath) and os.path.getsize(wav_filepath) > 0:
        print(f"WAV file {wav_filepath} already exists and is not empty. Skipping conversion.")
        return

    print(f"Converting {mp3_filepath} to {wav_filepath}...")
    FNULL = open(os.devnull, 'w')
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-threads", "0",
        "-i", mp3_filepath,
        "-f", "wav",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        wav_filepath
    ]
    subprocess.run(cmd, stdout=FNULL, stderr=subprocess.STDOUT, check=True)


def generate_subtitles(wav_filepath):
    output_name = os.path.splitext(wav_filepath)[0]
    temp_output_file = f"{output_name}_temp_output.txt"

    print(f"Generating subtitles for {wav_filepath}...")
    cmd = f'./main -l ja -m models/ggml-large.bin --beam-size 5  --output-srt --output-file {output_name} {wav_filepath} 2>&1 | tee {temp_output_file}'
    print(cmd)
    subprocess.run(cmd, shell=True, check=True)

    # Now, read the output from the temp_output_file and check for repeated lines
    with open(temp_output_file, 'r') as f:
        lines = f.readlines()

    consecutive_duplicate_count = 0
    last_line_content = ""
    for line in lines:
        line_content = line.strip().split(']')[-1].strip()
        if line_content == last_line_content:
            consecutive_duplicate_count += 1
        else:
            consecutive_duplicate_count = 0
            last_line_content = line_content

        if consecutive_duplicate_count > 5:
            os.rename(f"{output_name}.srt", f"{output_name}_buggy.srt")
            break

    # Optionally, remove the temporary output file
    os.remove(temp_output_file)


def process_directory(directory_path):
    files_sizes = []
    bytes_processed = 0
    start_time = time.time()

    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".mp3"):
            mp3_filepath = os.path.join(directory_path, filename)
            file_size = os.path.getsize(mp3_filepath)
            files_sizes.append(file_size)

    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".mp3"):
            mp3_filepath = os.path.join(directory_path, filename)
            wav_filepath = os.path.splitext(mp3_filepath)[0] + ".wav"
            srt_filepath = os.path.splitext(mp3_filepath)[0] + ".srt"

            # Check if the SRT file already exists and is not empty
            if os.path.exists(srt_filepath) and os.path.getsize(srt_filepath) > 0:
                print(f"SRT file {srt_filepath} already exists and is not empty. Skipping conversion and recognition.")
                continue

            convert_mp3_to_wav(mp3_filepath, wav_filepath)
            generate_subtitles(wav_filepath)
            # Update bytes processed
            bytes_processed += os.path.getsize(mp3_filepath)

            # Print the estimated time left
            time_left = estimate_time_left(files_sizes, bytes_processed, start_time)
            print(f"Estimated time left: {time_left}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MP3 files to WAV and generate SRT subtitles.")
    parser.add_argument("dir", type=str, help="Directory containing MP3 files.")
    args = parser.parse_args()

    process_directory(args.dir)
