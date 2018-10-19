import json
import os


class Translation(object):
    def __init__(self, default_lang='de'):
        self.__langs = {}
        self.__default_lang = default_lang

        # loading translations
        path = os.path.dirname(os.path.abspath(__file__))
        lang_files = {
            'de': path + '/../assets/translations/de.json',
            'en': path + '/../assets/translations/en.json'
        }
        for key, file in lang_files.iteritems():
            with open(file) as data_file:
                self.__langs[key] = json.load(data_file)

    def tl(self, msg, lang=None):
        language = self.__default_lang if lang is None else lang
        if len(self.__langs[language]) == 0:
            return msg

        assert language in self.__langs
        result = msg
        if msg in self.__langs[language]:
            unic = unicode(self.__langs[language][msg])
            result = unic.encode('utf-8')
        else:
            # todo use logging_base for the following debug output
            print "Translation: \'{}\' not found! Please add message to json file.".format(msg)
        return result


T = Translation()
