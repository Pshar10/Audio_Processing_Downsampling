#importing important libraries.
import pyaudio
import wave
import scipy
from scipy.fft import fft 
import matplotlib.pyplot as plt
import scipy.signal as sg
from ctypes import *
import struct
import numpy as np
import getch
from scipy.io import wavfile

#handled the warnings.
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)  
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)


#Starting the process from here.

FORMAT = pyaudio.paInt16
CHANNELS = 1 # we are taking mono channel 
RATE = 32000  # "RATE" is the number of samples collected per second (samples/sec)

CHUNK = 512  #"CHUNK" is the  number of frames
RECORD_SECONDS = 5 #setting the time peroid to record

WAVE_OUTPUT_FILENAME = "file.wav" #this will be the output file name

[b,a]=scipy.signal.iirfilter(4, 1900/16000,rp=60,btype='lowpass') #getting coefficients filter process,Numerator (b) and denominator (a) polynomials of the IIR filter

w,h = sg.freqz(b,a)
x = w * RATE * 1.0 / (2 * np.pi)
y = 20 * np.log10(abs(h))
plt.figure(figsize=(10,5))
plt.semilogx(x, y,1e-10)
plt.ylabel('Amplitude [dB]')
plt.xlabel('Frequency [Hz]')
plt.title('Frequency response')
plt.axis((10, 1e6, -100, 10))
plt.grid(which='both', axis='both')
plt.show()

mem=np.zeros(5-1)

rec = True
 
audio = pyaudio.PyAudio()

print("Please press space to proceed")


char = ord('1')

while(char != ord(' ')):

    char = getch.getch()
    char = ord(char)



# start Recording
if rec == True:
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
    print ("recording...")
    frames = []
 
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    
        data = stream.read(CHUNK)
        #Convert from stream of bytes to a list of short integers
        shorts = (struct.unpack( 'h' * CHUNK, data ))  
        samples=np.array(list(shorts),dtype=float)

    
        [samples,mem]=scipy.signal.lfilter(b, a, samples, zi=mem) #used filter here,applies filter forward in time 

    #Start the main DSP

    #Downsampling rate of N:
        N=2.0 
        s=(np.arange(0,CHUNK)%N)==0 #array of a unit pulse train(downsampled)
        #print(len(s))
    #multiply the signal with the unit pulse train:
        samples=samples*s
        samples=np.clip(samples, -32000,32000) #Clip (limit) the values in an array.
        samples=samples.astype(int)

    #converting from short integers to a stream of bytes in "data":

        data = struct.pack('h' * len(samples), *samples)

        frames.append(data) #put them back in frames
    
    print ("finished recording...")
 

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
 
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
print("Name of file : ",WAVE_OUTPUT_FILENAME)
waveFile.setnchannels(CHANNELS)
print("CHANNELS: ",CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
print("FORMAT: ",FORMAT)
waveFile.setframerate(RATE)
print("FRAME RATE: ",RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

spf = wave.open("file.wav", "r") #Plotting audio of saved file
signalb = spf.readframes(-1)
signalb = np.fromstring(signalb, "Int16")
plt.plot(signalb, label='After downsampling and filtering')
plt.legend()
plt.show()



play=pyaudio.PyAudio() #play the recorded audio
stream_play=play.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      output=True)
for data in frames: 
    stream_play.write(data)
stream_play.stop_stream()
stream_play.close()
play.terminate()