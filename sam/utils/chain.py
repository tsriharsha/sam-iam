import abc
import platform

import pkg_resources

skip = ['.DS_Store', '__init__.py', '__pycache__']


class Chain(metaclass=abc.ABCMeta):

    def __init__(self, successor=None):
        self._successor = successor

    @abc.abstractmethod
    def handle_request(self):
        pass


class ChromeDriverChain(Chain):

    def __init__(self, system, path, successor=None):
        super().__init__(successor)
        self.path = path
        self.system = system

    def handle_request(self):
        this_system = platform.system()
        if self.system == this_system:  # if can_handle:
            try:
                print("Attempting to use driver in path " + self.path)
                from selenium import webdriver
                wd = webdriver.Chrome(self.path)
                wd.get("https://www.google.com")
                wd.close()
                return self.path
            except Exception as e:
                if self._successor is not None:
                    return self._successor.handle_request()
        elif self._successor is not None:
            return self._successor.handle_request()


def add_to_chain(prev, system, path):
    if prev is not None:
        return ChromeDriverChain(system, path, prev)
    else:
        return ChromeDriverChain(system, path)


def attempt_correct_drivers():
    from pkg_resources import resource_listdir

    CDC_list = []
    prev = None

    for dir in resource_listdir('sam.drivers', ''):
        if dir not in skip:
            driver_v_pkg = 'sam.drivers.{}'.format(dir)
            drivers = resource_listdir(driver_v_pkg, '')
            drivers.reverse()
            for driver in drivers:
                # print(pkg_resources.resource_filename(driver_v_pkg, driver))
                if driver not in skip:
                    full_driver_path = pkg_resources.resource_filename(driver_v_pkg, driver)
                    if full_driver_path.endswith(".exe"):
                        cdc = add_to_chain(prev, 'Windows', full_driver_path)
                        CDC_list.append(cdc)
                        prev = cdc
                    else:
                        cdc = add_to_chain(prev, 'Darwin', full_driver_path)
                        CDC_list.append(cdc)
                        prev = cdc

    return CDC_list[-1].handle_request()
