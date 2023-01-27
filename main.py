# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

# <code>
import eyed3
import time
from eyed3.id3.frames import ImageFrame
from io import BytesIO

import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import configparser
import urllib.request as urllib2
from logging import getLogger
from pydub import AudioSegment

from scipy.io.wavfile import read

# (in main)
# Suppress WARNINGS generated by eyed3
getLogger().setLevel('ERROR')

import azure.cognitiveservices.speech as speechsdk
import requests, uuid, json
from azure.cognitiveservices.speech import PropertyId



# edit your ~/.bash_profile:
# export SPEECH_KEY=your-speech-key
# export SPEECH_REGION=your-speech-region
speech_key = os.environ.get('SPEECH_KEY')
service_region = os.environ.get('SPEECH_REGION')

# speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
#                                        region=os.environ.get('SPEECH_REGION'))

# # Ask for detailed recognition result
# speech_config.output_format = speechsdk.OutputFormat.Detailed

subfolders = [ f.path for f in os.scandir(".") if f.is_dir() and  f.name.startswith('Audio_') ]

for subfolder in subfolders:
    # print(subfolder)
    onlyfiles = [f for f in sorted(listdir(subfolder)) if isfile(join(subfolder, f)) ]
    # print(onlyfiles)
    config_file = configparser.ConfigParser()
    # print(mp3_tags.sections())
    config_file.read(subfolder + "/" + "config.ini")
    # print(subfolder + "/" + "config.ini")
    # print(config_file.sections())

    mp3_tags_artist = config_file['MP3_TAGS']['Artist']
    mp3_tags_album = config_file['MP3_TAGS']['Album']
    mp3_tags_genre = config_file['MP3_TAGS']['Genre']
    mp3_image =config_file['MP3_TAGS']['Cover_Image']

    # print(mp3_tags_artist)

    for filename in onlyfiles:
        if Path(filename).suffix == ".mp3":
            # print ( " ")
            # print ( " Processing new file .... ")

            filename_with_path = subfolder + "/" + filename
            print(filename_with_path)
            sound = AudioSegment.from_mp3(filename_with_path)
            sound.export(subfolder + "/" + "temp.wav", format="wav")

            # <SpeechRecognitionWithFile>
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.set_property_by_name("ConversationTranscriptionInRoomAndOnline", "true")
            speech_config.set_property_by_name("DifferentiateGuestSpeakers", "true")
            speech_config.set_property(PropertyId.SpeechServiceConnection_ContinuousLanguageIdPriority,  "Latency")

            # Ask for detailed recognition result
            # speech_config.output_format = speechsdk.OutputFormat.Detailed

            audio_config = speechsdk.audio.AudioConfig(filename=subfolder + "/" + "temp.wav")
            # # Creates a speech recognizer using a file as audio input, also specify the speech language
            auto_detect_source_language_config =\
                      speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                      languages=[config_file['SPEECH']['Language1'],
                       config_file['SPEECH']['Language2']])

            speech_recognizer = speechsdk.SpeechRecognizer(
                 speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config, audio_config=audio_config)

            done = False
            def stop_cb(evt: speechsdk.SessionEventArgs):
                """callback that signals to stop continuous recognition upon receiving an event `evt`"""
                print('CLOSING on {}'.format(evt))
                global done
                done = True

            text_result = ""
            def compose_text_result(txt):
                global text_result
                text_result += txt
                # print(txt)

            # Connect callbacks to the events fired by the speech recognizer
            # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
            # speech_recognizer.recognized.connect(lambda evt: print(evt.result.text): text_result =  text_result + evt.result.text)
            speech_recognizer.recognized.connect(lambda evt: compose_text_result(  evt.result.text))

            # speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
            # speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
            # speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
            # stop continuous recognition on either session stopped or canceled events
            speech_recognizer.session_stopped.connect(stop_cb)
            speech_recognizer.canceled.connect(stop_cb)

            # Start continuous speech recognition
            speech_recognizer.start_continuous_recognition()
            while not done:
                time.sleep(.2)
            speech_recognizer.stop_continuous_recognition()
            text_result = text_result.replace(".", ".\n\n")
            # print(text_result)
            # </SpeechContinuousRecognitionWithFile>

            #
            print( "loading mp3 ... {}".format(filename_with_path))
            audio_file_eyed3            = eyed3.load(filename_with_path)
            audio_file_eyed3.initTag(version=(2, 4, 0))
            audio_file_eyed3.tag.artist = mp3_tags_artist
            audio_file_eyed3.tag.album  = mp3_tags_album
            # audio_file_eyed3.tag.title  = Path(filename).stem
            audio_file_eyed3.tag.genre  = mp3_tags_genre
            audio_file_eyed3.tag.lyrics.set(text_result )
            # FRONT_COVER = eyed3.id3.frames.ImageFrame.FRONT_COVER
            #
            audio_file_eyed3.tag.images.set(ImageFrame.FRONT_COVER, open(subfolder + "/" + mp3_image, 'rb').read(), 'image/jpeg')

            audio_file_eyed3.tag.save()
            os.remove(subfolder + "/" + "temp.wav")

# Checks result.
# if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#      print("Speech synthesized to speaker for text [{}]".format(text))
# elif result.reason == speechsdk.ResultReason.Canceled:
#      cancellation_details = result.cancellation_details
#      print("Speech synthesis canceled: {}".format(cancellation_details.reason))
#      if cancellation_details.reason == speechsdk.CancellationReason.Error:
#          if cancellation_details.error_details:
#              print("Error details: {}".format(cancellation_details.error_details))
#     print("Did you update the subscription info?")

