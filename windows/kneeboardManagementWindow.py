import enum
from re import I
import tkinter as tk
from tkinter import ttk, filedialog

import os
import json
import requests
import time

from downloader import downloadKneeboards
from frames.scrollFrame import ScrollFrame
from frames.toggleFrame import ToggledFrame


class KneeboardManagementWindow(tk.Frame):
    def __init__(self, root, frame, setup_data):
        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        self.setup_data = setup_data
        self.kneeboards_json_path = f"{setup_data['management_folder_path']}/kneeboards.json"

        if not os.path.isfile(self.kneeboards_json_path):
            paths_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/Kneeboards.json'
            response = requests.get(paths_url).text
            self.kneeboards = json.loads(response)
            with open(self.kneeboards_json_path, 'w') as f: # Save kneeboards.json locally
                f.write(json.dumps(self.kneeboards, indent=4))
        else:
            with open(self.kneeboards_json_path, 'r') as f:
                self.kneeboards = json.load(f)

        tk.Label(self.scrollFrame.viewPort, text="Manage Kneeboards").pack()

        frame.place_forget()
        self.t_frames = []
        self.backBtn = None
        self.downloadBtn = None
        self.editLbl = None
        self.editBtn = None

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

                ttk.Label(t.sub_frame, text="Files: ").pack()
                listBox = tk.Listbox(t.sub_frame, width=60, height=len(subcategory["files"]) + 1)
                for i, file in enumerate(subcategory["files"]):
                    listBox.insert(i + 1, file)
                listBox.pack()

                tk.Button(t.sub_frame, text="selectFiles",
                    command=lambda address=address: self.selectFiles(address, root, frame, setup_data),
                    bg="gray").pack()
                tk.Button(t.sub_frame, text="Delete",
                    command=lambda address=address: self.deleteSubcat(address, root, frame, setup_data),
                    bg="red").pack()


                ttk.Label(t.sub_frame, text="").pack()
                t.sub_frame.place()

            tk.Button(t, text="Delete Category",
                command=lambda address=address: self.deleteCategory(category["name"], root, frame, setup_data),
                bg="red").pack()

            self.t_frames.append(t) # Add subcategories


    def generate_btns(self, frame):
        self.backBtn = tk.Button(self.scrollFrame.viewPort, text="Back", command=lambda: self.back(frame=frame), bg="gray")
        self.downloadBtn = tk.Button(self.scrollFrame.viewPort, text="Download", command=self.download, bg="blue")

        self.editLbl = tk.Label(self.scrollFrame.viewPort, text="To rename or add new categories or subcategories, you are still to edit it in the file for now")
        self.editBtn = tk.Button(self.scrollFrame.viewPort, text="Edit", command=lambda: os.system(f"notepad.exe {self.kneeboards_json_path}"), bg="Gray")

    def place_btns(self):
        self.backBtn.pack()
        self.downloadBtn.pack()
        self.editLbl.pack()
        self.editBtn.pack()
    
    def delete_btns(self):
        self.backBtn.destroy()
        self.downloadBtn.destroy()
        self.editLbl.destroy()
        self.editBtn.destroy()

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
                        with open(self.kneeboards_json_path, 'w') as f:
                            f.write(json.dumps(self.kneeboards, indent=4))
                        break
                    
        self.refresh(root, frame, setup_data)

    def selectFiles(self, address, root, frame, setup_data):
        files = filedialog.askopenfilenames(initialdir=setup_data["management_folder_path"], title="Select files")
        category_name, subcategory_name = address
        for i, cat in enumerate(self.kneeboards):
            if cat["name"] == category_name:
                for x, subcat in enumerate(cat["subcat"]):
                    if subcat["name"] == subcategory_name:
                        self.kneeboards[i]["subcat"][x]["files"] = []
                        for file in files:
                            file_name = file.replace(setup_data["management_folder_path"], '')
                            self.kneeboards[i]["subcat"][x]["files"].append(file_name)

                        with open(self.kneeboards_json_path, 'w') as f:
                            f.write(json.dumps(self.kneeboards, indent=4))
                        break
        self.refresh(root, frame, setup_data)

    def deleteSubcat(self, address, root, frame, setup_data):
        category_name, subcategory_name = address
        for i, cat in enumerate(self.kneeboards):
            if cat["name"] == category_name:
                for x, subcat in enumerate(cat["subcat"]):
                    if subcat["name"] == subcategory_name:
                        self.kneeboards[i]["subcat"].pop(x)

                        with open(self.kneeboards_json_path, 'w') as f:
                            f.write(json.dumps(self.kneeboards, indent=4))
                        break
        self.refresh(root, frame, setup_data)

    def deleteCategory(self, category_name, root, frame, setup_data):
        for i, cat in enumerate(self.kneeboards):
            if cat["name"] == category_name:
                self.kneeboards.pop(i)
                with open(self.kneeboards_json_path, 'w') as f:
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