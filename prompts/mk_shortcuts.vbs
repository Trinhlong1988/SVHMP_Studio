' mk_shortcuts.vbs — tao shortcut Desktop tro toi launcher .cmd trong repo.
' Chay bang cscript (KHONG PowerShell). Portable: tu suy ra repo tu vi tri file.
Set fso = CreateObject("Scripting.FileSystemObject")
promptsDir = fso.GetParentFolderName(WScript.ScriptFullName)   ' <repo>\prompts
repo = fso.GetParentFolderName(promptsDir)
Set S = CreateObject("WScript.Shell")
D = S.SpecialFolders("Desktop")

Mk "SVHMP PIPELINE (control).lnk", "launch_control.cmd"
Mk "SVHMP CMD BUILD.lnk",          "launch_build.cmd"
Mk "SVHMP CMD ARCH.lnk",           "launch_arch.cmd"
Mk "SVHMP CMD QA.lnk",             "launch_qa.cmd"
Mk "SVHMP CMD RELEASE.lnk",        "launch_release.cmd"
WScript.Echo "Desktop shortcuts created -> " & D

Sub Mk(lnkName, cmdFile)
  Set L = S.CreateShortcut(D & "\" & lnkName)
  L.TargetPath = promptsDir & "\" & cmdFile
  L.WorkingDirectory = repo
  L.IconLocation = "shell32.dll,167"
  L.Save
End Sub
