import datetime
import time
import os
import sys
import zipfile
from baseapplib import human_space, Console


# Global
console = Console()


class RingFile:
    def __init__(self, file_name: str, full_path: str, size: int,
                 date_modify: datetime.datetime):
        self.__name = str(file_name)
        self.__full_path = str(full_path)
        self.__size = int(size)
        self.__date_modify = date_modify

    def __str__(self) -> str:
        """
        Возвращает имя файла
        """
        return self.__name

    def get_file_name(self) -> str:
        """
        Возвращает имя файла
        """
        return self.__name

    def get_full_path(self) -> str:
        """
        Возвращает полный путь к файлу
        """
        return self.__full_path

    def get_date_modify(self) -> datetime.datetime:
        """
        Возвращает дату изменения файла
        """
        return self.__date_modify

    def get_size(self) -> int:
        """
        Возвращает размер файла
        """
        return self.__size

    def get_age(self) -> int:
        """
        Возвращает "возраст" файла в днях с округлением
        """
        date_now = datetime.datetime.now()
        date_modify = self.__date_modify

        age_seconds = (date_now - date_modify).total_seconds()
        age = round(age_seconds / 60 / 60 / 24)

        return age

    def get_content(self) -> (bool, str):
        """
        Возвращает содержимое архива и итог по числу файлов и объему
        """
        try:
            zip_file = zipfile.ZipFile(self.__full_path, 'r')
        except zipfile.BadZipfile:
            return False, 'Ошибка формата zip-файла!'

        # Name List of files inside archive
        name_list = zip_file.namelist()

        # Counters
        files_count = 0
        files_size = 0
        files_compress_size = 0

        # Create new Name List (w/o folders)
        names = []

        for line in name_list:
            # if it is file
            if len(line) > 0 and line[-1] != '/':
                # append line to Name List
                names.append(line)

                # + files counter
                files_count += 1

                # get zip-info about curent file (line)
                info = zip_file.getinfo(line)

                # + total files size counter
                files_size += info.file_size

                # + total files compress counter
                files_compress_size += info.compress_size

        # init result
        result = ''

        # creating result
        if names == None:
            return False, result

        for name in names:
            result += name + '\n'

        # for draw line
        result += '-' * 55 + '\n'

        # for total files count
        result += '\33[35mИТОГО:\33[37m Файлов в архиве - '
        result += str(files_count) + ' | '

        # for total size
        result += human_space(files_size)
        result += ' >>> '
        result += human_space(files_compress_size) + ' '

        # for compress percents
        if files_size > 0:
            result += '\33[32m'
            result += str(int(files_compress_size / files_size * 100))
            result += '%' + '\33[37m'

        return True, result

    def zip_test(self) -> (bool, str):
        """
        Возвращает результат тестирования архива
        """
        ok = True

        try:
            zip_file = zipfile.ZipFile(self.__full_path, 'r')
        except zipfile.BadZipfile:
            ok = False
            result = 'Это не zip-файл!'
            return ok, result

        result = zip_file.testzip()

        if result == None:
            result = '\33[32mок!\33[37mТест успешно пройден.'
        else:
            ok = False

        return ok, result

    def delete_from_disk(self) -> (bool, str):
        """
        Удаляет файл с диска средствами ОС,
        пишет об этом сообщение в консоль
        """
        try:
            os.remove(self.__full_path)
            print('Файл удален: {}'.format(self.__name))
        except Exception:
            console.print('Ошибка при удалении файла {}'.format(self.__name),
                          color='red',
                          )


