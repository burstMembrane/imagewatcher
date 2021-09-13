#!/usr/bin/python3

import logging
from os import environ, path
import dearpygui.dearpygui as dpg
from sys import exit
from subprocess import check_output
import time
import statistics
import logging


class ImageViewer:
    def __init__(self):
        self.img_id = 0
        # IMAGE SETUP
        self.directory = ""
        self.current_img = 0
        self.img_paths = []
        self.img_path = ''
        self.paddingW = 0
        self.paddingH = 70
        self.dragTimer = 0.0
        self.drag_x = []
        self.drag_y = []
        screeninfo = check_output(["/usr/bin/xrandr"])
        for line in screeninfo.decode().split("\n"):
            if "primary" in line:
                f = line.find("primary")
                logging.debug(f)

        self.window_size = (640,
                            480)

        self.w, self.h = self.window_size

        # create viewport takes in config options too!
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=True, clear_color=[0, 0, 0, 0])

        dpg.set_viewport_max_height(1080)
        dpg.set_viewport_clear_color([0.0, 0.0, 0.0, 0.0])

        # MOUSE SETUP
        dpg.setup_dearpygui(viewport=self.viewport)
        dpg.show_viewport(self.viewport)

        dpg.setup_registries()

        logging.debug(
            f"vp_client_w: {self.w} vp_client_h:  {self.h}")

        # WINDOW SETUP
        dpg.set_viewport_always_top(True)
        with dpg.window(label="Imagewatcher",  collapsed=True, modal=False, width=self.w, height=self.h, id="main_window", no_scrollbar=True, no_background=True) as w:
            self.window = w
        with dpg.theme(id="theme_id"):
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize,
                                0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,
                                0)
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,
                                (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_Border,
                                (0, 0, 0, 0))
            dpg.add_theme_style(dpg.mvStyleVar_Alpha,)

        dpg.set_item_theme("main_window", "theme_id")
        # dpg.set_item_theme(self.viewport, "theme_id")
        dpg.set_viewport_clear_color([0, 0.0, 0.0, 0.0])
        logging.debug(dpg.get_viewport_configuration(dpg.mvThemeCol_WindowBg))
        dpg.set_primary_window("main_window", True)
        dpg.add_key_press_handler(callback=self.handle_keys)
        dpg.add_mouse_drag_handler(callback=self.handle_windowdrag)
        self.show_info = False
        self.shouldquit = False
        self.init_dialog_selector()

        # self.init_menu_bar()

    def init_menu_bar(self):
        with dpg.menu_bar(parent="main_window", id="menu_bar"):
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="Open Directory", callback=lambda: dpg.show_item("directory_dialog"))
                dpg.add_menu_item(label="Quit", callback=self.quit)
            with dpg.menu(label="IMAGEWATCHER v0.1", parent="menu_bar", indent=self.w-150):
                dpg.add_menu_item(
                    label="About", callback=lambda: logging.debug("hello"))
    # define moving average function

    def handle_windowdrag(self, sender, dragpos, user_data):

        if self.dragTimer == 0:
            self.dragTimer = time.time()
        logging.debug(self.dragTimer)
        # self.print_cb_data(sender, dragpos, user_data)
        currX, currY = dpg.get_item_pos("main_window")
        if(currX == 100):
            self.dragTimer = 0
        posX = dragpos[1]
        posY = dragpos[2]
        self.drag_x.append(posX)
        self.drag_y.append(posY)
        meanX = statistics.mean(self.drag_x)
        meanY = statistics.mean(self.drag_y)
        logging.debug(f"dragpos {posX,posY} currPos{currX, currY}")

        if(time.time() - self.dragTimer > 0.1):

            dpg.set_viewport_pos(
                [meanX,  meanY])

            self.dragTimer = 0.0
            self.drag_x.clear()
            self.drag_y.clear()

    def print_cb_data(self, sender, app_data, user_data):
        logging.debug(f"sender is: {sender}")
        logging.debug(f"app_data is: {app_data}")
        logging.debug(f"user_data is: {user_data}")

    def handle_dialog(self, sender, app_data, user_data):
        self.directory = path.join(
            app_data["file_path_name"], app_data["file_name"])
        logging.debug(f"setting dir to {self.directory}")
        dpg.add_text(f"watching.. {self.directory}", parent="main_window")

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

    def show_image(self):
        """ Loads the image and adds it to the window"""

    def clear(self):
        """ Clears the window  """

    def set_image(self, image_path):
        if self.img_id > 0:
            dpg.delete_item("main_image")
        dpg.hide_item("main_window")
        logging.debug("setting image")
        self.img_path = image_path
        #  clear the screen
        if len(image_path) > 0:
            width, height, channels, data = dpg.load_image(image_path)

            with dpg.texture_registry() as reg_id:
                texture_id = dpg.add_static_texture(
                    width, height, data, parent=reg_id)
                vp_width = self.w
                vp_height = self.h
                if height > vp_height or width > vp_width:
                    diff = abs((vp_width/vp_height) / (width/height)) + 0.5

                    logging.debug(f"difference:  {diff}")
                    height = height / diff
                    width = width / diff
                    logging.debug(
                        f"image is larger than window... resizing to {width}x{height}")

                dpg.set_viewport_height(height)
                dpg.set_viewport_width(width)

                self.img_id = dpg.add_image(
                    texture_id, parent="main_window", id='main_image', width=width, height=height)

                logging.debug(self.img_id)

            # load the image
            dpg.show_item("main_window")
            if image_path not in self.img_paths:
                self.img_paths.append(image_path)
                logging.info(self.img_paths)

    def handle_keys(self, sender, key, user_data):
        self.print_cb_data(sender, key, user_data)
        if (key == 265):
            logging.debug("jumping to start of images")
            self.set_image(self.img_paths[0])
        if (key == 264):
            logging.debug("jumping to end of images")
            self.set_image(self.img_paths[-1])
        if(key == 262):
            logging.debug("pressed right")
            if len(self.img_paths) > 1:

                self.current_img = self.img_paths.index(self.img_path) - 1
                self.current_img = max(
                    self.current_img, 0)
                logging.info(f" K_LEFT setting to image:  {self.current_img}")
                self.set_image(self.img_paths[self.current_img])
        if(key == 263):
            if len(self.img_paths) > 1 & self.current_img < len(self.img_paths):
                self.current_img += 1

                self.set_image(
                    self.img_paths[self.current_img % len(self.img_paths)])
        if(key == 256):

            self.quit()

    def run(self):
        while dpg.is_dearpygui_running():
            try:

                dpg.render_dearpygui_frame()
                self.show_image()
                #     run main loop
            except KeyboardInterrupt or SystemExit:
                logging.info("quitting...")
                self.quit()

    def quit(self):
        logging.debug("quitting...")
        dpg.stop_dearpygui()
        dpg.cleanup_dearpygui()


if __name__ == '__main__':
    # test
    viewer = ImageViewer()
    viewer.set_image('test.jpeg')

    viewer.run()
    viewer.quit()
