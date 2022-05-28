import tkinter as tk
from tkinter import filedialog, Text, StringVar

import os
import json

from downloader import downloadLiveries
from management import generatePaths
from windows.kneeboardWindow import KneeboardWindow
from windows.missionKneeboardWindow import MissionKneeboardWindow

root = tk.Tk()
apps = []

LOCAL_VERSION = 3

pathLblVar = StringVar()

root.title("Wildcats File Downloader")

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


def seeKneeboards():
    KneeboardWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)
    

def seeMissionKneeboards():
    MissionKneeboardWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)


canvas = tk.Canvas(root, height=700, width=700, bg="#263D42")
canvas.pack()

frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)


downloadLiveriesBtn = tk.Button(frame, text="Download Liveries", padx=10, pady=5,
             fg="white", bg="#263D42", command=lambda: downloadLiveries(setup_data["dcs_path"], plane="all"))
downloadLiveriesBtn.pack()

kneeboardsBtn = tk.Button(frame, text="Kneeboards", padx=10, pady=5,
             fg="white", bg="#263D42", command=seeKneeboards)
kneeboardsBtn.pack()

missionKneeboardsBtn = tk.Button(frame, text="Mission Kneeboards", padx=10, pady=5,
             fg="white", bg="#263D42", command=seeMissionKneeboards)
missionKneeboardsBtn.pack()

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