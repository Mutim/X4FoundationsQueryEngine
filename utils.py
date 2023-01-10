import tkinter as tk
import tkinter.ttk as ttk
from typing import Union
import xml.etree.ElementTree as ET

Widget = Union[tk.Widget, ttk.Widget]


class SyntaxHighlighter:
    def __init__(self, xml_file, textbox, keywords):
        self.xml_file = xml_file
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()
        self.textbox = textbox
        self.keywords = keywords

    def highlight(self):
        xml_string = ET.tostring(self.root, encoding='UTF-8').decode()

        # insert the xml string into the textbox
        self.textbox.insert("end", xml_string)
        # create a list to store the indices of the start and end of each keyword
        tag_indices = []
        # iterate over the string and look for keywords
        for i, c in enumerate(xml_string):
            if c in self.keywords:
                start_index = f"{i}.0"
                end_index = f"{i + len(c)}.0"
                tag_indices.append((start_index, end_index))
        print(tag_indices)

        # apply tags to the keywords based on the indices stored in tag_indices
        for start_index, end_index in tag_indices:
            self.textbox.tag_add("keyword", start_index, end_index)

        # configure the tags to change the text color not working....
        self.textbox.tag_config("keyword", foreground="red")


class ToolTip(tk.Toplevel):
    # amount to adjust fade by on every animation frame
    FADE_INC: float = .07
    # amount of milliseconds to wait before next animation state
    FADE_MS: int = 20

    def __init__(self, master, **kwargs):
        tk.Toplevel.__init__(self, master)
        # make window invisible, on the top, and strip all window decorations/features
        self.attributes('-alpha', 0, '-topmost', True)
        self.overrideredirect(1)
        # style and create label. you can override style with kwargs
        style = dict(bd=2, relief='raised', font='courier 10 bold', bg='#F0F8FF', anchor='w', border='1.0')
        self.label = tk.Label(self, **{**style, **kwargs})
        self.label.grid(row=0, column=0, sticky='w')
        # used to determine if an opposing fade is already in progress
        self.fout: bool = False

    def bind(self, target: Widget, text: str, **kwargs):
        # bind Enter(mouseOver) and Leave(mouseOut) events to the target of this tooltip
        target.bind('<Enter>', lambda e: self.fadein(0, text, e))
        target.bind('<Leave>', lambda e: self.fadeout(1 - ToolTip.FADE_INC, e))

    def fadein(self, alpha: float, text: str = None, event: tk.Event = None):
        # if event and text then this call came from target
        # ~ we can consider this a "fresh/new" call
        if event and text:
            # if we are in the middle of fading out jump to end of fade
            if self.fout:
                self.attributes('-alpha', 0)
                # indicate that we are fading in
                self.fout = False
            # assign text to label
            self.label.configure(text=f'{text:^{len(text) + 2}}')
            # update so the proceeding geometry will be correct
            self.update()
            # x and y offsets
            offset_x = event.widget.winfo_width() + 2
            offset_y = int((event.widget.winfo_height() - self.label.winfo_height()) / 2)
            # get geometry
            w = self.label.winfo_width()
            h = self.label.winfo_height()
            x = event.widget.winfo_rootx() + offset_x
            y = event.widget.winfo_rooty() + offset_y
            # apply geometry
            self.geometry(f'{w}x{h}+{x}+{y}')

        # if we aren't fading out, fade in
        if not self.fout:
            self.attributes('-alpha', alpha)

            if alpha < 1:
                self.after(ToolTip.FADE_MS, lambda: self.fadein(min(alpha + ToolTip.FADE_INC, 1)))

    def fadeout(self, alpha: float, event: tk.Event = None):
        # if event then this call came from target
        # ~ we can consider this a "fresh/new" call
        if event:
            # indicate that we are fading out
            self.fout = True

        # if we aren't fading in, fade out
        if self.fout:
            self.attributes('-alpha', alpha)

            if alpha > 0:
                self.after(ToolTip.FADE_MS, lambda: self.fadeout(max(alpha - ToolTip.FADE_INC, 0)))
