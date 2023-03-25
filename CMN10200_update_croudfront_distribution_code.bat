
@ECHO OFF

SET BatFileName=%~n0
SET JobName=%BatFileName:~0,-5%

d:
cd User_Application\%JobName%
call venv\Scripts\activate
code d:\User_Application\%JobName%