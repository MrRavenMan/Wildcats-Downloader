from re import I
import tkinter as tk
from tkinter import ttk

import os
import json
import requests

from downloader import downloadMissionKneeboards
from frames.scrollFrame import ScrollFrame
from frames.toggleFrame import ToggledFrame


class MissionKneeboardWindow(tk.Frame):
    def __init__(self, root, frame, setup_data):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        self.setup_data = setup_data       

        paths_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/eventFlights.json'
        response = requests.get(paths_url).text
        self.event_flights = json.loads(response)

        title = tk.Label(self.scrollFrame.viewPort, text="Mission Kneeboards", fg='white', bg='#202020')
        title.config(font=('TkTextFont', 25))
        title.pack(pady=(20, 20))

        frame.place_forget()
        self.t_frames = []
        self.backBtn = None

        self.generate_categories(root, frame, setup_data)
        self.place_t_frames()
        self.generate_btns(frame)
        self.place_btns()

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def generate_categories(self, root, frame, setup_data):
        for squadron in self.event_flights:
            t = ToggledFrame(self.scrollFrame.viewPort, text=squadron["name"], relief="raised", borderwidth=1)

            for flight in squadron["flights"]:
                s_title = tk.Label(t.sub_frame, text=flight["flight_name"])
                s_title.config(font=('TkTextFont', 12))
                s_title.pack(pady=(10, 0))
                
                flight_name = flight["flight_name"]
                tk.Button(t.sub_frame, text="Download",
                command=lambda flight_name=flight_name: self.download(flight_name),
                bg="blue").pack(pady=5)

                ttk.Label(t.sub_frame, text="").pack()
                ttk.Separator(t.sub_frame, orient='horizontal').pack(fill='x', pady=(5, 5))
                t.sub_frame.place()
            
            self.t_frames.append(t)

    def generate_btns(self, frame):
        self.backBtn = tk.Button(self.scrollFrame.viewPort, text="Back", command=lambda: self.back(frame=frame), bg="gray")

    def place_btns(self):
        self.backBtn.pack(pady=(10, 5))
    
    def delete_btns(self):
        self.backBtn.destroy()
            
    def place_t_frames(self):
        for t in self.t_frames:
            t.pack(fill="x", expand=1, pady=7, padx=40, anchor="n")

    def download(self, flight):
        downloadMissionKneeboards(save_path=self.setup_data["dcs_path"], flight=flight)
        
    def back(self, frame):
        frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)
        self.destroy()

    def refresh(self, root, frame, setup_data):
        self.delete_t_frames()
        self.delete_btns()
        self.generate_categories(root, frame, setup_data)
        self.place_t_frames()
        self.generate_btns(frame)
        self.place_btns()