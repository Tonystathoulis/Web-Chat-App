@echo off

pip install python-socketio flask eventlet

echo  complete

set "countdown_duration=3"

echo Closing In %countdown_duration% 
for /l %%i in (%countdown_duration%,-1,1) do (
    echo   %%i
    timeout /nobreak /t 1 >nul
)
exit
