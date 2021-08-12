
from scipy.io import wavfile
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import librosa
import soundfile as sf
import os
from tkinter import StringVar
from tkinter import Menu
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import Tk
from tkinter import Frame
from tkinter import Label
from tkinter import IntVar
from tkinter import SOLID
from tkinter import Entry
from tkinter import Radiobutton
from tkinter import Button
from tkinter import DISABLED
from tkinter import HORIZONTAL
from tkinter import END
from tkinter import W
import json
import webbrowser
import re
import uuid

class MenuBar(Menu):
    def __init__(self, ws):
        Menu.__init__(self, ws)

        file = Menu(self, tearoff=False)
        file.add_command(label="Open Config",command=self.openConfig)    
        file.add_separator()
        file.add_command(label="Exit", underline=1, command=self.quit)
        self.add_cascade(label="File",underline=0, menu=file)

        help = Menu(self, tearoff=0)  
        help.add_command(label="About", command=self.about)  
        help.add_command(label="Release Notes", command=self.release)  
        help.add_command(label="Instructions", command=self.instruction)  

        self.add_cascade(label="Help", menu=help)  

    def openConfig(self):
        curr_directory = os.getcwd()
        try:
            os.system("notepad config.json")
        except Exception as e:
            messagebox.showerror('Error', str(e)+'\nCannot locate config.json at ' + curr_directory)

    def exit(self):
        self.exit
    def release(self):
        webbrowser.open('https://github.com/jinlee487/pitch_shifter')
    def instruction(self):
        curr_directory = os.getcwd()
        try:
            os.system("notepad instruction.txt")
        except Exception as e:
            messagebox.showerror('Error', str(e)+'\nCannot locate instruction.txt at ' + curr_directory)
    def about(self):
        messagebox.showinfo('About', 'This is an open source mp3/wav file pitch shifter made by me, Jinlee487.' 
                    +' I will not assume any responsibility of others using this resource in any fashion.')

