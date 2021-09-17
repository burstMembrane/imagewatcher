from dearpygui.dearpygui import add_menu_item, menu, menu_bar, show_item
import logging


class ImageViewerMenuBar:
    def __init__(self, parent_id, menu_id):
        self.id = menu_id
        with menu_bar(parent=parent_id, id=self.id):
            with menu(label="File"):
                add_menu_item(
                    label="Open Directory", callback=lambda: show_item("directory_dialog"))
                add_menu_item(label="Quit", callback=self.quit)
            with menu(label="IMAGEWATCHER v0.1", parent="menu_bar"):
                add_menu_item(
                    label="About", callback=lambda: logging.debug("hello"))
