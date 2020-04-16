import queue
import sys
import tkinter as tk
from multiprocessing import Process, Value
from pathlib import Path
from time import sleep

import sounddevice as sd
import soundfile as sf

path = Path("recordings")
path.mkdir(exist_ok=True)

with open("utts.data", "r") as f:
    arctic = f.readlines()
labels = list(map(lambda x: x[2:14], arctic))
utts = list(map(lambda x: x[16:-4], arctic))

print(sd.query_devices())
# Fill in the device you want to use for input (and set the channel you want to record over, in my case device 10 is an
# audio interface, and the microphone is plugged into the first input (channel 1)) and output (used for playback)
in_device = 10
out_device = 3
CHANNEL = 1
fs = 44100
sd.default.device = [in_device, out_device]
sd.default.samplerate = fs


def audio_process(labels, play, record, i):
    while True:
        if record.value:
            rec(labels[i.value], record)
        if play.value:
            playback(labels[i.value])
            play.value = 0
        sleep(0.1)


def playback(name):
    file = path / (name + ".wav")
    print("Playback", file)
    if file.is_file():
        data, fs = sf.read(path / (name + ".wav"), dtype='float32')
    else:
        data, fs = sf.read(path / "not_found.wav")
    sd.play(data, fs)


def rec(name, record):
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())
    
    print("Recording", name)
    # Make sure the file is opened before recording anything:
    with sf.SoundFile(path / (name + ".wav"), mode='w', samplerate=fs, channels=CHANNEL, subtype=None) as file:
        with sd.InputStream(samplerate=fs, device=in_device, channels=CHANNEL, callback=callback):
            while record.value:
                file.write(q.get())


# Recorder GUI
if __name__ == "__main__":
    i = 0
    i_mp = Value('i', i)
    record = Value('i', 0)
    play = Value('i', 0)
    
    root = tk.Tk()
    text = tk.StringVar()
    label = tk.StringVar()
    text.set("{}".format(utts[i]))
    label.set("{}:".format(labels[i]))
    
    p = Process(target=audio_process, args=(labels, play, record, i_mp))
    p.daemon = True
    p.start()
    
    
    def key(event):
        global i, play
        code = event.keycode
        i_mp.value = i
        
        if code == 32:
            # Record/stop recording - space
            if record.value == 0:
                record.value = 1
            else:
                record.value = 0
            l.config(fg="green" if not record.value else "red")
            p.join(0)
        elif code == 80:
            # Play/pause - p
            play.value = 1
            p.join(0)
            set_colour = lambda c: l.config(fg=c)
            set_colour("yellow")
            frame.after(1000, lambda: set_colour("green"))
        elif code == 38:
            # up
            if i <= 0:
                i = -1
                text.set("This was the first sentence! Go forward instead!")
            else:
                i -= 1
                text.set("{}".format(utts[i]))
                label.set("{}".format(labels[i]))
        
        elif code == 40:
            # down
            if i == len(utts) - 1:
                i = len(utts)
                text.set("End of list already reached! Go back :)")
            else:
                i += 1
                text.set("{}".format(utts[i]))
                label.set("{}".format(labels[i]))
                if record.value:
                    i_mp.value = i
                    record.value = 0
                    p.join(0.01)
                    record.value = 1
                    p.join(0)
        elif code == 81:
            # quit - q
            p.terminate()
            root.destroy()
    
    
    frame = tk.Frame(root, width=900, height=900)
    frame.bind("<Key>", key)
    frame.pack()
    frame.focus_set()
    
    ll = tk.Label(textvariable=label, fg="green", font=("Helvetica", 60), anchor="sw", justify="left")
    # Make wraplength some function of window size and adjust placement accordingly in the future
    l = tk.Label(textvariable=text, fg="green", font=("Helvetica", 60), anchor="center", justify="center",
                 wraplength=600)
    ll.place(y=0)
    l.place(rely=0.2, relx=0.2)
    
    root.mainloop()
