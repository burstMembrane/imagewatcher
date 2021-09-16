echo "Building ImageWatcher...\n"
pyinstaller imagewatcher.py --onefile --clean --hidden-import dearpygui --collect-all dearpygui
echo "copying to ~/bin"
ASSETS_PATH=~/.config/imagewatcher/
mkdir $ASSETS_PATH
cp ./assets/imagewatcher.png $ASSETS_PATH
sudo cp dist/imagewatcher ~/bin/imagewatcher