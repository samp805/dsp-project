from PIL import Image, ImageOps
import os, wave, math, array, argparse, sys, timeit
from functools import wraps
import numpy as np

# constants
MIN_FREQ = 200
MAX_FREQ = 20000
Fs = 44100 # samples/second
PIXELS_PS = 30 # pixels/second
SAMPLES_PP = Fs / PIXELS_PS # samples/pixel

def memoize(func):
    cache = dict()
    @wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",
                        help="Text to be converted")
    parser.add_argument("-o",
                        "--output",
                        help="Name of the output wav file. Default value: out.wav).")
    args = parser.parse_args()

    if args.output:
        output = args.output
    else:
        output = 'converted.wav'

    print('Text Entered: %s.' % args.input)

    return (args.input, output)

def get_input_image(inpt):
    chars = list(inpt)
    images = list()
    for char in chars:
        filename = get_char_filename(char)
        images.append(Image.open(filename).convert('L'))

    result_width = sum(map(lambda x:x.size[0], images))
    result_height = min(map(lambda x:x.size[1], images))

    result = Image.new('RGB', (result_width, result_height))
    index = 0
    for image in images:
        if index == 0:
            width = 0
        else:
            width += images[index-1].size[0]
        result.paste(im=image, box=(width, 0))
        index += 1

    result.save('outtest.png', format='png') # for testing
    return result.convert('L')

def convert(inpt, output):
    output = wave.open(output, 'w')
    output.setparams((1, 2, Fs, 0, 'NONE', 'not compressed'))

    text_image = ImageOps.invert(get_input_image(inpt))
    interval = (MAX_FREQ - MIN_FREQ) / text_image.size[1]

    tm = timeit.default_timer()
    data = array.array('h')
    for x in xrange(text_image.size[0]):
        row = list()
        for y in xrange(text_image.size[1]):
            freq = (text_image.size[1] - y - 1) * interval + MIN_FREQ
            if (text_image.getpixel((x,y)) > 0):
                row.append(genwave(freq, 500))
            else:
                row.append(genwave(freq, 10))

        for i in xrange(SAMPLES_PP):
            for j in row:
                try:
                    data[i + x * SAMPLES_PP] += j[i]
                except(IndexError):
                    data.insert(i + x * SAMPLES_PP, j[i])
                except(OverflowError):
                    if j[i] > 0:
                        data[i + x * SAMPLES_PP] = 32767
                    else:
                        data[i + x * SAMPLES_PP] = -32767

        sys.stdout.write("Conversion progress: %d%%   \r" % (float(x) / text_image.size[0]*100) )
        sys.stdout.flush()

    output.writeframes(data.tostring())
    output.close()

    tms = timeit.default_timer()

    print("Conversion progress: 100%")
    print("Success. Completed in %d seconds." % int(tms-tm))

@memoize
def genwave(f, ampl):
    freq = float(f / PIXELS_PS)/float(SAMPLES_PP)
    window = make_hamming(SAMPLES_PP)
    a = list()
    for i in xrange(SAMPLES_PP):
        x = float(ampl) * window[i] * math.sin(2 * math.pi * freq * i)
        a.append(int(math.floor(x)))
    return a

def make_hamming(N):
    """returns a length N hamming window"""
    return map(lambda x: 0.54 - 0.46 * math.cos(2*math.pi*x/(N-1)),
               range(N))

def get_char_filename(char):
    folder = os.path.join(os.getcwd(), 'characters')
    suffix = '.PNG'

    # if it's in range a - z or 0 - 9, it's just the letter itself
    if (char >= 'a' and char <= 'z') or (char >= '0' and char <= '9'):
        return os.path.join(folder, char + suffix)
    # if it's in range A - Z, it's like AA.PNG, for example
    elif (char >= 'A' and char <= 'Z'):
        return os.path.join(folder, char + char + suffix)
    # here comes the grueling part
    elif char == '_':
        return os.path.join(folder, '_' + suffix)
    elif char == '&':
        return os.path.join(folder, 'ampersand' + suffix)
    elif char == '\'':
        return os.path.join(folder, 'apostrophe' + suffix)
    elif char == '*':
        return os.path.join(folder, 'asterisk' + suffix)
    elif char == '\\':
        return os.path.join(folder, 'backslash' + suffix)
    elif char == '^':
        return os.path.join(folder, 'carrot' + suffix)
    elif char == ':':
        return os.path.join(folder, 'colon' + suffix)
    elif char == ',':
        return os.path.join(folder, 'comma' + suffix)
    elif char == '{':
        return os.path.join(folder, 'curly_bracket_start' + suffix)
    elif char == '}':
        return os.path.join(folder, 'curly_bracket_end' + suffix)
    elif char == '$':
        return os.path.join(folder, 'dollar_sign' + suffix)
    elif char == '=':
        return os.path.join(folder, 'equal' + suffix)
    elif char == '!':
        return os.path.join(folder, 'exclamation_point' + suffix)
    elif char == '/':
        return os.path.join(folder, 'forward_slash' + suffix)
    elif char == '>':
        return os.path.join(folder, 'greater_than' + suffix)
    elif char == '<':
        return os.path.join(folder, 'less_than' + suffix)
    elif char == '<':
        return os.path.join(folder, 'less_than' + suffix)
    elif char == '-':
        return os.path.join(folder, 'minus' + suffix)
    elif char == '|':
        return os.path.join(folder, 'or' + suffix)
    elif char == '(':
        return os.path.join(folder, 'parentheses_start' + suffix)
    elif char == ')':
        return os.path.join(folder, 'parentheses_end' + suffix)
    elif char == '%':
        return os.path.join(folder, 'percent' + suffix)
    elif char == '.':
        return os.path.join(folder, 'period' + suffix)
    elif char == '+':
        return os.path.join(folder, 'plus' + suffix)
    elif char == '#':
        return os.path.join(folder, 'pound' + suffix)
    elif char == '?':
        return os.path.join(folder, 'question_mark' + suffix)
    elif char == '"':
        return os.path.join(folder, 'quotes' + suffix)
    elif char == ';':
        return os.path.join(folder, 'semicolon' + suffix)
    elif char == ' ':
        return os.path.join(folder, 'space' + suffix)
    elif char == '[':
        return os.path.join(folder, 'square_bracket_start' + suffix)
    elif char == ']':
        return os.path.join(folder, 'square_bracket_end' + suffix)
    elif char == '~':
        return os.path.join(folder, 'twoodle' + suffix)

if __name__ == '__main__':
    inpt = parser()
    convert(*inpt)
