rem use "python -m site", to get your path variables.
set python_site_packages=C:\Users\YOUR_ACCOUNT_NAME\AppData\Local\Programs\Python\Python310\lib\site-packages

rd /S /Q dist\settings
rd /S /Q dist\settings_old
rd /S /Q dist\config_launcher
rd /S /Q dist\nodriver_tixcraft
rd /S /Q dist\chrome_tixcraft
rd /S /Q dist\
mkdir dist

@python -m PyInstaller settings.py --icon assets\icons\maxbot_logo2_settings.ico --hidden-import ddddocr --hidden-import=numpy --hidden-import onnxruntime --noconfirm --noupx

@python -m PyInstaller settings_old.py --icon assets\icons\maxbot_logo2_settings.ico --hidden-import ddddocr --hidden-import=numpy --hidden-import onnxruntime --noconfirm --noupx

@python -m PyInstaller config_launcher.py --icon assets\icons\maxbot_logo2_settings.ico --noconfirm --noupx

@python -m PyInstaller nodriver_tixcraft.py --icon assets\icons\maxbot_logo2_settings.ico --noconfirm --noupx

@python -m PyInstaller chrome_tixcraft.py --icon assets\icons\maxbot_logo2.ico --hidden-import undetected_chromedriver --hidden-import ddddocr --hidden-import onnxruntime --noconfirm --noupx

copy /Y settings.json dist\chrome_tixcraft
copy /Y config_launcher.json dist\chrome_tixcraft

mkdir dist\chrome_tixcraft\assets
mkdir dist\chrome_tixcraft\assets\icons
mkdir dist\chrome_tixcraft\assets\sounds

copy /Y assets\icons\*.gif dist\chrome_tixcraft\assets\icons
copy /Y assets\icons\*.ppm dist\chrome_tixcraft\assets\icons
copy /Y assets\sounds\*.wav dist\chrome_tixcraft\assets\sounds
copy /Y assets\sounds\*.mp3 dist\chrome_tixcraft\assets\sounds

mkdir dist\chrome_tixcraft\webdriver
copy /Y webdriver\*.crx dist\chrome_tixcraft\webdriver

xcopy /S /Y dist\settings\* dist\chrome_tixcraft
rd /S /Q dist\settings

xcopy /S /Y dist\settings_old\* dist\chrome_tixcraft
rd /S /Q dist\settings_old

xcopy /S /Y dist\config_launcher\* dist\chrome_tixcraft
rd /S /Q dist\config_launcher

xcopy /S /Y dist\nodriver_tixcraft\* dist\chrome_tixcraft
rd /S /Q dist\nodriver_tixcraft

rem if need support firefox.
copy webdriver\geckodriver.exe dist\chrome_tixcraft\webdriver

rd /S /Q dist\chrome_tixcraft\webdriver\Maxbotplus_1.0.0
mkdir dist\chrome_tixcraft\webdriver\Maxbotplus_1.0.0
xcopy /S /Y webdriver\Maxbotplus_1.0.0 dist\chrome_tixcraft\webdriver\Maxbotplus_1.0.0

rd /S /Q dist\chrome_tixcraft\webdriver\Maxblockplus_1.0.0
mkdir dist\chrome_tixcraft\webdriver\Maxblockplus_1.0.0
xcopy /Q /S /Y webdriver\Maxblockplus_1.0.0 dist\chrome_tixcraft\webdriver\Maxblockplus_1.0.0

xcopy /Y webdriver\*.crx dist\chrome_tixcraft\webdriver
mkdir dist\chrome_tixcraft\_internal\ddddocr

copy /Y %python_site_packages%\ddddocr\*.onnx dist\chrome_tixcraft\_internal\ddddocr

rd /S /Q dist\chrome_tixcraft\_internal\ddddocr\__pycache__
del /Q dist\chrome_tixcraft\_internal\ddddocr\*.py

mkdir dist\chrome_tixcraft\www
xcopy /Y/S  www\* dist\chrome_tixcraft\www

rd /S /Q build
rd /S /Q __pycache__
del *.spec