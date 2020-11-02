import datetime


class RingFile:

    def __init__(self, file_name: str, path: str):
        self.__name = file_name
        self.__path = path
        self.__size = 0
        self.__date_modify = datetime.datetime(1999, 1, 1)

    def __str__(self):
        return self.__date_modify

    def set_date_modify(self, year: int, month: int, day: int, hour: int,
                        minute: int, second: int):
        self.__date_modify = datetime.datetime(year, month, day, hour,
                                               minute, second)

    def set_size(self, size: int):
        self.__size = size

    def get_date_modify(self) -> datetime.datetime:
        return self.__date_modify

    def get_date_modify_one_string(self) -> str:
        result = ''
        result += '{:04d}'.format(self.__date_modify.year)
        result += '{:02d}'.format(self.__date_modify.month)
        result += '{:02d}'.format(self.__date_modify.day)
        result += '{:02d}'.format(self.__date_modify.hour)
        result += '{:02d}'.format(self.__date_modify.minute)
        result += '{:02d}'.format(self.__date_modify.second)
        return result

    def get_size(self) -> int:
        return self.__size

    def delete_from_disk(self):
        print('Файл типа удален')

class Ring:
    def __init__(self):
        self.files = []

    def sort(self):
        new_list = sorted(self.files, key=lambda file: file.get_date_modify())
        self.files= new_list

    def append(self, file_object: object):
        self.files.append(file_object)

    def clear(self):
        self.files = []

    def load(self, path: str):
        pass

    def cut_count(self, count: int) -> bool:
        ok = True
        while len(self.files) > count:
            self.files[0].delete_from_disk()
            self.files.pop(0)
        return ok

    def cut_time(self, days: int) -> bool:
        ok = True
        return ok

    def cut_space(self, gigabytes: int) -> bool:
        ok = True
        return ok
