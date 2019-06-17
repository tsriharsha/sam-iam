import errno
import os
from configparser import ConfigParser
from functools import wraps

SECTION = 'default'
key_list = ['chrome_driver_path', "aws_sso_url"]


def load_config(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        with SAMIAMConfig(SECTION) as sic:
            os.environ['CHROME_DRIVER_LOC'] = sic.get(SECTION, key_list[0])
            os.environ['AWS_SSO_URL'] = sic.get(SECTION, key_list[1])
            r = f(*args, **kwargs)
            return r

    return wrapped


class TomlConfig(object):

    def __init__(self, sections, path, cp=None) -> None:
        super().__init__()
        self.path = path
        self.sections = sections
        self.changes = []
        if cp is None:
            self._cp = ConfigParser()
        else:
            self._cp = cp

    def _init_configparser(self):
        aws_credentials_file = os.path.expanduser(self.path)
        if os.path.exists(aws_credentials_file):
            self._cp.read(aws_credentials_file)
        else:
            try:
                os.makedirs(os.path.dirname(aws_credentials_file))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(aws_credentials_file, "w") as f:
                pass
            self._cp.read(aws_credentials_file)

    def _init_sections(self):
        if isinstance(self.sections, str):
            if self._cp.has_section(self.sections) is False:
                self._cp.add_section(self.sections)
        elif isinstance(self.sections, list):
            for section in self.sections:
                if self._cp.has_section(section) is False:
                    self._cp.add_section(section)

    def __append_change(self, section, key, value, action):
        change = {
            "section": section,
            "key": key,
            "value": value,
            "action": action

        }
        self.changes.append(change)

    def set(self, section, key, value):
        self.__append_change(section, key, value, "SET")
        self._cp.set(section, key, value)

    def get(self, section, key):
        return self._cp.get(section, key)

    @property
    def credentials_file(self):
        return os.path.expanduser(self.path)

    def _save(self):
        if len(self.changes) > 0:
            with open(self.credentials_file, 'w') as stream:
                self._cp.write(stream)

    def __enter__(self):
        self._init_configparser()
        self._init_sections()
        return self

    def __exit__(self, *args):
        self._save()


class AWSTomlConfig(TomlConfig):

    def __init__(self, sections, path="~/.aws/credentials", cp=None) -> None:
        super().__init__(sections, path, cp)


class SAMIAMConfig(TomlConfig):
    def __init__(self, sections, path="~/.samiam/config", cp=None) -> None:
        super().__init__(sections, path, cp)
