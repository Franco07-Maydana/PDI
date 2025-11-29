[Setup]
AppName=Sistema de Stock Remoto
AppVersion=1.0
DefaultDirName={autopf}\SistemaStock
DefaultGroupName=Sistema de Stock
LanguageDetectionMethod=locale

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source:"ClienteStock.exe"; DestDir:"{app}"
Source:"ServidorStock.exe"; DestDir:"{app}"

[Icons]
Name: "{commondesktop}\Cliente Stock"; Filename: "{app}\ClienteStock.exe"
Name: "{commondesktop}\Servidor Stock"; Filename: "{app}\ServidorStock.exe"

[Run]
Filename: "{app}\ServidorStock.exe"; Flags: nowait postinstall shellexec

