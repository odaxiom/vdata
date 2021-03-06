import os
import glob
import pickle
import shutil


PATH = '.vdata'


class Data:
    extension = 'vdata'

    def __init__(self, name: str, namespace: str):
        self.name = name
        self.namespace = namespace

        self._reload()

    def _reload(self):
        self.file_path = os.path.join(PATH, self.namespace, self.name)

        self.max_version = self.get_max_version()
        self.file_path_version = self._get_file_path_version(self.max_version)

        self.current_file_path = self._current_file_path()

        if self.current_file_path:
            self.extension = self.current_file_path.split('.')[-1]

    def get(self, revision='latest'):
        if revision == 'latest':
            version = self.get_max_version()
        else:
            version = revision

        file_path = self._get_file_path_version(version)

        if self.extension != 'vdata':
            return file_path

        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def update(self, data=None, file_path=None):
        version = self.max_version + 1
        file_path_version = self._get_file_path_version(version)

        os.makedirs('/'.join(file_path_version.split('/')[0:-1]), exist_ok=True)

        if file_path is None:
            with open(file_path_version, 'wb') as f:
                pickle.dump(data, f)
        else:
            self.extension = file_path.split('.')[-1]
            shutil.copy(file_path, self._get_file_path_version(version))

        with open(self._get_head_path(), 'wb') as f:
            pickle.dump(version, f)

        self._reload()

    def _get_file_path_version(self, version: int):
        return os.path.join(PATH, self.namespace, self.name + f'.{version}' + f'.{self.extension}')

    def _get_head_path(self):
        return os.path.join(PATH, self.namespace, self.name + '.head')

    def _current_file_path(self):
        version = self.get_max_version()
        if version != -1:
            path = self._get_file_path_version(version)
            if not os.path.isfile(path):
                files = glob.glob(os.path.join(self.file_path + f'.{version}.*'))
                return files[0]
            return path
        return None

    def get_max_version(self):
        if not os.path.isfile(self._get_head_path()):
            return -1

        with open(self._get_head_path(), 'rb') as f:
            return pickle.load(f)

    def get_versions(self):
        files = glob.glob(os.path.join(self.file_path + '.*'))
        files = [file for file in files if not file.endswith('.head')]
        versions = sorted([int(file.split('.')[-2]) for file in files])
        return versions
