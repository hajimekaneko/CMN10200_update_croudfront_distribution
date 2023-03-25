
@ECHO OFF

SET BatFileName=%~n0
SET JobName=%BatFileName:~0,-4%

d:
cd User_Application\%JobName%
call venv\Scripts\activate
start "%JobName%"