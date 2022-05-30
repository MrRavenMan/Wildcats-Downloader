import enum
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
        self.f_title_val = tk.StringVar()
        self.form_frame = None  
        self.flights_form_data = []
        
        self.generate_categories(root, frame, setup_data)
        self.place_t_frames()
        self.generate_btns(frame)
        self.place_btns()

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def generate_categories(self, root, frame, setup_data):
        for squadron_idx, squadron in enumerate(self.event_flights):
            t = ToggledFrame(self.scrollFrame.viewPort, text=squadron["name"], relief="raised", borderwidth=1)

            # add New Flight Form
            s_form_frame_title = tk.Label(t.sub_frame, text="Add New Flight")
            s_form_frame_title.config(font=('TkTextFont', 12))
            s_form_frame_title.pack(pady=10, padx=20)
            
            self.flights_form_data.append(tk.StringVar()) # name

            s_f_title_lbl = tk.Label(t.sub_frame, text="Name:")
            s_f_title_lbl.pack()
            s_f_title = ttk.Entry(t.sub_frame, width=30, textvariable=self.flights_form_data[squadron_idx])
            s_f_title.pack()

            add_btn = tk.Button(t.sub_frame, text="Add Flight", command=lambda squadron_idx=squadron_idx: 
                                    self.add_flight(squadron_idx, root, frame))
            add_btn.pack(pady=10)
            ttk.Separator(t.sub_frame, orient='horizontal').pack(fill='x')

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
            tk.Button(t, text="Delete Squadron",
                command=lambda squadron_name=squadron_name: self.delete_squadron(squadron_name, root, frame, setup_data),
                bg="red").pack(pady=7)
            self.t_frames.append(t)

        # Add New Squadron Form
        self.form_frame = tk.Frame(self.scrollFrame.viewPort, bg="#505050")
        form_frame_title = tk.Label(self.form_frame, text="Add New Squadron", bg='#505050', fg='white')
        form_frame_title.config(font=('TkTextFont', 15))
        form_frame_title.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        f_title_lbl = tk.Label(self.form_frame, text="Name:", bg='#505050', fg="white")
        f_title_lbl.grid(row=1, column=0)
        self.f_title = ttk.Entry(self.form_frame, width=30, textvariable=self.f_title_val)
        self.f_title.grid(row=1, column=1)

        add_btn = tk.Button(self.form_frame, text="Add Squadron", command=lambda: self.add_squadron(self.f_title_val, root, frame))
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)
    
    def add_squadron(self, name, root, frame):
        # Clear the text box
        cat = {
            "name": name.get(),
            "flights": []
        }
        
        print(cat)
        self.event_flights.append(cat)
        with open(self.event_flights_json_path, 'w') as f: # Save eventFlights.json locally
            f.write(json.dumps(self.event_flights, indent=4))

        self.f_title_val.set("")
        self.refresh(root, frame, self.setup_data)

    def add_flight(self, squadron_idx, root, frame):
        # Clear the text box
        flight = {
            "flight_name": self.flights_form_data[squadron_idx].get(),
        }
        
        self.event_flights[squadron_idx]["flights"].append(flight)
        with open(self.event_flights_json_path, 'w') as f: # Save eventFlights.json locally
            f.write(json.dumps(self.event_flights, indent=4))
        self.refresh(root, frame, self.setup_data)

    def generate_btns(self, frame):
        self.backBtn = tk.Button(self.scrollFrame.viewPort, text="Back", command=lambda: self.back(frame=frame), bg="gray")

    def place_btns(self):
        self.form_frame.pack(pady=(15, 5))
        self.backBtn.pack(pady=(10, 5))
    
    def delete_btns(self):
        self.form_frame.destroy()
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