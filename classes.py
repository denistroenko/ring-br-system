import datetime


class RingFile:

    def __init__(self, file_name: str, path: str, size: int,
                 date_modify: datetime.datetime):
        self.__name = str(file_name)
        self.__path = str(path)
        self.__size = int(size)
        self.__date_modify = date_modify

    def __str__(self) -> str:
        return self.__name

    def get_file_name(self) -> str:
        return self.__name

    def get_path(self) -> str:
        return self.__path

    def get_date_modify(self) -> datetime.datetime:
        return self.__date_modify

    def get_size(self) -> int:
        return self.__size

    def delete_from_disk(self):
        print('Файл типа удален')


class Ring:

    def __init__(self):
        self.__files = []
        self.__total_files = 0
        self.__total_space = 0

    def __calculate(self):
        self.__total_files = len(self.__files)
        self.__total_space = 0
        for file in self.__files:
            self.__total_space += file.get_size()

    def sort(self):
        new_list = sorted(self.__files,
                          key=lambda file: file.get_date_modify())
        self.__files = new_list

    def append(self, file_object: object):
        self.__files.append(file_object)
        self.__calculate()

    def clear(self):
        self.__files = []

    def load(self, path: str):
        pass

    def cut_by_count(self, count: int) -> bool:
        ok = True
        while len(self.__files) > count:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)
        self.__calculate()
        return ok

    def cut_by_time(self, days: int) -> bool:
        ok = True
        return ok

    def cut_by_space(self, gigabytes: int) -> bool:
        ok = True
        return ok

    def get_files(self):
        return self.__files

    def get_total_space(self):
        self.__calculate()
        return self.__total_space

    def get_total_files(self):
        self.__calculate()
        return self.__total_files
