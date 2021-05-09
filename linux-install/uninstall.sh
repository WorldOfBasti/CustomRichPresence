#!/bin/bash

echo "Removing files.."

rm -rf /usr/bin/CustomRichPresence
rm -rf /usr/share/applications/customrichpresence.desktop
rm -rf /usr/share/pixmaps/CustomRichPresence.png

if [ $? -eq 0 ]; then
	echo "Uninstallation succeeded"
else
	echo "An error occured. Are you root?"
fi
