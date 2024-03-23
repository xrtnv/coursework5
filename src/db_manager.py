import psycopg2
from psycopg2 import sql


class DBManager:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()

    def create_database(self, dbname):
        query = f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'"
        self.cur.execute(query)
        exists = self.cur.fetchone()
        if not exists:
            create_query = f"CREATE DATABASE {dbname}"
            self.cur.execute(create_query)
            print(f"База данных {dbname} создана успешно.")
        else:
            print(f"База данных {dbname} уже существует.")

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS companies (
        company_id SERIAL PRIMARY KEY,
        company_name VARCHAR UNIQUE
        );
    
        CREATE TABLE IF NOT EXISTS vacancies (
        vacancy_id SERIAL PRIMARY KEY,
        vacancy_name TEXT NOT NULL,
        salary INT,
        vacancy_url VARCHAR NOT NULL
        );
    
        CREATE TABLE IF NOT EXISTS company_vacancies (
        company_id INT REFERENCES companies(company_id),
        vacancy_id INT REFERENCES vacancies(vacancy_id),
        PRIMARY KEY (company_id, vacancy_id)
        );
        """
        self.cur.execute(query)

    def get_companies_and_vacancies_count(self):
        query = """
            SELECT company_name, COUNT(*) as vacancies_count
            FROM company_vacancies
            JOIN companies ON company_vacancies.company_id = companies.company_id
            GROUP BY company_name
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_all_vacancies(self):
        query = """
            SELECT company_name, vacancy_name, salary, vacancy_url
            FROM company_vacancies
            JOIN companies ON company_vacancies.company_id = companies.company_id
            JOIN vacancies ON company_vacancies.vacancy_id = vacancies.vacancy_id
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_avg_salary(self):
        query = """
            SELECT AVG(salary) as avg_salary
            FROM vacancies
        """
        self.cur.execute(query)
        return self.cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self):
        avg_salary = self.get_avg_salary()
        query = sql.SQL("""
            SELECT company_name, vacancy_name, salary, vacancy_url
            FROM company_vacancies
            JOIN vacancies ON company_vacancies.vacancy_id = vacancies.vacancy_id
            JOIN companies ON company_vacancies.company_id = companies.company_id
            WHERE salary > %s
        """)
        self.cur.execute(query, [avg_salary])
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        query = sql.SQL("""
            SELECT company_name, vacancy_name, salary, vacancy_url
            FROM company_vacancies
            JOIN vacancies ON company_vacancies.vacancy_id = vacancies.vacancy_id
            JOIN companies ON company_vacancies.company_id = companies.company_id
            WHERE LOWER(vacancy_name) LIKE %s
        """)
        self.cur.execute(query, ['%' + keyword.lower() + '%'])
        return self.cur.fetchall()

    def save_employers_and_vacancies(self, employers_dict, vacancies):
        # Предполагается, что employers_dict имеет структуру {'Название компании': 'ID компании'}
        # и vacancies представляет собой список словарей вакансий с данными

        # Сначала сохраняем компании в таблицу companies, если они еще не существуют
        for company_name, company_id in employers_dict.items():
            query = """
                INSERT INTO companies (company_id, company_name) 
                VALUES (%s, %s) 
                ON CONFLICT (company_id) DO NOTHING;
            """
            self.cur.execute(query, (company_id, company_name))

        # Затем сохраняем вакансии в таблицу vacancies, если они еще не существуют
        for vacancy in vacancies:
            query = """
                INSERT INTO vacancies (vacancy_name, salary, vacancy_url) 
                VALUES (%s, %s, %s) 
                ON CONFLICT DO NOTHING;
            """
            self.cur.execute(query, (vacancy['vacancy_name'], vacancy['salary'], vacancy['url']))

        # Наконец, сохраняем связи между компаниями и вакансиями в таблицу company_vacancies
        for company_name, company_id in employers_dict.items():
            for vacancy in vacancies:
                if vacancy['company'] == company_name:
                    query = """
                        INSERT INTO company_vacancies (company_id, vacancy_id) 
                        SELECT %s, vacancies.vacancy_id 
                        FROM vacancies 
                        WHERE vacancies.vacancy_name = %s AND vacancies.vacancy_url = %s
                        ON CONFLICT (company_id, vacancy_id) DO NOTHING;
                    """
                    self.cur.execute(query, (company_id, vacancy['vacancy_name'], vacancy['url']))

        # Коммитим транзакцию
        self.conn.commit()

    def __del__(self):
        self.cur.close()
        self.conn.close()
