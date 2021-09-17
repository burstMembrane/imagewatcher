import dearpygui.dearpygui as dpg
import logging
from os import path


class ImageViewerDialog:
    def __init__(self):
        self.init_dialog_selector()

    def handle_dialog(self, sender, app_data, user_data):
        self.directory = path.join(
            app_data["file_path_name"], app_data["file_name"])
        logging.debug(f"setting dir to {self.directory}")

    def get_directory(self):
        return self.directory

    def init_dialog_selector(self):
        with dpg.file_dialog(directory_selector=True, modal=True, show=False, callback=self.handle_dialog, id="directory_dialog"):
            dpg.add_file_extension(".*", color=(255, 255, 255, 255))
            dpg.add_file_extension(
                "Source files (*.cpp *.h *.hpp){.cpp,.h,.hpp}", color=(0, 255, 255, 255))
            dpg.add_file_extension(".cpp", color=(255, 255, 0, 255))
            dpg.add_file_extension(".h", color=(
                255, 0, 255, 255), custom_text="header")
            dpg.add_file_extension(
                "Python(.py){.py}", color=(0, 255, 0, 255))
