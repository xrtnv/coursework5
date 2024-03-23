CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR UNIQUE
);

CREATE TABLE vacancies (
    vacancy_id SERIAL PRIMARY KEY,
    vacancy_name TEXT NOT NULL,
    salary INT,
    vacancy_url VARCHAR NOT NULL
);

CREATE TABLE company_vacancies (
    company_id INT REFERENCES companies(company_id),
    vacancy_id INT REFERENCES vacancies(vacancy_id),
    PRIMARY KEY (company_id, vacancy_id)
);
