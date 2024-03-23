from src.db_manager import DBManager
from src.hh_api import DataRetriever


def main():
    # Получаем информацию о работодателях
    response = DataRetriever()
    employers_dict = response.companies
    employers_all_vacancies = response.get_vacancies()

    # Создаем экземпляр класса DBManager для взаимодействия с базой данных
    database = DBManager(dbname='hh_db', user='postgres', password='asBF_13cam')

    # Создаем базу данных
    database.create_database("hh_db")

    # Создаем таблицы
    database.create_tables()

    # Сохраняем информацию в базу данных
    database.save_employers_and_vacancies(employers_dict, employers_all_vacancies)

    # Выводим список компаний и количество вакансий в каждой компании
    print("Список компаний и количество вакансий в компаниях:")
    for row in database.get_companies_and_vacancies_count():
        print(f"{row[0]} - {row[1]}")

    # Выводим список всех вакансий с указанием названия компании
    print("Список всех вакансий с указанием названия компании:")
    for row in database.get_all_vacancies():
        print(f"{row[0]} - {row[1]}")

    # Выводим среднюю зарплату по вакансиям
    print("Средняя зарплата по вакансиям:")
    print(database.get_avg_salary())

    # Выводим список всех вакансий, у которых зарплата выше средней по всем вакансиям
    print("Список всех вакансий, у которых зарплата выше средней по всем вакансиям:")
    for row in database.get_vacancies_with_higher_salary():
        print(f"{row[0]}")

    # Задаем ключевое слово для поиска
    keyword = 'Разработчик'

    # Выводим список всех вакансий, в названии которых содержатся переданные в метод слова
    print("Список всех вакансий, в названии которых содержатся переданные в метод слова:")
    for row in database.get_vacancies_with_keyword(keyword):
        print(f"{row[0]}")


if __name__ == '__main__':
    main()
