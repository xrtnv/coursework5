import requests


class DataRetriever:
    """Класс для получения данных из API HH.ru и заполнения таблиц в базе данных"""

    companies = {'Megafon': '3127',
                 'MTS': '3776',
                 'Beeline': '4934',
                 'SBER': '3529',
                 'VTB Bank (PJSC)': '4181',
                 'Tinkoff': '78638',
                 'Avito': '84585',
                 '2GIS': '64174',
                 'Gazprombank': '3388',
                 'Ozon': '2180'}

    @staticmethod
    def fetch_data(company_id: str) -> dict:
        """Получает список вакансий с информацией о зарплате для заданной компании"""
        parameters = {
            "page": 1,
            "per_page": 100,
            "employer_id": company_id,
            "only_with_salary": True,
            "only_with_vacancies": True
        }
        return requests.get("https://api.hh.ru/vacancies/", params=parameters).json()['items']

    def get_vacancies(self) -> list:
        """Получает список вакансий"""
        vacancies = []
        for company_name, company_id in self.companies.items():
            company_vacancies = self.fetch_data(company_id)
            for vacancy in company_vacancies:
                if vacancy['salary']['from'] is None:
                    salary = 0
                else:
                    salary = vacancy['salary']['from']
                vacancies.append(
                    {'url': vacancy['alternate_url'], 'salary': salary,
                     'vacancy_name': vacancy['name'], 'company': company_name})
        return vacancies
