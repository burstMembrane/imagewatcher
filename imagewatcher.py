#  watches a folder for updates in image fiels
# pushes most recent file to an array and shows it on screen in borderless window
# arrow keys to switch between iamges and filename display

import argparse
from src.ui.imageviewer import ImageViewer
from src.filewatcher.imagecreationwatcher import ImageCreationWatcher
import logging
from threading import Thread
from src.ui.utils import is_dir

logger = logging.getLogger(__name__)


def main(args):
    viewer = ImageViewer()
    # create file watcher
    imwatcher = ImageCreationWatcher(
        directory=args.directory, viewer=viewer)
    viewer.set_directory(args.directory, imwatcher.images)
    watcher_thread = Thread(target=imwatcher.run)
    watcher_thread.setDaemon(True)
    watcher_thread.start()
    viewer.run()
    watcher_thread.join(timeout=1.0)
    viewer.quit()
    quit(0)


if __name__ == "__main__":
    # parse directory argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory',
                        help="a directory of images to watch for changes", default="", type=lambda d: is_dir(parser, d), required=True)

    parser.add_argument('-v', '--debug',
                        help="log debug messages to console", default=False, type=bool, required=False)

    args = parser.parse_args()
    logging.basicConfig(format='[ %(asctime)s.%(msecs)03d ] %(message)s',
                        level=logging.INFO,
                        datefmt=f"%d-%m-%y %H:%M:%S")

    main(args)
