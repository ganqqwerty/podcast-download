import os
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

def process_file_pair(args):
    mp3_path, srt_path, output_folder, show_name = args
    subprocess.run(['python3', 'srt_to_anki.py',
                    '--audio_file', mp3_path,
                    '--srt_file', srt_path,
                    '--output_folder', output_folder,
                    '--show_name', show_name])

def process_directory(directory, show_name, output_folder, error_log_path, num_processes):
    # Get all files in the directory
    files = os.listdir(directory)

    # Filter out the .mp3 and .srt files
    mp3_files = sorted([f for f in files if f.endswith('.mp3')])
    srt_files = sorted([f for f in files if f.endswith('.srt')])

    # Create a dictionary with mp3 filenames as keys and corresponding srt filenames as values
    file_dict = {mp3: mp3.replace('.mp3', '.srt') for mp3 in mp3_files}
    tasks = []

    with open(error_log_path, 'w') as error_log:
        for mp3, srt in file_dict.items():
            if srt not in srt_files:
                error_log.write(f"Missing SRT for {mp3}\n")
                continue

            mp3_path = os.path.join(directory, mp3)
            srt_path = os.path.join(directory, srt)
            tasks.append((mp3_path, srt_path, output_folder, show_name))

        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            list(executor.map(process_file_pair, tasks))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process all MP3 and SRT pairs in a directory and output the results in tab-separated format.')
    parser.add_argument('--directory', type=str, required=True, help='Path to the directory containing MP3 and SRT files.')
    parser.add_argument('--show_name', type=str, required=True, help='Name of the show.')
    parser.add_argument('--output_folder', type=str, required=True, help='Folder to save the split audio segments.')
    parser.add_argument('--error_log', type=str, default='error_log.txt', help='Path to the error log file.')
    parser.add_argument('--num_processes', type=int, default=4, help='Number of parallel processes to run.')

    args = parser.parse_args()
    process_directory(args.directory, args.show_name, args.output_folder, args.error_log, args.num_processes)
