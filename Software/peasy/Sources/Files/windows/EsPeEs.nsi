;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

  !define MUI_ICON "EsPeEs\GUIs\Icons\espees.ico"
;--------------------------------
;General

  ;Name and file
  Name "EsPeEs"
  OutFile "EsPeEs_v0.4.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\EsPeEs"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\EsPeEs" "InstallDir"

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

Section "EsPeEs" SECGPH

  SetOutPath "$INSTDIR"

  File /r EsPeEs

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EsPeEs" "DisplayName" "EsPeEs"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EsPeEs" "UninstallString" '"$INSTDIR\Uninstall.exe""'

  SetOutPath "$INSTDIR\EsPeEs"

  CreateDirectory "$SMPROGRAMS\EsPeEs"
  CreateShortCut "$SMPROGRAMS\EsPeEs\EsPeEs.lnk" "$INSTDIR\EsPeEs\python\pythonw.exe" "EsPeEs-Client.py" "$INSTDIR\EsPeEs\python\pythonw.exe" 0
  CreateShortCut "$SMPROGRAMS\EsPeEs\EsPeEs-Server.lnk" "$INSTDIR\EsPeEs\python\python.exe" "EsPeEs-Server.py" "$INSTDIR\EsPeEs\python\python.exe" 0
  CreateShortCut "$SMPROGRAMS\EsPeEs\Uninstall EsPeEs.lnk" "$INSTDIR\Uninstall.exe"

  SetOutPath "$INSTDIR"

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "EsPeEs."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section



Section "Uninstall"

  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\EsPeEs\EsPeEs.lnk"
  Delete "$SMPROGRAMS\EsPeEs\EsPeEs-Server.lnk"
  Delete "$SMPROGRAMS\EsPeEs\Uninstall EsPeEs.lnk"
  RMDir "$SMPROGRAMS\EsPeEs"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EsPeEs"
  DeleteRegKey /ifempty HKCU "Software\EsPeEs"

SectionEnd

Function .onInit
 
  ReadRegStr $R0 HKLM \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\EsPeEs" \
  "UninstallString"
  StrCmp $R0 "" done
 
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "EsPeEs is already installed. $\n$\nClick `OK` to remove the \
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
