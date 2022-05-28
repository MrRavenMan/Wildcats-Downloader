import requests, json, os, time

from popup import Win


def downloadLiveries(save_path: str, plane="all", download_management=False):
    Win().popup("Download Liveries", "I may time out during the download. That is okay. I am just working very hard. Please keep me alive during the download. \n Please wait for download complete message, before doing anything \n\n Press OK to start download")

    SAVE_PATH = save_path

    # Get paths file
    # paths_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/paths.json'
    # response = requests.get(paths_url).text
    # paths = json.loads(response)
    with open('paths.json', 'r') as f:
        paths = json.load(f)

    # Load local paths file which is used to identify already downloaded liveries
    if os.path.isfile('local_paths.json'):
        with open('local_paths.json', 'r') as f:
          local_paths = json.load(f)
    else: # Generate local paths file if not exist
        local_paths = []
        for idx, path in enumerate(paths):
            local_path = path
            local_path["date"] = 0
            local_path["idx"] = idx

            if local_path["delete"] is True:
                deleteLivery(f"{SAVE_PATH}{local_path['path']}")
                continue # do not add to local paths
            local_paths.append(path)

    # Prepare and start download
    download = Download()
    for path in paths:
        # Find local path with corresponding ID
        local_path = None
        for i, local_p in enumerate(local_paths):
            if local_p["id"] == path["id"]:
                local_path = local_p
        if path["delete"] is True:
            #DELETE AND REMOVE FROM local_path
            deleteLivery(f"{SAVE_PATH}{path['path']}")
            # local_paths.pop(i)
            continue
        
        if not download_management:
            if local_path["date"] > path["date"] and os.path.exists(f"{SAVE_PATH}{path['path']}"):
                continue # File is up to date
            local_paths[local_path["idx"]]["date"] = int(time.time())
            download.addDownloadFile(url=f"https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master{path['path']}",
                        save_path=f"{SAVE_PATH}{path['path']}",
                        size=path['size'])
        else:
            download.addDownloadFile(url=f"https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master{path['path']}",
                        save_path=f"{SAVE_PATH}{path['path']}",
                        size=path['size'])

    download.startDownload()

    # Save new/updated local_paths.json
    if not download_management:
        with open('local_paths.json', 'w') as f:
            f.write(json.dumps(local_paths, indent=4))
        print("Livery download complete")

def deleteLivery(path):
    if os.path.isfile(path):
        os.remove(path)
        print(f"Deleted deprecated livery at {path}")

def downloadKneeboards(save_path: str, download_all=False):
    Win().popup("Download Kneeboards", "I may time out during the download. That is okay. I am just working very hard. Please keep me alive during the download. \n Please wait for download complete message, before doing anything \n\n Press OK to start download")

    SAVE_PATH = save_path
    download = Download()
    if not os.path.isfile('kneeboards.json'):
        print("Please make sure a kneeboards.json file is generated first!")
        return
    with open('kneeboards.json', 'r') as f:
        kneeboards = json.load(f)

    for cat in kneeboards:
        for subcat in cat["subcat"]:
            if subcat["default"] or download_all:
                for file in subcat["files"]:
                    path = f"{cat['parent']}{file}"
                    download.addDownloadFile(url=f"https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master{path}",
                    save_path=f"{SAVE_PATH}{path}",
                    size=0)
    download.startDownload(disable_size=True)
    print("Kneeboard download complete")


def downloadMissionKneeboards(save_path: str, flight: str, delete=False):
    paths_url = f"https://api.github.com/repos/drumbart/VFA-27_Ready_Room/contents/eventKneeboards/{flight}"
    response = requests.get(paths_url).text
    flight_kneeboards = json.loads(response)

    download = Download()
    for kneeboard in flight_kneeboards:
        download_url = f"https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/eventKneeboards/{flight}/{kneeboard['name']}"
        size = int(kneeboard["size"])
        save_path = save_path + "/Kneeboard/" + kneeboard["name"]

        if delete and os.path.isfile(save_path):
            os.remove(save_path)
        else:
            download.addDownloadFile(
                url=download_url,
                save_path=save_path,
                size=size
            )
    if not delete:
        download.startDownload()

class Download:
    def __init__(self):
        self.download_files = []
        self.downloaded_files = []
        self.download_size = 0
        self.downloaded_size = 0
        self.amount_to_download = 0

    def addDownloadFile(self, url, save_path, size):
        file = DownloadFile(url, save_path, size)
        self.download_files.append(file)
        self.download_size += file.size

    def DownloadFileDone(self, last, disable_size):
        if last:
            self.downloaded_files.append(self.download_files[-1])
            self.downloaded_size += self.download_files[-1].size
            self.download_files = self.download_files[ : -1]

            if not disable_size:
                print(f"{len(self.downloaded_files)} of {self.amount_to_download} files downloaded - {int(self.downloaded_size / 1000000)} MB of {int(self.download_size / 1000000)} MB downloaded")
            else:
                print(f"{len(self.downloaded_files)} of {self.amount_to_download} files downloaded")


    def startDownload(self, last=True, disable_size=False):
        self.amount_to_download = len(self.download_files)
        for _ in self.download_files: 
            if last:
                # Check if subfolders exist
                folder_paths = self.download_files[-1].save_path.split('/')[ : -1]
                folder_path = '/'.join(folder_paths)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # Get file and download it
                response = requests.get( self.download_files[-1].download_url)
                open( self.download_files[-1].save_path, "wb").write(response.content)

                self.DownloadFileDone(last, disable_size)

        Win().popup("Message", "Download complete")

class DownloadFile():
    def __init__(self, url, save_path, size):
        self.download_url = url
        self.save_path = save_path
        self.size = size
                


