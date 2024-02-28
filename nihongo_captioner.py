import sys
import os

import requests

from PIL import Image, ImageFont, ImageDraw
import fugashi

FONT_DIR = "./fonts/"
OUTPUT_DIR = "./outputs/"
INPUT_DIR = "./inputs/"

# FONT = "nijimi-mincho.otf"
FONT = "NotoSerifJP.otf"
FONT_SIZE = 40
MAX_LENGTH = 14

# tagger = fugashi.Tagger()
tagger = fugashi.Tagger('-Owakati')


def stick_punctiation(tokens):
    for i, token in reversed(list(enumerate(tokens))):
        if token == "「":
            tokens[i+1] = tokens[i] + tokens[i+1]
            del tokens[i]
        elif token in "、。！？」〜ー":
            tokens[i-1] = tokens[i-1] + tokens[i]
            del tokens[i]
    return tokens


def parse_nihongo(quote):
    words = tagger(quote)
    words = [str(w) for w in words]
    words = stick_punctiation(words)
    lines = {0: ""}
    i = 0 
    for word in words:
        # print(word, len(word))
        if word == "　":
            i += 1
            lines[i] = ""
        elif len(lines[i]) + len(word) <= MAX_LENGTH:
            lines[i] += word
        else:
            i += 1
            lines[i] = word
    print(lines)
    quote = ""
    for j in range(i):
        quote += lines[j] + "\n"
    quote += lines[i]
    return quote


def make_meme(media, quote, localImage):

    response = requests.get(media, stream=True)
    img = Image.open(response.raw)
    if len(quote):
        quote = parse_nihongo(quote)

        newLineCount = len(quote.split('\n'))
        textFont = ImageFont.truetype(FONT_DIR + FONT, FONT_SIZE)
        width, height = img.size
        draw = ImageDraw.Draw(img)
        left, top, right, bottom = draw.multiline_textbbox((0, 0), quote, font=textFont)
        textWidth, textHeight = right - left, bottom - top

        baseX, baseY = ((width - textWidth)/2, height - (20 + textHeight + newLineCount * 20))
        shadowcolor = 'black'

        delta = 2
        for x in [-1, 1, 0]:
            for y in [1, -1, 0]:
                posX = baseX + delta*x
                posY = baseY + delta*y
                draw.multiline_text((posX, posY), quote, 
                                    font=textFont, fill=shadowcolor, align='center', spacing=20)

        draw.multiline_text((baseX, baseY), quote, font=textFont, align='center', spacing=20)

    img.save(OUTPUT_DIR + localImage + '.png')


def get_url(url):
    return url.replace("caption", "meme")


def parse_input(meme_name):
    meme_input = INPUT_DIR + meme_name
    os.makedirs(OUTPUT_DIR + meme_name, exist_ok=True)
    with open(meme_input, "r") as f:
        for i, line in enumerate(f.readlines()):
            line = line.strip()
            if i % 2 == 0:
                url = get_url(line)
            else:
                make_meme(url, line, meme_name + "/" + str(i//2))


if __name__ == "__main__":
    parse_input(sys.argv[1])
