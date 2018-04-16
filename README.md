Alt-H1
======
Tool to hide text in a wavfile's spectrogram.
Dependency: PIL (Python Imaging Library)

#How to use:
1. Clone this repository.
2. Make sure you have PIL (Python Imaging Library) installed.
3. Run something like the example below  
   -`python text_to_wav.py "hello world" --output="example.wav"`
4. Look at the spectrogram of your wav file (example.wav in this case)  
    -In Matlab:  
    -`[data, Fs] = audioread('example.wav')`  
    -`spectrogram(data, 1000, 0, 1000, 44100, 'yaxis')`  
    -Or you can look at it in realtime using an online spectrum analyzer
    or something.
5. In the Matlab view, you may need to stretch it vertically if your input
text was long
