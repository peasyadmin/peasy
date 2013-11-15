;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

  !define MUI_ICON "Peasy\GUIs\Icons\espees.ico"
;--------------------------------
;General

  ;Name and file
  Name "Peasy"
  OutFile "Peasy_v0.1.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Peasy"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Peasy" "InstallDir"

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Peasy" SECGPH

  SetOutPath "$INSTDIR"

  File /r Peasy

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Peasy" "DisplayName" "Peasy"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Peasy" "UninstallString" '"$INSTDIR\Uninstall.exe""'

  SetOutPath "$INSTDIR\Peasy"

  CreateDirectory "$SMPROGRAMS\Peasy"
  CreateShortCut "$SMPROGRAMS\Peasy\Peasy.lnk" "$INSTDIR\Peasy\python\pythonw.exe" "Peasy-Client.py" "$INSTDIR\Peasy\python\pythonw.exe" 0
  CreateShortCut "$SMPROGRAMS\Peasy\Peasy-Server.lnk" "$INSTDIR\Peasy\python\python.exe" "Peasy-Server.py" "$INSTDIR\Peasy\python\python.exe" 0
  CreateShortCut "$SMPROGRAMS\PeasyE\Uninstall Peasy.lnk" "$INSTDIR\Uninstall.exe"

  SetOutPath "$INSTDIR"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "Peasy."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section



Section "Uninstall"

  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\Peasy\Peasy.lnk"
  Delete "$SMPROGRAMS\Peasy\Peasy-Server.lnk"
  Delete "$SMPROGRAMS\Peasy\Uninstall Peasy.lnk"
  RMDir "$SMPROGRAMS\Peasy"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Peasy"
  DeleteRegKey /ifempty HKCU "Software\Peasy"

SectionEnd

Function .onInit
 
  ReadRegStr $R0 HKLM \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\Peasy" \
  "UninstallString"
  StrCmp $R0 "" done
 
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "Peasy is already installed. $\n$\nClick `OK` to remove the \
  previous version or `Cancel` to cancel this upgrade." \
  IDOK uninst
  Abort
 
;Run the uninstaller
uninst:
  ClearErrors
  ExecWait '$R0 _?=$INSTDIR' ;Do not copy the uninstaller to a temp file
 
  IfErrors no_remove_uninstaller done
    ;You can either use Delete /REBOOTOK in the uninstaller or add some code
    ;here to remove the uninstaller. Use a registry key to check
    ;whether the user has chosen to uninstall. If you are using an uninstaller
    ;components page, make sure all sections are uninstalled.
  no_remove_uninstaller:
 
done:
 
FunctionEnd
