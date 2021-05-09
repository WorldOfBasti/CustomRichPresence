#!/bin/bash

echo "Copying files.."

cp -r CustomRichPresence /usr/bin/
chmod +x /usr/bin/CustomRichPresence
cp -r customrichpresence.desktop /usr/share/applications/
cp -r CustomRichPresence.png /usr/share/pixmaps/

if [ $? -eq 0 ]; then
	echo "Installation succeeded"
else
	echo "An error occured. Are you root?"
fi
