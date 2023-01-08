"""
    Configuration File. Some things are changed from within the application. Most settings should be fine to be left
    as is, though if you find that you want more fine control, feel free to change an entry from this file.
"""

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
    "text_scale": 100
}
