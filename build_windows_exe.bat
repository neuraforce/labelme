@echo off
setlocal

REM Create a virtual environment if it does not exist
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Upgrade pip and install required packages
pip install --upgrade pip
pip install pyinstaller
pip install .

for /f %%i in ('python -c "import os, osam; print(os.path.dirname(osam.__file__))"') do set OSAM_PATH=%%i
set LABELME_PATH=%cd%\labelme

REM Get onnxruntime path
for /f %%i in ('python -c "import os, onnxruntime; print(os.path.dirname(onnxruntime.__file__))"') do set ONNX_PATH=%%i

pyinstaller %LABELME_PATH%\__main__.py ^
  --name=Labelme ^
  --windowed ^
  --noconfirm ^
  --specpath=build ^
  --hidden-import=labelme ^
  --hidden-import=labelme.app ^
  --hidden-import=osam ^
  --hidden-import=onnxruntime ^
  --collect-all labelme ^
  --collect-all osam ^
  --collect-all onnxruntime ^
  --add-binary=%ONNX_PATH%\capi\*.dll;. ^
  --add-data=%OSAM_PATH%\_models\yoloworld\clip\bpe_simple_vocab_16e6.txt.gz;osam\_models\yoloworld\clip ^
  --add-data=%LABELME_PATH%;labelme ^
  --add-data=%LABELME_PATH%\config\default_config.yaml;labelme\config ^
  --add-data=%LABELME_PATH%\icons\*;labelme\icons ^
  --add-data=%LABELME_PATH%\translate\*;translate ^
  --icon=%LABELME_PATH%\icons\icon.png ^
  --onedir

call deactivate
endlocal
