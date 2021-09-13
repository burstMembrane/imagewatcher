echo "Building ImageWatcher...\n"
pyinstaller imagewatcher.py --onefile
echo "copying to ~/bin"
sudo cp dist/imagewatcher ~/bin/imagewatcher