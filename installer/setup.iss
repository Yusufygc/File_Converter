; Inno Setup 6 Script for FileConvert
; =========================================

#define MyAppName "FileConvert"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Yusuf YGC"
#define MyAppURL "https://github.com/Yusufygc/File_Converter"
#define MyAppExeName "FileConvert.exe"

; Tesseract OCR — kurulum sihirbazında isteğe bağlı indirme adımı için.
; UB-Mannheim kurulumu NSIS tabanlıdır: sessiz kurulum parametresi /S (Inno'nun /VERYSILENT'ı değil).
#define TesseractUrl "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
; Varsayılan Tesseract kurulumu yalnızca İngilizce dil paketiyle gelir; uygulama "tur+eng" tercih ediyor.
#define TesseractTurUrl "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/tur.traineddata"

[Setup]
AppId={{8E478C22-671A-4D7A-A144-C9271DB89F42}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Kurulum Sihirbazı
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist\installer
OutputBaseFilename=FileConvert_Setup_v{#MyAppVersion}
SetupIconFile=..\assets\icons\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=auto
; Program Files'a kurulum için yönetici hakkı zorunlu kılınır (Tesseract
; alt-kurulumu da aynı yetkiyi gerektiriyor).
PrivilegesRequired=admin

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "installtesseract"; Description: "Tesseract OCR motorunu indir ve kur — taranmış (görüntü tabanlı) PDF'lerden düzenlenebilir metin çıkarmak için gerekir. Normal (dijital) PDF'ler bu olmadan da dönüştürülebilir. Türkçe dil paketi de eklenir. İnternet bağlantısı gerektirir, ~70 MB indirilir."; GroupDescription: "İsteğe Bağlı Bileşenler:"; Flags: unchecked

[Files]
Source: "..\dist\FileConvert\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\assets\icons\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\assets\icons\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
const
  TesseractManualUrl = 'https://github.com/UB-Mannheim/tesseract/wiki';

function TesseractDir(): String;
begin
  Result := ExpandConstant('{pf}\Tesseract-OCR');
end;

function TesseractAlreadyInstalled(): Boolean;
begin
  Result := FileExists(TesseractDir() + '\tesseract.exe');
end;

function DownloadFile(const Url, Dest: String): Boolean;
var
  ResultCode: Integer;
  PsCommand: String;
begin
  PsCommand := '-NoProfile -ExecutionPolicy Bypass -Command "try { '
    + '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
    + '$ProgressPreference = ''SilentlyContinue''; '
    + 'Invoke-WebRequest -Uri ''' + Url + ''' -OutFile ''' + Dest + ''' -UseBasicParsing '
    + '} catch { exit 1 }"';
  Result := Exec('powershell.exe', PsCommand, '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
            and (ResultCode = 0) and FileExists(Dest);
end;

procedure SetStatus(const Msg: String);
begin
  WizardForm.StatusLabel.Caption := Msg;
  WizardForm.Update;
end;

function InstallTesseract(): Boolean;
var
  ResultCode: Integer;
  TempExe: String;
begin
  Result := True;
  if TesseractAlreadyInstalled() then
    Exit;

  TempExe := ExpandConstant('{tmp}\tesseract-setup.exe');
  SetStatus('Tesseract OCR indiriliyor, lütfen bekleyin...');
  if not DownloadFile('{#TesseractUrl}', TempExe) then
  begin
    MsgBox('Tesseract OCR indirilemedi (internet bağlantınızı kontrol edin). ' +
           'FileConvert yine de kuruldu; taranmış PDF''lerden OCR ile metin çıkarma özelliği olmadan çalışır. ' +
           'Daha sonra elle kurabilirsiniz: ' + TesseractManualUrl, mbInformation, MB_OK);
    Result := False;
    Exit;
  end;

  SetStatus('Tesseract OCR kuruluyor...');
  if not (Exec(TempExe, '/S', '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
          and (ResultCode = 0) and TesseractAlreadyInstalled()) then
  begin
    MsgBox('Tesseract OCR kurulumu tamamlanamadı. FileConvert yine de kuruldu; ' +
           'bu özelliği daha sonra elle ekleyebilirsiniz: ' + TesseractManualUrl, mbInformation, MB_OK);
    Result := False;
  end;
end;

procedure EnsureTurkishLanguagePack();
var
  TurFile: String;
begin
  TurFile := TesseractDir() + '\tessdata\tur.traineddata';
  if FileExists(TurFile) or not DirExists(TesseractDir() + '\tessdata') then
    Exit;

  SetStatus('Tesseract Türkçe dil paketi indiriliyor...');
  if not DownloadFile('{#TesseractTurUrl}', TurFile) then
    MsgBox('Tesseract Türkçe dil paketi indirilemedi; OCR İngilizce dil paketiyle çalışmaya devam edecek.', mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('installtesseract') then
  begin
    if InstallTesseract() then
      EnsureTurkishLanguagePack();
  end;
end;
