# Zoom Bot (join.py is the main file)

## This is a simple zoom bot to get into your zoom classes online

### The biggest thing here is the captcha bypassing

- unittest library for running and error handeling
- [Bmi speech recognition](https://speech-to-text-demo.ng.bluemix.net/) to bypass recaptcha
- and of B-spline for simulate human mouse movements.

## Install firefox if you haven't already to run the program
### I used Firefox as my webdriver to create this bot that gets into my zoom class
### It won't run if you don't have Firefox, or you can edit my code to run it via Chrome, then you need a chromedriver
### to install it run the commmand:
```
brew install --cask chromedriver
```

## run it
```
cd /path/to/repository/
pip install -r requirements.txt
```
then
```
python3 join.py
```
### or make it an executable
```
chmod u+x join.py
./join.py
```
