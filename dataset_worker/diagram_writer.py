import yaml
import os
import matplotlib.pyplot as plt
import numpy as np
import zipfile


class DiagramWriter:
    def get_names_dict(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data["names"]

    def get_one_frame_category(self, file_path: str):
        first_values = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Разделяем строку по пробелам и берем первое значение
                first_value = line.split()[0]
                # Добавляем первое значение в список
                first_values.append(first_value)
        return first_values

    def get_all_frame_category(self, dir_path: str):
        res_dict = dict()
        category_name_dict = dict()

        files_list = os.listdir(dir_path)
        print(files_list)
        for file_name in files_list:
            one_frame_category = self.get_one_frame_category(file_path=f"{dir_path}/{file_name}")
            for one_dish in one_frame_category:
                one_dish = int(one_dish)

                if not one_dish in category_name_dict:
                    category_name_dict[one_dish] = [file_name]
                else:
                    category_name_dict[one_dish].append(file_name)

                if one_dish not in res_dict:
                    res_dict[one_dish] = 1
                else:
                    res_dict[one_dish] += 1
        return res_dict, category_name_dict

    def create_diagram(self, data: dict, shot = False):
        # Преобразуем ключи в числа и значения в список
        # keys = list(map(int, data.keys()))
        keys = list(data.keys())
        values = list(data.values())

        # Увеличиваем размер графика
        plt.figure(figsize=(12, 6))

        colors = plt.cm.viridis(np.linspace(0, 1, len(keys)))  # Используем цветовую карту viridis

        # Создаем гистограмму с разными цветами для каждого столбца
        plt.bar(keys, values, color=colors)

        # Поворачиваем метки на оси X для лучшей читаемости
        plt.xticks(keys, rotation=90, fontsize=8)

        # Устанавливаем целочисленные значения на оси Y
        max_value = max(values)  # Максимальное значение для оси Y
        plt.yticks(np.arange(0, max_value + 1, 1))  # Шаг 1, только целые числа
        plt.savefig('./tmp_out/histogram.png')  # Сохраняем график в файл

    def unzip_data(self, zip_path: str, extract_path: str):
        """Распаковываем архив"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            print(f"Архив успешно распакован в {extract_path}")


    def create_txt_file(self, data: dict, names_dict: dict, file_categories: dict):
        names_count_dict = dict()
        for key in names_dict:
            names_count_dict[key] = 0
        for i in data:
            names_count_dict[i] = data[i]

        self.save_txt_file(name="obj.txt", data=names_count_dict, categry_dict=names_dict, file_categories=file_categories)

        print(names_count_dict)

    def save_txt_file(self, name: str, data: dict, categry_dict: dict, file_categories: dict):
        with open(f"./tmp_out/{name}", 'w', encoding='utf-8') as file:
            # Записываем каждую пару ключ-значение в файл
            for key, value in data.items():
                len_str_key = len(str(key))
                if len_str_key == 1:
                    str_key = f"___{key}:"
                elif len_str_key == 2:
                    str_key = f"__{key}:"
                elif len_str_key == 3:
                    str_key = f"_{key}:"
                else:
                    str_key = f"{key}:"
                if key in file_categories:
                    file.write(f"{str_key} {value} ---> {categry_dict[key]} -> {file_categories[key]}\n")
                else:
                    file.write(f"{str_key} {value} ---> {categry_dict[key]}\n")


if __name__ == '__main__':
    obj = DiagramWriter()

    names = obj.get_names_dict(file_path="./tmp_in/data.yaml")

    print(names)

    # one_value = obj.get_one_frame_category(file_path="./dataset/train/frame_2024-12-04_04-26-05.txt")
    #
    # print(one_value)

    data = obj.get_all_frame_category(dir_path="./tmp_in/labels/train")

    obj.create_diagram(data=data)

    obj.create_txt_file(data=data, names_dict=names)

    # obj.unzip_data(zip_path="./tmp_in/dataset.zip", extract_path="./tmp_in")

