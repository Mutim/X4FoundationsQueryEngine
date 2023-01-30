import re
"""
    Configuration File. Some things are changed from within the application. Most settings should be fine to be left
    as is, though if you find that you want more fine control, feel free to change an entry from this file.
"""

tags = "#ffd700"
parameters = "#5F9EA0"
strings = "#8fbc8f"
comments = "#329664"
misc = "#ff5700"


configuration = {
    # Window Configuration
    "window_width": 1100,
    "window_height": 650,
    "appearance_mode": "System",  # Modes: "System" (standard), "Dark", "Light"
    "color_theme": "blue",  # Themes (Button Colors): "blue" (standard), "green", "dark-blue"

    # Data Configuration - Search
    "extracted_path": r"D:\\SteamLibrary\\steamapps\\common\\X4 Foundations\\extracted\\",
    "exact_match": False,

    # Text Configuration
    "text_scale": 100,
    # List of keywords to be highlighted by syntax highlighter. Feel free to add/remove/change colors.
    "syntax_keywords": [
        # Tags
        (">", tags), ("<", tags), ("/>", tags), ("</", tags), ("xmlns", tags), ("cues", tags), ("xsi", tags),
        ("mdscript", tags), ("cue", tags), ("replace", tags), ("do_if", tags), ("actions", tags), ("library", tags),
        ("substitute_text", tags), ("run_actions", tags), ("param", tags), ("set_value", tags),

        # Strings
        ("=", strings),
        (re.compile(r"([a-zA-Z]+)\s*=\s*([a-zA-Z]+)"), strings),

        # Comments
        (re.compile(r"(<!--[\s\S]*?-->)"), comments)

    ]
}
