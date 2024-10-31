import os
import argparse
import shutil
import logging

def move_correct_files(src_directory, dest_directory, silent_mode):
    # Set up logging
    logging.basicConfig(level=(logging.ERROR if silent_mode else logging.INFO))

    if not os.path.exists(dest_directory):
        os.makedirs(dest_directory)

    moved_count = 0
    for filename in os.listdir(src_directory):
        if filename.endswith('.mp3'):
            base, _ = os.path.splitext(filename)
            mp3_path = os.path.join(src_directory, filename)
            wav_path = os.path.join(src_directory, base + '.wav')
            srt_path = os.path.join(src_directory, base + '.srt')
            buggy_srt_path = os.path.join(src_directory, base + '_buggy.srt')

            if os.path.isfile(wav_path) and os.path.isfile(srt_path): #and not os.path.isfile(buggy_srt_path):
                # Move files
                shutil.move(mp3_path, dest_directory)
                shutil.move(wav_path, dest_directory)
                shutil.move(srt_path, dest_directory)
                moved_count += 1
                logging.info(f'Moved group: {filename}, {base}.wav, {base}.srt')
            else:
                # Logging reasons why not moved
                if not os.path.isfile(wav_path):
                    logging.info(f'Left {filename} because corresponding .wav file is missing.')
                if not os.path.isfile(srt_path):
                    logging.info(f'Left {filename} because corresponding .srt file is missing.')
                # if os.path.isfile(buggy_srt_path):
                #     logging.info(f'Left {filename} because of the presence of a _buggy.srt file.')

    logging.info(f'Moved {moved_count} file groups in total.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Move correct groups of mp3, wav, and srt files to another directory.')
    parser.add_argument('src_directory', help='Source directory containing the files.')
    parser.add_argument('dest_directory', help='Destination directory to move correct files to.')
    parser.add_argument('--silent', help='Activate silent mode (no output).', action='store_true')

    args = parser.parse_args()

    move_correct_files(args.src_directory, args.dest_directory, args.silent)
