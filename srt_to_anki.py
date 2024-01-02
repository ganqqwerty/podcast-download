import os
import argparse
from pydub import AudioSegment
from pysrt import open as open_srt


def make_segment(audio, start_time_ms, end_time_ms, segment_file):
    # Adding 500ms margin to both sides to ensure that the voice is not cut mid-sentence
    start_margin = max(0, start_time_ms - 500)  # Ensuring start time is not negative
    end_margin = min(len(audio), end_time_ms + 500)  # Ensuring end time is not beyond audio length
    segment = audio[start_margin:end_margin]
    segment.export(segment_file, format="mp3")


def is_segment_too_small(start_time_ms, end_time_ms, subtitle_text, min_duration_ms, min_text_length):
    return (end_time_ms - start_time_ms < min_duration_ms) or (len(subtitle_text) < min_text_length)


def get_subtitle_text(subs, index):
    if 0 <= index < len(subs):
        return subs[index].text
    return ""


def get_audio_segment(audio, start, end):
    return audio[start:end]


def create_context_audio_file(audio, start_time_ms, end_time_ms, output_folder, audio_filename, index):
    context_audio_file = os.path.join(output_folder, audio_filename)
    context_segment = get_audio_segment(audio, start_time_ms, end_time_ms)
    context_segment.export(context_audio_file, format="mp3")
    return context_audio_file


def split_audio_by_srt(audio_file, srt_file, output_folder, show_name, min_duration_ms=1000, min_text_length=10):
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    subs = open_srt(srt_file)
    audio = AudioSegment.from_file(audio_file, format="mp3" if audio_file.endswith(".mp3") else "wav")

    for index, sub in enumerate(subs):
        # Calculate the start and end times of the current subtitle
        start_time_ms = sub.start.ordinal
        end_time_ms = sub.end.ordinal

        # Handle segment too small
        if is_segment_too_small(start_time_ms, end_time_ms, sub.text, min_duration_ms, min_text_length):
            continue

        # Create main segment with 500ms margin
        segment_audio_filename = f"{base_name}_segment_{index}.mp3"
        segment_file = os.path.join(output_folder, segment_audio_filename)
        make_segment(audio, start_time_ms, end_time_ms, segment_file)

        # Create context text: previous sub + current sub + next sub
        context = " ".join([get_subtitle_text(subs, index - 1), sub.text, get_subtitle_text(subs, index + 1)])

        # Calculate start and end times for context audio segment
        prev_sub_start_time_ms = 0 if index == 0 else subs[index - 1].start.ordinal
        next_sub_end_time_ms = len(audio) if index + 1 >= len(subs) else subs[index + 1].end.ordinal

        # Create context audio file
        context_audio_filename = f"{base_name}_context_{index}.mp3"
        create_context_audio_file(audio, prev_sub_start_time_ms, next_sub_end_time_ms,
                                                       output_folder, context_audio_filename, index)

        # Print output
        timing = f"{sub.start} --> {sub.end}"
        print(
            f"{sub.text}\t[Sound:{segment_audio_filename}]\t{context}\t[Sound:{context_audio_filename}]\t{base_name}\t{timing}\t{show_name}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Split an audio file based on SRT subtitles and output the results in tab-separated format.')
    parser.add_argument('--audio_file', type=str, required=True, help='Path to the audio file (MP3 or WAV).')
    parser.add_argument('--srt_file', type=str, required=True, help='Path to the corresponding SRT subtitle file.')
    parser.add_argument('--output_folder', type=str, required=True, help='Folder to save the split audio segments.')
    parser.add_argument('--show_name', type=str, required=True, help='Name of the show.')
    parser.add_argument('--min_duration_ms', type=int, default=1000, help='Minimum duration of a segment in milliseconds.')
    parser.add_argument('--min_text_length', type=int, default=10, help='Minimum length of subtitle text for a segment.')

    args = parser.parse_args()
    split_audio_by_srt(args.audio_file, args.srt_file, args.output_folder, args.show_name, args.min_duration_ms, args.min_text_length)
