Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oLink = WshShell.CreateShortcut(strDesktop & "\Student OS.lnk")
oLink.TargetPath = "wscript.exe"
oLink.Arguments = """C:\Users\Shaunak Rane\Desktop\Projects\Automation\Student_OS\start_student_os.vbs"""
oLink.WorkingDirectory = "C:\Users\Shaunak Rane\Desktop\Projects\Automation\Student_OS"
oLink.IconLocation = "C:\Users\Shaunak Rane\Desktop\Projects\Automation\Student_OS\student_os.ico, 0"
oLink.Description = "Student OS Autonomous Academic and Career Copilot"
oLink.Save
WScript.Echo "SUCCESS: Shortcut created at " & strDesktop & "\Student OS.lnk"
