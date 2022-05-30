import tkinter as tk
from tkinter import filedialog, StringVar, ttk, PhotoImage

import os
import json
import requests

from downloader import downloadKneeboards, downloadLiveries
from management import generatePaths
from windows.kneeboardWindow import KneeboardWindow
from windows.missionKneeboardWindow import MissionKneeboardWindow
from windows.kneeboardManagementWindow import KneeboardManagementWindow
from windows.missionKneeboardManagementWindow import MissionKneeboardManagementWindow
from popup import Win

root = tk.Tk()
apps = []

LOCAL_VERSION = 4
PATH = os.path.abspath(os.getcwd()).replace('\\', '/')

pathLblVar = StringVar()

root.title("Wildcats File Downloader")
root.iconbitmap(f"{PATH}/img/icon.ico")
root.resizable(False, False)

if os.path.isfile('setup.json'):
    with open('setup.json', 'r') as f:
        setup_data = json.load(f)
else: # Generate setup data
    setup_data = {
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
    Win().popup("Alert", "Please restart the application after selecting path")
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

def download_liveries(plane="all"):
    if setup_data['dcs_path'] != "":
        downloadLiveries(setup_data["dcs_path"], plane=plane)

def seeKneeboards(): # view kneeboardWindow
    if setup_data['dcs_path'] != "":
        KneeboardWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)
    
def seeMissionKneeboards(): # view missionKneeboardWindow
    if setup_data['dcs_path'] != "":
        MissionKneeboardWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)

def seeKneeboardManagement(): # view kneeboardManagementWindow
    KneeboardManagementWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)

def seeMissionKneeboardManagement(): # view missionKneeboardManagementWindow 
    MissionKneeboardManagementWindow(root=canvas, frame=frame, setup_data=setup_data).pack(side="top", fill="both", expand=True)

def openGuide(): # open guide for management of files for the downloader
    guide_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/Wildcats Downloader Management Guide.pdf'
    local_path = "Guide.pdf"
    response = requests.get(guide_url)
    open(local_path, "wb").write(response.content)
    os.system(f"start {local_path}")

# populate window with widgets
canvas = tk.Canvas(root, height=800, width=700, bg="#202020")
canvas.pack()

frame = tk.Frame(root, bg="#202020")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

title = tk.Label(frame, text="DCS Wildcats Downloader", fg='white', bg='#202020')
title.config(font=('TkTextFont', 25))
title.pack(pady=(0, 20))

# check not admin and add image. Image cannot be added for admin users as there is not enough space for image and management buttons
if not setup_data["admin"]:
    img = PhotoImage(file=f"{PATH}/img/profile-img.png")
    tk.Label(frame, image=img, bg="#202020").pack()

# add buttons for downloading
downloadLiveriesBtn = tk.Button(frame, text="Download Liveries", padx=10, pady=5,
            fg="#01EEFF", bg="#1D1D1D", command=lambda: download_liveries(plane="all"))
downloadLiveriesBtn.pack(pady=10)

kneeboardsBtn = tk.Button(frame, text="Kneeboards", padx=10, pady=5,
            fg="#01EEFF", bg="#1D1D1D", command=seeKneeboards)
kneeboardsBtn.pack(pady=10)

missionKneeboardsBtn = tk.Button(frame, text="Mission Kneeboards", padx=10, pady=5,
            fg="#01EEFF", bg="#1D1D1D", command=seeMissionKneeboards)
missionKneeboardsBtn.pack(pady=10)

# add button to select path and display path label
selectPathBtn = tk.Button(frame, text="Select Path", padx=10, pady=5,
             fg="#01EEFF", bg="#202020", command=selectPath)
selectPathBtn.pack(pady=10)
setPathLabel()
pathLbl = tk.Label(frame, textvariable=pathLblVar, fg='#FF9A00', bg='#1D1D1D')
pathLbl.pack(pady=(15))


if setup_data["admin"]: # add management menu if admin is set to true
    ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)
    lbl = tk.Label(frame, text="Management", fg='#FF9A00', bg='#202020')
    lbl.config(font=('TkTextFont', 15))
    lbl.pack(pady=(10, 5))
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

    helpBtn = tk.Button(frame, text="Management Guide", padx=10, pady=5,
            fg="white", bg="#1D1D1D", command=openGuide)
    helpBtn.pack(pady=(10, 0))

for app in apps:
    label = tk.Label(frame, text=app)
    label.pack()

# run window
root.mainloop()


# TO COMPILE
# USE: pyinstaller --onefile main.py
# To generate installer: USE NSIS