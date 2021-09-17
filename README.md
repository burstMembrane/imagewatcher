# ImageWatcher

![ImageWatcher UI Preview](assets/preview.png)

<br>
A command line utility to watch for explore and watch image creation in a folder.

Built in Python using [DearPyGui](https://github.com/hoffstadt/DearPyGui) and [watchdog](https://github.com/gorakhargosh/watchdog).

<br>
## Installation
<br>
clone the repo

```
git clone https://github.com/burstMembrane/imagewatcher
```

create a virtual env for the project
<br>
``` bash
virtualenv imagewatcher
source virtualenv/bin/activate
```

install requirements.txt

```
pip install -r requirements.txt
```

## Usage

```
python imagewatcher.py -d </path/to/directory/to/watch>
```

## Key bindings

```
ESC -- quit application
ARROW_KEYS -- cycle images in folder
f -- toggle fullscreen
```