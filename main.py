import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

plt.close('all')
matplotlib.use('inline')



year = 2023
regions = [
    ['Москва', f'4368/{year}'],
    ['Санкт-Петербург', f'4079/{year}'],
    ['Ленинск-Кузнецкий', f'11835/{year}'],
    ['Кемерово', f'4693/{year}'],
    ['Южно-Сахалинск', f'4894/{year}'],
    ['Тула', f'4392/{year}'],
    ['Коркино', f'12863/{year}'],
    ['Мирный', f'4022/{year}'],
    ['Железногорск', f'11995/{year}'],
    ['Старый Оскол', f'5024/{year}'],
    ['Прокопьевск', f'11348/{year}'],
    ['Калтан', f'12548/{year}'],
    ['Новокузнецк', f'4721/{year}'],
    ['Междуреченск', f'4722/{year}'],
    ['Березовский', f'149909/{year}'],
    ['Гай', f'11300/{year}'],
    ['Новошахтинск', f'12724/{year}'],
    ['Полевский', f'12770/{year}'],
    ['Нижний Тагил', f'4478/{year}'],
    ['Рыбинск', f'4298/{year}'],
    ['Пермь', f'4476/{year}'],
    ['Белгород', f'5039/{year}'],
    ['Губкин', f'11423/{year}'],
    ['Каменногорск', f'162378/{year}'],
    ['Асбест', f'11395/{year}'],
    ['Кизилюрт', f'12494/{year}'],
    ['Улан-Удэ', f'4804/{year}'],
    ['Павловск', f'5043/{year}'],
    ['Нерюнгри', f'11827/{year}'],
    ['Турныауз', f'11747/{year}']
]
months = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
    'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
    'Ноябрь', 'Декабрь']


# Функция для создания нужных папок
def dirs_creator():
    if not os.path.exists('pages'):
        os.mkdir('pages')
    for i, region in enumerate(regions):
        if not os.path.exists(f'pages/{i + 1}.{region[0]}'):
            os.mkdir(f'pages/{i + 1}.{region[0]}')

    if not os.path.exists('pictures'):
        os.mkdir('pictures')
    for i, region in enumerate(regions):
        if not os.path.exists(f'pictures/{i + 1}.{region[0]}'):
            os.mkdir(f'pictures/{i + 1}.{region[0]}')

    if not os.path.exists('tables'):
        os.mkdir('tables')
    for i, region in enumerate(regions):
        if not os.path.exists(f'tables/{i + 1}.{region[0]}'):
            os.mkdir(f'tables/{i + 1}.{region[0]}')


class WebPage:
    def __init__(self, url=None, path=None):
        self.url = url
        self.path = path

    def download_page(self):
        # Заголовки для запроса
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'}
        src = requests.get(self.url, headers=headers)
        with open(self.path, 'w', encoding='utf-8') as page:
            page.write(src.text)

        return None



