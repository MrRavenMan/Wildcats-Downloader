from re import I
import tkinter as tk
from tkinter import ttk

import os
import json
import requests

from downloader import downloadMissionKneeboards
from frames.scrollFrame import ScrollFrame
from frames.toggleFrame import ToggledFrame


class MissionKneeboardManagementWindow(tk.Frame):
    def __init__(self, root, frame, setup_data):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        self.setup_data = setup_data       

        self.event_flights_json_path = f"{setup_data['management_folder_path']}/eventFlights.json"

        if not os.path.isfile(self.event_flights_json_path):
            paths_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/eventFlights.json'
            response = requests.get(paths_url).text
            self.event_flights = json.loads(response)
            with open(self.event_flights_json_path, 'w') as f: # Save kneeboards.json locally
                f.write(json.dumps(self.event_flights, indent=4))
        else:
            with open(self.event_flights_json_path, 'r') as f:
                self.event_flights = json.load(f)

        title = tk.Label(self.scrollFrame.viewPort, text="Manage Mission Kneeboards", fg='#FF9A00', bg='#202020')
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
                address = (squadron["name"], flight["flight_name"])
                tk.Button(t.sub_frame, text="Delete Flight",
                command=lambda address=address: self.delete_flight(address, root, frame, setup_data),
                bg="red").pack(pady=5)

                ttk.Label(t.sub_frame, text="").pack()
                ttk.Separator(t.sub_frame, orient='horizontal').pack(fill='x', pady=(5, 5))
                t.sub_frame.place()
            
            squadron_name = squadron["name"]
            tk.Button(t, text="Delete Category",
                command=lambda squadron_name=squadron_name: self.delete_squadron(squadron_name, root, frame, setup_data),
                bg="red").pack(pady=7)
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

    def delete_t_frames(self):
        for t in self.t_frames:
            t.destroy()
        self.t_frames = []

    def delete_flight(self, address, root, frame, setup_data):
        squadron_name, flight_name = address
        for i, squadron in enumerate(self.event_flights):
            if squadron["name"] == squadron_name:
                for x, flight in enumerate(squadron["flights"]):
                    if flight["flight_name"] == flight_name:
                        self.event_flights[i]["flights"].pop(x)

        with open(self.event_flights_json_path, 'w') as f: # Save eventFlights.json
            f.write(json.dumps(self.event_flights, indent=4))
        self.refresh(root, frame, setup_data)

    def delete_squadron(self, squadron_name, root, frame, setup_data):
        for i, squadron in enumerate(self.event_flights):
            if squadron["name"] == squadron_name:
                self.event_flights.pop(i)

        with open(self.event_flights_json_path, 'w') as f: # Save eventFlights.json
            f.write(json.dumps(self.event_flights, indent=4))
        self.refresh(root, frame, setup_data)
        
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