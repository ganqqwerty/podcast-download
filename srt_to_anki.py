import os
import argparse
from pydub import AudioSegment
from pysrt import open as open_srt

def make_segment(audio, start_time_ms, end_time_ms, segment_file):
    segment = audio[start_time_ms:end_time_ms]
    segment.export(segment_file, format="mp3")

def is_segment_too_small(start_time_ms, end_time_ms, subtitle_text, min_duration_ms, min_text_length):
    return (end_time_ms - start_time_ms < min_duration_ms) or (len(subtitle_text) < min_text_length)

def split_audio_by_srt(audio_file, srt_file, output_folder, show_name, min_duration_ms=1000, min_text_length=10):
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    subs = open_srt(srt_file)
    audio = AudioSegment.from_file(audio_file, format="mp3" if audio_file.endswith(".mp3") else "wav")

    previous_end_time_ms = 0
    previous_segment_file = None

    for index, sub in enumerate(subs):
        start_time_ms = (sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds) * 1000 + sub.start.milliseconds
        end_time_ms = (sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds) * 1000 + sub.end.milliseconds

        if is_segment_too_small(start_time_ms, end_time_ms, sub.text, min_duration_ms, min_text_length) and previous_segment_file:
            make_segment(audio, previous_end_time_ms, end_time_ms, previous_segment_file)
        else:
            segment_file = os.path.join(output_folder, f"{base_name}_segment_{index}.mp3")
            make_segment(audio, start_time_ms, end_time_ms, segment_file)
            previous_end_time_ms = end_time_ms
            previous_segment_file = segment_file

        timing = f"{sub.start} --> {sub.end}"
        print(f"{index+1}\t{timing}\t{base_name}\t{show_name}\t{sub.text}\t{segment_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split an audio file based on SRT subtitles and output the results in tab-separated format.')
    parser.add_argument('--audio_file', type=str, required=True, help='Path to the audio file (MP3 or WAV).')
    parser.add_argument('--srt_file', type=str, required=True, help='Path to the corresponding SRT subtitle file.')
    parser.add_argument('--output_folder', type=str, required=True, help='Folder to save the split audio segments.')
    parser.add_argument('--show_name', type=str, required=True, help='Name of the show.')
    parser.add_argument('--min_duration_ms', type=int, default=1000, help='Minimum duration of a segment in milliseconds.')
    parser.add_argument('--min_text_length', type=int, default=10, help='Minimum length of subtitle text for a segment.')

    args = parser.parse_args()
    split_audio_by_srt(args.audio_file, args.srt_file, args.output_folder, args.show_name, args.min_duration_ms, args.min_text_length)
