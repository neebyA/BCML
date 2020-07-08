# pylint: skip-file
import logging
import os
import platform

from webviewb.util import WebViewException

logger = logging.getLogger("pywebview")
guilib = None
forced_gui_ = None


def initialize(forced_gui=None):
    def import_gtk():
        global guilib

        try:
            import webviewb.platforms.gtk as guilib

            logger.debug("Using GTK")

            return True
        except (ImportError, ValueError) as e:
            logger.exception("GTK cannot be loaded")

            return False

    def import_qt():
        global guilib

        try:
            import webviewb.platforms.qt as guilib

            return True
        except ImportError as e:
            logger.exception("QT cannot be loaded")
            return False

    def import_winforms():
        global guilib

        try:
            import webviewb.platforms.winforms as guilib

            return True
        except ImportError as e:
            logger.exception("pythonnet cannot be loaded")
            return False

    def try_import(guis):
        while guis:
            import_func = guis.pop(0)

            if import_func():
                return True

        return False

    global forced_gui_

    if not forced_gui:
        forced_gui = "qt" if "KDE_FULL_SESSION" in os.environ else None
        forced_gui = (
            os.environ["PYWEBVIEW_GUI"].lower()
            if "PYWEBVIEW_GUI" in os.environ
            and os.environ["PYWEBVIEW_GUI"].lower() in ["qt", "gtk", "cef"]
            else None
        )

    forced_gui_ = forced_gui

    if platform.system() == "Linux" or platform.system() == "OpenBSD":
        if forced_gui == "qt":
            guis = [import_qt, import_gtk]
        else:
            guis = [import_gtk, import_qt]

        if not try_import(guis):
            raise WebViewException(
                "You must have either QT or GTK with Python extensions installed in order to use pywebview."
            )

    elif platform.system() == "Windows":
        guis = [import_winforms]

        if not try_import(guis):
            raise WebViewException(
                "You must have pythonnet installed in order to use pywebview."
            )
    else:
        raise WebViewException(
            "Unsupported platform. Only Windows, Linux, OpenBSD are supported."
        )

    return guilib
