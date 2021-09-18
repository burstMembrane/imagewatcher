#  watches a folder for updates in image fiels
# pushes most recent file to an array and shows it on screen in borderless window
# arrow keys to switch between iamges and filename display

import argparse
from src.ui.imageviewer import ImageViewer
from src.filewatcher.imagecreationwatcher import ImageCreationWatcher
import logging
from threading import Thread
from src.ui.utils import is_dir
import coloredlogs

logger = logging.getLogger(__name__)


def main(args):
    if args.verbose:
        logger.debug("Printing debug messages to the console")
    viewer = ImageViewer()
    # create file watcher
    imwatcher = ImageCreationWatcher(
        directory=args.directory, viewer=viewer)
    viewer.set_directory(args.directory, imwatcher.images)
    watcher_thread = Thread(target=imwatcher.run)
    watcher_thread.setDaemon(True)
    watcher_thread.start()
    viewer.run()
    watcher_thread.join(timeout=0.01)
    exit(0)


if __name__ == "__main__":
    # parse directory argument
    parser = argparse.ArgumentParser(
        description="ImageWatcher: views created images in a folder")
    parser.add_argument('-d', '--directory',
                        help="a directory of images to watch for changes", default="", type=lambda d: is_dir(parser, d), required=True)
    parser.add_argument('-v', '--verbose',
                        help="log debug messages to console",  action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger(__name__)

    coloredlogs.install(
        logger=logger,
        fmt='[ ImageWatcher ][ %(asctime)s ] [%(name)s.%(funcName)s()] [%(levelname)s] %(message)s',
    )

    main(args)
