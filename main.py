import os

import requests
from dotenv import load_dotenv
from time import sleep
from terminaltables import AsciiTable


def get_vacansis_hh(language):
    moscow_id_for_hh = 1
    total_vacances_money_hh = 0
    vacancees_processed = 0
    page = 1
    pages_number = 2

    while page < pages_number:

        payload = {
            'text': f'программист{language}',
            'area': moscow_id_for_hh,
            'page': page
        }
        response = requests.get('https://api.hh.ru/vacancies', params=payload)
        response.raise_for_status()
        vacancies_page = response.json()
        page += 1
        pages_number = response.json()['pages']
        for vacancy in vacancies_page['items']:
            if vacancy['salary']:
                salary = (predict_rub_salary_for_head_hunter(vacancy['salary']))
                if salary:
                    total_vacances_money_hh += salary
                    vacancees_processed += 1
        average_salary = int(total_vacances_money_hh / vacancees_processed)
        language_params = {
            'language': language,
            'vacancies_found': vacancies_page['found'],
            'vacancies_processed': vacancees_processed,
            'average_salary': average_salary
        }

    return language_params


def get_vacansis_sj(language):
    moscow_id_for_sj = 4
    page_count = 100
    total_vacances_money_sj = 0
    vacancees_processed = 0
    page = 1
    headers = {
        'X-Api-App-Id': sj_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    while True:
        try:
            payload = {
                'id': moscow_id_for_sj,
                'keyword': f'программист {language}',
                'page': page,
                'count': page_count
            }
            response = requests.get('https://api.superjob.ru/2.0/vacancies', headers=headers, params=payload)
            response.raise_for_status()
            vacancies_page = response.json()
            if not vacancies_page['objects']:
                return
            page += 1
            for vacancy in vacancies_page['objects']:
                salary = predict_rub_salary_for_superjob(vacancy)
                if salary:
                    total_vacances_money_sj += salary
                    vacancees_processed += 1
            if not vacancies_page['more']:
                break
        except requests.exceptions.ConnectionError:
            sleep(2)
    if vacancees_processed:
        average_salary = int(total_vacances_money_sj / vacancees_processed)
    else:
        average_salary = 0
    language_params = {
        'language': language,
        'vacancies_found': vacancies_page['total'],
        'vacancies_processed': vacancees_processed,
        'average_salary': average_salary
    }
    return language_params


def predict_rub_salary_for_head_hunter(salary):
    if salary['currency'] == 'RUR':
        if salary['from'] and salary['to']:
            return (salary['from'] + salary['to']) / 2
        elif salary['from']:
            return salary['from'] * 1.2
        elif salary['to']:
            return salary['to'] * 0.8


def predict_rub_salary_for_superjob(vacancy):
    if vacancy['currency'] == 'rub':
        if vacancy['payment_from'] and vacancy['payment_to']:
            return (vacancy['payment_from'] + vacancy['payment_to']) / 2
        elif vacancy['payment_from']:
            return vacancy['payment_from'] * 1.2
        elif vacancy['payment_to']:
            return vacancy['payment_to'] * 0.8


def make_table(languages_params):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],

    ]
    for language_params in languages_params:
        if language_params:
            table_row = [
                language_params['language'],
                language_params['vacancies_found'],
                language_params['vacancies_processed'],
                language_params['average_salary']
            ]
        table_data.append(table_row)
    table = AsciiTable(table_data)
    return table.table

if __name__ == '__main__':
    load_dotenv()
    sj_key = os.environ['SUPERJOB_KEY']
    languages = [
        'Python',
        'Java',
        'JavaScript',
    ]
    sj_top_languages = []
    hh_top_languages = []

    for language in languages:
        top_languages_sj.append(get_vacansis_sj(language))
        top_languages_hh.append((get_vacansis_hh(language)))
    print(make_table(top_languages_sj))
    print(make_table(top_languages_hh))
