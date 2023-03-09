# easy sampler

[English] [[中文](#easy-sampler-1)]

This is a music sampler and tracker to make music with musicpy.

![image](previews/1.jpg)

## Download

You can download the latest version of easy sampler from [here](https://www.jianguoyun.com/p/DfRvuNUQhPG0CBiVkqYE)

## Usage

You can write any musicpy codes inside the input text area at the bottom.

To play or export a musicpy data structure, like note, chord, track and piece, there are 3 ways to write in the input text area.

1. You can just write the musicpy data structure in one line and press `Play Musicpy Code` to play it and press `Export` to export to audio files. 
   Note that in this way you must write the musicpy data structure in one line to make it work, for example,
   ```python
   C('Cmaj7') % (1, 1/8) * 2
   ```

2. To write more complicated musicpy codes to get the resulted musicpy data structure you want to play or export, you can just write musicpy codes as usual, but you must write
   ```python
   play [musicpy data structure], bpm, channel_number
   ```
   to set the current music object to be play or export. When you run the code, it will play the musicpy data structure, when you click the export button to export, it will export  the musicpy data structure.  
   The BPM and channel number could be omitted, if the BPM is omitted, the sampler will use default BPM, if the channel number is omitted, the sampler will use channel number 1.
   Note that channel number is 1-based.
   Here is an example,
   ```python
   part1 = C('Cmaj7') % (1, 1/8) * 2
   part2 = C('Am7') % (1, 1/8) * 2
   result = part1 | part2
   play result
   # with BPM and channel number: play result, 150, 1
   ```

3. You can also use `play` and `export` function that takes essentially the same parameters as the `play` and `export` function of the sampler in musicpy sampler module, which supports more parameters for more customized play and export requirements.  
   For the usage of `play` and `export` function, you can refer to the documentation of musicpy sampler module, I will give the link below.
   
   ```python
   play(current_chord,
        bpm=None,
        channel=1,
        length=None,
        extra_length=None,
        track_lengths=None,
        track_extra_lengths=None,
        soundfont_args=None)
   
   export(current_chord,
          mode='wav',
          action='export',
          channel=1,
          bpm=None,
          length=None,
          extra_length=None,
          track_lengths=None,
          track_extra_lengths=None,
          export_args={},
          soundfont_args=None,
          write_args={})
   ```

The input text area can accept any python codes, so you can combine musicpy codes with any of the python codes (musicpy itself is a python package).

For all of the functionalities and features of easy sampler, you can refer to the documentation of musicpy sampler module (click [here](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy-sampler-module)).

If there are visualized replacements of some parts of the functionalities in easy sampler (buttons and listboxes), then you don't need to look at those parts, since they are a non-GUI version of the functionalities of easy sampler, and they are not supported in the input text area in easy sampler.

For the other parts, they are supported in the input text area in easy sampler.

Note that when you have any special effects, pans, volumes in your musicpy data structure to play, easy sampler will automatically convert it to an audio object firstly and then play it, this will usually be slower than directly play it, so you need to wait for a little time. 

`esp` is the project file format I invented specially for easy sampler, which stands for `Easy Sampler Project`, it stores the information of your current project, and you can save your current working progress to an esp file at any time and reload it by opening the esp file again in easy sampler.

Update (2021/9/5): Now soundfonts files are supported, you can load any .sf2, .sf3, .dls files into this sampler and use it to play and export audio files, making music using soundfonts files with musicpy.

Update (2021/10/12): Now there is a debug window, you can open the debug window first and then write `output(object1, object2, ...)` in the input text area, when you run the code, the objects in the `output` function will be printed in the debug window, the usage is like `print` function.

# easy sampler

[[English](#easy-sampler)] [中文]

这是一个音乐取样机和tracker，可以用musicpy制作音乐。

![image](previews/2.jpg)

## 下载

你可以从[这里](https://www.jianguoyun.com/p/DfRvuNUQhPG0CBiVkqYE)下载easy sampler的最新版本

## 使用

你可以在底部的输入文本区写任何musicpy代码。

要播放或导出一个musicpy数据结构，如音符、和弦、音轨和乐曲，有3种方法可以在输入文本区写。

1. 你可以只写一行musicpy数据结构，然后按`演奏musicpy代码`来播放它，按`导出`来导出音频文件。
   注意，在这种方式下，你必须把musicpy的数据结构写在一行中才行，比如说
   ```python
   C('Cmaj7') % (1, 1/8) * 2
   ```

2. 要写更复杂的musicpy代码来获得你想播放或导出的musicpy数据结构，你可以像往常一样写musicpy代码，但你必须写
   ```python
   play [musicpy数据结构], bpm, 通道编号
   ```
   来设置要用来播放或者导出的音乐对象。当你运行代码时，会播放这个musicpy的数据结构，当你点击导出按钮进行导出时，会导出这个musicpy的数据结构。
   BPM和通道编号可以省略，如果省略BPM，取样机将使用默认BPM，如果省略通道编号，取样机将使用通道编号1。
   注意，通道编号是基于1的。下面是一个例子
   ```python
   part1 = C('Cmaj7') % (1, 1/8) * 2
   part2 = C('Am7') % (1, 1/8) * 2
   result = part1 | part2
   play result
   # 用BPM和通道编号: play result, 150, 1
   ```

3. 你也可以使用和musicpy取样机模块的取样机的`play`和`export`函数的参数基本相同的`play`和`export`函数，支持更多参数和更加定制化的播放和导出的要求。  
   如何使用`play`和`export`函数，你可以参考musicpy取样机模块的使用文档，我在下面会给链接。
   ```python
   play(current_chord,
        bpm=None,
        channel=1,
        length=None,
        extra_length=None,
        track_lengths=None,
        track_extra_lengths=None,
        soundfont_args=None)
   
   export(current_chord,
          mode='wav',
          action='export',
          channel=1,
          bpm=None,
          length=None,
          extra_length=None,
          track_lengths=None,
          track_extra_lengths=None,
          export_args={},
          soundfont_args=None,
          write_args={})
   ```

输入文本区可以接受任何python代码，因此你可以将musicpy代码与任何python代码结合起来（musicpy本身就是一个python包）。

关于easy sampler的所有功能和特点，你可以参考musicpy取样机模块的使用文档(点击[这里](https://github.com/Rainbow-Dreamer/musicpy/wiki/musicpy%E5%8F%96%E6%A0%B7%E6%9C%BA%E6%A8%A1%E5%9D%97))。

如果easy sampler中的某些功能部分（按钮和列表框）有可视化的替换，那么你不需要看这些部分，因为它们是easy sampler的非GUI版本的功能，而且在easy sampler的输入文本区不支持它们。

对于其他部分，它们在easy sampler的输入文本区中是被支持的。

注意，当你的musicpy数据结构中有任何特效、平移、音量要播放时，easy sampler会先自动把它转换成音频对象，然后再播放，这通常会比直接播放慢，所以你需要等待一点时间。

`esp`是我专门为easy sampler发明的工程文件格式，它代表`Easy Sampler Project`，它存储了你当前工程的信息，你可以随时把你当前的工程进度保存到esp文件中，并在easy sampler中再次打开esp文件来重新加载。

更新 (2021/9/5): 现在已经添加对于soundfonts音源文件的支持，你可以加载任何的.sf2, .sf3, .dls 音源文件到这个取样机中来播放和导出音频文件，用soundfonts音源文件和musicpy来制作音乐。

更新 (2021/10/12): 新增调试窗口，你可以打开调试窗口，然后在输入文本区写 `output(object1, object2, ...)`, 当你运行代码, 在 `output` 函数里的对象会被打印到调试窗口中, 用法与 `print` 函数相同。

