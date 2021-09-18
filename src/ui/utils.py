import os
from time import sleep
from argparse import ArgumentParser
from random import choice
import shutil
import subprocess
import logging


def print_cb_data(sender, app_data, user_data):
    logging.info(f"sender is: {sender}")
    logging.info(f"app_data is: {app_data}")
    logging.info(f"user_data is: {user_data}")


def get_resolution_linux():
    cmd = ['xrandr']
    cmd2 = ['grep', '*']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
    p.stdout.close()
    resolution_string, _ = p2.communicate()
    resolution = resolution_string.decode().split()[0]
    width, height = resolution.split('x')
    return int(width), int(height)


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


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-d', '--directory',  type=str, default="images")

    args = parser.parse_args()
    while True:
        copy_random(args.directory)
