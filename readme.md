# Basic SpeechRecorder clone

`rec.py` contains a basic
[SpeechRecorder](http://www.cstr.ed.ac.uk/research/projects/speechrecorder/) clone written
in Python which should be system-agnostic. Tested using Python 3.7, but 3.6+ should work
well.

This code is set up to record Arctic A, but it is easy to adopt it for other texts.

Current version only saves one take. If you redo a part, it will overwrite the previous
take.

This code is not the prettiest, I just wanted a quick tool that works. I do think all the
bits around it (like saving multiple takes or loading different utterances) should be very
easy to add if you know some python. Currently this tool spins up a separate process that
handles audio recording/playback. I tried using a simple thread for this, but portaudio
would not find the ASIO driver for my audio interface then. If anyone can figure out how
to make this work with threads, that would be better (no while True: loop needed).

## Prerequisites
Python packages:

* [PySoundFile](https://pysoundfile.readthedocs.io/en/latest/)
* [python-sounddevice](https://python-sounddevice.readthedocs.io/en/0.3.15/installation.html)
    * I recommend using [this](https://www.lfd.uci.edu/~gohlke/pythonlibs/#sounddevice)
      version (e.g. `pip install sounddevice‑0.3.15‑cp37‑cp37m‑win_amd64.whl`) as it
      includes a working version of PyAudio

You need to configure the correct Input and Output devices by hand for this tool to work:

Run the following commands to list available audio devices in a Python interpreter:

```python
import sounddevice as sd
print(sd.query_devices())
``` 

From the list, note the indices of the devices you want to use for playback/recording and fill their numbers into the following lines of code in `rec.py`:
```python
in_device = 10
out_device = 3
CHANNEL = 1
``` 
If you're using an audio interface with many input channels, and your microphone is plugged into input 8, put `CHANNEL=8`.

The default will record in 16kHz as this is the sampling rate used for building the voice
according to [the unit selection
assignment](http://www.speech.zone/exercises/build-a-unit-selection-voice/?style=onepage).
If you need higher/lower quality recordings, change `fs` to the required sampling
rate. Default recording setting is 32bit float - sounddevice also allows for 16/24bit
recordings. Look into the documentation to change it if necessary.

## How to use
Run `rec.py` with `python rec.py`.

* Press `up` and `down` to navigate sentences
* Press `space` to record
* Press `down` while recording to immediately record the next utterance (without stopping
  in between)
* When not recording, press `p` to listen to the recorded audio
* Press `q` to quit.

To use a text other than Arctic A, change `labels` and `utts` to be (same-length) python
lists containing the identifier (used for saved file names) and utterances.


