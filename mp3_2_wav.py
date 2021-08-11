
# import required modules
from os import path
from pydub import AudioSegment
import uuid

def temporaryFileNameGenerator():
    return str(uuid.uuid4()) 
# assign files
input_file = "Giveon - HEARTBREAK ANNIVERSARY (Karaoke Version).mp3"
output_file = temporaryFileNameGenerator()+".wav"
  
 
# convert mp3 file to wav file
sound = AudioSegment.from_mp3(input_file)
sound.export(output_file, format="wav")