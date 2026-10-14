from lib.common import helpers

BANNER = r"""
=====================================================
   ______  _____  ____   _    _  ___   _____  _   _
  |  _   \|_   _|/ __ \ | |  | ||_  | |  __ \| | | |
  | |_)  |  | | | /  \ \| |__| |  | | | |__) | | | |
  |  _  <   | | | |  | ||  __  |  | | |  ___/| | | |
  | |_)  | _| |_| \__/ /| |  | | _| |_| |    | |_|
  |______/ |_____| \____/ |_|  |_|_____|_|     \___/

        YERLI VEIL FRAMEWORK  v{ver}
        MALWARE GENERATION SUITE
        github.com/memetcanwq31
=====================================================
"""

def title_screen():
    print(BANNER.format(ver=helpers.__dict__.get('VERSION', '1.0')))
