"""" Tgus module handles the windowing fucntions for ImageWatcher"""
from src.ui.imageviewerkeyhandler import ImageViewerKeyHandler


from src.ui.utils import get_resolution_linux, print_cb_data
import dearpygui.dearpygui as dpg
import logging
import time
from PIL import Image


class ImageViewerWindow:
    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.clientW, self.clientH = get_resolution_linux()
        self.w, self.h = (1024, 768)
        self.vp_min_width, self.vp_min_height = (640, 480)
        self.image_w, self.image_h = (0, 0)
        self.dragTimer = 0.0
     # create viewport takes in config options too!
        self.img_paths = []
        self.init_viewport()
        self.init_window()
        self.key_handler = ImageViewerKeyHandler(
            self.img_paths, self.quit, self.toggle_fullscreen, self.set_image)
        self.init_dpg()

        self.currW = dpg.get_viewport_width()
        self.currH = dpg.get_viewport_height()

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
                self.stored_pos = dpg.get_viewport_pos()
                self.dragTimer = 0.0

    def init_dpg(self):
        dpg.setup_registries()
        dpg.set_viewport_always_top(True)
        dpg.add_key_press_handler(callback=self.key_handler.handle_keys)
        dpg.add_mouse_drag_handler(callback=self.handle_windowdrag)

    def init_viewport(self):
        dpg.create_viewport(
            title='ImageWatcher',
            width=self.w,
            height=self.h,
            decorated=False, resizable=True,
            clear_color=[0, 0, 0, 0],
            min_width=self.vp_min_width,
            min_height=self.vp_min_height,
            x_pos=self.clientW//2,
            y_pos=self.clientH//2)
        self.viewport = dpg.get_viewport_title()
        dpg.set_viewport_clear_color([0.0, 0.0, 0.0, 0.0])

        dpg.setup_dearpygui(viewport=self.viewport)
        logging.debug(f"setup viewport with id: {self.viewport}")
        # self.center_viewport()
        self.logger.debug(
            "clientW:  {} \n clientH: {}".format(self.clientW, self.clientH))
        dpg.set_viewport_clear_color([0, 0.0, 0.0, 0.0])
        dpg.show_viewport(self.viewport)

        self.stored_pos = dpg.get_viewport_pos()
        self.logger.debug(f"init viewport pos: {self.stored_pos}")

        self.stored_w = dpg.get_viewport_width()
        self.stored_h = dpg.get_viewport_height()

    def init_window(self):
        with dpg.window(label="Imagewatcher",
                        collapsed=True,
                        modal=False,
                        width=self.w,
                        height=self.h,
                        id="main_window",
                        no_scrollbar=True,
                        no_background=True) as w:
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
        dpg.add_resize_handler(
            self.window, callback=self.resize_image_to_viewport)

    def center_viewport(self, xoff=0, yoff=0):

        self.currW = dpg.get_viewport_width()
        self.currH = dpg.get_viewport_height()
        self.logger.debug(f"currH: {self.currW} \n currH: {self.currH}")

        dpg.set_viewport_pos(
            [self.clientW//2-xoff, self.clientH//2 - yoff])

    def resize_viewport(self, width, height):
        if not self.fullscreen:
            dpg.set_viewport_height(height)
            dpg.set_viewport_width(width)
            pos = [0, 0]
        elif self.fullscreen or dpg.is_viewport_decorated():
            pos = [self.clientW//2 - width//2,
                   self.clientH//2 - height//2]
            logging.info(f"setting pos: {pos}")

        return pos

    def store_vp_dims(self):

        x, y = dpg.get_viewport_pos()
        w, h = (dpg.get_viewport_width(), dpg.get_viewport_height())
        if x or y == 0:
            return
        if w > self.clientW or h >= self.clientH:
            return
        if x > 0 or y > 0:
            self.stored_pos = [x, y]
        self.logger.debug(f"storing pos {x,y}")

        self.stored_w = dpg.get_viewport_width()
        self.stored_h = dpg.get_viewport_height()

    def toggle_fullscreen(self):
        """ Toggles fullscreen off and on for the current viewport"""
        #  TODO: modify to send a fullscreen event to the inherited class
        # TODO: simplify logic
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.store_vp_dims()
            time.sleep(0.1)
            self.logger.debug(
                f"stored pos: {self.stored_pos}  stored_dim:  {'x'.join((str(self.stored_w), str(self.stored_h)))}")
            dpg.set_viewport_resizable(True)

            dpg.configure_viewport(dpg.get_viewport_title(
            ), width=self.clientW, height=self.clientH, x_pos=0, y_pos=0)

            dpg.set_item_pos(
                self.window, [-self.stored_pos[0], -self.stored_pos[1]])

            self.logger.debug(
                f"vp pos: {dpg.get_viewport_pos()}")

        else:
            self.logger.debug(
                f"window mode, setting to stored pos: {self.stored_pos}  stored_dim:  {'x'.join((str(self.stored_w), str(self.stored_h)))}")

            time.sleep(0.2)
            dpg.set_viewport_resizable(True)
            dpg.configure_viewport(dpg.get_viewport_title(
            ),  width=self.stored_w, height=self.stored_h, x_pos=self.stored_pos[0], y_pos=self.stored_pos[1])
            time.sleep(0.2)
            dpg.set_viewport_pos(self.stored_pos)

    def resize_image_to_viewport(self, sender, size, user_data):
        w, h = size
        if not self.img_id:
            dpg.set_item_pos(
                self.logo_id, [w//2 - self.image_w//2, h//2 - self.image_h//2])
            self.position_intro_text()
            return

        dpg.set_item_width(self.img_id, self.image_w)
        dpg.set_item_height(self.img_id, self.image_h)
        if self.fullscreen:
            dpg.set_item_pos(
                self.img_id, [w//2 - self.image_w//2, h//2 - self.image_h//2])
        else:
            if dpg.is_viewport_resizable():
                dpg.set_item_pos(
                    self.img_id, [w//2 - self.image_w//2, h//2 - self.image_h//2])
            else:
                dpg.set_item_pos(
                    self.img_id, [0, 0])
            image_w = dpg.get_item_width(self.img_id)
            image_h = dpg.get_item_height(self.img_id)
            image_ratio = image_w / image_h
            window_ratio = w/h
            tex_data = dpg.get_value(self.texture_id)

            self.logger.info(f"image_ratio: {image_ratio}")
            self.logger.info(f"image wxh: {image_w}x{image_h}")
            self.logger.info(f"window wxh: {w}x{h}")
            self.logger.info(f"window_ratio: {window_ratio}")

    def quit(self):

        self.logger.info("ImageWatcher quitting...")
        dpg.stop_dearpygui()
