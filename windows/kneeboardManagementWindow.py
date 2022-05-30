import enum
from re import I
import tkinter as tk
from tkinter import ttk, filedialog

import os
import json
from turtle import width
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

        title = tk.Label(self.scrollFrame.viewPort, text="Manage Kneeboards", fg='#FF9A00', bg='#202020')
        title.config(font=('TkTextFont', 25))
        title.pack(pady=(20, 20))

        frame.place_forget()
        self.t_frames = []
        self.backBtn = None
        self.downloadBtn = None
        self.editLbl = None
        self.editBtn = None
        self.f_title = None
        self.f_path = None
        self.f_title_val = tk.StringVar()
        self.f_path_val = tk.StringVar(value="/Kneeboard/")
        self.form_frame = None  
        self.subcat_form_data = []

        self.generate_categories(root, frame, setup_data)
        self.place_t_frames()
        self.generate_btns(frame)
        self.place_btns()

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)

    def generate_categories(self, root, frame, setup_data):
        for cat_index, category in enumerate(self.kneeboards):
            t = ToggledFrame(self.scrollFrame.viewPort, text=category["name"], relief="raised", borderwidth=1)

            # add New Subcategory Form
            s_form_frame_title = tk.Label(t.sub_frame, text="Generate New Subcategory")
            s_form_frame_title.config(font=('TkTextFont', 12))
            s_form_frame_title.pack(pady=10, padx=20)
            
            self.subcat_form_data.append((tk.StringVar(), tk.StringVar())) # (title, desc)

            s_f_title_lbl = tk.Label(t.sub_frame, text="Name:")
            s_f_title_lbl.pack()
            s_f_title = ttk.Entry(t.sub_frame, width=30, textvariable=self.subcat_form_data[cat_index][0])
            s_f_title.pack()
            s_f_desc_lbl = tk.Label(t.sub_frame, text="Description:")
            s_f_desc_lbl.pack()
            s_f_desc = tk.Entry(t.sub_frame, width=80, textvariable=self.subcat_form_data[cat_index][1])
            s_f_desc.pack()

            add_btn = tk.Button(t.sub_frame, text="Add Subcategory", command=lambda cat_idx=cat_index: 
                                    self.add_subcat(cat_idx, root, frame))
            add_btn.pack(pady=10)
            ttk.Separator(t.sub_frame, orient='horizontal').pack(fill='x')

            # Loop through and display subcategories
            for subcategory in category["subcat"]:
                s_title = tk.Label(t.sub_frame, text=subcategory["name"])
                s_title.config(font=('TkTextFont', 12))
                s_title.pack(pady=(12, 0))
                tk.Label(t.sub_frame, text=subcategory["description"]).pack(pady=5)
                address = (category["name"], subcategory["name"])
                if subcategory["default"]:
                    tk.Button(t.sub_frame, text="Enabled",
                    command=lambda address=address: self.toggleGroup(address, root, frame, setup_data),
                    bg="green").pack()
                elif not subcategory["default"]:
                    tk.Button(t.sub_frame, text="Disabled",
                    command=lambda address=address: self.toggleGroup(address, root, frame, setup_data),
                    bg="red").pack()

                ttk.Label(t.sub_frame, text="Files: ").pack(pady=(10, 0))
                listBox = tk.Listbox(t.sub_frame, width=60, height=len(subcategory["files"]) + 1)
                for i, file in enumerate(subcategory["files"]):
                    listBox.insert(i + 1, file)
                listBox.pack(pady=(0, 5))

                tk.Button(t.sub_frame, text="selectFiles",
                    command=lambda address=address: self.selectFiles(address, root, frame, setup_data),
                    bg="gray").pack(pady=5)
                tk.Button(t.sub_frame, text="Delete",
                    command=lambda address=address: self.deleteSubcat(address, root, frame, setup_data),
                    bg="red").pack(pady=15)

                ttk.Separator(t.sub_frame, orient='horizontal').pack(fill='x')
                t.sub_frame.place()

            tk.Button(t, text="Delete Category",
                command=lambda address=address: self.deleteCategory(category["name"], root, frame, setup_data),
                bg="red").pack(pady=7)

            self.t_frames.append(t) # Add subcategories

        # Add New Category Form
        self.form_frame = tk.Frame(self.scrollFrame.viewPort, bg="#505050")
        form_frame_title = tk.Label(self.form_frame, text="Generate New Category", bg='#505050', fg='white')
        form_frame_title.config(font=('TkTextFont', 15))
        form_frame_title.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        f_title_lbl = tk.Label(self.form_frame, text="Name:", bg='#505050', fg="white")
        f_title_lbl.grid(row=1, column=0)
        self.f_title = ttk.Entry(self.form_frame, width=30, textvariable=self.f_title_val)
        self.f_title.grid(row=1, column=1)
        self.f_path_lbl = tk.Label(self.form_frame, text="Path:", bg='#505050', fg="white")
        self.f_path_lbl.grid(row=2, column=0)
        self.f_path = tk.Entry(self.form_frame, width=30, textvariable=self.f_path_val)
        self.f_path.grid(row=2, column=1)

        add_btn = tk.Button(self.form_frame, text="Add Category", command=lambda: self.add_cat(self.f_title_val, self.f_path_val, root, frame))
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)

              
    
    def add_cat(self, title, path, root, frame):
        # Clear the text box
        cat = {
            "name": title.get(),
            "parent": path.get(),
            "hide": True,
            "subcat": []
        }
        
        print(cat)
        self.kneeboards.append(cat)
        with open(self.kneeboards_json_path, 'w') as f: # Save kneeboards.json locally
            f.write(json.dumps(self.kneeboards, indent=4))

        self.f_title_val.set("")
        self.f_path_val.set("/Kneeboard/")

        self.refresh(root, frame, self.setup_data)

    def add_subcat(self, cat_idx, root, frame):
        # Clear the text box
        subcat = {
            "name": self.subcat_form_data[cat_idx][0].get(),
            "default": False,
            "date": int(time.time()),
            "description": self.subcat_form_data[cat_idx][1].get(),
            "files": []
        }
        
        self.kneeboards[cat_idx]["subcat"].append(subcat)
        with open(self.kneeboards_json_path, 'w') as f: # Save kneeboards.json locally
            f.write(json.dumps(self.kneeboards, indent=4))
        self.refresh(root, frame, self.setup_data)


    def generate_btns(self, frame):
        self.form_frame.pack(pady=(15, 5))
        self.backBtn = tk.Button(self.scrollFrame.viewPort, text="Back", command=lambda: self.back(frame=frame), bg="gray")
        self.downloadBtn = tk.Button(self.scrollFrame.viewPort, text="Download", command=self.download, bg="blue")

        self.editLbl = tk.Label(self.scrollFrame.viewPort, text="To rename or add new categories or subcategories, you are still to edit it in the file for now")
        self.editBtn = tk.Button(self.scrollFrame.viewPort, text="Edit", command=lambda: os.system(f"notepad.exe {self.kneeboards_json_path}"), bg="Gray")

    def place_btns(self):
        self.backBtn.pack(pady=(10, 5))
        self.downloadBtn.pack(pady=(3, 5))
        self.editLbl.pack(pady=(5, 1))
        self.editBtn.pack(pady=(0, 10))
    
    def delete_btns(self):
        self.form_frame.destroy()
        self.backBtn.destroy()
        self.downloadBtn.destroy()
        self.editLbl.destroy()
        self.editBtn.destroy()

    def place_t_frames(self):
        for t in self.t_frames:
            t.pack(fill="x", expand=1, pady=7, padx=40, anchor="n")

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

    def deleteCategory(self, category_name, root, frame, setup_data):
        for i, cat in enumerate(self.kneeboards):
            if cat["name"] == category_name:
                self.kneeboards.pop(i)
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
        time.sleep(0.4)
        # self.__init__(root, frame, setup_data)
        self.generate_categories(root, frame, setup_data)
        self.place_t_frames()
        self.generate_btns(frame)
        self.place_btns()
