#!/usr/bin/python3
import pygame
from pygame.locals import NOFRAME, VIDEORESIZE, DOUBLEBUF, HWSURFACE
import logging
from os import environ


class ImageViewer:
    def __init__(self, ObserverThread=""):
        environ['SDL_VIDEO_WINDOW_POS'] = "center"
        pygame.init()
        self.directory = ""
        self.ObserverThread = ObserverThread
        self.current_img = 0
        self.img_paths = []
        self.img_path = ''
        self.lasttxt = ''
        self.mouse_events = [pygame.MOUSEBUTTONDOWN,
                             pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]
        self.dragging = False
        self.window_size = (640, 480)
        self.w, self.h = self.window_size
        wininfo = pygame.display.Info()
        pygame.display._set_autoresize(False)

        logging.debug(f"using driver:  {pygame.display.get_driver()}")
        self.screenW = wininfo.current_w
        self.screenH = wininfo.current_h
        self.gameDisplay = pygame.display.set_mode(
            self.window_size, NOFRAME)

        self.colours = {
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255)
        }
        self.show_info = True

        self.clock = pygame.time.Clock()
        self.shouldquit = False
        self.lastimg = pygame.Surface(self.window_size)
        self.font = pygame.font.Font(pygame.font.match_font('notosans'), 24)
        self.draw_text_centered(
            f"Watching {self.directory} for images")

    def show_image(self):
        self.img = pygame.image.load(self.img_path).convert_alpha()
        self.gameDisplay.blit(self.img, (0, 0))

    def clear(self):
        self.gameDisplay.fill(self.colours["BLACK"])
        pygame.display.update()

    def set_image(self, image_path):

        self.gameDisplay.fill(self.colours["BLACK"])
        if len(image_path) > 0:
            try:
                self.img = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e:
                logging.error(e)

            imgstring = pygame.image.tostring(self.img, "RGB", True)

            if imgstring is not self.lastimg:
                rect = self.img.get_rect()
                x, y, w, h = rect
                if w > self.screenW or h > self.screenH:
                    self.img = pygame.transform.scale(
                        self.img, (w//2, h//2))
                    w = w//2
                    h = h//2

                if self.window_size[0] != w or self.window_size[1] != h:
                    self.gameDisplay = pygame.display.set_mode(
                        (w, h), NOFRAME | DOUBLEBUF | HWSURFACE)
                self.window_size = (w, h)
                self.gameDisplay.blit(self.img, (0, 0))
                self.last_img = imgstring
                pygame.display.update()
                if image_path not in self.img_paths:
                    self.img_paths.append(image_path)
                    logging.debug(self.img_paths)

    def handle_keys(self, key):

        if(key == pygame.K_LEFT):
            if len(self.img_paths) > 1:
                self.current_img -= 1
                self.current_img = max(
                    self.current_img, len(self.img_paths))
                logging.debug(f"setting to image:  {self.current_img}")
                self.set_image(self.img_paths[self.current_img])
        if(key == pygame.K_RIGHT):
            if len(self.img_paths) > 1:
                self.current_img += 1
                self.current_img = min(
                    self.current_img, len(self.img_paths))
                self.set_image(
                    self.current_img)

    def draw_text_centered(self, text):
        self.font_surface = self.font.render(
            text, True, (255, 255, 255), self.colours["BLACK"])
        text_rect = self.font_surface.get_rect(center=(self.w//2, self.h/2))
        self.gameDisplay.blit(self.font_surface, text_rect)
        pygame.display.update()

    def display_info(self, text):
        if self.show_info:
            self.font_surface = self.font.render(
                text, True, (255, 255, 255), self.colours["BLACK"])
            self.gameDisplay.blit(self.font_surface, (10, 10))
            pygame.display.update()
        else:
            self.clear_font_surface()

    def handle_mouse(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            # logging.debug(f"button: {event.button}\npos: {event.pos}")
            if event.button == 1:
                logging.debug("mouse down!")
                self.dragging = True
                mouse_x, mouse_y = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                logging.debug("mouse up")
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:

            mouse_x, mouse_y = event.pos
            # environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(
            #     mouse_x, mouse_y)
            # set window position

    def clear_font_surface(self):
        current_surface = pygame.display.get_surface()
        self.font_surface = pygame.Surface((0, 0))
        self.gameDisplay.blit(self.font_surface, (10, 10))
        pygame.display.update()

    def run(self):
        while not self.shouldquit:
            try:
                for event in pygame.event.get():
                    if event.type in self.mouse_events:
                        self.handle_mouse(event)
                    if event.type == pygame.KEYDOWN:
                        self.handle_keys(event.key)
                        if(event.key == pygame.K_ESCAPE):
                            self.shouldquit = True
                            self.quit()
                    if event.type == pygame.QUIT:
                        self.shouldquit = True
                        self.quit()
                    elif event.type == VIDEORESIZE:
                        pass
                        # self.gameDisplay.blit(pygame.transform.scale(
                        #     self.img, event.dict['size']), (0, 0))

                self.clock.tick(30)
            except KeyboardInterrupt or SystemExit:
                logging.info("quitting...")
                self.quit()

    def quit(self):
        pygame.quit()
        quit()


if __name__ == '__main__':
    # test
    viewer = ImageViewer()
    while not viewer.shouldquit:
        viewer.set_image('test.jpeg')
        viewer.run()
    viewer.quit()
