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

        tk.Label(self.scrollFrame.viewPort, text="Mission Kneeboards").pack()

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
                tk.Label(t.sub_frame, text=flight["flight_name"]).pack()
                tk.Button(t.sub_frame, text="Download",
                command=lambda: self.download(flight["flight_name"]),
                bg="blue").pack()

                ttk.Label(t.sub_frame, text="").pack()
                t.sub_frame.place()
            
            self.t_frames.append(t)

    def generate_btns(self, frame):
        self.backBtn = tk.Button(self.scrollFrame.viewPort, text="Back", command=lambda: self.back(frame=frame), bg="gray")

    def place_btns(self):
        self.backBtn.pack()
    
    def delete_btns(self):
        self.backBtn.destroy()
            
    def place_t_frames(self):
        for t in self.t_frames:
            t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

    def toggleGroup(self, address, root, frame, setup_data):
        category_name, subcategory_name = address
        for i, cat in enumerate(self.kneeboards):
            if cat["name"] == category_name:
                for x, subcat in enumerate(cat["subcat"]):
                    if subcat["name"] == subcategory_name:
                        self.kneeboards[i]["subcat"][x]["default"] = not self.kneeboards[i]["subcat"][x]["default"]
                        with open('kneeboards.json', 'w') as f:
                            f.write(json.dumps(self.kneeboards, indent=4))
                        break
                    
        self.refresh(root, frame, setup_data)

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