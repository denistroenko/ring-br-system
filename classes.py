import datetime
import os
import time
from baseapplib import human_space
import zipfile


class RingFile:

    def __init__(self, file_name: str, full_path: str, size: int,
                 date_modify: datetime.datetime):
        self.__name: str = str(file_name)
        self.__full_path: str = str(full_path)
        self.__size: int = int(size)
        self.__date_modify = date_modify

    def __str__(self) -> str:
        return self.__name

    def get_file_name(self) -> str:
        return self.__name

    def get_full_path(self) -> str:
        return self.__full_path

    def get_date_modify(self):
        return self.__date_modify

    def get_size(self) -> int:
        return self.__size

    def get_shelf_life(self):
        date_now = datetime.datetime.now()
        date_modify = self.__date_modify
        shelf_life = (date_now - date_modify).total_seconds()
        shelf_life = round(shelf_life / 60 / 60 / 24)
        return shelf_life

    def get_zip_info(self):
        pass

    def get_zip_content(self):
        zip_file = zipfile.ZipFile(self.__full_path, 'r')
        names = zip_file.namelist()
        result = ''
        for name in names:
            result += name + '\n'
        return result

    def test(self):
        try:
            zip_file = zipfile.ZipFile(self.__full_path, 'r')
        except zipfile.BadZipfile:
            return False, 'Это не zip-файл!'
        result = zip_file.testzip()
        if result == None:
            return True, 'Тест успешно пройден.'
        else:
            return False, result

    def delete_from_disk(self):
        os.remove(self.__full_path)
        print('Файл удален:', self.__name)


class Ring:

    def __init__(self):
        self.__files: list = []
        self.__total_files: int = 0
        self.__total_space: int = 0

    def __calculate(self):
        self.__total_files = int(len(self.__files))
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
        self.__calculate()

    def load(self, path: str, prefix: str, show_excluded: bool = True):
        all_files_list = os.listdir(path)
        excluded_files_count = 0
        excluded_files_size = 0
        for file_name in all_files_list:
            # Получаем объем файла средствами ОС
            full_path = path + file_name
            size = os.path.getsize(full_path)
            if file_name[0:len(prefix)] == prefix:
                # Получаем дату изм. файла средствами ОС
                date_modify = os.path.getmtime(full_path)
                # Преобразуем в локальное время (будет строка)
                date_modify = time.ctime(date_modify)
                # Преобразуем в datetime.datetime
                date_modify = datetime.datetime.strptime(
                        date_modify, "%a %b %d %H:%M:%S %Y")
                file = RingFile(file_name, full_path, size, date_modify)
                self.append(file)
            else:
                if show_excluded:
                    print('Исключен файл:', file_name)
                excluded_files_count += 1
                excluded_files_size += size
        if excluded_files_count > 0:
            excluded_files_size = human_space(excluded_files_size)
            print('Файлы существуют в папке, но не соответствуют префиксу:')
            print('Количество:', excluded_files_count)
            print('Общий объем:', excluded_files_size)
            print('Они исключены из работы.')

    def cut_by_count(self, count: int) -> bool:
        ok = True
        while len(self.__files) > count:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)
        self.__calculate()
        return ok

    def cut_by_time(self, max_shelf_life: int) -> bool:
        ok = True

        while len(self.__files) > 0 and \
                self.__files[0].get_shelf_life() > max_shelf_life:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)
        self.__calculate()
        return ok

    def cut_by_space(self, gigabytes: int) -> bool:
        ok = True
        while self.__total_space > gigabytes * 1024**3:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)
        self.__calculate()
        return ok

    def get_files(self) -> list:
        return self.__files

    def get_total_space(self) -> int:
        return self.__total_space

    def get_total_files(self):
        self.__calculate()
        return self.__total_files
