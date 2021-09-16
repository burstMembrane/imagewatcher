#!/usr/bin/python3

import logging
from os import environ, path
import dearpygui.dearpygui as dpg
from sys import exit
from subprocess import check_output
import time
import statistics
import logging
from PIL import Image
logging.basicConfig(level=logging.INFO)


class ImageViewerPDG:
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
        self.lastPosX = 0
        self.lastPosY = 0
        self.texture_id = 0

        screeninfo = check_output(["/usr/bin/xrandr"])
        for line in screeninfo.decode().split("\n"):
            if "primary" in line:
                f = line.find("primary")
                logging.debug(f)

        self.window_size = (1280,
                            800)

        self.w, self.h = self.window_size
        self.vMinW, self.vMinH = (300, 300)
        # create viewport takes in config options too!
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=True, clear_color=[0, 0, 0, 0], min_width=self.vMinW, min_height=self.vMinH)
        # print(dpg.get_available_content_region(self.viewport))

        dpg.set_viewport_clear_color([0.0, 0.0, 0.0, 0.0])

        # MOUSE SETUP
        dpg.setup_dearpygui(viewport=self.viewport)

        config = dpg.get_viewport_configuration(dpg.mvThemeCol_WindowBg)
        self.clientW = config["client_width"]
        self.clientH = config["client_height"]
        self.center_viewport()
        print(f"clientW:  {self.clientW} \n clientH: {self.clientH}")
        dpg.set_viewport_clear_color([0, 0.0, 0.0, 0.0])
        self.center_viewport()
        dpg.show_viewport(self.viewport)
        dpg.setup_registries()
        self.registry_id = dpg.texture_registry()

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

        dpg.set_primary_window("main_window", True)
        dpg.add_key_press_handler(callback=self.handle_keys)
        dpg.add_mouse_drag_handler(callback=self.handle_windowdrag)
        self.show_info = True
        self.shouldquit = False
        # self.init_dialog_selector()

    def set_directory(self, path, files):
        self.directory = path
        self.img_paths = files
        print(self.img_paths)

    # self.init_menu_bar()
    def center_viewport(self, xoff=0, yoff=0):
        config = dpg.get_viewport_configuration(dpg.mvThemeCol_WindowBg)
        self.currW = dpg.get_viewport_width()
        self.currH = dpg.get_viewport_height()
        logging.debug(f"currH: {self.currW} \n currH: {self.currH}")

        dpg.set_viewport_pos(
            [(self.clientW//2), self.clientH//2])
        dpg.set_viewport_max_width(self.clientW)
        dpg.set_viewport_max_height(self.clientH)

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
        thresh = 5
        if self.dragTimer == 0:
            self.dragTimer = time.time()
            self.lastPosX = dragpos[1]
            self.lastPosY = dragpos[2]

        if(time.time() - self.dragTimer > 0.03):
            logging.debug(self.dragTimer)
            # self.print_cb_data(sender, dragpos, user_data)
            currX, currY = dpg.get_viewport_pos()
            currX = float(currX)
            currY = float(currY)
            posX = dragpos[1] + currX
            posY = dragpos[2] + currY
            if posX >= self.lastPosX-thresh or posX <= self.lastPosX+thresh or posY >= self.lastPosY-thresh or posY <= self.lastPosY+thresh:
                logging.debug(f"dragpos {posX,posY} currPos{currX, currY}")
            if posX > 0.0 and posY > 0.0 and currX > 0.0 and currY > 0.0:
                dpg.set_viewport_pos(
                    [posX,   posY])
                self.lastPosX = posX
                self.lastPosY = posY
                self.dragTimer = 0.0

    def print_cb_data(self, sender, app_data, user_data):
        logging.debug(f"sender is: {sender}")
        logging.debug(f"app_data is: {app_data}")
        logging.debug(f"user_data is: {user_data}")

    def handle_dialog(self, sender, app_data, user_data):
        self.directory = path.join(
            app_data["file_path_name"], app_data["file_name"])
        logging.debug(f"setting dir to {self.directory}")

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

        if image_path != self.img_path:
            if self.img_id > 0:
                dpg.delete_item("main_image")
                dpg.delete_item("text")
            dpg.hide_item("main_window")
            # dpg.minimize_viewport()
            logging.debug("setting image")
            self.img_path = image_path
            #  clear the screen

            width, height, channels, data = dpg.load_image(image_path)
            self.imageW = width
            self.imageH = height

            with dpg.texture_registry() as reg_id:

                vp_width = self.w
                vp_height = self.h

                if height > vp_height or width > vp_width:
                    diff = abs((vp_width/vp_height) / (width/height)) * 2

                    logging.debug(f"difference:  {diff}")
                    height = height / diff
                    width = width / diff
                    logging.debug(
                        f"image is larger than window... resizing to {width}x{height}")
                if self.imageW < self.vMinW or self.imageH < self.vMinH:
                    logging.info("image is less thhan min size... resizing")
                    width = width * 2
                    height = height * 2
                self.texture_id = dpg.add_static_texture(
                    self.imageW, self.imageH, data, parent=reg_id)
                dpg.set_viewport_height(height)
                dpg.set_viewport_width(width)

                # self.center_viewport(xoff=width//2, yoff=height//2)
                self.img_id = dpg.add_image(
                    self.texture_id, parent="main_window", id='main_image', width=width, height=height, label=self.img_path)

                if self.show_info:
                    dpg.add_text(f"File: {self.img_path} Size: {self.imageW}x{self.imageH}",
                                 parent="main_window", id="text", before="main_image")
                    w = dpg.get_item_width("text")
                    h = dpg.get_item_height("text")
                    window_w = dpg.get_item_width("main_window")

                logging.debug(self.img_id)

                # load the image
                dpg.show_item("main_window")
                # dpg.show_viewport(self.viewport)
                if image_path not in self.img_paths:
                    self.img_paths.append(image_path)
                    logging.info(self.img_paths)

    def handle_keys(self, sender, key, user_data):
        self.print_cb_data(sender, key, user_data)
        print(key)
        if (key == 265):
            logging.info(f"jumping to start of images {self.img_paths[0]}")
            self.set_image(self.img_paths[0])
        if (key == 264):
            logging.info(f"jumping to end of images:  {self.img_paths[-1]}")
            self.set_image(self.img_paths[-1])
        if(key == 263):
            logging.debug("pressed right")
            if len(self.img_paths) > 1 and self.img_path != '':
                self.current_img = self.img_paths.index(self.img_path) - 1
                self.current_img = max(
                    self.current_img, 0)
                logging.info(f" K_LEFT setting to image:  {self.current_img}")
                self.set_image(self.img_paths[self.current_img])
        if(key == 262):
            if len(self.img_paths) > 1 & self.current_img < len(self.img_paths) and self.img_path != '':
                self.current_img = self.img_paths.index(self.img_path) + 1
                self.set_image(
                    self.img_paths[self.current_img % len(self.img_paths)])
                logging.info(f" K_RIGHT setting to image:  {self.current_img}")
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
    viewer = ImageViewerPDG()
    viewer.set_image('dowKP.jpeg')

    viewer.run()
    viewer.quit()
