Sub Wait(n As Long)<br>
    Dim t As Date<br>
    t = Now<br>
    Do<br>
        DoEvents<br>
    Loop Until Now &gt;= DateAdd("s", n, t)<br>
End Sub
 
Private Sub Document_Open()<br>
     Wait 3                      ' Wait for Word to load the document<br>
     SendKeys "^({ESC})", True   ' Open Windows bar<br>
     Wait 0.5                    ' Allow the workstation to set the cursor, etc.<br>
     SendKeys "calc.exe", True   ' Send "calc.exe" to the bar<br>
     SendKeys "%~^~", True       ' Send the "special" ENTER<br>
 End Sub
