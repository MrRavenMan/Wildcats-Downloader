from re import I
import tkinter as tk
from tkinter import ttk

import os
import json
import requests

from downloader import downloadKneeboards
from frames.scrollFrame import ScrollFrame
from frames.toggleFrame import ToggledFrame


class KneeboardWindow(tk.Frame):
    def __init__(self, root, frame, setup_data):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        self.setup_data = setup_data       

        paths_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/Kneeboards.json'
        response = requests.get(paths_url).text
        self.kneeboards = json.loads(response)
        if os.path.isfile('kneeboards.json'):
            with open('kneeboards.json', 'r') as f:
                old_kneeboards = json.load(f)
            for i, cat in enumerate(self.kneeboards): # Transfer old kneeboard setup to new
                for x, old_cat in enumerate(old_kneeboards):
                    if self.kneeboards[i]["name"] == old_kneeboards[x]["name"]:
                        for y, subcat in enumerate(self.kneeboards[i]["subcat"]):
                            for z, old_subcat in enumerate(old_kneeboards[x]["subcat"]):
                                if self.kneeboards[i]["subcat"][y]["name"] == old_kneeboards[x]["subcat"][z]["name"]:
                                    self.kneeboards[i]["subcat"][y]["default"] = old_kneeboards[x]["subcat"][z]["default"]
        with open('kneeboards.json', 'w') as f: # Save kneeboards.json locally
            f.write(json.dumps(self.kneeboards, indent=4))

        tk.Label(self.scrollFrame.viewPort, text="Kneeboards").pack()

        frame.place_forget()
        self.t_frames = []
        self.backBtn = None
        self.downloadBtn = None

        self.generate_categories(root, frame, setup_data)
        self.place_t_frames()
        self.generate_btns(frame)
        self.place_btns()

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def generate_categories(self, root, frame, setup_data):
        for category in self.kneeboards:
            t = ToggledFrame(self.scrollFrame.viewPort, text=category["name"], relief="raised", borderwidth=1)

            for subcategory in category["subcat"]:
                tk.Label(t.sub_frame, text=subcategory["name"]).pack()
                tk.Label(t.sub_frame, text=subcategory["description"]).pack()
                address = (category["name"], subcategory["name"])
                if subcategory["default"]:
                    tk.Button(t.sub_frame, text="Enabled",
                    command=lambda address=address: self.toggleGroup(address, root, frame, setup_data),
                    bg="green").pack()
                elif not subcategory["default"]:
                    tk.Button(t.sub_frame, text="Disabled",
                    command=lambda address=address: self.toggleGroup(address, root, frame, setup_data),
                    bg="red").pack()
                ttk.Label(t.sub_frame, text="").pack()
                t.sub_frame.place()
            
            self.t_frames.append(t)

    def generate_btns(self, frame):
        self.backBtn = tk.Button(self.scrollFrame.viewPort, text="Back", command=lambda: self.back(frame=frame), bg="gray")
        self.downloadBtn = tk.Button(self.scrollFrame.viewPort, text="Download", command=self.download, bg="blue")

    def place_btns(self):
        self.backBtn.pack()
        self.downloadBtn.pack()
    
    def delete_btns(self):
        self.backBtn.destroy()
        self.downloadBtn.destroy()
            
    def place_t_frames(self):
        for t in self.t_frames:
            t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

    def delete_t_frames(self):
        for t in self.t_frames:
            t.destroy()
        self.t_frames = []

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

    def download(self):
        downloadKneeboards(save_path=self.setup_data["dcs_path"])
        self.refresh()
        
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