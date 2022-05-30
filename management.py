import requests, json, uuid, os

def generatePaths(management_path): # function to generate paths.json file which is a file used for downloading liveries
    management_path = management_path
    paths = []
    for root, dirs, files in os.walk(f"{management_path}/Liveries"):
        if os.path.isdir(f"{root}{files}"): # Skip folders
            continue 

        # Get current paths
        # paths_url = 'https://raw.githubusercontent.com/drumbart/VFA-27_Ready_Room/master/paths.json'
        # response = requests.get(paths_url).text
        # current_paths = json.loads(response)
        with open('paths.json', 'r') as f:
            current_paths = json.load(f)

        for file in files:
            file_path = f"{root}/{file}".replace('\\','/').replace(management_path, '')
            pathId = None

            # Check if path already exist in current path file
            for current_path in current_paths:
                if current_path["path"] == file_path:
                    pathId = current_path["id"] # Assign already current id
            if pathId is None:
                pathId = generatePathId() # No id exist. Generate one

            path = {
                "path": file_path,
                "date": int(os.path.getmtime(f"{management_path}{file_path}")),
                "delete": False,
                "size": int(os.path.getsize(f"{management_path}{file_path}")),
                "id": pathId
            }
            paths.append(path)

        # Loop through and get now deleted paths
        for current_path in current_paths:
            exist = os.path.exists(f"{management_path}{current_path['path']}") # Exist in management folder
            print(f"Generating path for {current_path['path']}")
            if exist is False:
                current_path["delete"] = True
                paths.append(current_path)
            
    with open(f'{management_path}/paths.json', 'w') as f: # save paths.json file in management folder
        f.write(json.dumps(paths, indent=4))


def generatePathId(): # generate ID for path
    id = str(uuid.uuid4())
    return id