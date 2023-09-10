import argparse
import os

from Mykytea import Mykytea


def add_furigana(text):
    # create an object with an option string
    mk = Mykytea("-model ./jp-0.4.7-1.mod")

    # Get all analyzed tags for potential readings
    tags = mk.getAllTags(text)

    furigana_list = []
    all_readings = []

    for word in tags:
        surface = word.surface
        readings = [reading[0] for reading in word.tag[1]]
        primary_reading = readings[0]

        if surface != primary_reading:
            furigana_list.append(f"{surface}({primary_reading})")
        else:
            furigana_list.append(surface)

        all_readings.append("/".join(readings))

    furigana_text = " ".join(furigana_list)
    readings_attribute = " ".join(all_readings)

    return furigana_text, readings_attribute



def read_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip().split('\n\n')


def extract_timestamp_and_text(srt_block):
    lines = srt_block.split('\n')
    start_timestamp, end_timestamp = lines[1].split(' --> ')

    # Extracting only the mm:ss from the timestamps
    visible_start = ":".join(start_timestamp.split(":")[1:3]).split(',')[0]

    text = ' '.join(lines[2:])
    return visible_start, start_timestamp, end_timestamp, text


def generate_html_content(srt_blocks):
    html_blocks = []

    for idx, block in enumerate(srt_blocks, 1):
        visible_timestamp, start_timestamp, end_timestamp, text = extract_timestamp_and_text(block)

        text_with_furigana, possible_readings = add_furigana(text)
        html_block = f'<div>\n\t<a id="sub-{idx}" href="#sub-{idx}"><span class="timestamp" data-subbegin="{start_timestamp}" data-subend="{end_timestamp}" data-possiblereadings="{possible_readings}">{visible_timestamp}</span></a>\n\t<p class="subtitle-text">{text_with_furigana}</p>\n</div>\n'
        print(html_block)
        html_blocks.append(html_block)

    return '\n'.join(html_blocks)



def wrap_html(html_content, filename):
    template = '''<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subtitles to HTML</title>
    <style>
        body{{
            margin: 40px auto;
            max-width: 650px;
            line-height: 1.6;
            font-size: 18px;
            color: #444;
            padding: 0 10px;
        }}
        h1{{
            line-height: 1.2;
        }}
        .timestamp, .timestamp a, a:link {{
            color: lightgrey;
            font-size: small;
            font-style: italic;
            font-family: "Arial", sans-serif;
            text-decoration: none;
            bor
        }}
        .subtitle-text {{
            font-size: larger;
            font-family: "Yu Gothic", sans-serif;
        }}
    </style>
</head>

<body>
<h1>{filename}</h1>
{content}
</body>

</html>
'''
    return template.format(content=html_content, filename=filename)


def main():
    parser = argparse.ArgumentParser(description="Convert .srt file to an HTML format with custom styling.")
    parser.add_argument('input', type=str, help="Path to the .srt file")
    parser.add_argument('output', type=str, help="Path to save the generated HTML file")

    args = parser.parse_args()

    srt_content = read_srt(args.input)
    html_blocks = generate_html_content(srt_content)

    # Extract filename without extension
    filename_without_ext = os.path.basename(args.input).split('.')[0]

    final_html = wrap_html(html_blocks, filename_without_ext)

    with open(args.output, 'w', encoding='utf-8') as out_file:
        out_file.write(final_html)

    print(f"HTML file generated at: {args.output}")


if __name__ == "__main__":
    main()
