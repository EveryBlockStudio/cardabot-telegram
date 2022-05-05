"""Manage HTML bot replies."""
import os


class HTMLReplies:
    supported_languages = (
        "EN",  # english
        "PT",  # portuguese/brazil
        "KR",  # korean
        "JP",  # japanese
    )

    def __init__(self) -> None:
        self.language = self.default_lang

    @property
    def default_lang(self) -> str:
        """Return default language."""
        return "EN"

    def set_language(self, lang: str) -> bool:
        """Set preferred language.

        Returns True if the change was successful; otherwise, return False if the
        language is not supported and make no changes to language settings.

        """
        if lang.upper() in self.supported_languages:
            self.language = lang.upper()
            return True

        return False

    def reply(self, html_file: str, **kwargs):
        """Return HTML reply in the selected language.

        In case a specific reply is not available in the chosen language, return a reply
        using the default language.

        Args:
            html_file: html template file for the desired reply
            **kwargs: extra variables to be replaced inside the template

        Returns:
            A string containing the formatted html response.

        """
        path = f"templates/{self.language}/{html_file}"

        # return html in default language in case there's no html template available
        # for the currently selected language
        if not os.path.exists(path):
            path = f"templates/{self.default_lang}/{html_file}"

        with open(path, encoding="utf-8") as f:
            html = f.read().format(**kwargs).rstrip("\n")
        return html