class DataPade:
    def __init__(self, srcdir=None, save_pic_dir=None, save_table_dir=None):
        self.src_dir = srcdir
        self.save_pic_dir = save_pic_dir
        self.save_table_dir = save_table_dir

    def make_soup(self):
        with open(self.src_dir, 'r', encoding='utf-8') as page:
            txt = page.read()
        soup = BeautifulSoup(txt, 'html.parser')

        return soup

    def make_df(self, soup):
        dir_list = []
        speed_list = []
        table_row_list = soup.find('tbody').find_all('tr')
        for row in table_row_list:
            row_element_list = row.find_all('td')[-1].text.split()
            if len(row_element_list) == 0:
                pass
            else:
                if len(row_element_list) > 1:
                    dir = row_element_list[0]
                    speed = int(row_element_list[1].strip('м/с'))
                else:
                    dir = 'Ш'
                    speed = 0

                dir_list.append(dir)
                speed_list.append(speed)

        df = pd.DataFrame({'direction': dir_list, 'speed': speed_list})
        df_grouped = df.groupby('direction', as_index=None, observed=False)['speed'].agg(['mean', 'count'])

        direction_list = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ', 'Ш']
        for direct in direction_list:
            if direct not in df_grouped.direction.unique():
                row = pd.DataFrame({'direction': [direct], 'mean': [0], 'count': [0]})
                df_grouped = pd.concat([df_grouped, row])

        df_grouped['direction'] = pd.Categorical(df_grouped['direction'], categories=direction_list, ordered=True)
        df_sorted = df_grouped.sort_values('direction', ignore_index=True)

        return df_sorted

    def export_df(self, df, is_year=False):
        if is_year:
            lst = self.save_table_dir.split("/")
            savedir = f'{lst[0]}/{lst[1]}/{lst[2].split("_")[0]}_{year}.xlsx'
        else:
            savedir = self.save_table_dir
        df.to_excel(savedir, index=False)

        return None

    def make_picture(self, df, is_year=False):
        if is_year:
            title = year
            lst = self.save_pic_dir.split("/")
            savedir = f'{lst[0]}/{lst[1]}/{lst[2].split("_")[0]}_{year}.png'
        else:
            title = self.src_dir.split('/')[-1].split('_')[-1][:-5]
            savedir = self.save_pic_dir

        directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']

        values = df.drop(df.index[-1])['count'].tolist()
        angles = np.linspace(0, 2 * np.pi, len(directions), endpoint=False)
        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, values, color='r', linewidth=1, label='Количество дней')
        ax.fill(angles, values, 'pink', alpha=0.5)
        ax.plot((angles[-1], angles[0]), (values[-1], values[0]), color='r', linewidth=1)
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.pi / 2)
        ax.set_xticks(angles)
        ax.set_xticklabels([f'{dir}' for dir in directions], fontsize=12)
        ax.grid(True, which='major', linestyle='--')
        ax.set_title(title, loc='center')
        plt.savefig(savedir)
        plt.close()

        return None

    def year_df(self, df_list):
        for df in df_list:
            df['mean_count'] = df['mean'] * df['count']
        year_df = pd.concat(df_list)
        groupped_df = year_df.groupby('direction', as_index=False, observed=False).agg(
            {'count': 'sum', 'mean_count': 'sum'})
        groupped_df['mean'] = groupped_df['mean_count'] / groupped_df['count']
        direction_list = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ', 'Ш']
        for direct in direction_list:
            if direct not in groupped_df.direction.unique():
                row = pd.DataFrame({'direction': [direct], 'mean': [0], 'count': [0]})
                groupped_df = pd.concat([groupped_df, row])

        groupped_df['direction'] = pd.Categorical(groupped_df['direction'], categories=direction_list, ordered=True)
        df_sorted = groupped_df.sort_values('direction', ignore_index=True)
        return df_sorted







if __name__ == '__main__':
    print('creating dirs')
    dirs_creator()
    print('dirs have created')

    for i, region in enumerate(regions):
        for j, month in enumerate(months):
            url = f'https://www.gismeteo.ru/diary/{region[1]}/{j + 1}'
            path = f'pages/{i + 1}.{region[0]}/{region[0]}_{month}.html'
            webpage = WebPage(url, path)
            webpage.download_page()
            print(f'{path} has downloaded')

    for region_dir in os.listdir('pages'):
        months_page_list = os.listdir(f'pages/{region_dir}')
        df_list = []
        for page in months_page_list:
            src_dir = f'pages/{region_dir}/{page}'
            save_pic_dir = f'pictures/{region_dir}/{page.split(".")[0]}.png'
            save_table_dir = f'tables/{region_dir}/{page.split(".")[0]}.xlsx'

            datapage = DataPade(src_dir, save_pic_dir, save_table_dir)
            print(datapage.src_dir, end = '\t')
            soup = datapage.make_soup()
            mounth_df = datapage.make_df(soup)
            datapage.export_df(mounth_df)
            print('export ✔', end ='\t')
            datapage.make_picture(mounth_df)
            print('print ✔')
            df_list.append(mounth_df)
        year_df = datapage.year_df(df_list)
        datapage.export_df(year_df, is_year=True)
        datapage.make_picture(year_df, is_year=True)
