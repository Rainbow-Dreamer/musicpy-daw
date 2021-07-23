# easy sampler

This is a music sampler and tracker to make music with musicpy.

![image](https://github.com/Rainbow-Dreamer/easy-sampler/blob/main/previews/1.jpg?raw=True)

You can write any musicpy codes inside the input text area at the bottom.

To play or export a musicpy data structure, like note, chord, track and piece, there are 2 ways to write in the input text area.

1. You can just write the musicpy data structure in one line and press `Play Musicpy Code` to play it and press `Export` to export to audio files. 
Note that in this way you must write the musicpy data structure in one line to make it work, for example,
```python
C('Cmaj7') % (1, 1/8) % 2
```

2. To write more complicated musicpy codes to get the resulted musicpy data structure you want to play or export, you can just write musicpy codes as usual, but on the last line you must write `play [musicpy data structure], bpm, channel number`, the BPM and channel number could be omitted, if the BPM is omitted, the sampler will use default BPM, if the channel number is omitted, the sampler will use channel number 1. 
Note that channel number is 1-based. Here is an example,
```python
part1 = C('Cmaj7') % (1, 1/8) % 2
part2 = C('Am7') % (1, 1/8) % 2
result = part1 | part2
play result
# with BPM and channel number: play result, 150, 1
```

The input text area can accept any python codes, so you can combine musicpy codes with any of the python codes (musicpy itself is a python package).

For all of the functionalities and features of easy sampler, you can refer to the documentation of musicpy sampler module (click [here](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy-sampler-module)).

If there are visualized replacements of some parts of the functionalities in easy sampler (buttons and listboxes), then you don't need to look at those parts, since they are a non-GUI version of the functionalities of easy sampler, and they are not supported in the input text area in easy sampler.

For the other parts, they are supported in the input text area in easy sampler.

Note that when you have any special effects, pans, volumes in your musicpy data structure to play, easy sampler will automatically convert it to an audio object firstly and then play it, this will usually be slower than directly play it, so you need to wait for a little time. 

`esp` is the project file format I invented specially for easy sampler, which stands for `Easy Sampler Project`, it stores the information of your current project, and you can save your current working progress to an esp file at any time and reload it by opening the esp file again in easy sampler.
