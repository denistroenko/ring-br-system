import datetime
import time
import os
import zipfile
from baseapplib import human_space


# ПЕРЕДЕЛАТЬ: clean & pep8
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

    def get_age(self):
        date_now = datetime.datetime.now()
        date_modify = self.__date_modify
        age = (date_now - date_modify).total_seconds()
        age = round(age / 60 / 60 / 24)
        return age

    def get_zip_info(self):
        pass

    def zip_content(self):
        try:
            zip_file = zipfile.ZipFile(self.__full_path, 'r')
        except zipfile.BadZipfile:
            return False, 'Ошибка чтения содержимого файла!'

        name_list = zip_file.namelist()

        files_count = 0
        files_size = 0
        files_compress_size = 0
        # Create new list with out folders
        names = []
        for line in name_list:
            if len(line) > 0 and line[-1] != '/':
                names.append(line)
                files_count += 1
                info = zip_file.getinfo(line)
                files_size += info.file_size
                files_compress_size += info.compress_size

        result = ''
        if names != None:
            for name in names:
                result += name + '\n'
            result += '-' * 55 + '\n'
            result += '\33[35mИТОГО:\33[37m Файлов в архиве - '
            result += str(files_count) + ' | '
            result += human_space(files_size)
            result += ' >>> '
            result += human_space(files_compress_size) + ' '
            if files_size > 0:
                result += '\33[32m'
                result += str(int(files_compress_size / files_size * 100))
                result += '%' + '\33[37m'

            return True, result
        else:
            return False, result

    def zip_test(self):
        try:
            zip_file = zipfile.ZipFile(self.__full_path, 'r')
        except zipfile.BadZipfile:
            return False, 'Это не zip-файл!'

        result = zip_file.testzip()

        if result == None:
            return True, '\33[32mок!\33[37mТест успешно пройден.'
        else:
            return False, result

    def delete_from_disk(self):
        os.remove(self.__full_path)
        print('Файл удален:', self.__name)


