
from watchdog.events import PatternMatchingEventHandler
from imagewatcher.ui.imageviewer import ImageViewer
import logging
import time
from os import stat, path

logger = logging.getLogger(__name__)


class ImageCreationEvent(PatternMatchingEventHandler):
    def __init__(self, images=[], viewer=ImageViewer):
        super(ImageCreationEvent, self).__init__()
        self.viewer = viewer
        self.images = images
        self._ignore_directories = True
        self._patterns = ['*.jpeg', '*.png', '*.jpg', '*.bmp']
        self.filetypes = [pattern.split('.')[-1] for pattern in self.patterns]
        logger.info(
            f"watcher found {len(self.images)} existing images in folder.")
        logger.info(f"watching for filetypes:  {' '.join(self.filetypes)}")

    def on_deleted(self, event):
        logger.info(f"file deleted at {event.src_path}")
        new_file_path = event.src_path
        self.viewer.remove_image(path.basename(new_file_path))

    def wait_for_size(self, file):
        last_size, size = -1, 0
        while size != last_size:
            time.sleep(0.1)
            try:
                last_size, size = size, stat(file).st_size
            except FileNotFoundError:
                logger.error(f"wait_for_size: file was moved or deleted")
                return False
            if(size == last_size):
                return True

    def on_created(self, event):
        new_file_path = event.src_path
        logger.info(f"file created at path:  {new_file_path}")
        print(new_file_path.split('.')[-1])
        if new_file_path.split('.')[-1] in self.filetypes:
            logger.info(f"loading image at {new_file_path}")
            if self.wait_for_size(new_file_path):
                self.viewer.set_image(new_file_path)
        else:
            logger.info(f'{new_file_path} not an image:  skipping')
