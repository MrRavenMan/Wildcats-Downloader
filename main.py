from re import I
import tkinter as tk
from tkinter import filedialog, Text, StringVar
from tkinter import ttk

import os
import json
from turtle import bgcolor, color
import requests

from downloader import downloadLiveries, downloadKneeboards
from management import generatePaths
from scrollFrame import ScrollFrame
from toggleFrame import ToggledFrame


root = tk.Tk()
apps = []

LOCAL_VERSION = 3

pathLblVar = StringVar()

if os.path.isfile('setup.json'):
    with open('setup.json', 'r') as f:
        setup_data = json.load(f)
else: # Generate setup data
    setup_data = {
        "firstTime": True,
        "admin": False,
        "local_ver": LOCAL_VERSION,
        "liveries_date": 0,
        "dcs_path": "",
        "management_folder_path": ""
    }



def selectPath():
    path = filedialog.askdirectory(initialdir="/", title="Select DCS Saved Games Folder",
    )
    setup_data["dcs_path"] = path
    saveSetupFile()
    setPathLabel()


def createManagementFolder():
    management_folder_path = filedialog.askdirectory(initialdir="/", title="Select Management Folder")
    setup_data["management_folder_path"] = management_folder_path
    downloadLiveries(management_folder_path, plane="all", download_management=True)
    saveSetupFile()

def saveSetupFile():
    with open('setup.json', 'w') as f:
        f.write(json.dumps(setup_data, indent=4))

def setPathLabel():
    pathLblVar.set(f"Selected path: {setup_data['dcs_path']}")


def ManageKneeboards():
    # Get current paths
    KneeboardWindow(canvas).pack(side="top", fill="both", expand=True)
    

class KneeboardWindow(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
    
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


        frame.place_forget()        
        for category in self.kneeboards:
            t = ToggledFrame(self.scrollFrame.viewPort, text=category["name"], relief="raised", borderwidth=1)
            t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

            for subcategory in category["subcat"]:
                tk.Label(t.sub_frame, text=subcategory["name"]).pack()
                tk.Label(t.sub_frame, text=subcategory["description"]).pack()
                address = (category["name"], subcategory["name"])
                if subcategory["default"]:
                    tk.Button(t.sub_frame, text="Enabled",
                    command=lambda address=address: self.toggleGroup(address),
                    bg="green").pack()
                elif not subcategory["default"]:
                    tk.Button(t.sub_frame, text="Disabled",
                    command=lambda address=address: self.toggleGroup(address),
                    bg="red").pack()
                ttk.Label(t.sub_frame, text="").pack()
                t.sub_frame.place()


        tk.Button(self.scrollFrame.viewPort, text="Back", command=self.back, bg="gray").pack()
        tk.Button(self.scrollFrame.viewPort, text="Download", command=self.download, bg="blue").pack()
        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def toggleGroup(self, address):
        category_name, subcategory_name = address
        for i, cat in enumerate(self.kneeboards):
            if cat["name"] == category_name:
                for x, subcat in enumerate(cat["subcat"]):
                    if subcat["name"] == subcategory_name:
                        self.kneeboards[i]["subcat"][x]["default"] = not self.kneeboards[i]["subcat"][x]["default"]
                        with open('kneeboards.json', 'w') as f:
                            f.write(json.dumps(self.kneeboards, indent=4))
                        break
                    
        self.refresh()

    def download(self):
        downloadKneeboards(save_path=setup_data["dcs_path"])
        self.refresh()
        
    def back(self):
        frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)
        self.destroy()

    def refresh(self):
        ManageKneeboards()
        self.destroy()


canvas = tk.Canvas(root, height=700, width=700, bg="#263D42")
canvas.pack()

frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)


downloadLiveriesBtn = tk.Button(frame, text="Download Liveries", padx=10, pady=5,
             fg="white", bg="#263D42", command=lambda: downloadLiveries(setup_data["dcs_path"], plane="all"))
downloadLiveriesBtn.pack()

KneeboardsBtn = tk.Button(frame, text="Kneeboards", padx=10, pady=5,
             fg="white", bg="#263D42", command=ManageKneeboards)
KneeboardsBtn.pack()

selectPathBtn = tk.Button(frame, text="Select Path", padx=10, pady=5,
             fg="white", bg="#263D42", command=selectPath)
selectPathBtn.pack()

setPathLabel()
pathLbl = tk.Label(frame, textvariable=pathLblVar)
pathLbl.pack()



if setup_data["admin"]:
    lbl = tk.Label(frame, text="Management Buttons")
    lbl.pack()
    createManagementFolderBtn = tk.Button(frame, text="Generate Management Folder", padx=10, pady=5,
                fg="white", bg="#263D42", command=createManagementFolder)
    createManagementFolderBtn.pack()
    generatePathsBtn = tk.Button(frame, text="Select Management Folder", padx=10, pady=5,
                fg="white", bg="#263D42", command=lambda: generatePaths(filedialog.askdirectory(initialdir="/", title="Select Management Folder")))
    generatePathsBtn.pack()



for app in apps:
    label = tk.Label(frame, text=app)
    label.pack()

root.mainloop()