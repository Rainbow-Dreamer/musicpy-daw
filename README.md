# easy sampler

[English] [[中文](#easy-sampler-1)]

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

# easy sampler

[[English](#easy-sampler)] [中文]

这是一个音乐取样机和tracker，可以用musicpy制作音乐。

![image](https://github.com/Rainbow-Dreamer/easy-sampler/blob/main/previews/2.jpg?raw=True)

你可以在底部的输入文本区写任何musicpy代码。

要播放或导出一个musicpy数据结构，如音符、和弦、音轨和乐曲，有2种方法可以在输入文本区写。

1. 你可以只写一行musicpy数据结构，然后按`演奏musicpy代码`来播放它，按`导出`来导出音频文件。
注意，在这种方式下，你必须把musicpy的数据结构写在一行中才行，比如说
```python
C('Cmaj7') % (1, 1/8) % 2
```

2. 要写更复杂的musicpy代码来获得你想播放或导出的musicpy数据结构，你可以像往常一样写musicpy代码，但在最后一行你必须写`play [musicpy data structure], bpm, channel number`，BPM和通道编号可以省略，如果省略BPM，取样机将使用默认BPM，如果省略通道编号，取样机将使用通道编号1。
注意，通道编号是基于1的。下面是一个例子
```python
part1 = C('Cmaj7') % (1, 1/8) % 2
part2 = C('Am7') % (1, 1/8) % 2
result = part1 | part2
play result
#用BPM和通道编号: play result, 150, 1
```

输入文本区可以接受任何python代码，因此你可以将musicpy代码与任何python代码结合起来（musicpy本身就是一个python包）。

关于easy sampler的所有功能和特点，你可以参考musicpy取样机模块的文档(点击[这里](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy-sampler-module-musicpy%E5%8F%96%E6%A0%B7%E6%9C%BA%E6%A8%A1%E5%9D%97))。

如果easy sampler中的某些功能部分（按钮和列表框）有可视化的替换，那么你不需要看这些部分，因为它们是easy sampler的非GUI版本的功能，而且在easy sampler的输入文本区不支持它们。

对于其他部分，它们在easy sampler的输入文本区中是被支持的。

注意，当你的musicpy数据结构中有任何特效、平移、音量要播放时，easy sampler会先自动把它转换成音频对象，然后再播放，这通常会比直接播放慢，所以你需要等待一点时间。

`esp`是我专门为easy sampler发明的工程文件格式，它代表`Easy Sampler Project`，它存储了你当前工程的信息，你可以随时把你当前的工程进度保存到esp文件中，并在easy sampler中再次打开esp文件来重新加载。
