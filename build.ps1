pyinstaller --onefile src/main.py --name UTILITARIO --distpath ./WSACTION-EXTENSION/CHROME-PROFILE
Compress-Archive -Path ./WSACTION-EXTENSION/CHROME-PROFILE/* -DestinationPath CHROME-PROFILE.zip