# ПЕРЕДЕЛАТЬ: clean & pep8
class Ring:

    def __init__(self, path: str = '', prefix: str = '',
                 show_excluded: bool = True):
        self.__path = path
        self.__files_prefix = prefix
        self.__show_excluded = show_excluded
        self.__files = []
        self.__total_files = 0
        self.__total_space = 0

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
        self.__path = path
        self.__files_prefix = prefix
        self.__show_excluded = show_excluded

        all_files_list = os.listdir(self.__path)
        excluded_files_count = 0
        excluded_files_size = 0
        for file_name in all_files_list:
            # Получаем объем файла средствами ОС
            full_path = self.__path + file_name
            size = os.path.getsize(full_path)
            if file_name[0:len(self.__files_prefix)] == self.__files_prefix \
                    and os.path.isfile(full_path):
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
            print('Файлы в папке, но не соответствуют префиксу:')
            print('Количество:', excluded_files_count, end='; ')
            print('Общий объем:', excluded_files_size)
            print('Они исключены из работы.')

    def cut_by_count(self, count: int) -> bool:
        ok = True
        while len(self.__files) > count:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)
            self.__calculate()
        return ok

    def cut_by_age(self, max_age: int) -> bool:
        ok = True

        while len(self.__files) > 0 and \
                self.__files[0].get_age() > max_age:
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

    def kill(self, file_index: int):
        killing_file = self.__files[file_index]

        print('Удаляется', killing_file.get_full_path())
        killing_file.delete_from_disk()
        self.__files.pop(file_index)
        self.__calculate()

    def get_files(self) -> list:
        return self.__files

    def get_total_space(self) -> int:
        return self.__total_space

    def get_total_files(self):
        return self.__total_files

    def new_archive(self, zip_file_name: str, source_dir: str, objects: dict,
                    deflated: bool = True, compression_level: int = None,
                    only_today_files: bool = False,
                    exclude_file_names: list = []):
        ok = True
        zip_compression = zipfile.ZIP_STORED
        if deflated:
            zip_compression = zipfile.ZIP_DEFLATED
        full_path = '{}{}'.format(self.__path, zip_file_name)

        with zipfile.ZipFile(
                full_path, mode='w',
                compression = zip_compression,
                allowZip64=True,
                compresslevel = compression_level) as zip_file:
            total_file_sizes = 0
            total_file_compress_sizes = 0
            total_files = 0

            print('Создаю:', full_path)
            for folder in objects:
                print('\33[35m', folder, '\33[37m', sep = '')
                for file in objects[folder]:
                    file_name = str(file.split('/')[-1])

                    if file_name == '':
                        continue

                    file_print = file[-50:]
                    if file_print != file:
                        file_print = '[..]{}'.format(file_print)
                    else:
                        file_print += f'{" " * (54 - len(file_print))}'
                    print('+ {}'.format(file_print), end = ' ',
                          flush=True)

                    # Имя файла внутри zip-архива такое:
                    if file[:len(source_dir)] == source_dir:
                        arcname = folder + file[len(source_dir)-1:]
                    else:
                        arcname = folder + '/absolute_path/'+ file
                    # Исключение двойной косой //
                    arcname = arcname.replace('//', '/')

                    # Если только сегодняшние, то проверить дату. Если все
                    # подряд - просто добавть файл, не проверяя дату
                    if only_today_files:
                        date_now = '{:04d}-{:02d}-{:02d}'.format(
                            datetime.datetime.now().year,
                            datetime.datetime.now().month,
                            datetime.datetime.now().day)
                        # Получаем дату изм. файла средствами ОС
                        date_modify = os.path.getmtime(file)
                        # Преобразуем в локальное время (будет строка)
                        date_modify = time.ctime(date_modify)
                        # Преобразуем в datetime.datetime
                        date_modify = datetime.datetime.strptime(
                                date_modify, "%a %b %d %H:%M:%S %Y")
                        date_modify = str(date_modify)[:10]
                        if date_now == date_modify:
                            if file_name in exclude_file_names:
                                print(' ИСКЛЮЧЕН!')
                                continue
                            else:
                                try:
                                    zip_file.write(file, arcname)
                                except FileNotFoundError:
                                    print('Файл не найден: ', file)
                        else:
                            print(' НЕСВЕЖИЙ!')
                            continue
                    else:
                        if file_name in exclude_file_names:
                            print(' ИСКЛЮЧЕН!')
                            continue
                        else:
                            try:
                                zip_file.write(file, arcname)
                            except FileNotFoundError:
                                print('Файл не найден: ', file)

                    compress_size = (
                            zip_file.infolist()[-1].compress_size)
                    total_file_compress_sizes += compress_size
                    file_size = (
                        zip_file.infolist()[-1].file_size)
                    total_file_sizes += file_size

                    if file_size > 0:
                        file_compression = '\33[32m{:3d}%\33[37m '.format(
                            int(compress_size / file_size * 100))

                    if file_size != 0:
                        print(file_compression, human_space(file_size),
                              ' >>> ', human_space(compress_size),
                              sep = '')
                    else:
                        print('\33[32m   =\33[37m')
                    # Прибавить к счетчику файлов, если это файл, а не папка
                    if os.path.isfile(file):
                        total_files += 1

        if total_file_sizes > 0:
            total_file_compression = '\33[32m{}%\33[37m'.format(
                int(total_file_compress_sizes / total_file_sizes * 100))
        else:
            total_file_compression = ' '
        print('-' * 56)
        print('\33[35mИТОГО\33[37m:',
              total_file_compression,
              human_space(total_file_sizes), '>>>',
              human_space(total_file_compress_sizes),
              f'\33[37m({total_files} файлов)\33[37m', sep=' ', end = '\n')

        if total_file_sizes > 0:
            total_file_compression_result = \
                str(int(total_file_compress_sizes /
                        total_file_sizes * 100)) + '%, '

            result = f'Добавлен:\n{zip_file_name}\n' +\
                total_file_compression_result +\
                f'{human_space(total_file_sizes)} >>> ' +\
                f'{human_space(total_file_compress_sizes)}, ' +\
                f'{total_files} файлов\n'
        else:
            total_file_compression_result = ''
            ok = False

            os.remove(full_path)
            print('Пустой архив. Удален!')

            result = ''
        return ok, result

    def get_content(self, file_index: int = -1):
        ok = True

        try:
            file = self.__files[file_index]
        except IndexError:
           ok = False
           result = 'Нет файла с номером {}!'.format(file_index)
           return ok, result

        full_path = file.get_full_path()

        print('Читаю файл {} ...'.format(full_path))
        result = file.zip_content()[1]
        return ok, result

    def test_archive(self, file_index: int = -1):
        ok = True

        try:
            file = self.__files[file_index]
        except IndexError:
            ok = False
            result = 'Нет файла с номером {}!'.format(file_index)
            return ok, result

        full_path = file.get_full_path()

        print('Тестирую файл {} ...'.format(full_path))
        ok, result = file.zip_test()
        return ok, result
