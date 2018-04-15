from PIL import Image, ImageOps
import os, wave, math, array, argparse, sys, timeit

# constants
MIN_FREQ = 200
MAX_FREQ = 20000
Fs = 44100
PIXELS_PS = 30


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",
                        help="Text to be converted")
    parser.add_argument("-o",
                        "--output",
                        help="Name of the output wav file. Default value: out.wav).")
    args = parser.parse_args()

    if args.output is not None:
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
    text_image = get_input_image(inpt)

    output = wave.open(output, 'w')
    output.setparams((1, 2, Fs, 0, 'NONE', 'not compressed'))

    interval = (MAX_FREQ - MIN_FREQ) / text_image.size[1]

    frames_pp = Fs / PIXELS_PS
    data = array.array('h')

    tm = timeit.default_timer()

    for x in xrange(text_image.size[0]):
        row = list()
        for y in xrange(text_image.size[1]):
            yinv = text_image.size[1] - y - 1
            ampl = text_image.getpixel((x,y))
            if (ampl > 0):
                row.append( genwave(yinv * interval + MIN_FREQ, ampl, frames_pp, Fs) )

        for i in xrange(frames_pp):
            for j in row:
                try:
                    data[i + x * frames_pp] += j[i]
                except(IndexError):
                    data.insert(i + x * frames_pp, j[i])
                except(OverflowError):
                    if j[i] > 0:
                      data[i + x * frames_pp] = 32767
                    else:
                      data[i + x * frames_pp] = -32768

        sys.stdout.write("Conversion progress: %d%%   \r" % (float(x) / text_image.size[0]*100) )
        sys.stdout.flush()

    output.writeframes(data.tostring())
    output.close()

    tms = timeit.default_timer()

    print("Conversion progress: 100%")
    print("Success. Completed in %d seconds." % int(tms-tm))

def genwave(f, ampl, samples, Fs):
    cycles = samples * f / Fs
    a = list()
    for i in xrange(samples):
        x = math.sin(float(cycles) * 2 * math.pi * i / float(samples)) * float(ampl)
        a.append(int(math.floor(x)))
    return a

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
