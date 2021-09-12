#!/usr/bin/python3

import logging
from os import environ
import dearpygui.dearpygui as dpg
from threading import Thread


class ImageViewer:
    def __init__(self):
        self.img_id = 0
        # IMAGE SETUP
        self.directory = ""
        self.current_img = 0
        self.img_paths = []
        self.img_path = ''

        self.window_size = (640, 480)

        self.w, self.h = self.window_size
        # create viewport takes in config options too!
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=True, x_pos=10, y_pos=10)

        # MOUSE SETUP
        dpg.setup_dearpygui(viewport=self.viewport)
        dpg.show_viewport(self.viewport)
        # dpg.start_dearpygui()
        # WINDOW SETUP

        with dpg.window(label="Imagewatcher", width=self.window_size[0], height=self.window_size[1], id="main_window") as w:
            self.window = w

        dpg.set_primary_window("main_window", True)

        self.firstrun = True
        self.show_info = False
        self.shouldquit = False

    def show_image(self):
        """ Loads the image and adds it to the window"""

    def clear(self):
        """ Clears the window  """

    def set_image(self, image_path, parent=None):
        if self.img_id > 0:
            dpg.delete_item("main_image")
        print("setting image")
        self.img_path = image_path
        #  clear the screen
        if len(image_path) > 0:

            width, height, channels, data = dpg.load_image(image_path)
            if(width > self.window_size[0] or height > self.window_size[1]):
                dpg.set_viewport_height(height)

            with dpg.texture_registry() as reg_id:
                texture_id = dpg.add_static_texture(
                    width, height, data, parent=reg_id)
                if height > dpg.get_viewport_height():
                    dpg.set_viewport_height(height)
                    print("image is larger than window... resizing")

                if parent is None:
                    print("IMAGE")
                    self.img_id = dpg.add_image(
                        texture_id, parent=self.window, id='main_image', width=dpg.get_viewport_width(), height=height)
                    print(self.img_id)
                else:
                    self.img_id = dpg.add_image(texture_id, id='main_image')

            # load the image

            if image_path not in self.img_paths:
                self.img_paths.append(image_path)
                logging.debug(self.img_paths)

    def handle_keys(self, key):
        pass
        # if(key == pygame.K_LEFT):
        #     if len(self.img_paths) > 1:

        #         self.current_img = self.img_paths.index(self.img_path) - 1
        #         self.current_img = max(
        #             self.current_img, 0)
        #         logging.info(f" K_LEFT setting to image:  {self.current_img}")
        #         self.set_image(self.img_paths[self.current_img])
        # if(key == pygame.K_RIGHT):
        #     if len(self.img_paths) > 1 & self.current_img < len(self.img_paths):
        #         self.current_img += 1

        #         self.set_image(
        #             self.img_paths[self.current_img % len(self.img_paths)])

    def draw_text_centered(self, text):
        pass
        # self.font_surface = self.font.render(
        #     text, True, (255, 255, 255), self.colours["BLACK"])
        # text_rect = self.font_surface.get_rect(center=(self.w//2, self.h/2))
        # self.gameDisplay.blit(self.font_surface, text_rect)
        # pygame.display.update()

    def display_info(self, text):
        pass
        # if self.show_info:
        #     self.font_surface = self.font.render(
        #         text, True, (255, 255, 255), self.colours["BLACK"])
        #     self.gameDisplay.blit(self.font_surface, (10, 10))
        #     pygame.display.update()
        # else:
        #     self.clear_font_surface()

    def handle_mouse(self, event):
        pass
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     # logging.debug(f"button: {event.button}\npos: {event.pos}")
        #     if event.button == 1:
        #         logging.debug("mouse down!")
        #         self.dragging = True
        #         mouse_x, mouse_y = event.pos

        # elif event.type == pygame.MOUSEBUTTONUP:
        #     if event.button == 1:
        #         logging.debug("mouse up")
        #         self.dragging = False

        # elif event.type == pygame.MOUSEMOTION and self.dragging:

        # mouse_x, mouse_y = event.pos
        # environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(
        #     mouse_x, mouse_y)
        # set window position

    def clear_font_surface(self):
        pass
        # current_surface = pygame.display.get_surface()
        # self.font_surface = pygame.Surface((0, 0))
        # self.gameDisplay.blit(self.font_surface, (10, 10))
        # pygame.display.update()

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
        dpg.cleanup_dearpygui()
        quit()


if __name__ == '__main__':
    # test
    viewer = ImageViewer()
    viewer.set_image('test.jpeg')
    # worker = Thread(target=viewer.run)
    # worker.setDaemon(True)
    # worker.start()
    viewer.run()
    viewer.quit()
