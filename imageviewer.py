#!/usr/bin/python3

from utils import get_resolution_linux
import os
import time
import logging
import dearpygui.dearpygui as dpg
from imageviewerkeyhandler import ImageViewerKeyHandler
logging.basicConfig(level=logging.INFO)

# TODO: Split into key handling, image updating and viewport setup classes


class ImageViewer:
    def __init__(self):
        self.img_id = 0
        self.clientW, self.clientH = get_resolution_linux()
        self.directory = ''
        self.img_path = ''
        self.img_paths = []
        self.fullscreen = False

        self.dragTimer = 0.0
        self.show_info = True
        self.shouldquit = False
        self.text_added = False
        self.intro_text = 0
        self.w, self.h = (1024, 768)
        self.vp_min_width, self.vp_min_height = (300, 300)

        self.image_w, self.image_h = (self.w//2, self.h//2)
        # create viewport takes in config options too!
        self.init_viewport()
        self.init_window()
        self.key_handler = ImageViewerKeyHandler(
            self.img_paths, self.quit, self.toggle_fullscreen, self.set_image)
        self.init_dpg()
        self.icon_path = os.path.expanduser(
            "~/.config/imagewatcher/imagewatcher.png")
        print(self.icon_path)
        self.set_image(self.icon_path)
        # get icon pos

    def init_icon_img(self):
        dpg.set_viewport_width(self.image_w + 80)

        if dpg.get_item_pos("main_image")[0] == 0:
            dpg.set_item_pos("main_image", [40, 100])
        else:
            dpg.set_item_pos("main_image", [0, 100])
        self.position_intro_text()

    def position_intro_text(self):
        x, y = dpg.get_item_pos("main_image")
        w = dpg.get_item_width("main_image")
        h = dpg.get_item_height("main_image")
        print(w, h)
        dpg.set_global_font_scale(1.5)
        if self.intro_text == 0:
            self.intro_text = dpg.add_text(f"watching directory: {os.path.join(os.getcwd(), self.directory)} for changes...",
                                           parent="main_window", id="intro_text", pos=[x, y+h], tracked=True, track_offset=0, wrap=w+20)

    def init_dpg(self):
        dpg.setup_registries()
        dpg.set_viewport_always_top(True)
        dpg.add_key_press_handler(callback=self.key_handler.handle_keys)
        dpg.add_mouse_drag_handler(callback=self.handle_windowdrag)

    def init_viewport(self):
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=True, clear_color=[0, 0, 0, 0], min_width=self.vp_min_width, min_height=self.vp_min_height)
        dpg.set_viewport_clear_color([0.0, 0.0, 0.0, 0.0])
        # MOUSE SETUP
        dpg.setup_dearpygui(viewport=self.viewport)
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
                                (15, 15, 15, 0))
            dpg.add_theme_color(dpg.mvThemeCol_Border,
                                (0, 0, 0, 0))

        dpg.set_item_theme("main_window", "theme_id")
        dpg.set_primary_window("main_window", True)

    def center_viewport(self, xoff=0, yoff=0):

        self.currW = dpg.get_viewport_width()
        self.currH = dpg.get_viewport_height()
        logging.debug(f"currH: {self.currW} \n currH: {self.currH}")

        dpg.set_viewport_pos(
            [self.clientW//2 - xoff, self.clientH//2 - yoff])
        dpg.set_viewport_max_width(self.clientW)
        dpg.set_viewport_max_height(self.clientH)

    def resize_viewport(self, width, height):
        if not self.fullscreen:
            dpg.set_viewport_height(height)
            dpg.set_viewport_width(width)
            pos = [0, 0]
        else:
            pos = [self.clientW//2 - width//2,
                   self.clientH//2 - height//2]
        return pos

    def remove_image(self, path):
        if path in self.img_paths:
            self.img_paths.remove(path)

    def set_directory(self, path, files):
        self.directory = path
        self.img_paths = files
        time.sleep(1)
        self.init_icon_img()
        self.key_handler.update_img_paths(self.img_paths, self.img_path)

    def handle_windowdrag(self, sender, dragpos, user_data):
        if self.dragTimer == 0:
            self.dragTimer = time.time()
        if(time.time() - self.dragTimer > 0.01):
            currX, currY = dpg.get_viewport_pos()
            posX = dragpos[1] + currX
            posY = dragpos[2] + currY
            if all([posX, posY, currX, currY]) > 0.0:
                dpg.set_viewport_pos(
                    [posX,   posY])
                self.dragTimer = 0.0

    def check_img_size(self, width, height):
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
        if self.image_w < self.vp_min_width or self.image_h < self.vp_min_height:
            logging.info("image is less than min size... resizing")
            width = width * 2
            height = height * 2
        return width, height

    def delete_img_if_changed(self):
        # if we already have an image, delete it and it's associated text
        if self.img_id > 0:
            dpg.delete_item("main_image")
            if self.intro_text > 0:
                dpg.hide_item(self.intro_text)
            if self.text_added:
                dpg.delete_item("text")

    def show_image_text(self, image_path, width, height):
        if self.show_info and image_path is not self.icon_path:
            dpg.add_text(f"File: {image_path} Size: {width}x{height}",
                         parent="main_window", id="text", before="main_image")
            self.text_added = True

    def print_cb_data(self, sender, app_data, user_data):

        logging.debug(f"sender is: {sender}")
        logging.debug(f"app_data is: {app_data}")
        logging.debug(f"user_data is: {user_data}")
# NEEDS REFACTOR -- IS GIANT!

    def set_image(self, image_path):
        print(f"img_id:  {self.img_id}")
        # if the image hasn't changed, return
        if image_path == self.img_path:
            return
        self.delete_img_if_changed()
        # hide the window

        logging.debug("setting image")
        self.img_path = image_path
        #  clear the screen

        width, height, _, data = dpg.load_image(image_path)
        self.image_w = width
        self.image_h = height
        initial_w = width
        initial_h = height

        self.show_image_text(image_path, initial_w, initial_h)

        with dpg.texture_registry() as reg_id:
            self.reg_id = reg_id
            width, height = self.check_img_size(width, height)
            self.texture_id = dpg.add_static_texture(
                self.image_w, self.image_h, data, parent=reg_id)

        pos = self.resize_viewport(width, height)
        self.img_id = dpg.add_image(
            self.texture_id, parent="main_window", id='main_image', width=width, height=height, label=self.img_path, pos=pos)
        self.image_w = width
        self.image_h = height
        self.update_image_paths(image_path)

    def update_image_paths(self, image_path):
        if image_path in self.img_paths or image_path == self.icon_path:
            return
        self.img_paths.append(image_path)
        logging.info(self.img_paths)
        self.key_handler.update_img_paths(
            self.img_paths, self.img_path)

    def toggle_fullscreen(self):
        """ Toggles fullscreen off and on for the current viewport"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.stored_w = dpg.get_viewport_width()
            self.stored_h = dpg.get_viewport_height()
            dpg.set_viewport_resizable(True)
            # sleep a little to let the viewport catchup
            time.sleep(0.05)
            dpg.configure_viewport(dpg.get_viewport_title(
            ), width=self.clientW, height=self.clientH, position=[0, 0])
            if self.img_id:
                dpg.set_item_width("main_image", self.image_w)
                dpg.set_item_height("main_image", self.image_h)
                dpg.set_item_pos(
                    "main_image", [self.clientW//2 - self.image_w//2, self.clientH//2 - self.image_h//2])

                self.position_intro_text()
        else:
            dpg.configure_viewport(dpg.get_viewport_title(
            ),  width=self.image_w if self.image_w else self.stored_w, height=self.image_h if self.image_h else self.stored_h, position=[self.stored_w, self.stored_h])
            time.sleep(0.1)
            dpg.set_viewport_resizable(False)
            self.center_viewport(xoff=self.w//2, yoff=self.h//2)
            if self.img_id:
                dpg.set_item_width("main_image", self.image_w)
                dpg.set_item_height("main_image", self.image_h)
                if self.img_path != self.icon_path:
                    dpg.set_item_pos(
                        "main_image", [0, 0])
                else:
                    self.init_icon_img()

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
    viewer = ImageViewer()
    viewer.set_image('dowKP.jpeg')

    viewer.run()
