import tkinter as tk
import tkinter.ttk as ttk
from typing import Union
from lxml import etree
import json
import xmltodict
import re
import os

import config

Widget = Union[tk.Widget, ttk.Widget]


class SyntaxHighlighter:
    def __init__(self, xml_file, textbox):
        self.xml_file = xml_file
        self.tree = etree.parse(self.xml_file)
        self.root = self.tree.getroot()
        self.textbox = textbox

    def highlight(self):
        char_count = 0

        xml_string = etree.tostring(self.root, encoding='unicode', pretty_print=True)
        self.textbox.insert("end", xml_string, "utf-8")
        tag_re = re.compile(r'(<[^\s<>]+>)')
        close_tag_re = re.compile(r'(</[^\s<>]+>)')
        param_re = re.compile(r'(<[^\s<>]+(?= ))')
        strings_re = re.compile(r'"([^"]*)"')
        comment_re = re.compile(r"(<!--.*?-->)", re.DOTALL)

        for m in tag_re.finditer(xml_string):
            keyword_str = m.group()
            start_index = m.start()
            end_index = m.end()
            adjusted_start = "end-%dc" % (len(xml_string) - start_index + char_count + 1)
            adjusted_end = "end-%dc" % (len(xml_string) - end_index + char_count + 1)
            self.textbox.tag_config(keyword_str, foreground="#ffd700")
            self.textbox.tag_add(keyword_str, adjusted_start, adjusted_end)

        for m in close_tag_re.finditer(xml_string):
            keyword_str = m.group()
            start_index = m.start()
            end_index = m.end()
            adjusted_start = "end-%dc" % (len(xml_string) - start_index + char_count + 1)
            adjusted_end = "end-%dc" % (len(xml_string) - end_index + char_count + 1)
            self.textbox.tag_config(keyword_str, foreground="#ffd700")
            self.textbox.tag_add(keyword_str, adjusted_start, adjusted_end)

        for m in param_re.finditer(xml_string):
            keyword_str = m.group()
            start_index = m.start()
            end_index = m.end()
            adjusted_start = "end-%dc" % (len(xml_string) - start_index + char_count + 1)
            adjusted_end = "end-%dc" % (len(xml_string) - end_index + char_count + 1)
            self.textbox.tag_config(keyword_str, foreground="#5F9EA0")
            self.textbox.tag_add(keyword_str, adjusted_start, adjusted_end)

        for m in strings_re.finditer(xml_string):
            keyword_str = m.group()
            start_index = m.start()
            end_index = m.end()
            adjusted_start = "end-%dc" % (len(xml_string) - start_index + char_count + 1)
            adjusted_end = "end-%dc" % (len(xml_string) - end_index + char_count + 1)
            self.textbox.tag_config(keyword_str, foreground="#8fbc8f")
            self.textbox.tag_add(keyword_str, adjusted_start, adjusted_end)

        for m in comment_re.finditer(xml_string):
            char_count = 0
            comment_str = m.group()
            print(comment_str)
            start_index = xml_string.index(comment_str, char_count)
            end_index = start_index + len(comment_str)
            print(f"Start Index: {start_index}, End Index: {end_index}")
            adjusted_start = "end-%dc" % (len(xml_string) - start_index + char_count + 1)
            adjusted_end = "end-%dc" % (len(xml_string) - end_index + char_count + 1)
            print(f"Adjusted Start: {adjusted_start}, Adjusted End: {adjusted_end}")
            self.textbox.tag_config("comment", foreground="#329664")
            self.textbox.tag_add("comment", adjusted_start, adjusted_end)
            char_count += len(comment_str)

        self.textbox.insert("end", "\n", "utf-8")


def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def xml_to_json(xml_file):
    with open(xml_file, encoding='utf-8') as f:
        xml_string = f.read()
    data = xmltodict.parse(xml_string)
    json_string = json.dumps(data, ensure_ascii=True, indent=4)

    return json_string


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
