import os
from time import sleep
from argparse import ArgumentParser
from random import choice
import shutil

#  funtion to cpy random images in and out of the "images" folder for testing


def copy_random(directory):
    image_files = os.listdir(args.directory)
    random_image = choice(image_files)
    print(f"moving {random_image}")
    shutil.move(os.path.join(directory, random_image),
                os.path.abspath(os.getcwd()))
    sleep(1)
    print(f"moving {random_image} back to {directory}/")
    shutil.move(os.path.join(os.path.abspath(os.getcwd()), random_image),
                os.path.join(directory, random_image))
    sleep(1)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-d', '--directory',  type=str, default="images")

    args = parser.parse_args()
    while True:
        copy_random(args.directory)
