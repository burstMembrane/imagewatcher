import dearpygui.dearpygui as dpg
import logging

logger = logging.getLogger(__name__)


class ImageViewerKeyHandler():
    def __init__(self, img_paths, quit_cb, fullscreen_cb, set_image_cb):
        self.img_paths = img_paths
        self.quit = quit_cb
        self.toggle_fullscreen = fullscreen_cb
        self.set_image = set_image_cb
        self.img_path = ""

    def handle_arrow_keys(self, key):
        # if we don't have enough paths to cycle between images then return
        if len(self.img_paths) < 1 or not self.img_paths[0]:
            return
        # if self.img_path == self.icon_path:
        #     self.img_path = self.img_paths[0]
        if (key == dpg.mvKey_Up):
            logger.info(f"jumping to start of images {self.img_paths[0]}")
            self.set_image(self.img_paths[0])
            self.img_path = self.img_paths[0]
        elif (key == dpg.mvKey_Down):
            self.set_image(self.img_paths[-1])
            logger.info(
                f"jumping to end of images:  {self.img_paths[-1]}")
            self.img_path = self.img_paths[-1]
        elif(key == dpg.mvKey_Left):
            self.current_img = self.img_paths.index(self.img_path) - 1
            self.current_img = max(
                self.current_img, 0)
            self.set_image(self.img_paths[self.current_img])
            self.img_path = self.img_paths[self.current_img]
            logger.info(
                f" K_LEFT setting to image:  {self.current_img}")
        elif(key == dpg.mvKey_Right):
            self.current_img = self.img_paths.index(self.img_path) + 1
            self.set_image(
                self.img_paths[self.current_img % len(self.img_paths)])
            logger.info(
                f" K_RIGHT setting to image:  {self.current_img}")
            self.set_image(
                self.img_paths[self.current_img % len(self.img_paths)])

    def update_img_paths(self, img_paths, img_path):
        self.img_paths = img_paths
        self.img_path = img_paths

    def handle_keys(self, sender, key, user_data):
        if key == dpg.mvKey_F:
            self.toggle_fullscreen()
        if(key == dpg.mvKey_Escape):
            self.quit()
        self.handle_arrow_keys(key)
