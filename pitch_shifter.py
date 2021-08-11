
from scipy.io import wavfile
import numpy as np
import os
from pydub import AudioSegment
import uuid
from pydub.playback import play
import librosa
import soundfile as sf

def temporaryFileNameGenerator():
    return str(uuid.uuid4()) 

# assign files
input_file = "Giveon - HEARTBREAK ANNIVERSARY (Karaoke Version).mp3"
file_name = os.path.splitext(input_file)[0]
output_file = temporaryFileNameGenerator()+".wav"

print('pitch change steps')
n = input()
 
# convert mp3 file to wav file
sound = AudioSegment.from_mp3(input_file)
sound.export(output_file, format="wav")

y, sr = librosa.load(output_file, sr=16000) # y is a numpy array of the wav file, sr = sample rate
y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=n) # shifted by 4 half steps

#export / save pitch changed sound
sf.write(file_name +"_"+str(n) + "_steps_shifted.wav", y_shifted, sr, subtype='PCM_24')

os.remove(output_file)
