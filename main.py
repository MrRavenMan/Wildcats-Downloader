import tkinter as tk
from tkinter import filedialog, Text, StringVar, ttk

import os
import json

from downloader import downloadKneeboards, downloadLiveries
from management import generatePaths
from windows.kneeboardWindow import KneeboardWindow
from windows.missionKneeboardWindow import MissionKneeboardWindow
from windows.kneeboardManagementWindow import KneeboardManagementWindow
from windows.missionKneeboardManagementWindow import MissionKneeboardManagementWindow

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
    downloadKneeboards(management_folder_path, download_all=True)
    saveSetupFile()

def saveSetupFile():
    with open('setup.json', 'w') as f:
        f.write(json.dumps(setup_data, indent=4))

def setPathLabel():
    if setup_data['dcs_path'] == "":
        msg = "****Please select 'DCS Saved Games folder' as path before downloading anything!****"
    else:
        msg = f"Selected path: {setup_data['dcs_path']}"
    pathLblVar.set(msg)


def seeKneeboards():
    KneeboardWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)
    
def seeMissionKneeboards():
    MissionKneeboardWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)

def seeKneeboardManagement():
    KneeboardManagementWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)

def seeMissionKneeboardManagement():
    MissionKneeboardManagementWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)


canvas = tk.Canvas(root, height=780, width=700, bg="#202020")
canvas.pack()

frame = tk.Frame(root, bg="#202020")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

title = tk.Label(frame, text="DCS Wildcats Downloader", fg='white', bg='#202020')
title.config(font=('TkTextFont', 25))
title.pack(pady=(0, 20))

downloadLiveriesBtn = tk.Button(frame, text="Download Liveries", padx=10, pady=5,
             fg="#01EEFF", bg="#1D1D1D", command=lambda: downloadLiveries(setup_data["dcs_path"], plane="all"))
downloadLiveriesBtn.pack(pady=10)

kneeboardsBtn = tk.Button(frame, text="Kneeboards", padx=10, pady=5,
             fg="#01EEFF", bg="#1D1D1D", command=seeKneeboards)
kneeboardsBtn.pack(pady=10)

missionKneeboardsBtn = tk.Button(frame, text="Mission Kneeboards", padx=10, pady=5,
             fg="#01EEFF", bg="#1D1D1D", command=seeMissionKneeboards)
missionKneeboardsBtn.pack(pady=10)

selectPathBtn = tk.Button(frame, text="Select Path", padx=10, pady=5,
             fg="#01EEFF", bg="#202020", command=selectPath)
selectPathBtn.pack(pady=10)

setPathLabel()
pathLbl = tk.Label(frame, textvariable=pathLblVar, fg='#FF9A00', bg='#1D1D1D')
pathLbl.pack(pady=(15))

# Management Menu
if setup_data["admin"]:
    ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
    lbl = tk.Label(frame, text="Management Buttons", fg='#FF9A00', bg='#202020')
    lbl.config(font=('TkTextFont', 15))
    lbl.pack(pady=(10))
    createManagementFolderBtn = tk.Button(frame, text="Generate Management Folder", padx=10, pady=5,
                fg="#FF9A00", bg="#1D1D1D", command=createManagementFolder)
    createManagementFolderBtn.pack(pady=10)

    generatePathsBtn = tk.Button(frame, text="Generate Livery Paths", padx=10, pady=5,
                fg="#FF9A00", bg="#1D1D1D", command=lambda: generatePaths(setup_data["management_folder_path"]))
    generatePathsBtn.pack(pady=10)

    manageKneeboardsBtn = tk.Button(frame, text="Manage Kneeboards", padx=10, pady=5,
            fg="#FF9A00", bg="#1D1D1D", command=seeKneeboardManagement)
    manageKneeboardsBtn.pack(pady=10)

    manageMissionKneeboardsBtn = tk.Button(frame, text="Manage Mission Kneeboards", padx=10, pady=5,
            fg="#FF9A00", bg="#1D1D1D", command=seeMissionKneeboardManagement)
    manageMissionKneeboardsBtn.pack(pady=10)



for app in apps:
    label = tk.Label(frame, text=app)
    label.pack()

root.mainloop()