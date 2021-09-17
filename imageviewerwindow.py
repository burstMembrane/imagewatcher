
from imageviewerkeyhandler import ImageViewerKeyHandler
from utils import get_resolution_linux
import dearpygui.dearpygui as dpg
import logging
import time
logger = logging.getLogger(__name__)


class ImageViewerWindow:
    def __init__(self):
        self.clientW, self.clientH = get_resolution_linux()
        self.w, self.h = (1024, 768)
        self.vp_min_width, self.vp_min_height = (640, 480)
     # create viewport takes in config options too!
        self.img_paths = []
        self.init_viewport()
        self.init_window()
        self.key_handler = ImageViewerKeyHandler(
            self.img_paths, self.quit, self.toggle_fullscreen, self.set_image)
        self.init_dpg()

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

    def init_dpg(self):
        dpg.setup_registries()
        dpg.set_viewport_always_top(True)
        dpg.add_key_press_handler(callback=self.key_handler.handle_keys)
        dpg.add_mouse_drag_handler(callback=self.handle_windowdrag)

    def init_viewport(self):
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=True, clear_color=[0, 0, 0, 0], min_width=self.vp_min_width, min_height=self.vp_min_height)
        dpg.set_viewport_clear_color([0.0, 0.0, 0.0, 0.0])
        dpg.setup_dearpygui(viewport=self.viewport)
        self.center_viewport(xoff=self.w//2, yoff=self.h//2)
        logging.debug(f"clientW:  {self.clientW} \n clientH: {self.clientH}")
        dpg.set_viewport_clear_color([0, 0.0, 0.0, 0.0])
        dpg.show_viewport(self.viewport)

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

    def toggle_fullscreen(self):
        """ Toggles fullscreen off and on for the current viewport"""

        # TODO: simplify logic
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.stored_pos = dpg.get_viewport_pos()
            self.stored_w = dpg.get_viewport_width()
            self.stored_h = dpg.get_viewport_height()
            dpg.set_viewport_resizable(True)
            # sleep a little to let the viewport catchup
            time.sleep(0.05)
            dpg.configure_viewport(dpg.get_viewport_title(
            ), width=self.clientW, height=self.clientH, position=[0, 0])
            if self.img_id:
                img_id = self.img_id
            else:
                img_id = self.logo_id
            dpg.set_item_width(img_id, self.image_w)
            dpg.set_item_height(img_id, self.image_h)
            dpg.set_item_pos(
                img_id, [self.clientW//2 - self.image_w//2, self.clientH//2 - self.image_h//2])
            self.position_intro_text()
        else:
            dpg.configure_viewport(dpg.get_viewport_title(
            ),  width=self.stored_w, height=self.stored_h, position=[self.stored_pos])
            time.sleep(0.1)
            self.set_image(self.img_path)
            dpg.set_viewport_resizable(False)
            # self.center_viewport(xoff=self.w//2, yoff=self.h//2)
            self.init_icon_img()
            if self.img_id == 0:
                self.position_intro_text()
                return

            dpg.set_item_pos(
                self.img_id, [0, 0])
            dpg.set_item_width(self.img_id, dpg.get_viewport_width())
            dpg.set_item_height(self.img_id, dpg.get_viewport_height())

    def set_image(self, image_path, image_id="main_image"):
        logging.debug(f"img_id:  {self.img_id}")

        # if the image hasn't changed, return
        if image_path == self.img_path:
            return
        if image_path is not self.icon_path:
            dpg.hide_item(self.logo_id)
            # dpg.hide_item(self.intro_text)
            # dpg.hide_item("intro_text")
        self.delete_img_if_changed()
        # hide the window

        logging.debug("setting image")
        self.img_path = image_path
        #  clear the screen

        width, height, _, data = dpg.load_image(image_path)
        initial_w = width
        initial_h = height
        self.show_image_text(image_path, initial_w, initial_h)
        self.img_id = self.add_image(width, height, data, image_id=image_id)
        self.update_image_paths(image_path)

    def quit(self):
        try:
            logging.debug("quitting...")
            dpg.minimize_viewport()
            dpg.stop_dearpygui()
            dpg.cleanup_dearpygui()
            dpg.destroy_context()

        except:
            pass
