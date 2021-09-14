echo "Building ImageWatcher...\n"
pyinstaller imagewatcher.py --onefile --clean --hidden-import dearpygui --collect-all dearpygui
echo "copying to ~/bin"
sudo cp dist/imagewatcher ~/bin/imagewatcher