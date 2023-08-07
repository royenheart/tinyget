from abc import ABCMeta, abstractclassmethod


class PackageManagerBase(metaclass=ABCMeta):
    @abstractclassmethod
    def get_packages(self):
        pass
