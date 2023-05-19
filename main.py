import os
from pathlib import Path
from time import sleep
from datetime import datetime
from dataclasses import dataclass
import re

@dataclass
class FileInfo:
    
    filepath: Path
    last_modified: int
    
    def from_path(path:Path):
        return FileInfo(path, last_modified=os.path.getmtime(path.as_posix()))
    
    def read(self):
        return open(self.filepath.as_posix()).read()
    
    def has_been_updated(self):
        latest_modified = os.path.getmtime(self.filepath.as_posix())
        if latest_modified == self.last_modified:
            return False
        self.last_modified = latest_modified
        return True

OUTFILE = "./out/index.html"
OUTFILE2 = "./index.html"
INFILE = "./index.html"
GLOBAL = 'global'
UI_DIR = "./ui"
GLOBAL_DIR = os.path.join(UI_DIR, GLOBAL)
SCREENS_DIR = os.path.join(UI_DIR, "screens")
OUT_HTML_FILENAME = "index.html"
INCLUDE_RGX = "@include\(\"(.*)\"\)"
CONTENT_RGX = "@content\(\"(.*)\"\)"
TIMEOUT = 1

def get_all_files_in_directory(directory_path:str):
    for filename in os.listdir(directory_path):
        yield (filename, Path(os.path.join(directory_path, filename)))


def as_html(path:str):
    content = open(path).read()
    if content == "":
        return ""
    
    return {
        ".html": content,
        ".css": f"<style scoped>\n{content}\n</style>",
        ".js": f"<script>{content}</script>",
    }[Path(path).suffix]
    

def resolve_html_includes(output_html:FileInfo):    
    output_html_content = output_html.read()
    
    for path in re.findall(INCLUDE_RGX, output_html_content):
        to_replace = f"@include(\"{path}\")"
        if path.startswith("./"):
           path = output_html.filepath.parent.joinpath(path).as_posix()
    
        output_html_content = output_html_content.replace(to_replace, as_html(path))
    return output_html_content



def generate_html(files:dict[str, dict[str, FileInfo]]):
    output_html = files[GLOBAL][OUT_HTML_FILENAME]
    output_html_content = resolve_html_includes(output_html) 
    
    content_screen = re.search(CONTENT_RGX, output_html_content)
    if content_screen is None:
        raise Exception(f""" must provide first screen folder name as {'@content("[FIRST_SCREEN_FOLDER_NAME]")'}""")
    
    insert_screens = lambda screensStr: output_html_content.replace(content_screen.group(), screensStr)

    first_screen_name = content_screen.groups()[0]
    
    all_screens_content = ""
    for screen, screen_path in files.items():
        
        if screen == GLOBAL: continue
        screen_info = screen_path.get(OUT_HTML_FILENAME)
        if screen_info is None: continue
        content = resolve_html_includes(screen_info)
        
        display = "" if screen == first_screen_name else "invisible"
        all_screens_content += "\n" + content.replace("@page", f'page="{screen}" {display}')
        
    with open(OUTFILE, 'w') as f:
        result = insert_screens(all_screens_content)
        f.write(result)
        print("updated", OUTFILE)
        
    with open(OUTFILE2, 'w') as f:
        result = insert_screens(all_screens_content)
        f.write(result)
        print("updated", OUTFILE2)
    


def main():
    files: dict[str, dict[str, FileInfo]] = {GLOBAL: {}}
    while True:
        
        should_recompile = False
        
        for filename, filepath in get_all_files_in_directory(GLOBAL_DIR):
            if not filename in files[GLOBAL]:
               files[GLOBAL][filename] = FileInfo.from_path(filepath)
               should_recompile = True

            if files[GLOBAL][filename].has_been_updated():
                should_recompile = True  
                print(filepath, "has been updated")
                
        if not OUT_HTML_FILENAME in files[GLOBAL]:
            raise Exception(f"must include {OUT_HTML_FILENAME} in {GLOBAL_DIR}")
            
        for (dirname, dirpath) in get_all_files_in_directory(SCREENS_DIR):
            if not dirname in files:
                files[dirname] = {}
                print("new screen dir", dirname)
            
            for filename, filepath in get_all_files_in_directory(dirpath):
                if not filename in files[dirname]:
                   files[dirname][filename] = FileInfo.from_path(filepath)
                   should_recompile = True

                if files[dirname][filename].has_been_updated():
                    should_recompile = True  
                    print(filepath, "has been updated")
                   
        if should_recompile:          
           generate_html(files) 
        
        sleep(TIMEOUT) 
    

if __name__ == "__main__":
    main()