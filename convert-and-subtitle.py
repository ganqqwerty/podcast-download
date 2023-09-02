import os
import argparse
import subprocess

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
    srt_filepath = output_name + ".srt"

    # Check if the SRT file already exists and is not empty
    if os.path.exists(srt_filepath) and os.path.getsize(srt_filepath) > 0:
        print(f"SRT file {srt_filepath} already exists and is not empty. Skipping subtitle generation.")
        return

    print(f"Generating subtitles for {wav_filepath}...")
    cmd = [
        "./main",
        "-l", "ja",
        "-m", "models/ggml-large.bin",
        "--output-srt",
        "--output-file", output_name,
        wav_filepath
    ]
    subprocess.run(cmd, check=True)

def process_directory(directory_path):
    for filename in os.listdir(directory_path):
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

            # Optionally, delete the WAV file after processing if needed.
            # os.remove(wav_filepath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MP3 files to WAV and generate SRT subtitles.")
    parser.add_argument("dir", type=str, help="Directory containing MP3 files.")
    args = parser.parse_args()

    process_directory(args.dir)
