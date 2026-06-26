' SVHMP Dashboard launcher — round 14
' Khởi động server background + mở browser, không hiện console.
' Save .vbs để Desktop shortcut click 1 phát mở dashboard.

Set sh = CreateObject("WScript.Shell")
dashDir = "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\tools\dashboard"
sh.CurrentDirectory = dashDir

' Start server hidden (window style 0 = hidden, wait=False)
sh.Run "python server.py", 0, False

' Wait 2s for server warmup
WScript.Sleep 2000

' Open browser to widget
sh.Run "http://127.0.0.1:57910/"
