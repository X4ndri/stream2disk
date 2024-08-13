import dearpygui.dearpygui as dpg
from pathlib import Path
import subprocess
import threading
import sys



stop_event = threading.Event()

library = {}
library_path = ''
output_text = ''
MAX_LINES = 22


def stream(sender, app_data):
    main()


def open_file_dialog(sender, app_data):
    # Open the file dialog to select a directory
    dpg.show_item("file_dialog")


def update_directory_path(sender, app_data):
    global library
    global library_path

    library_path = Path(app_data['file_path_name'])

    dpg.set_value("directory_text_field", app_data['file_path_name'])
    dpg.show_item("lib_params")
    library = group_paths_by_parent(read_library(dpg.get_value("directory_text_field")))
    s = [k for k in library.keys()]
    s.append("other")

    dpg.add_radio_button(parent="lib_params_season_radio_buttons", items=s, horizontal=True, callback=parse_season, tag="seasons", default_value='other')
    dpg.add_input_text(parent="lib_params_season_radio_buttons", width=hper(0.05), show=True, tag="input_season_name")


def parse_season(sender, app_data):
    if app_data == "other":
        dpg.show_item("input_season_name")
    else:
        dpg.set_value("input_season_name", '')
        dpg.hide_item("input_season_name")

        l = len(parse_season_contents(app_data))
        dpg.show_item("episode_counter")
        dpg.set_value("episode_counter", l)


def show_file_dialog(sender, app_data):
    # Show the file dialog when the button is clicked
    dpg.show_item("file_dialog")


def vper(height_percentage):
    viewport_height = dpg.get_viewport_height()
    height = int(viewport_height * height_percentage)
    return height


def hper(width_percentage):
    viewport_width = dpg.get_viewport_width()
    width = int(viewport_width * width_percentage)
    return width

def read_library(filepath):
    filepath = Path(filepath)
    # find all .mp4 files
    mp4files = list(filepath.rglob('*.mp4'))
    return mp4files

def group_paths_by_parent(paths):
    # Dictionary to store parent folder and corresponding list of stems
    result = {}
    for p in paths:
        parent_folder = p.parent
        stem = p.stem
        if parent_folder in result:
            result[parent_folder].append(stem)
        else:
            result[parent_folder] = [stem]
    result = {parent_folder.stem: stems for parent_folder, stems in result.items()}
    
    return result
    

def parse_season_contents(key):
    if key in list(library.keys()):
        return library[key]
    else:
        return []
    

def update_output_text():
    # Update the text widget with the latest output
    dpg.set_value("output_text", output_text)



def run_ffmpeg_command(link, output_path):
    global output_text
    # Command to run ffmpeg
    cmd = ["ffmpeg", 
           "-i",
           str(link),
        # "https://aa.bigtimedelivery.net/_v13/d453ac692b52eae60bea6cb749c9fe53172d2c2019e9288a5f1aee55412b4e31ccb2118ca9e7dbf2db03ef56e9ce8e9d863e126e1bb36faab28e5b4a353c4ee9cc66eeb51dc18895faa1f49d3f7c0118dc3be3b9e93cb82f859bd2d6827a350a0e7df28171542f3697a6a7c964e43188292eb9e15322a8253209e34288b093e2/playlist.m3u8",
           "-c", 
           "copy", 
           "-bsf:a", 
           "aac_adtstoasc",
        #    "/home/ahmad/Download//home/ahmad/projects/stream2disk/himym/test.mp4" 
           str(output_path)
           ]

    # Run the command and capture output
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # # Read stdout and stderr in real-time
    # while True:
    #     output = process.stderr.readline()
    #     print(output)
    #     if output == "" and process.poll() is not None:
    #         break
    #     if output:
    #         output_text += output
    #         update_output_text()
    
    while not stop_event.is_set():
        output = process.stderr.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            output_text += output

            # Split text into lines
            lines = output_text.splitlines()

            # If more than MAX_LINES, keep only the most recent lines
            if len(lines) > MAX_LINES:
                lines = lines[-MAX_LINES:]

            # Join lines back into a single string and update the text field
            output_text = "\n".join(lines) + "\n"
            update_output_text()

    process.terminate()
    output_text += "\nSTOPPED\n"
    update_output_text()
    stop_event.clear()
    process.wait()


def start_ffmpeg_thread(link, output_path):
    # Run the ffmpeg command in a separate thread to avoid blocking the GUI
    threading.Thread(target=run_ffmpeg_command, args=[link, output_path], daemon=True).start()



def archx():

    dpg.create_context()
    dpg.create_viewport(title='Stream2Disk', height=750, width=900)
    dpg.setup_dearpygui()



    # link input window
    with dpg.window(label="Stream Info", height=vper(0.1), width=hper(0.8), pos=[hper(0.1),vper(0.01)]):
        dpg.add_input_text(label="Enter m3u8 stream", default_value="playlist.m3u8", height=50, width=500, tag="link_field")
            # Directory text field
        dpg.add_input_text(label="Directory Path", tag="directory_text_field", width=400)
        
        # Browse button
        dpg.add_button(label="Browse", callback=show_file_dialog)

        with dpg.file_dialog(directory_selector=True, callback=update_directory_path, tag="file_dialog", show=False, height=vper(0.4), width=hper(0.8)):
            dpg.add_file_extension(".*")

    # library window
    with dpg.window(label='Library Parameters', tag="lib_params", height=vper(0.3), width=hper(0.4), pos=[hper(0.3),vper(0.15)], show=False):
        dpg.add_text("seasons found in library", color=(255, 255, 255))
        with dpg.group(horizontal=False):
            dpg.add_spacer()
            dpg.add_group(tag="lib_params_season_radio_buttons", horizontal=True)
            dpg.add_spacer()
            dpg.add_spacer(height=vper(0.04))
            dpg.add_group(tag="lib_params_episode_params")
            dpg.add_spacer()
            dpg.add_spacer(height=vper(0.04))
            dpg.add_group(tag='submit_group')

        dpg.add_input_int(
            parent="lib_params_episode_params", 
            label="episode counter", 
            tag="episode_counter", 
            default_value=0, 
            min_value=0, 
            max_value=500,
            width = hper(0.09),
            show=True
        )
        
        
        dpg.add_button(parent='submit_group', callback=stream, width=hper(0.1), label="Stream")
        dpg.add_button(parent='submit_group', callback=stop_event.set, width=hper(0.1), label="Stop")


    # progress window
    with dpg.window(label='progress', tag="cmd", height=vper(0.5), width=hper(0.8), pos=[hper(0.1),vper(0.46)], show=True):
        # Add a text widget to display the output
        dpg.add_text("FFmpeg Output:")
        
        # Add an input text widget to display the output
        dpg.add_input_text(tag="output_text", multiline=True, readonly=True, width=780, height=550)







    dpg.show_viewport()

    dpg.start_dearpygui()
    dpg.destroy_context()


def main():

    link = dpg.get_value("link_field")
    sn = dpg.get_value("seasons")
    if sn == 'other':
        sn = dpg.get_value("input_season_name")    
    episode = str(dpg.get_value("episode_counter"))
    output_season_path = library_path.joinpath(sn)
    output_season_path.mkdir(exist_ok=True, parents=True)
    output_episode_path = output_season_path.joinpath(episode).with_suffix('.mp4')
    # try:
    if output_season_path.is_file():
        raise FileExistsError
    # except:
    start_ffmpeg_thread(link, output_path=output_episode_path)


if __name__ == "__main__":
    archx()