[Setup]
AppName=BobLoader MF4
AppVersion=1.0
DefaultDirName={commonpf}\BobLoader MF4
DefaultGroupName=BobLoader MF4
OutputDir=dist
OutputBaseFilename=Installer-BobLoaderMF4
SetupIconFile=src\media\icon-logo.ico

[Files]
Source: "build\BobLoader MF4\*"; DestDir: "{app}"
Source: "build\BobLoader MF4\lib\*"; DestDir: "{app}\lib"; Flags: recursesubdirs
Source: "build\BobLoader MF4\src\*"; DestDir: "{app}\src"; Flags: recursesubdirs

[Icons]
Name: "{group}\BobLoader MF4"; Filename: "{app}\BobLoader MF4.exe"
Name: "{commondesktop}\BobLoader MF4"; Filename: "{app}\BobLoader MF4.exe"

