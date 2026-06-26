' Silent launcher for SVHMP Auto-Watch daemon (memory feedback_wscript_launcher_pattern)
' Run với wscript.exe để hide console window (chống flash khi scheduled task chạy)
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"
sh.Run "python tools\auto_watch.py", 0, False
