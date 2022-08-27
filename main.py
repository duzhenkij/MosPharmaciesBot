import pandas as pd
import re

from Parser import Parser
from loguru import logger

# logging is necessary for catching errors in progress of using and future troubleshooting
logger.add('debug.json', format='{time} {level} {message}', level='DEBUG', rotation='10 MB',
           compression='zip', serialize=True)


def get_dataframe(titles: list, dosages: list, prices: list, pharmacy_name: str):
    df = pd.DataFrame({
        'title': titles,
        'dosage': dosages,
        'price': prices,
    })
    df['pharmacy_name'] = pharmacy_name

    df = df[pd.to_numeric(df['price'], errors='coerce').notnull()]
    return df


def normalize_dataframe(dataframe):
    regex_count = r'(№\s\d+|N\s\d+|N\d+|№\d+|\d+ш.+|\d+\s+ш.+)'
    regex_dosage = r'(\d+м.|\d+\s+м.|\d+г|\d+г.)'
    replace_words_dict = {
        r'^[Тт]аблетки|[Тт]абл\S|[Тт]аб\b': 'таб.',
        r'^[Кк]апсулы|[Кк]апсул\S|[Кк]апс\b': 'капс.',
        r'^[Рр]аствор|[Рр]аств\S': 'р-р',
        r'^[Пп]орошок': 'пор.',
        r'^[Гг]ранулы|[Гг]ранул\S': 'гран.',
        r'[Дд]ля\s': 'д/',
        r'[Уу]влажняющий': 'увлаж.',
        r'[Пп]итательный': 'питат.',
        r'[Оо]чищающий': 'очищ.',
        r'[Сс]ироп': 'сироп',
        r'[Гг]ель': 'гель',
        r'[Кк]рем': 'крем'
    }

    count_medicine_list = []
    dosage_medicine_list = []
    dosage_medicine_unit_list = []
    type_medicine_list = []

    for i in list(dataframe['dosage']):
        if type(i) is str:
            count_num = ''.join(re.findall(regex_count, i))
            count_extraction = ''.join(re.findall(r'(\d+)', count_num)).strip() + ' шт.'
            dosage_str = ''.join(re.findall(regex_dosage, i)).strip()
            dosage_extraction = ''.join(re.findall(r'\d+', dosage_str))
            dosage_unit_extraction = ''.join(re.findall(r'[мг.|мг|г|г.|мл|мл.]', dosage_str))
            type_extraction = re.split(r'(\d+)|(N|№)', i)[0].strip()

            count_medicine_list.append(count_extraction)
            dosage_medicine_list.append(dosage_extraction)
            dosage_medicine_unit_list.append(dosage_unit_extraction)
            type_medicine_list.append(type_extraction)
        else:
            count_medicine_list.append(None)
            dosage_medicine_list.append(None)
            dosage_medicine_unit_list.append(None)
            type_medicine_list.append(None)

    dataframe['count'] = count_medicine_list
    dataframe['dosage_med'] = dosage_medicine_list
    dataframe['dosage_unit'] = dosage_medicine_unit_list
    dataframe['type'] = type_medicine_list
    dataframe['type'] = dataframe['type'].replace(regex=replace_words_dict)
    return dataframe


def get_result_dataframe(dataframes: list, user_query):
    df = pd.concat(dataframes, ignore_index=True)
    df['title_lower'] = df['title'].str.lower()
    df = df.astype({'price': 'float'})
    if len(user_query) <= 5:
        df = df[df['title_lower'].str.contains(user_query.lower())]
    else:
        df = df[df['title_lower'].str.contains(user_query[:-2].lower())]

    df_normalized = normalize_dataframe(df)

    df_sorted = df_normalized.sort_values(by=['price', 'count'], ascending=True)
    df_head = df_sorted.head(25)
    df_reset_indexes = df_head.reset_index(drop=True)
    return df_reset_indexes


def prettify_result_df_to_beautiful_string(frame):
    df_dict = frame.to_dict()

    df_list = []
    for i in range(0, len(frame)):
        line = str(i + 1) + ') ' + \
               str(df_dict.get('pharmacy_name').get(i)) + ' — ' + \
               str(df_dict.get('title').get(i)) + ', ' + \
               str(df_dict.get('type').get(i)) + ', ' + \
               str(df_dict.get('dosage_med').get(i)) + ' ' + \
               str(df_dict.get('dosage_unit').get(i)) + ', ' + \
               str(df_dict.get('count').get(i)) + ' — ' + \
               str(int(round(df_dict.get('price').get(i)))) + ' руб.\n'

        df_list.append(
            line.replace(', None', '').
                replace('..', '.').
                replace(', шт. ', '').
                replace('  ,', '').
                replace(' None', '')
        )

    result_text = '\n'.join(df_list)

    return result_text


@logger.catch()
def get_result_to_user(user_query):
    logger.debug(f'Запрос пользователя --- {user_query}')
    try:
        pharmacy366_data = Parser(user_query).parse_pharmacy_36_6()
    except Exception:
        pharmacy366_data = ([], [], [])
    try:
        pharmacy366_frame = get_dataframe(pharmacy366_data[0], pharmacy366_data[1], pharmacy366_data[2], 'Аптека 36.6')
    except TypeError:
        pharmacy366_frame = get_dataframe([], [], [], 'Аптека 36.6')
    try:
        gorzdrav_data = Parser(user_query).parse_gorzdrav()
    except Exception:
        gorzdrav_data = ([], [], [])
    try:
        gorzdrav_frame = get_dataframe(gorzdrav_data[0], gorzdrav_data[1], gorzdrav_data[2], 'Горздрав')
    except TypeError:
        gorzdrav_frame = get_dataframe([], [], [], 'Горздрав')
    try:
        samson_data = Parser(user_query).parse_samson_pharma()
    except Exception:
        samson_data = ([], [], [])
    try:
        samson_frame = get_dataframe(samson_data[0], samson_data[1], samson_data[2], 'Самсон-Фарма')
    except TypeError:
        samson_frame = get_dataframe([], [], [], 'Самсон-Фарма')
    try:
        zdorov_ru_data = Parser(user_query).parse_zdorov_ru()
    except Exception:
        zdorov_ru_data = ([], [], [])
    try:
        zdorov_ru_frame = get_dataframe(zdorov_ru_data[0], zdorov_ru_data[1], zdorov_ru_data[2], 'Здоров.ру')
    except TypeError:
        zdorov_ru_frame = get_dataframe([], [], [], 'Здоров.ру')
    try:
        stolichki_data = Parser(user_query).parse_stolichki()
    except Exception:
        stolichki_data = ([], [], [])
    try:
        stolichki_frame = get_dataframe(stolichki_data[0], stolichki_data[1], stolichki_data[2], 'Аптеки Столички')
    except TypeError:
        stolichki_frame = get_dataframe([], [], [], 'Аптеки Столички')

    pharmacies_frames = [pharmacy366_frame, gorzdrav_frame, samson_frame, zdorov_ru_frame, stolichki_frame]
    result_frame = get_result_dataframe(pharmacies_frames, user_query)
    pretty_string_frame = prettify_result_df_to_beautiful_string(result_frame)

    logger.info(f'Запрос пользователя --- {user_query} --- выполнен')
    logger.debug(f'Результат запроса\n{pretty_string_frame}')

    return pretty_string_frame
