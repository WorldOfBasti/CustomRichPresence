from .en import en
from .de import de
import platform
if platform.system() == "Darwin":
    from Foundation import NSLocale
else:
    import locale


class AppResourceManager(object):
    # Save language code
    def __init__(self):
        if platform.system() == "Darwin":
            self.current_language = list(NSLocale.preferredLanguages())[0][:-3].lower()
        else:
            self.current_language = locale.getdefaultlocale()[0][:-3].lower()

        self.check_availability()

    # Return text in right language
    def get_string(self, text):
        return globals()[self.current_language].get(text)

    # Check if language is available, otherwise use english
    def check_availability(self):
        if self.current_language != "en" and self.current_language != "de":
            self.current_language = "en"
