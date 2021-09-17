from watchdog.observers import Observer
import logging
import glob
import os
import time

# relative imports
from imageviewer.filewatcher.imagecreationevent import ImageCreationEvent
from imageviewer.ui.imageviewer import ImageViewer

logger = logging.getLogger(__name__)


class ImageCreationWatcher:
    def __init__(self, directory=".", viewer=ImageViewer):
        self.viewer = viewer
        self.src_path = directory
        self.patterns = ['*.jpeg', '*.png', '*.jpg', '*.bmp']
        self.images = []
        for pattern in self.patterns:
            self.images.extend(glob.glob(os.path.join(
                directory, pattern), recursive=True))

        self.event_handler = ImageCreationEvent(
            images=self.images, viewer=self.viewer)
        self.event_observer = Observer()
        logger.info(f"Watching directory {directory} for images.")

    def run(self):
        if os.path.isdir(self.src_path):
            self.start()
        else:
            logger.info(f"{self.src_path} is not a valid directory")
            self.stop()
            exit()
        try:
            while True:
                # logger.info('Checking...')
                time.sleep(30)
        except KeyboardInterrupt:
            self.stop()
        self.event_observer.join()

    def start(self):
        self.schedule()
        self.event_observer.start()

    def stop(self):
        self.event_observer.stop()
        self.event_observer.join()

    def schedule(self):
        self.event_observer.schedule(
            self.event_handler,
            self.src_path,
            recursive=True
        )
