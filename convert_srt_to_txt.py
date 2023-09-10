import argparse
import re

def remove_timestamps(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_content = []
    for line in lines:
        # Skip subtitle sequence numbers and timestamps
        if re.match(r'^\d+$', line.strip()) or re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line.strip()):
            continue
        cleaned_content.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(cleaned_content))

def main():
    parser = argparse.ArgumentParser(description="Remove timestamps and sequence numbers from an SRT file.")
    parser.add_argument("input_file", help="Path to the input SRT file.")
    parser.add_argument("output_file", help="Path to save the cleaned SRT file.")

    args = parser.parse_args()

    remove_timestamps(args.input_file, args.output_file)
    print(f"Timestamps and sequence numbers removed. Cleaned content saved to {args.output_file}")

if __name__ == "__main__":
    main()
