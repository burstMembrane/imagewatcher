#!/usr/bin/python3


import os
import time
import logging
import dearpygui.dearpygui as dpg

from imageviewer.ui.imageviewerwindow import ImageViewerWindow
import coloredlogs

logging.basicConfig(format='[ %(asctime)s.%(msecs)03d ] [%(levelname)s] %(message)s',
                    level=logging.INFO,
                    datefmt=f"%d-%m-%y %H:%M:%S")

logger = logging.getLogger(__name__)

coloredlogs.install(level='INFO', logger=logger)


class ImageViewer(ImageViewerWindow):
    def __init__(self):
        # initialize the base class
        ImageViewerWindow.__init__(self)

        self.img_id = 0

        self.directory = ''
        self.img_path = ''

        self.fullscreen = False
        self.dragTimer = 0.0

        # self.image_w, self.image_h = (self.w//2, self.h//2)

        self.icon_path = os.path.expanduser(
            "~/.config/imagewatcher/imagewatcher.png")
        logging.debug(self.icon_path)

        self.logo_id = "logo"
        width, height, _, data = dpg.load_image(self.icon_path)

        self.add_image(width, height, data, image_id=self.logo_id)
        # get icon pos

    def init_icon_img(self):
        logging.debug("setting icon image")
        dpg.set_item_pos(
            self.logo_id, [self.vp_min_width//2-self.image_w//2, self.vp_min_height//2-self.image_h//2])
        self.position_intro_text()

    def position_intro_text(self):

        logging.debug("positioning intro text")
        x, y = dpg.get_item_pos(self.logo_id)
        w = dpg.get_item_width(self.logo_id)
        logging.debug(f"logo width {w}")
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
        time.sleep(1)
        self.init_icon_img()
        self.key_handler.update_img_paths(self.img_paths, self.img_path)

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
            logger.info(
                f"image is larger than window... resizing to {width}x{height}")
        # if self.image_w < self.vp_min_width or self.image_h < self.vp_min_height:
        #     logger.info("image is less than min size... resizing")
        #     width = width * 2
        #     height = height * 2
        return width, height

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

        logging.debug(f"sender is: {sender}")
        logging.debug(f"app_data is: {app_data}")
        logging.debug(f"user_data is: {user_data}")
# NEEDS REFACTOR -- IS GIANT!

    def add_image(self, width, height, data, image_id="main_image"):

        with dpg.texture_registry() as reg_id:
            self.reg_id = reg_id

        self.texture_id = dpg.add_static_texture(
            width, height, data, parent=reg_id)
        width, height = self.check_img_size(width, height)
        self.image_w = width
        self.image_h = height
        pos = self.resize_viewport(width, height)
        return dpg.add_image(
            self.texture_id, parent="main_window", id=image_id, width=width, height=height,  pos=pos)

    def update_image_paths(self, image_path):
        if image_path in self.img_paths or image_path == self.icon_path:
            return
        self.img_paths.append(image_path)
        logger.info(self.img_paths)
        self.key_handler.update_img_paths(
            self.img_paths, self.img_path)

    def run(self):
        while dpg.is_dearpygui_running():
            try:

                dpg.render_dearpygui_frame()

            except KeyboardInterrupt or SystemExit:
                logger.info("quitting...")
                self.quit()


if __name__ == '__main__':
    # test
    viewer = ImageViewer()
    viewer.set_image('dowKP.jpeg')

    viewer.run()
