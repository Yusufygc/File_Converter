; FileConvert kurulum sihirbazi (Inno Setup 6).
; Derleme: python build_installer.py  (surum /DAppVersion ile version.py'den gelir; elle derleme yok)
#ifndef AppVersion
  #error AppVersion tanimli degil: python build_installer.py ile derle
#endif

#define MyAppName "FileConvert"
#define MyAppPublisher "Yusuf YGC"
#define MyAppURL "https://github.com/Yusufygc/File_Converter"
#define MyAppExeName "FileConvert.exe"

; Tesseract OCR — kurulum sihirbazinda istege bagli indirme adimi icin.
; UB-Mannheim kurulumu NSIS tabanlidir: sessiz kurulum parametresi /S (Inno'nun /VERYSILENT'i degil).
#define TesseractUrl "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
; Varsayilan Tesseract kurulumu yalnizca Ingilizce dil paketiyle gelir; uygulama "tur+eng" tercih ediyor.
#define TesseractTurUrl "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/tur.traineddata"

[Setup]
; AppId SABIT: degisirse sonraki surum ustune yazmaz, ikinci kurulum olur (1.0.0 kurulumuyla da ayni)
AppId={{8E478C22-671A-4D7A-A144-C9271DB89F42}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppVerName={#MyAppName} {#AppVersion}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Kurulum Sihirbazı
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
; PrivilegesRequired=lowest iken {autopf} = %LOCALAPPDATA%\Programs
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
DisableProgramGroupPage=yes
; UAC sormaz: uygulama ici guncelleme sessiz calisir, derleme sonrasi deneme mumkun olur.
; Kullanici isterse "tum kullanicilar icin" (yonetici) secebilir.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Guncellemede calisan uygulama kapatilir (dosya kilidi olmasin); yeniden acmayi [Run] yapar
CloseApplications=yes
RestartApplications=no
SetupIconFile=..\assets\icons\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\dist\installer
; Surumlu ad: guncelleyici bu desene bakar (FileConvert-Setup-X.Y.Z.exe)
OutputBaseFilename=FileConvert-Setup-{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "installtesseract"; Description: "Tesseract metin tanıma programını indir ve kur — taranmış (görüntü tabanlı) PDF'lerden düzenlenebilir metin çıkarmak için gerekir. Normal (dijital) PDF'ler bu olmadan da dönüştürülebilir. Türkçe dil paketi de eklenir. İnternet bağlantısı ve yönetici onayı gerektirir, ~70 MB indirilir."; GroupDescription: "İsteğe Bağlı Bileşenler:"; Flags: unchecked

[Files]
Source: "..\dist\FileConvert\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
; Uygulama ici guncelleme (/SILENT): kurulumdan sonra uygulama kendiliginden yeniden acilir
Filename: "{app}\{#MyAppExeName}"; Flags: nowait; Check: RelaunchAfterUpdate

; Kullanici verisi (%LOCALAPPDATA%\FileConvert: gunluk, guncelleme tercihleri) kaldirici tarafindan SILINMEZ.

[Code]
const
  TesseractManualUrl = 'https://github.com/UB-Mannheim/tesseract/wiki';
  OldUninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8E478C22-671A-4D7A-A144-C9271DB89F42}_is1';

function HasParam(const Name: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), Name) = 0 then
    begin
      Result := True;
      Exit;
    end;
end;

{ /SILENT (guncelleme) yeniden acar; /VERYSILENT (derleme sonrasi deneme) acmaz. WizardVerySilent diye bir islev yoktur. }
function RelaunchAfterUpdate: Boolean;
begin
  Result := WizardSilent and not HasParam('/VERYSILENT');
end;

{ ---------------------------------------------------------------- 1.0.0 (yonetici) kurulumunun gecisi
  1.0.0 PrivilegesRequired=admin ile Program Files'a kuruluyordu (kayit HKLM'de). Kullanici-basina
  kurulum HKCU'ya yazar: eski kurulum kaldirilmazsa "Uygulamalar ve ozellikler"de iki FileConvert olur. }

function OldAdminUninstallString(var Uninstall: String): Boolean;
begin
  Result := RegQueryStringValue(HKLM64, OldUninstallKey, 'UninstallString', Uninstall)
            or RegQueryStringValue(HKLM32, OldUninstallKey, 'UninstallString', Uninstall);
end;

function InitializeSetup(): Boolean;
var
  Uninstall: String;
  ResultCode: Integer;
begin
  Result := True;
  if IsAdminInstallMode or WizardSilent then
    Exit;
  if not OldAdminUninstallString(Uninstall) then
    Exit;
  if MsgBox('FileConvert''ün eski bir sürümü bu bilgisayara tüm kullanıcılar için kurulu.' + #13#10#13#10 +
            'Yeni sürüm yalnızca sizin hesabınıza kurulacak. Eski sürüm şimdi kaldırılsın mı? ' +
            '(Yönetici onayı istenir; ayarlarınız korunur.)', mbConfirmation, MB_YESNO) = IDYES then
  begin
    if not ShellExec('', RemoveQuotes(Uninstall), '/SILENT /NORESTART /SUPPRESSMSGBOXES', '',
                     SW_SHOW, ewWaitUntilTerminated, ResultCode) then
      MsgBox('Eski sürüm kaldırılamadı. Kurulum devam edecek; eski sürümü daha sonra ' +
             '"Uygulamalar ve özellikler" bölümünden kaldırabilirsiniz.', mbInformation, MB_OK);
  end;
end;

{ ---------------------------------------------------------------- istege bagli Tesseract }

function TesseractDir(): String;
begin
  Result := ExpandConstant('{commonpf64}\Tesseract-OCR');
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

{ Tesseract Program Files'a kurulur ve tessdata oraya yazilir: ikisi de yonetici ister. FileConvert
  kullanici-basina kuruldugu icin indirmeler yetkisiz yapilir, kurulum + dil paketi kopyalama TEK bir
  yukseltilmis PowerShell surecinde yapilir (tek UAC onayi). }
procedure InstallTesseractWithLanguage();
var
  ResultCode: Integer;
  SetupExe, TurFile, Script: String;
  NeedInstall, NeedTur: Boolean;
begin
  NeedInstall := not TesseractAlreadyInstalled();
  NeedTur := not FileExists(TesseractDir() + '\tessdata\tur.traineddata');
  if not NeedInstall and not NeedTur then
    Exit;

  SetupExe := ExpandConstant('{tmp}\tesseract-setup.exe');
  TurFile := ExpandConstant('{tmp}\tur.traineddata');

  if NeedInstall then
  begin
    SetStatus('Tesseract indiriliyor, lütfen bekleyin...');
    if not DownloadFile('{#TesseractUrl}', SetupExe) then
    begin
      MsgBox('Tesseract indirilemedi (internet bağlantınızı kontrol edin). ' +
             'FileConvert yine de kuruldu; taranmış PDF''lerden metin okuma özelliği olmadan çalışır. ' +
             'Daha sonra elle kurabilirsiniz: ' + TesseractManualUrl, mbInformation, MB_OK);
      Exit;
    end;
  end;

  SetStatus('Tesseract Türkçe dil paketi indiriliyor...');
  if not DownloadFile('{#TesseractTurUrl}', TurFile) then
    TurFile := '';

  Script := '& { ';
  if NeedInstall then
    Script := Script + '$p = Start-Process -FilePath ''' + SetupExe + ''' -ArgumentList ''/S'' -Wait -PassThru; '
                     + 'if ($p.ExitCode -ne 0) { exit 1 }; ';
  if TurFile <> '' then
    Script := Script + 'Copy-Item -LiteralPath ''' + TurFile + ''' -Destination '''
                     + TesseractDir() + '\tessdata\tur.traineddata'' -Force; ';
  Script := Script + '}';

  SetStatus('Tesseract kuruluyor (yönetici onayı istenecek)...');
  if not (ShellExec('runas', 'powershell.exe',
                    '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "' + Script + '"',
                    '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
          and (ResultCode = 0) and TesseractAlreadyInstalled()) then
    MsgBox('Tesseract kurulumu tamamlanamadı (yönetici onayı verilmemiş olabilir). FileConvert yine de kuruldu; ' +
           'bu özelliği daha sonra elle ekleyebilirsiniz: ' + TesseractManualUrl, mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  { Sessiz kurulumda (uygulama ici guncelleme) onceki gorev secimleri hatirlanir: UAC penceresi cikmasin. }
  if (CurStep = ssPostInstall) and not WizardSilent and WizardIsTaskSelected('installtesseract') then
    InstallTesseractWithLanguage();
end;
