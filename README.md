# Azure Speech to Text

Using this Framework from Azure https://learn.microsoft.com/en-gb/azure/cognitive-services/speech-service/how-to-use-conversation-transcription?pivots=programming-language-python

This main.py will extract the text from an audio file and update the
lyrics tag in the .mp3 file with the text read.

Use the config.ini for the configuration parameters.

To be installed:

- pip install azure-cognitiveservices-speech

- python3 -m pip install requests

- pip install eyeD3
- pip install configparser

- pip install pydub
- on macOs:
  - brew install ffmpeg
- on Ubuntu:
  - apt-get install ffmpeg


Then you need to setup ( create ) a new speech service within your Azure subscription:

https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/TextTranslation

Then edit your ~/.bash_profile:
export SPEECH_KEY=your-key
export SPEECH_REGION=your-region

Modify the config.ini in the main folder:
[SPEECH]
Language_from = pl

After you add the environment variables, run source ~/.bash_profile from your console window to make the changes effective.

Then running python3 main.py it will scan through the audiofiles folder for .mp3 files and for each of them it will extract the words 
in the language defined in config.ini and it will add the text to the .mp3 file as lyrics tag.

