#  ewatches a folder for updates in image fiels
# pushes most recent file to an array and shows it on screen in borderless window
# arrow keys to switch between iamges and filename display

from genericpath import isdir
import time
import argparse

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from imageviewer_pdg import ImageViewerPDG
from imageviewer_pg import ImageViewerPG
import time
from os import stat
from os.path import splitext
import logging
from threading import Thread
import glob
import os


def is_dir(parser, arg):
    if not os.path.isdir(arg):
        parser.error("The dir %s does not exist!" % arg)
    else:
        return arg  # the dir path


def check_backend(parser, arg):
    if arg in ["pg", "pdg"]:
        return arg
    else:
        parser.error("Please specify a backend to use: pdg | pg")


# parse directory argument
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory',
                    help="a directory of images to watch for changes", default="", type=lambda d: is_dir(parser, d), required=True)
parser.add_argument('-b', '--backend',
                    help="dearpygui or pygame as backend", default="pdg", type=lambda d: check_backend(parser, d), required=False)

parser.add_argument('-v', '--debug',
                    help="log debug messages to console", default=False, type=bool, required=False)


args = parser.parse_args()
logging.basicConfig(format='[ %(asctime)s.%(msecs)03d ] %(message)s',
                    level=logging.INFO,
                    datefmt=f"%d-%m-%y %H:%M:%S")

# TODO: ADD FILE MODIFIED EVENT (get all images in folder)


class ImageCreationWatcher:
    def __init__(self, directory="."):
        self.src_path = directory
        self.patterns = ['*.jpeg', '*.png', '*.jpg', '*.bmp']
        self.images = []
        for pattern in self.patterns:
            self.images.extend(glob.glob(os.path.join(
                directory, pattern), recursive=True))

        self.event_handler = ImageCreationEvent(images=self.images)
        self.event_observer = Observer()
        logging.info(f"Watching directory {directory} for images.")

    def run(self):
        if os.path.isdir(self.src_path):
            self.start()
        else:
            logging.info(f"{self.src_path} is not a valid directory")
            self.stop()
            exit()
        try:
            while True:
                # logging.info('Checking...')
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


class ImageCreationEvent(PatternMatchingEventHandler):
    def __init__(self, images=""):
        super(ImageCreationEvent, self).__init__()
        self.images = images
        self._ignore_directories = True
        self._patterns = ['*.jpeg', '*.png', '*.jpg', '*.bmp']
        self.filetypes = [pattern.split('.')[-1] for pattern in self.patterns]
        logging.info(
            f"watcher found {len(self.images)} existing images in folder.")
        logging.info(f"watching for filetypes:  {' '.join(self.filetypes)}")

    def on_deleted(self, event):
        logging.info(f"file deleted at {event.src_path}")
        new_file_path = event.src_path
        viewer.remove_image(os.path.basename(new_file_path))

    def wait_for_size(self, file):
        last_size, size = -1, 0
        while size != last_size:
            time.sleep(0.1)
            try:
                last_size, size = size, stat(file).st_size
            except FileNotFoundError:
                logging.error(f"wait_for_size: file was moved or deleted")
                return False
            if(size == last_size):
                return True

    def on_created(self, event):
        new_file_path = event.src_path
        logging.info(f"file created at path:  {new_file_path}")
        print(new_file_path.split('.')[-1])
        if new_file_path.split('.')[-1] in self.filetypes:
            logging.info(f"loading image at {new_file_path}")
            if self.wait_for_size(new_file_path):
                viewer.set_image(new_file_path)
        else:
            logging.info(f'{new_file_path} not an image:  skipping')


if __name__ == "__main__":
    if args.backend == "pg":
        viewer = ImageViewerPG()
    elif args.backend == "pdg":
        viewer = ImageViewerPDG()
    # create file watcher
    if(os.path.isdir(args.directory)):
        imwatcher = ImageCreationWatcher(directory=args.directory)
        # run the file watcher in a separate thread
        viewer.set_directory(args.directory, imwatcher.images)
        worker = Thread(target=imwatcher.run)
        worker.setDaemon(True)
        worker.start()
        viewer.run()
    else:
        logging.info("Not a valid directory.. Quitting")

worker.join(timeout=1.0)
viewer.quit()
quit(0)
