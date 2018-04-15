#!/usr/bin/env python

'''
Spectrology
This script is able to encode an image into audio file whose spectrogram represents input image.

License: MIT
Website: https://github.com/solusipse/spectrology
'''

from PIL import Image, ImageOps
import os, wave, math, array, argparse, sys, timeit

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT", help="Text to be converted")
    parser.add_argument("-o", "--output", help="Name of the output wav file. Default value: out.wav).")
    args = parser.parse_args()

    minfreq = 200
    maxfreq = 20000
    wavrate = 44100
    pxs     = 30
    output  = "out.wav"
    rotate  = False
    invert  = False

    if args.output:
        output = args.output

    print('Input %s.' % args.INPUT)

    return (args.INPUT, output, minfreq, maxfreq, pxs, wavrate, rotate, invert)

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

    result.save('test.png', format='png')
    return result.convert('L')

def convert(inpt, output, minfreq, maxfreq, pxs, wavrate, rotate, invert):
    img = get_input_image(inpt)

    # rotate image if requested
    if rotate:
      img = img.rotate(90)

    # invert image if requested
    if invert:
      img = ImageOps.invert(img)

    output = wave.open(output, 'w')
    output.setparams((1, 2, wavrate, 0, 'NONE', 'not compressed'))

    freqrange = maxfreq - minfreq
    interval = freqrange / img.size[1]

    fpx = wavrate / pxs
    data = array.array('h')

    tm = timeit.default_timer()

    for x in xrange(img.size[0]):
        row = []
        for y in xrange(img.size[1]):
            yinv = img.size[1] - y - 1
            amp = img.getpixel((x,y))
            if (amp > 0):
                row.append( genwave(yinv * interval + minfreq, amp, fpx, wavrate) )

        for i in xrange(fpx):
            for j in row:
                try:
                    data[i + x * fpx] += j[i]
                except(IndexError):
                    data.insert(i + x * fpx, j[i])
                except(OverflowError):
                    if j[i] > 0:
                      data[i + x * fpx] = 32767
                    else:
                      data[i + x * fpx] = -32768

        sys.stdout.write("Conversion progress: %d%%   \r" % (float(x) / img.size[0]*100) )
        sys.stdout.flush()

    output.writeframes(data.tostring())
    output.close()

    tms = timeit.default_timer()

    print("Conversion progress: 100%")
    print("Success. Completed in %d seconds." % int(tms-tm))

def genwave(frequency, amplitude, samples, samplerate):
    cycles = samples * frequency / samplerate
    a = []
    for i in xrange(samples):
        x = math.sin(float(cycles) * 2 * math.pi * i / float(samples)) * float(amplitude)
        a.append(int(math.floor(x)))
    return a

if __name__ == '__main__':
    inpt = parser()
    convert(*inpt)