class GUI(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.style = ttk.Style()
        self.style.theme_use("winnative")
        self.videoOrAudio = IntVar()
        self.title('pitch_shifter')
        self.geometry('575x400')
        frame = Frame(self,bd=2, relief=SOLID, padx=10, pady=10)

        Label(frame, text="File", font=('Times', 14)).grid(row=0, column=0, sticky=W, pady=10)
        Label(frame, text="Pitch", font=('Times', 14)).grid(row=1, column=0, sticky=W, pady=10)
        Label(frame, text="Path", font=('Times', 14)).grid(row=4, column=0, sticky=W, pady=10)
        
        self.FilePath = Entry(frame, font=('Times', 14), width=28,state=DISABLED)
        file_btn = Button(frame, width=4, text='new', font=('Times', 14), command=self.changeFilePath)

        current_value = StringVar(value=0.0)
        current_value.set(0.0)
        self.spin_box = ttk.Spinbox(
            frame,
            from_=-10,
            to=10,
            textvariable=current_value,
            wrap=True,
            increment=.5,
            width=10)
   
        self.downloadPath = Entry(frame, font=('Times', 14), width=28,state=DISABLED)
        path_btn = Button(frame, width=4, text='new', font=('Times', 14), command=self.changeDownloadPath)

        download_btn = Button(frame, width=10, text='PitchShift', font=('Times', 14), command=self.pitchShift)
        cancel_btn = Button(frame, width=10, text='Cancel', font=('Times', 14), command=self.destroy)

        self.FilePath.grid(row=0, column=1, columnspan=3, pady=2, padx=2)
        file_btn.grid(row=0, column=4)

        self.spin_box.grid(row=1, column=2, pady=2, padx=2)

        self.downloadText = scrolledtext.ScrolledText(frame,font=('Times', 14), height=3, width=38)

        self.downloadPath.grid(row=4, column=1, columnspan=3, pady=2, padx=2)
        path_btn.grid(row=4, column=4)

        self.downloadText.grid(row=5, column=1, columnspan=10, pady=3, padx=2)

        download_btn.grid(row=7, column=4, pady=2, padx=2)
        cancel_btn.grid(row=7, column=3, pady=2, padx=2)
        frame.place(x=50, y=50)

        menubar = MenuBar(self)  
        self.config(menu=menubar)
        self.readConfig()

    def pitchShift(self):

        input_file = self.FilePath.get()
        destination = self.downloadPath.get()
        self.downloadText.delete(1.0, END)
        self.downloadText.insert("end","")
        if not os.path.isfile(input_file):
            messagebox.showerror('Error', '\nCannot locate file')
            return
        if not self.check_steps():
            messagebox.showerror('Error', '\nchange the pitch change steps !')
            return
        else:
            n = float(self.spin_box.get())
        if destination.strip() == "":
            messagebox.showwarning("Warning", "Download file path is empty")
            return  

        file_name, ext = os.path.splitext(input_file)
        
        if ext.lower() != "wav":
            try:
                tempfile = self.convert_mp3_to_wav(input_file)
                self.downloadText.insert(1.0,"converting mp3 to wav \n")

            except Exception as e:
                return
        try:
            #shifting pitch using librosa
            if 'tempfile' in locals(): 
                y, sr = librosa.load(tempfile, sr=16000) # y is a numpy array of the wav file, sr = sample rate
                os.remove(tempfile)
            else:
                y, sr = librosa.load(input_file, sr=16000) # y is a numpy array of the wav file, sr = sample rate

            y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=n) # shifted by 4 half steps  
        except Exception as e:
            messagebox.showerror('Error', str(e)+'\nfailed to shift pitch!')
            return
        try:
            #export / save pitch changed sound
            export_file_path = self.uniquify(destination +"/"+os.path.basename(file_name) +"_"+str(n) + "_steps_shifted.wav")
            sf.write(export_file_path, y_shifted, sr, subtype='PCM_24')
            self.downloadText.insert(1.0,"Succefully saved file at location \n" + destination + "\n")
        except Exception as e:
            messagebox.showerror('Error', str(e)+'\nfailed export shifted wav file!')
            return
            
    def uniquify(self,path):
        filename, extension = os.path.splitext(path)
        counter = 1

        while os.path.exists(path):
            path = filename + "_" + str(counter) + "_" + extension
            counter += 1

        return path
    def check_steps(self):
        if not self.spin_box.get() or self.spin_box.get() == "0":
            return False
        else: 
            return True

    def convert_mp3_to_wav(self,input_file):
        # convert mp3 file to wav file
        print("convert_mp3_to_wav")
        try:
            output_file = os.getcwd() +"/"+self.temporaryFileNameGenerator()+".wav"
            sound = AudioSegment.from_mp3(input_file)
            sound.export(output_file, format="wav")
            print(output_file)
            return output_file
        except Exception as e:
            messagebox.showerror('Error', str(e)+'\nCannot convert mp3 to wav')
        
            
    def temporaryFileNameGenerator(self):
        return str(uuid.uuid4())
         
    def readConfig(self):
        curr_directory = os.getcwd()
        try:
            f = open('config.json')
            data = json.load(f)
            if 'directory' not in data:
                raise ValueError()
            path = data['directory']
            self.downloadPath.configure(state='normal')
            self.downloadPath.delete("0", "end")
            self.downloadPath.insert("end",path)
            self.downloadPath.configure(state=DISABLED)
        except ValueError as e:
            messagebox.showerror('Error', str(e)+'\nCannot find directory key in config.json. Check if config.json has been modified.')
        except Exception as e: 
            messagebox.showerror('Error', str(e)+'\nCannot locate config.json at ' + curr_directory)

    def changeDownloadPath(self):
        dir_name = filedialog.askdirectory()  
        if(dir_name == ""):
            return
        with open("config.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["directory"] = dir_name

        with open("config.json", "w") as jsonFile:
            json.dump(data, jsonFile)

        self.readConfig()

    def changeFilePath(self):
        dir_name = filedialog.askopenfilename(filetypes=[("MP3/WAV files", ".wav .mp3")])
        if(dir_name == ""):
            return
        curr_directory = os.getcwd()
        try:
            path = dir_name
            self.FilePath.configure(state='normal')
            self.FilePath.delete("0", "end")
            self.FilePath.insert("end",path)
            self.FilePath.configure(state=DISABLED)
        except ValueError as e:
            messagebox.showerror('Error', str(e)+'\nCannot find directory key in config.json. Check if config.json has been modified.')
        except Exception as e: 
            messagebox.showerror('Error', str(e)+'\nCannot locate config.json at ' + curr_directory)

if __name__ == "__main__":
    
    ws=GUI()
    ws.mainloop()