class Ring:
    """
    Кольцо архивов резервных копий. Содержит файлы (объекты)
    """

    def __init__(self):
        self.__total_files = 0
        self.__total_space = 0
        self.__files = []

    def __calculate(self):
        """
        Подсчитывает и присваевает атрибутам __total_files и __total_space
        количество файлов в ring и их совокупный объем
        """
        self.__total_files = int(len(self.__files))
        self.__total_space = 0
        for file in self.__files:
            self.__total_space += file.get_size()

    def sort(self):
        """
        Сортирует по дате модификации список файлов в атрибуте __files
        """
        new_list = sorted(self.__files,
                          key=lambda file: file.get_date_modify())

        self.__files = new_list

    def __append(self, file_object: object):
        """
        Присоединяет файл к списку (атрибуту __files)
        """
        self.__files.append(file_object)
        self.__calculate()

    def clear(self):
        """
        Полностью очищает список файлов
        """
        self.__files = []
        self.__calculate()

    def load(self, path: str, prefix: str, show_excluded: bool=True):
        """
        Загружает список файлов в атрибут __files и информацию о них
        непосредственно из указанной папки.
        """
        self.__path = path            # Full path to ring dir
        self.__files_prefix = prefix  # Name file prefix for include. '' - all
        self.__show_excluded = show_excluded  # show excluded files (if the
                                              # files doesn't match the prefix)
        # Get file list from OS
        all_files_list = os.listdir(self.__path)

        # init
        excluded_files_count = 0
        excluded_files_size = 0

        for file_name in all_files_list:
            full_path = self.__path + file_name

            # Получаем объем файла средствами ОС
            size = os.path.getsize(full_path)

            # Если файл соотв. префиксу и это файл, а не папка
            if file_name[:len(self.__files_prefix)] == self.__files_prefix \
                    and os.path.isfile(full_path):

                # Получаем дату изм. файла средствами ОС
                date_modify = os.path.getmtime(full_path)

                # Преобразуем в локальное время (будет строка)
                date_modify = time.ctime(date_modify)

                # Преобразуем в datetime.datetime
                date_modify = datetime.datetime.strptime(
                        date_modify, "%a %b %d %H:%M:%S %Y")

                # Создать объект RingFile
                file = RingFile(file_name=file_name,
                                full_path=full_path,
                                size=size,
                                date_modify=date_modify)

                # Присоединить файл (вызывается метод)
                self.__append(file)

                continue

            # Иначе показать, что файл исключен, если show_excluded
            if show_excluded:
                print('Исключен по префиксу:', file_name)

            # excluded files count and size counters
            excluded_files_count += 1
            excluded_files_size += size

        # Show excluded files info
        if excluded_files_count > 0:
            excluded_files_size = human_space(excluded_files_size)
            print('Исключенные по префиксу файлы в папке:')
            print('Количество:', excluded_files_count, end='; ')
            print('Общий объем:', excluded_files_size)

        self.__calculate()

    def cut_by_count(self, count: int):
        """
        Обрезает кольцо архивов в ring-папке по количеству файлов
        (лишние файлы удаляются физически с диска от старых к новым)
        """
        while len(self.__files) > count:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)

        self.__calculate()

    def cut_by_age(self, max_age: int):
        """
        Обрезает кольцо архивов в ring-папке по возрасту файлов
        (файлы, старше указанного возраста в днях,
        удаляются физически с диска)
        """
        while len(self.__files) > 0 and \
                self.__files[0].get_age() > max_age:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)

        self.__calculate()

    def cut_by_space(self, gigabytes: int):
        """
        Обрезает кольцо архивов в ring-папке по объему
        (файлы удаляются физически с диска до тех пор, пока их совокупный
        объем не будет меньше или равен переданному)
        """
        while self.__total_space > gigabytes * 1024**3:
            self.__files[0].delete_from_disk()
            self.__files.pop(0)
            self.__calculate()

    def kill(self, file_index: int):
        """
        Физически удаляет файл с диска (с указанным индексом)
        """
        killing_file = self.__files[file_index]

        print('Удаляется', killing_file.get_full_path())

        killing_file.delete_from_disk()

    def get_files(self) -> [object, ...]:
        """
        Возвращает список объектов RingFile
        """
        return self.__files

    def get_total_space(self) -> int:
        """
        Возвращает текущий совокупный объем файлов в ring-папке
        """
        return self.__total_space

    def get_total_files(self):
        """
        Возвращает количество файлов в ring-папке
        """
        return self.__total_files

    def new_archive(
            self,
            zip_file_name: str,        # Имя создаваемого архива
            source_dir_name: str,      # Имя папки-источника
            deflated: bool,            # флаг deflated - "сжатый"
            compression_level: int,    # степень сжатия
            only_today_files: bool,    # только сегодняшние файлы
            exclude_file_names: list,  # имена файлов-исключений
                                       # (не включаются в архив)
            objects: dict,  # словарь, заполненный сл. обр.:
                            # {'имя папки в архиве':
                            #  ['полный путь к файлу1',
                            #   'полный путь к файлу2',
                            #   ...
                            #  ],
                            #
                            #  ...
                            # }
            ):
        """
        СОЗДАЕТ АРХИВ И СКЛАДЫВАЕТ ЕГО В ring-ПАПКУ
        """
        ok = True

        zip_compression = zipfile.ZIP_STORED
        if deflated:
            zip_compression = zipfile.ZIP_DEFLATED

        full_path = '{}{}'.format(self.__path, zip_file_name)  # полный путь к
                                                               # архиву

        # Если будем забирать только сегодняшние файлы, то сразу сохранить дату
        if only_today_files:
            date_now = '{:04d}-{:02d}-{:02d}'.format(
                    datetime.datetime.now().year,
                    datetime.datetime.now().month,
                    datetime.datetime.now().day,
                    )

        with zipfile.ZipFile(full_path,
                             mode='w',
                             compression=zip_compression,
                             allowZip64=True,
                             compresslevel=compression_level,
                             ) as zip_file:
            # init
            total_file_sizes = 0
            total_file_compress_sizes = 0
            total_files = 0

            print('Создаю:', full_path)

            # Перечисляем 'source_dirs', т.е имена папок в корне архива,
            # которые задаются словарем objects (ключ)
            for folder in objects:
                console.print(color='purple', msg=folder)

                # Перечисляем Список файлов (значение)
                for file in objects[folder]:

                    # Пропускаем итерацию, если это папка
                    if os.path.isdir(file):
                        continue

                    # Отбрасываем пути и сохраняем в переменной чистое
                    # ИМЯ ФАЙЛА
                    file_name = str(file.split('/')[-1])

                    # Пропускаем итерацию, если имя файла в списке исключенных
                    if file_name in exclude_file_names:
                        print(' ИСКЛЮЧЕН!')
                        continue

                    # Получаем обрезанное имя файла (послед. 50 сим.)
                    file_print = file[-50:]
                    # Если обрезанное имя не совпадает с полным, то добавляем
                    # [...] к началу обрезанного имени
                    if file_print != file:
                        file_print = '[..]{}'.format(file_print)
                    # Иначе - заполняем пробелами
                    else:
                        file_print += f'{" " * (54 - len(file_print))}'

                    # Печатаем имя файла
                    print('+ {}'.format(file_print),
                          end=' ',
                          flush=True,
                          )

                    ### ТРЕБУЕТ ИСПРАВЛЕНИЯ SOURCE_DIRS ### !!! !!! !!!
                    # Имя файла внутри zip-архива такое:
                    if file[:len(source_dir_name)] == source_dir_name:
                        arcname = folder + file[len(source_dir_name)-1:]
                    else:
                        arcname = folder + '/absolute_path/'+ file

                    # Исключение двойной косой //
                    arcname = arcname.replace('//', '/')

                    # Если только сегодняшние
                    if only_today_files:

                        # Получаем дату изм. файла средствами ОС
                        date_modify = os.path.getmtime(file)
                        # Преобразуем в локальное время (будет строка)
                        date_modify = time.ctime(date_modify)
                        # Преобразуем в datetime.datetime
                        date_modify = datetime.datetime.strptime(
                                date_modify, "%a %b %d %H:%M:%S %Y")
                        date_modify = str(date_modify)[:10]

                        # Если не сегодняшний - пропустить итерацию
                        if date_now != date_modify:
                            print(' НЕСВЕЖИЙ!')
                            continue

                    # Записываем файл в архив
                    try:
                        zip_file.write(file, arcname)
                    except FileNotFoundError:
                        console.print(color='yellow',
                                      msg='Файл больше не существует!',
                                      )
                        continue

                    # Получаем сжатый размер файла в архиве
                    compress_size = (
                            zip_file.infolist()[-1].compress_size)

                    # Нарастить счетчик совокупного объема файлов в сжатом виде
                    total_file_compress_sizes += compress_size

                    # Получаем исходный размер файла в архиве
                    file_size = (
                        zip_file.infolist()[-1].file_size)

                    # Нарастить счетчик совокупного объема файлов в исход. виде
                    total_file_sizes += file_size

                    # Вывод на экран инф. о степени компрессии добавленного
                    # в архив файла
                    if file_size > 0: # Проверка, что больше 0,
                                      # предотвращение деления на 0
                        # Вычислить степень сжатия
                        file_compression = '{:3d}% '.format(
                            int(compress_size / file_size * 100))

                    # Вывод на экран  инф. о компрессии
                    if file_size != 0:
                        console.print(color='green',
                                      msg=file_compression,
                                      end='')
                        console.print(msg=human_space(file_size),
                                      end='')
                        console.print(color='green', msg=' >>> ', end='')
                        console.print(msg=human_space(compress_size))
                    # или знака = , если это папка?
                    else:
                        console.print(color='green', msg='   =')

                    # Нарастить счетчик файлов
                    total_files += 1

        # Вычислить присвоить общую компрессию
        total_file_compression = ' '
        if total_file_sizes > 0:
            percents = int(total_file_compress_sizes
                           / total_file_sizes * 100)
            total_file_compression = f'{percents}% '

        # Вывод на экран итога с количеством файлов и объемом
        print('-' * 56)
        console.print(color='purple', msg='ИТОГО: ', end='')
        print(f'{total_files} файлов | ', end='')
        console.print(color='green', msg=total_file_compression, end='')
        print(human_space(total_file_sizes), end='')
        console.print(color='green', msg=' >>> ', end='')
        print(human_space(total_file_compress_sizes))

        # Если файлы есть в архиве.......
        if total_file_sizes > 0:
            total_file_compression_result = \
                str(int(total_file_compress_sizes /
                        total_file_sizes * 100)) + '%, '

            result = f'Добавлен:\n{zip_file_name}\n' +\
                total_file_compression_result +\
                f'{human_space(total_file_sizes)} >>> ' +\
                f'{human_space(total_file_compress_sizes)}, ' +\
                f'{total_files} файлов\n'
        # Если нет - удаляем архив и ......
        else:
            total_file_compression_result = ''
            ok = False

            os.remove(full_path)
            print('Пустой архив. Удален!')

            result = ''
        return ok, result

    def get_content(self, file_index: int=-1) -> (bool, str):
        """
        Возвращает содержимое архива (ring-файла в папке ring)
        """
        ok = True

        try:
            file = self.__files[file_index]
        except IndexError:
            ok = False
            result = 'Нет файла с номером {}!'.format(file_index)
            return ok, result

        full_path = file.get_full_path()

        print('Читаю файл {} ...'.format(full_path))
        result = file.get_content()[1]
        return ok, result

    def test_archive(self, file_index: int=-1) -> (bool, str):
        """
        Тестирует архив в ring-папке (с конкретным индексом)
        на предмет ошибок zip-формата
        """
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

    def extract_archive(self,
                        file_index: int=-1,
                        dir_name: str='',
                        ) -> (bool, str):
        """
        Успешно.Извлекает содержимое архивного файла
        """
        ok = True
        result = 'Успешно.'

        dir_name =  dir_name + '/_RING_RESTORED/'

        try:
            file = self.__files[file_index]
        except IndexError:
            ok = False
            result = 'Нет файла с номером {}!'.format(file_index)
            return ok, result

        print('Извлекается', file.get_file_name(), 'в', dir_name)

        with zipfile.ZipFile(file.get_full_path(), 'r') as zip_file:

            zip_names_list = zip_file.namelist()
            total_files = len(zip_names_list)

            curent_number = 0
            for name in zip_names_list:
                curent_number += 1
                console.print(msg=f'- ({curent_number}/{total_files}) ', end='')
                console.print(
                        msg=human_space(zip_file.infolist()[zip_names_list.index(name)].compress_size),
                        end=' ',
                        )
                console.print(msg='{}...'.format(name), end='', flush=True)
                try:
                    zip_file.extract(name, dir_name)
                except OSError:
                    ok = False
                    result = 'Запись в ' + dir_name + 'невозможна!'
                    return ok, result

                console.print(msg='ok', color='green')

        return ok, result

