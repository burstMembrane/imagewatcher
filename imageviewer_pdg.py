#!/usr/bin/python3

import logging
from os import environ, path
import dearpygui.dearpygui as dpg
from sys import exit


class ImageViewer:
    def __init__(self):
        self.img_id = 0
        # IMAGE SETUP
        self.directory = ""
        self.current_img = 0
        self.img_paths = []
        self.img_path = ''
        self.paddingW = 0
        self.paddingH = 50
        self.window_size = (1280,
                            720)
        self.w, self.h = self.window_size
        # create viewport takes in config options too!
        self.viewport = dpg.create_viewport(
            title='Image Viewer', width=self.w, height=self.h, decorated=False, resizable=False)

        dpg.set_viewport_max_height(1080)

        # MOUSE SETUP
        dpg.setup_dearpygui(viewport=self.viewport)
        dpg.show_viewport(self.viewport)

        dpg.setup_registries()

        print(
            f"vp_client_w: {self.w} vp_client_h:  {self.h}")
        dpg.set_viewport_pos([100, 300])
        # WINDOW SETUP

        with dpg.window(label="Imagewatcher", collapsed=True, modal=False, width=self.window_size[0], height=self.window_size[1], id="main_window", no_scrollbar=True) as w:
            self.window = w

        dpg.set_primary_window("main_window", True)
        self.show_info = False
        self.shouldquit = False
        self.init_dialog_selector()
        self.init_menu_bar()

    def init_menu_bar(self):
        with dpg.menu_bar(parent="main_window", id="menu_bar"):
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="Open Directory", callback=lambda: dpg.show_item("directory_dialog"))
                dpg.add_menu_item(label="Quit", callback=self.quit)
            with dpg.menu(label="IMAGEWATCHER v0.1", parent="menu_bar", indent=self.w-150):
                dpg.add_menu_item(
                    label="About", callback=lambda: print("hello"))

    def handle_windowdrag(self, sender, app_data, user_data):
        self.print_cb_data(sender, app_data, user_data)

    def print_cb_data(self, sender, app_data, user_data):
        print(f"sender is: {sender}")
        print(f"app_data is: {app_data}")
        print(f"user_data is: {user_data}")

    def handle_dialog(self, sender, app_data, user_data):
        self.directory = path.join(
            app_data["file_path_name"], app_data["file_name"])
        print(f"setting dir to {self.directory}")
        dpg.add_text(f"watching.. {self.directory}", parent="main_window")

    def init_dialog_selector(self):
        with dpg.file_dialog(directory_selector=True, modal=True, show=False, callback=self.handle_dialog, id="directory_dialog"):
            dpg.add_file_extension(".*", color=(255, 255, 255, 255))
            dpg.add_file_extension(
                "Source files (*.cpp *.h *.hpp){.cpp,.h,.hpp}", color=(0, 255, 255, 255))
            dpg.add_file_extension(".cpp", color=(255, 255, 0, 255))
            dpg.add_file_extension(".h", color=(
                255, 0, 255, 255), custom_text="header")
            dpg.add_file_extension("Python(.py){.py}", color=(0, 255, 0, 255))

    def show_image(self):
        """ Loads the image and adds it to the window"""

    def clear(self):
        """ Clears the window  """

    def set_image(self, image_path):
        if self.img_id > 0:
            dpg.delete_item("main_image")
        print("setting image")
        self.img_path = image_path
        #  clear the screen
        if len(image_path) > 0:
            width, height, channels, data = dpg.load_image(image_path)
            with dpg.texture_registry() as reg_id:
                texture_id = dpg.add_static_texture(
                    width, height, data, parent=reg_id)
                vp_width = dpg.get_viewport_height()
                vp_height = dpg.get_viewport_height()
                if height > vp_height or width > vp_width:
                    diffW = abs(width-vp_width)
                    diffH = abs(height-vp_height)
                    print(f"difference_w:  {diffW}  difference_h: {diffH}")
                    height = height // 2.5
                    width = width // 2.5
                    print(
                        f"image is larger than window... resizing to {width}x{height}")
                dpg.set_viewport_height(height)
                dpg.set_viewport_width(width)

                self.img_id = dpg.add_image(
                    texture_id, parent="main_window", id='main_image', width=width, height=height, tracked=True)

                print(self.img_id)

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
        exit(0)


if __name__ == '__main__':
    # test
    viewer = ImageViewer()
    viewer.set_image('test.jpeg')
    # worker = Thread(target=viewer.run)
    # worker.setDaemon(True)
    # worker.start()
    viewer.run()
    viewer.quit()
