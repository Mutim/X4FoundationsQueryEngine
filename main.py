import customtkinter
import os
import sys
import re
import glob
import json
from PIL import Image

from utils import ToolTip, SyntaxHighlighter

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and restart the program")
else:
    from config import configuration as config

customtkinter.set_appearance_mode(config["appearance_mode"])
customtkinter.set_default_color_theme(config["color_theme"])

# Query Filings
query_t = []
query_md = []
query_libraries = []
query_index = []
query_aiscripts = []

mapped_list = {
            't': query_t,
            'md': query_md,
            'libraries': query_libraries,
            'index': query_index,
            'aiscripts': query_aiscripts
        }


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("X4 Foundations Query Engine (XQE)")
        self.geometry(f"{config['window_width']}x{config['window_height']}+0+0")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo.png")),
                                                 size=(56, 56))
        self.home_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "dark/home_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "light/home_light.png")),
            size=(36, 36))
        self.search_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "dark/search_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "light/search_light.png")),
            size=(36, 36))
        self.converter_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "dark/converter_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "light/converter_light.png")),
            size=(36, 36))

        # create sidebar frame with sections to tools
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="    X4 Query Engine",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.search_frame_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40,
                                                           border_spacing=10, text="Keyword Search",
                                                           fg_color="transparent", text_color=("gray10", "gray90"),
                                                           hover_color=("gray70", "gray30"),
                                                           image=self.search_image, anchor="w",
                                                           command=self.search_frame_button_event)
        self.search_frame_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=5, height=40,
                                                      border_spacing=10, text="Converter",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      image=self.converter_image, anchor="w",
                                                      command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        # # # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        # TODO: Add main configuration file, and the readme file.

        # # # create search frame
        self.search_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.search_frame.grid_columnconfigure(2, weight=1)
        self.search_frame.grid_rowconfigure(2, weight=1)

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self.search_frame, placeholder_text="Game File Query")
        self.entry.grid(row=3, column=1, columnspan=3, padx=(5, 5), pady=(20, 20), sticky="nsew")
        self.entry.bind('<Return>', self.on_enter)

        self.main_button_1 = customtkinter.CTkButton(master=self.search_frame, text='Search', fg_color="transparent", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), command=self.query_result)
        self.main_button_1.grid(row=3, column=4, padx=(10, 10), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self.search_frame, width=300, font=('DejaVu Sans Mono', 12, 'normal'))
        self.textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(10, 0), pady=(10, 0), sticky="nsew")

        # create tabs
        self.tabview = customtkinter.CTkTabview(self.search_frame, width=0)
        self.tabview.grid(row=0, rowspan=1, column=4, padx=(10, 10), pady=(0, 0), sticky="w")
        self.tabview.add("Filter")
        self.tabview.add("Options")
        self.tabview.add("Configure")
        self.tabview.tab("Filter").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Options").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Configure").grid_columnconfigure(0, weight=1)

        # # Scripts Menu
        self.scripts_menu = customtkinter.CTkLabel(self.tabview.tab("Filter"), text="Filter Result by Directory")
        self.scripts_menu.grid(row=0, column=0, padx=5, pady=(0, 0))
        # Script Type Buttons
        self.scripts_button1 = customtkinter.CTkButton(self.tabview.tab("Filter"), text="T",
                                                       command=lambda: self.sidebar_button_event('T'))
        self.scripts_button1.grid(row=1, column=0, padx=5, pady=(0, 10))
        self.scripts_button2 = customtkinter.CTkButton(self.tabview.tab("Filter"), text="MD",
                                                       command=lambda: self.sidebar_button_event('MD'))
        self.scripts_button2.grid(row=2, column=0, padx=5, pady=(0, 10))
        self.scripts_button3 = customtkinter.CTkButton(self.tabview.tab("Filter"), text="Libraries",
                                                       command=lambda: self.sidebar_button_event('Libraries'))
        self.scripts_button3.grid(row=3, column=0, padx=5, pady=(0, 10))
        self.scripts_button4 = customtkinter.CTkButton(self.tabview.tab("Filter"), text="Index",
                                                       command=lambda: self.sidebar_button_event('Index'))
        self.scripts_button4.grid(row=4, column=0, padx=5, pady=(0, 10))
        self.scripts_button5 = customtkinter.CTkButton(self.tabview.tab("Filter"), text="AI Scripts",
                                                       command=lambda: self.sidebar_button_event('AIScripts'))
        self.scripts_button5.grid(row=5, column=0, padx=5, pady=(0, 10))
        self.scripts_button5 = customtkinter.CTkButton(self.tabview.tab("Filter"), text="All Instance",
                                                       command=lambda: self.sidebar_button_event('AIScripts'))
        self.scripts_button5.grid(row=5, column=0, padx=5, pady=(0, 10))

        # # Options Menu

        self.dialog_button = customtkinter.CTkButton(self.tabview.tab("Options"), text="Open Dialog",
                                                     command=self.open_input_dialog_event)
        self.dialog_button.grid(row=0, column=0, padx=5, pady=(0, 10))

        # # Configuration Menu
        self.scripts_menu = customtkinter.CTkLabel(self.tabview.tab("Configure"), text="Configuration")
        self.scripts_menu.grid(row=0, column=0, padx=5, pady=(0, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.tabview.tab("Configure"), text="Appearance Mode:",
                                                            anchor="center")
        self.appearance_mode_label.grid(row=0, column=0, padx=5, pady=(0, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("Configure"),
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=2, column=0, padx=5, pady=(0, 10))

        # Set path to Extracted Game Files
        self.config_label_path_label = customtkinter.CTkLabel(self.tabview.tab("Configure"),
                                                              text="Set Path")
        self.config_label_path_label.grid(row=3)
        self.config_label_path_button = customtkinter.CTkButton(self.tabview.tab("Configure"), text="Extracted Files",
                                                                command=self.set_file_path)

        # Set Scaling Percentage
        self.scaling_label = customtkinter.CTkLabel(self.tabview.tab("Configure"), text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=5, column=0, padx=5, pady=(0, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab("Configure"),
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=6, column=0, padx=5, pady=(0, 10))

        tt = ToolTip(self)

        tt.bind(self.config_label_path_button, f'{config["extracted_path"]}')
        self.config_label_path_button.grid(row=4, column=0, padx=5, pady=(0, 10))

        # # # Create converter frame
        # TODO: Add XML to JSON converter: self.xml_to_json()
        self.converter_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.textbox.insert("0.0", self.example_text())
        self.select_frame_by_name("search_frame")  # select default frame


    # # Logical Helper Functions
    def set_file_path(self):
        dialog = customtkinter.CTkInputDialog(
            text="What is the location to your extracted game files?",
            title="Game File Location")
        config.update({'extracted_path': dialog.get_input()})
        # with open('config.py', 'w+') as f:
        #     json.dump(config['extracted_path'], f
        # self.extracted_path = str(dialog.get_input())

        print(config['extracted_path'])
        # print(f'Setting File Path: {dialog.get_input()}')

    def example_text(self):
        with open("test.xml", "r+") as f:
            contents = f.read()
            return contents

    def on_enter(self, event):
        self.query_result()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Search Commands")
        print("CTkInputDialog:", dialog.get_input())

    def sidebar_button_event(self, button):

        global mapped_list
        self.textbox.delete("0.0", customtkinter.END)

        post_filter_entries = mapped_list[button.lower()]
        print(f'{button} Sidebar button pressed')
        for e in post_filter_entries:
            self.textbox.insert("0.0", f"{e}\n")
        self.textbox.insert("0.0", f"Showing {len(post_filter_entries)} entries for {button.title()}\n\n")

    def pull_data(self, file: str):
        with open(file=file) as f:
            return f.read()

    def highlight_xml(self, file: str):
        highlighter = SyntaxHighlighter(file)
        highlighter.highlight()

    def change_scaling_event(self, new_scaling: str):
        # TODO: set config - int(new_scaling.replace("%", "") for persistence
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def query_result(self):
        global mapped_list
        self.entry.delete(0, customtkinter.END)
        self.textbox.delete("0.0", customtkinter.END)

        word = self.entry.get()
        keyword = re.compile(rf'{word}')
        file_path = config['extracted_path']
        files = glob.glob(f'{file_path}**\\*.xml')
        found_word = False
        number_found = 0

        if not config['exact_match']:
            keyword = re.compile(rf'{word}', re.IGNORECASE)

        print('Running Search....')
        for file in files:
            with open(file, encoding='utf-8') as f:
                contents = f.read()
                # TODO: Make it so that there is a slider in Options to allow for "Exact Match"
                if re.search(keyword, contents):
                    found_word = keyword.search(contents)
                    directory = file.split('\\')[-2]
                    path = '/'.join(file.split('\\')[-2:])
                    filename = '/'.join(file.split('\\')[-1:])
                    self.textbox.insert("0.0", text=f'Found "{found_word.group()}" in {str(path)}\n')
                    number_found += 1
                    if directory in mapped_list.keys():
                        mapped_list[directory].append(filename)
        if not found_word:
            self.textbox.insert("0.0", text=f'\nNo Results Found!\n')
        self.textbox.insert(
            "0.0",
            text=f'\nFound {number_found} files containing: "{keyword.pattern}"\n'
                 f'Select a filter option on the right to refine your search.\n\n')

    def xml_to_json(self, xml_file):
        with open(xml_file, encoding='utf-8') as f:
            xml_string = f.read()
        data = xmltodict.parse(xml_string)
        json_string = json.dumps(data, ensure_ascii=True, indent=4)

        return json_string

    # # #
    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.search_frame_button.configure(fg_color=("gray75", "gray25") if name == "search_frame" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "search_frame":
            self.search_frame.grid(row=0, column=1, columnspan=4, sticky="nsew")
        else:
            self.search_frame.grid_forget()
        if name == "frame_3":
            self.converter_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.converter_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def search_frame_button_event(self):
        self.select_frame_by_name("search_frame")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")


if __name__ == "__main__":
    app = App()
    app.mainloop()
