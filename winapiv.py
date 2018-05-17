"""
A tool to run a browser-based pseudo-screensaver in windows. 

Motivation.
There exist screen-savers that run a webpage, but are fairly inconsisent across Windows versions and configurations, group policies etc.
Automating a version with python and selenium for firefox allows:
1) using an existing browser profile (cookies etc)
2) No dependencies on windows Version and settings (screen-saver)
3) Serving from a static html file. 
4) Logging
5) Supports multiple monitors, with screensaver starting on a delay

created by Pavel Savine 5/14/2017
"""
import win32api
import webbrowser
import os, time, argparse, logging, json
from selenium import webdriver
from screeninfo import get_monitors
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
from selenium.webdriver.remote.remote_connection import LOGGER

from taskbar import hide_taskbar, unhide_taskbar 


# url = 'http://192.168.60.145:8000/jobcams.html'
mozilla = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
gecko = './deps/geckodriver.exe'


def init_logging(path):
    if path == '':
        path = os.getenv('LOCALAPPDATA') + '\\jobcams\\'
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = path + 'jobcam.log'
    if os.path.exists(file_path):
        os.remove(file_path)
    logging.basicConfig(filename=file_path, 
                        level=logging.DEBUG, 
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('starting jobcam screensaver at {}'.format(file_path))


def open_ff_browser(_url, n):
    options = webdriver.FirefoxOptions()
    binary = FirefoxBinary(gecko)
    fp = webdriver.FirefoxProfile()
    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    firefox_capabilities['binary'] = gecko
    driver = webdriver.Firefox(capabilities=firefox_capabilities)
    driver.set_window_position(n, 0)
    driver.fullscreen_window()
    driver.get(_url)
    return driver


def close_browsers(_browsers):
    unhide_taskbar()
    if _browsers is not None:
        logging.info('browsers closing')
        for b in _browsers:
            b.close()
            _browsers = None
        logging.info('browsers closed')
    return _browsers


def make_browsers(_url, delay, init_state):
    browsers = []
    hide_taskbar()
    for m in get_monitors():
        logging.info('launching : ' + str(m))
        browsers.append(open_ff_browser(_url, m.x))
        t = 0
        while t <= delay:
            time.sleep(1)
            t += 1
            state = str(win32api.GetLastInputInfo())
            if state != init_state:
                logging.info('browsers closed before opening completetly delay {} -> {}'.format(init_state, state))
                return close_browsers(browsers), state
    logging.info('detected {} monitors, and created browsers'.format(len(browsers)))
    return browsers, init_state


def sleep_timer(_url, time_out, delay):
    timer, last_state, browsers = 0, '', None
    while True:
        try:
            state = str(win32api.GetLastInputInfo())
            if state != last_state: 
                browsers = close_browsers(browsers)
                last_state = state
                timer = 0
            else: 
                timer +=  1 
            if timer > time_out and browsers is None:
                browsers, last_state = make_browsers(_url, delay, last_state)
            time.sleep(1)
        except Exception:
            logging.info('exception')
            browsers = close_browsers(browsers)


def parse_config(args):
    def parse_cfg(args, cfgs, k, d=''):
        return arg.get(k) if arg.get(k, d) != d else cfgs.get(k)

    with open(args.cfg_folder + '/config.json') as f:
        data = json.load(f)

    cfg = data.get(args.act, None)
    if cfg is None:
        print('config file not found')
        return args.url, abs(args.time_out  * 60), args.delay, ''

    arg = vars(args)
    url = parse_cfg(arg, cfg, 'url', '')
    delay = parse_cfg(arg, cfg, 'delay', -1)
    logdir = parse_cfg(arg, cfg, 'logdir', '')
    timeout = parse_cfg(arg, cfg, 'timeout', -1)
    return url, timeout * 60, delay, logdir


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='browser screensaver')
    parser.add_argument('-a', '--act', type=str, default='run')
    parser.add_argument('-f', '--cfg_folder', type=str, default='prod')
    parser.add_argument('-t', '--timeout', type=int, default=-1, help='how long to wait before starting screensaver')
    parser.add_argument('-d', '--delay', type=int, default=-1, help='If there are multiple screens, how long to wait between starting each one')
    parser.add_argument('-l', '--logdir', type=str, default='', help='location to log to')
    parser.add_argument('-u', '--url', type=str, default='', help='webpage url')
    
    args = parser.parse_args()
    LOGGER.setLevel(logging.WARNING)
    
    url, timeout, delay, logdir = parse_config(args)
    init_logging(logdir)
    sleep_timer(url, timeout, delay)



