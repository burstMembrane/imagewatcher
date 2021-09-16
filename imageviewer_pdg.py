#!/usr/bin/python3

import logging
from os import path
import dearpygui.dearpygui as dpg
import dearpygui._dearpygui as internal_dpg
import time
import logging

from utils import get_resolution

logging.basicConfig(level=logging.INFO)


class ImageViewerPDG:
    def __init__(self):
        self.img_id = 0
        self.clientW, self.clientH = get_resolution()

        self.directory = ""
        self.current_img = 0
        self.img_paths = []
        self.fullscreen = False
        self.img_path = ''
        self.paddingH = 70
        self.dragTimer = 0.0
        self.lastPosX = 0
        self.lastPosY = 0
        self.show_info = True
        self.shouldquit = False
        self.text_added = False

        self.w, self.h = (1024, 768)
        self.storedW, self.storedH = (1024, 768)
        self.vMinW, self.vMinH = (300, 300)
        self.vPos = (self.w//2, self.h//2)
        self.imageW, self.imageH = self.vPos
        # create viewport takes in config options too!
        self.init_viewport()
        self.init_window()
        self.init_dpg()
        self.icon_path = "assets/imagewatcher.png"
        self.set_image(self.icon_path)
        self.init_icon_img()

    def init_icon_img(self):
        dpg.set_viewport_width(self.imageW + 80)
        width, height, channels, data = dpg.load_image(self.icon_path)
        if dpg.get_item_pos("main_image")[0] == 0:
            dpg.set_item_pos("main_image", [40, 120])
        else:
            dpg.set_item_pos("main_image", [0, 120])

    def init_dpg(self):
        dpg.setup_registries()
        dpg.set_viewport_always_top(True)
        dpg.add_key_press_handler(callback=self.handle_keys)
        dpg.add_mouse_drag_handler(callback=self.handle_windowdrag)

    def init_viewport(self):
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=True, clear_color=[0, 0, 0, 0], min_width=self.vMinW, min_height=self.vMinH)
        dpg.set_viewport_clear_color([0.0, 0.0, 0.0, 0.0])
        # MOUSE SETUP
        dpg.setup_dearpygui(viewport=self.viewport)

        config = dpg.get_viewport_configuration(dpg.mvThemeCol_WindowBg)

        self.center_viewport(xoff=self.w//2, yoff=self.h//2)
        logging.debug(f"clientW:  {self.clientW} \n clientH: {self.clientH}")
        dpg.set_viewport_clear_color([0, 0.0, 0.0, 0.0])

        dpg.show_viewport(self.viewport)
        # self.center_viewport()

    def init_window(self):
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

        dpg.set_item_theme("main_window", "theme_id")
        dpg.set_primary_window("main_window", True)
        # dpg.set_item_theme(self.viewport, "theme_id")

    def remove_image(self, path):
        if path in self.img_paths:
            self.img_paths.remove(path)

    def set_directory(self, path, files):
        self.directory = path
        self.img_paths = files
        # if (len(files) > 0):
        #     self.set_image(self.img_paths[-1])

    def center_viewport(self, xoff=0, yoff=0):

        self.currW = dpg.get_viewport_width()
        self.currH = dpg.get_viewport_height()
        logging.debug(f"currH: {self.currW} \n currH: {self.currH}")

        dpg.set_viewport_pos(
            [self.clientW//2 - xoff, self.clientH//2 - yoff])
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

    def handle_windowdrag(self, sender, dragpos, user_data):
        thresh = 0.5
        if self.dragTimer == 0:
            self.dragTimer = time.time()
            self.lastPosX = dragpos[1]
            self.lastPosY = dragpos[2]

        if(time.time() - self.dragTimer > 0.01):
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

    def set_image(self, image_path):
        if image_path != self.img_path:
            if self.img_id > 0 and image_path != self.icon_path:
                dpg.delete_item("main_image")
                if self.text_added:
                    dpg.delete_item("text")
            dpg.hide_item("main_window")

            logging.debug("setting image")
            self.img_path = image_path
            #  clear the screen

            width, height, channels, data = dpg.load_image(image_path)
            self.imageW = width
            self.imageH = height

            with dpg.texture_registry() as reg_id:

                if height >= self.clientH or width >= self.clientW:
                    diff = abs((self.clientW/self.clientH) / (width/height))
                    if not self.fullscreen:
                        diff = diff
                    else:
                        diff = diff * 1.1

                    logging.debug(f"difference:  {diff}")
                    height = height / diff
                    width = width / diff
                    logging.info(
                        f"image is larger than window... resizing to {width}x{height}")
                if self.imageW < self.vMinW or self.imageH < self.vMinH:
                    logging.info("image is less thhan min size... resizing")
                    width = width * 2
                    height = height * 2
                self.texture_id = dpg.add_static_texture(
                    self.imageW, self.imageH, data, parent=reg_id)

                if not self.fullscreen:
                    dpg.set_viewport_height(height)
                    dpg.set_viewport_width(width)
                    pos = [0, 0]
                else:
                    pos = [self.clientW//2 - width//2,
                           self.clientH//2 - height//2]

                self.img_id = dpg.add_image(
                    self.texture_id, parent="main_window", id='main_image', width=width, height=height, label=self.img_path, pos=pos)
                self.imageW = width
                self.imageH = height
                if self.show_info and image_path is not self.icon_path:
                    dpg.add_text(f"File: {self.img_path} Size: {self.imageW}x{self.imageH}",
                                 parent="main_window", id="text", before="main_image")
                    self.text_added = True
                logging.debug(self.img_id)
                # load the image
                dpg.show_item("main_window")
                if image_path not in self.img_paths and image_path != self.icon_path:
                    self.img_paths.append(image_path)
                    logging.info(self.img_paths)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.storedW = dpg.get_viewport_width()
            self.storedH = dpg.get_viewport_height()
            dpg.set_viewport_resizable(True)
            time.sleep(0.05)
            dpg.configure_viewport(dpg.get_viewport_title(
            ), width=self.clientW, height=self.clientH, position=[0, 0])
            if self.img_id:

                dpg.set_item_width("main_image", self.imageW)
                dpg.set_item_height("main_image", self.imageH)
                dpg.set_item_pos(
                    "main_image", [self.clientW//2 - self.imageW//2, self.clientH//2 - self.imageH//2])
        else:
            dpg.configure_viewport(dpg.get_viewport_title(
            ),  width=self.imageW if self.imageW else self.storedW, height=self.imageH if self.imageH else self.storedH, position=[self.storedW, self.storedH])
            time.sleep(0.1)
            dpg.set_viewport_resizable(False)
            self.center_viewport(xoff=self.w//2, yoff=self.h//2)
            if self.img_id:
                dpg.set_item_width("main_image", self.imageW)
                dpg.set_item_height("main_image", self.imageH)
                if self.img_path != self.icon_path:
                    dpg.set_item_pos(
                        "main_image", [0, 0])
                else:
                    self.init_icon_img()

    def handle_keys(self, sender, key, user_data):
        self.print_cb_data(sender, key, user_data)
        if key == dpg.mvKey_F:
            self.toggle_fullscreen()

        if self.img_path != self.icon_path:
            if (key == dpg.mvKey_Up):
                logging.info(f"jumping to start of images {self.img_paths[0]}")

                self.set_image(self.img_paths[0])

            if (key == dpg.mvKey_Down):
                logging.info(
                    f"jumping to end of images:  {self.img_paths[-1]}")
                try:
                    self.set_image(self.img_paths[-1])
                except:
                    pass
            if(key == dpg.mvKey_Right):
                logging.debug("pressed right")
                if len(self.img_paths) > 1 and self.img_path != '':
                    self.current_img = self.img_paths.index(self.img_path) - 1
                    self.current_img = max(
                        self.current_img, 0)
                    logging.info(
                        f" K_LEFT setting to image:  {self.current_img}")
                    self.set_image(self.img_paths[self.current_img])
            if(key == dpg.mvKey_Left):
                if len(self.img_paths) > 1 & self.current_img < len(self.img_paths) and self.img_path != '':
                    self.current_img = self.img_paths.index(self.img_path) + 1
                    self.set_image(
                        self.img_paths[self.current_img % len(self.img_paths)])
                    logging.info(
                        f" K_RIGHT setting to image:  {self.current_img}")
        if(key == dpg.mvKey_Escape):
            self.quit()

    def run(self):
        while dpg.is_dearpygui_running():
            try:

                dpg.render_dearpygui_frame()

            except KeyboardInterrupt or SystemExit:
                logging.info("quitting...")
                self.quit()

    def quit(self):
        try:
            logging.debug("quitting...")
            dpg.minimize_viewport()
            dpg.stop_dearpygui()
            dpg.cleanup_dearpygui()
            dpg.destroy_context()
            self.shouldquit = True
        except:
            pass


if __name__ == '__main__':
    # test
    viewer = ImageViewerPDG()
    viewer.set_image('dowKP.jpeg')

    viewer.run()
