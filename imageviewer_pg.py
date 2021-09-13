#!/usr/bin/python3
import pygame
from pygame.locals import NOFRAME, VIDEORESIZE, DOUBLEBUF, HWSURFACE, RESIZABLE
import logging
from os import environ
from PIL import Image


class ImageViewer:
    def __init__(self):

        # IMAGE SETUP
        self.directory = ""
        self.current_img = 0
        self.img_paths = []
        self.img_path = ''
        self.img = []

        # MOUSE SETUP
        self.mouse_events = [pygame.MOUSEBUTTONDOWN,
                             pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]
        self.dragging = False

        # WINDOW SETUP
        pygame.init()
        wininfo = pygame.display.Info()
        print(wininfo)
        self.screenW = wininfo.current_w
        self.screenH = wininfo.current_h

        self.window_size = (640, 480)
        self.w, self.h = self.window_size
        self.imageW, self.imageH = self.window_size

        self.init_window(self.w, self.h)
        self.colours = {
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255)
        }

        self.clock = pygame.time.Clock()
        self.firstrun = True
        self.show_info = False
        self.shouldquit = False
        self.lastimg = pygame.Surface(self.window_size)

        # FONT SETUP
        self.font = pygame.font.Font(pygame.font.match_font('notosans'), 24)
        self.draw_text_centered(
            f"Watching {self.directory} for images")

    def init_window(self, width, height):

        windowX = (self.screenW//2) - (width//2)
        windowY = (self.screenH//2) - (height//2)
        logging.info(
            f"setting window  for {self.img_path} pos to: {windowX},{windowY}")
        environ['SDL_VIDEO_WINDOW_POS'] = f"{windowX},{windowY}"
        environ['SDL_VIDEO_CENTERD'] = "1"
        self.gameDisplay = pygame.display.set_mode(
            (width, height), NOFRAME | RESIZABLE)

    def resize_image(self, image, windowW, windowH):
        center_image = False

        image_w, image_h = image.get_size()

        screen_aspect_ratio = windowW / windowH
        photo_aspect_ratio = image_w / image_h
        logging.debug(
            f"screen aspect ratio:  {screen_aspect_ratio} \n photo aspect_ratio:  {photo_aspect_ratio}")
        if screen_aspect_ratio < photo_aspect_ratio:  # Width is binding
            new_image_w = windowW
            new_image_h = int(windowW / photo_aspect_ratio)
            image = pygame.transform.scale(image, (new_image_w, new_image_h))

        elif screen_aspect_ratio > photo_aspect_ratio:  # Height is binding
            new_image_h = windowH
            new_image_w = int(new_image_h * photo_aspect_ratio)
            # image = pygame.transform.scale(image, (new_image_w, new_image_h))
            image_x = (windowW - new_image_w) // 2 if center_image else 0
            image_y = 0

        else:  # Images have the same aspect ratio
            new_image_w = windowW
            new_image_h = windowH
            image_x = 0
            image_y = 0

        return (new_image_w, new_image_h)

    def show_image(self):
        self.img = pygame.image.load(self.img_path).convert_alpha()
        self.gameDisplay.blit(self.img, (0, 0))

    def clear(self):
        self.gameDisplay.fill(self.colours["BLACK"])
        pygame.display.flip()

    def set_image(self, image_path):
        self.img_path = image_path
        if self.firstrun:
            pygame.init()
            self.firstrun = False
        self.gameDisplay.fill(self.colours["BLACK"])
        if len(image_path) > 0:
            try:
                self.pil_img = Image.open(image_path)

                w = self.pil_img.width
                h = self.pil_img.height

                self.img = pygame.image.load(
                    image_path).convert_alpha()
                logging.debug(self.img)
            except pygame.error as e:
                logging.error(e)
            rect = self.img.get_rect()
            x, y, w, h = rect
            logging.debug(rect)
            if w != self.imageW or h != self.imageH:
                if w > self.screenW or h > self.screenH:

                    diff = abs((self.screenW/self.screenH) / (w / h))
                    logging.info(f"DIFF:   {diff}")
                    w = round(w / diff)
                    h = round(h / diff)

                    self.img = pygame.transform.scale(
                        self.img, (int(w), int(h)))
                self.imageW = w
                self.imageH = h
                pygame.event.post(pygame.event.Event(
                    VIDEORESIZE, {"size": (w, h), "w": w, "h": h}))
                if image_path not in self.img_paths:
                    self.img_paths.append(image_path)
                    logging.debug(self.img_paths)

    def handle_keys(self, key):
        if(key == pygame.K_LEFT):
            if len(self.img_paths) > 1:

                self.current_img = self.img_paths.index(self.img_path) - 1
                self.current_img = max(
                    self.current_img, 0)
                logging.info(f" K_LEFT setting to image:  {self.current_img}")
                self.set_image(self.img_paths[self.current_img])
        if(key == pygame.K_RIGHT):
            if len(self.img_paths) > 1 & self.current_img < len(self.img_paths):
                self.current_img += 1

                self.set_image(
                    self.img_paths[self.current_img % len(self.img_paths)])

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

        # elif event.type == pygame.MOUSEMOTION and self.dragging:

            # mouse_x, mouse_y = event.pos
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
                        print(event.dict)
                        if "size" in event.dict.keys():
                            event_w, event_h = event.dict["size"]

                            if self.img:
                                w, h = self.resize_image(
                                    self.img, event_w, event_h)
                                image = pygame.transform.scale(
                                    self.img, (w, h))

                                self.gameDisplay = pygame.display.set_mode(
                                    (w, h),  NOFRAME)
                                self.gameDisplay.blit(image, (0, 0))
                                pygame.display.flip()

                self.clock.tick(2)
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
