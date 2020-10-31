import datetime


class RingFile:

    def __init__(self, file_name: str, path: str):
        self.__name = file_name
        self.__path = path
        self.__size = 0
        self.__date_modify = datetime.datetime(1999, 1, 1)

    def set_date_modify(self, year: int, month: int, day: int, hour: int,
                        minute: int, second: int):
        self.__modify_date = datetime.datetime(year, month, day, hour,
                                               minute, second)

    def set_size(self, size: int):
        self.__size = size

    def get_modify_date(self) -> datetime.datetime:
        return self.__date_modify

    def get_size(self) -> int:
        return self.__size
