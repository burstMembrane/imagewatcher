#!/usr/bin/python3


import os
import logging
import dearpygui.dearpygui as dpg

from src.ui.imageviewerwindow import ImageViewerWindow
from PIL import Image
import numpy
import funcy


class ImageViewer(ImageViewerWindow):
    def __init__(self):
        # initialize the base class
        ImageViewerWindow.__init__(self)
        self.handlers = dpg.handler_registry()
        print(self.handlers)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.img_id = 0
        self.directory = ''
        self.img_path = ''
        self.fullscreen = False
        self.icon_path = os.path.expanduser(
            "~/.config/imagewatcher/imagewatcher.png")
        self.logger.debug(self.icon_path)
        self.logo_id = "logo"
        width, height, _, data = dpg.load_image(self.icon_path)
        self.add_image(width, height, data, image_id=self.logo_id)

        # get icon pos

    def init_icon_img(self):
        self.logger.debug("setting icon image")
        dpg.set_item_pos(
            self.logo_id, [self.vp_min_width//2-self.image_w//2, self.vp_min_height//2-self.image_h//2])
        self.position_intro_text()

    def position_intro_text(self):

        self.logger.debug("positioning intro text")
        x, y = dpg.get_item_pos(self.logo_id)
        w = dpg.get_item_width(self.logo_id)
        self.logger.debug("logo width {}".format(w))
        h = dpg.get_item_height(self.logo_id)

        dpg.set_global_font_scale(1)
        pos = [x-w//2, y+h]
        wrap = x+self.image_w+w
        if not "intro_text" in self.__dict__:
            self.intro_text = dpg.add_text(f"watching directory: {os.path.join(os.getcwd(), self.directory)}",
                                           parent="main_window", id="intro_text", pos=pos,  wrap=wrap)
        else:
            dpg.set_item_pos(self.intro_text, pos=pos)
            dpg.configure_item(self.intro_text, wrap=wrap)

    def remove_image(self, path):
        if path in self.img_paths:
            self.img_paths.remove(path)

    def set_directory(self, path, files):
        self.directory = path
        self.img_paths = files

        self.init_icon_img()
        self.key_handler.update_img_paths(self.img_paths, self.img_path)

    def check_img_size(self, width, height):
        if width < self.vp_min_width or height < self.vp_min_height:
            self.logger.info("image is less than min size... resizing")
            width = width * 1.5
            height = height * 1.5
        elif height >= self.clientH or width >= self.clientW:
            diff = abs((self.clientW/self.clientH) / (width/height))
            if self.fullscreen:
                diff = diff * 1.1
            else:
                diff = diff * 1.5
            self.logger.debug(f"difference:  {diff}")
            height = height // diff
            width = width // diff
            self.logger.info(
                f"image is larger than window... resizing to {width}x{height}")

        return int(width), int(height)

    def delete_img_if_changed(self):
        # if we already have an image, delete it and it's associated text
        if self.img_id > 0:
            dpg.delete_item("main_image")
            if self.intro_text > 0:
                dpg.hide_item(self.intro_text)
            if "text_id" in self.__dict__:
                dpg.delete_item(self.text_id)

    def show_image_text(self, image_path, width, height):
        if image_path is not self.icon_path:
            self.text_id = dpg.add_text(f"File: {image_path} Size: {width}x{height}",
                                        parent="main_window", id="text", before="main_image")

    def print_cb_data(self, sender, app_data, user_data):

        self.logger.debug(f"sender is: {sender}")
        self.logger.debug(f"app_data is: {app_data}")
        self.logger.debug(f"user_data is: {user_data}")

    def add_image(self, width, height, data, image_id="main_image", pil_image=False):
        logging.info(f"adding image of {width, height}")
        self.data = data
        with dpg.texture_registry() as reg_id:
            self.reg_id = reg_id

        self.texture_id = dpg.add_static_texture(
            width, height, data, parent=reg_id)

        self.image_w = width
        self.image_h = height
        pos = self.resize_viewport(width, height)
        return dpg.add_image(
            self.texture_id, parent="main_window", id=image_id, width=width, height=height,  pos=pos)

    @ funcy.print_durations(unit='ms')
    def set_image(self, image_path, image_id="main_image"):
        self.logger.debug(f"img_id:  {self.img_id}")

        # if the image hasn't changed, return
        if image_path == self.img_path:
            return
        if image_path is not self.icon_path:
            dpg.hide_item(self.logo_id)
            dpg.hide_item(self.intro_text)
            dpg.hide_item("intro_text")

        # hide the window

        self.logger.debug("setting image")
        self.img_path = image_path
        #  clear the screen

        pil_img = Image.open(image_path)

        pil_img.putalpha(255)

        width, height = pil_img.size
        initial_w = width
        initial_h = height
        self.delete_img_if_changed()
        width, height = self.check_img_size(width, height)

        pil_img = pil_img.resize((width, height))

        pil_image_data = numpy.frombuffer(
            pil_img.tobytes(), dtype=numpy.uint8) / 255.0

        self.img_id = self.add_image(
            width, height, pil_image_data, image_id=image_id, pil_image=True)
        if not self.fullscreen:
            dpg.set_viewport_width(width)
            dpg.set_viewport_height(height)
        self.show_image_text(image_path, initial_w, initial_h)
        self.update_image_paths(image_path)

    def update_image_paths(self, image_path):
        if image_path in self.img_paths or image_path == self.icon_path:
            return
        self.img_paths.append(image_path)
        self.logger.info(self.img_paths)
        self.key_handler.update_img_paths(
            self.img_paths, self.img_path)

    def run(self):
        while dpg.is_dearpygui_running():
            try:

                dpg.render_dearpygui_frame()

            except KeyboardInterrupt or SystemExit:
                self.logger.info("quitting...")
                self.quit()


if __name__ == '__main__':
    # test
    viewer = ImageViewer()
    viewer.set_image('dowKP.jpeg')

    viewer.run()
