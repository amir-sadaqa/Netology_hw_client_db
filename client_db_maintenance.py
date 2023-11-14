import psycopg2

# database = input('Введите название БД: ') # На случай, если для проверки будете создавать БД с другим названием
# user = input('Введите логин: ') # На случай, если логин в БД отличен от postgres
password = input('Введите пароль: ')
# conn = psycopg2.connect(database=database, user=user, password=password)

conn = psycopg2.connect(database='client_db_netology', user='postgres', password=password)
with conn.cursor() as cur:
    cur.execute('''
        DROP TABLE client CASCADE;
        DROP TABLE client_phone;
        ''')

    # 1. Создаем базу данных из двух отношений, где второе отношение (client_phone) ссылается на первое внешним ключом (client_id)
    def create_client_db(cursor, client, client_id, name, surname, email, client_phone, client_phone_id, phone_number):
        cur.execute(
            f'CREATE TABLE IF NOT EXISTS {client}(\n'
            f'{client_id} SERIAL PRIMARY KEY,\n'
            f'{name} VARCHAR(255) NOT NULL,\n'
            f'{surname} VARCHAR(255) NOT NULL,\n'
            f'{email} VARCHAR(255) NOT NULL UNIQUE);'
            
            f'CREATE TABLE IF NOT EXISTS {client_phone}(\n'
            f'{client_phone_id} SERIAL PRIMARY KEY,\n'
            f'{client_id} INTEGER NOT NULL,\n'
            f'{phone_number} VARCHAR(255) NULL UNIQUE,\n'
            f'CONSTRAINT fk_client_id FOREIGN KEY({client_id}) REFERENCES {client}({client_id}) ON DELETE CASCADE)'
        )

        return conn.commit()

    create_client_db(cur, client='client', client_id='client_id', name='name', surname='surname', email='email', client_phone='client_phone', client_phone_id='client_phone_id', phone_number='phone_number')

    # 2. Создаем функцию, позволяющую добавить нового клиента
    def add_client(cursor, name_added, surname_added, email_added):
        try:
            cur.execute(f'''
            INSERT INTO client(name, surname, email) VALUES('{name_added}', '{surname_added}', '{email_added}');
            ''')
        except psycopg2.errors.UniqueViolation:
            print(f'Адрес электронной почты {email_added} был добавлен в БД ранее')

        return conn.commit()

    add_client(cur, name_added='Amir', surname_added='Sadaqa', email_added='asadaka@inbox.ru')
    add_client(cur, name_added='Oleg', surname_added='Bulygin', email_added='obulygin@gmail.com')
    add_client(cur, name_added='Igor', surname_added='Sverchkov', email_added='isverch@mail.ru')
    add_client(cur, name_added='Artem', surname_added='Ivanov', email_added='aivanov@mail.ru')
    add_client(cur, name_added='Vasya', surname_added='Pupkin', email_added='asadaka@inbox.ru')  # Попытка добавить адрес эл. почты, добавленный в БД ранее (будет обработана через исключение, т.к. значение почты должно быть UNIQUE)

    # 3. Создаем ф-цию, позволяющую добавить телефон для существующего клиента
    def add_phone(cursor, client_id, phone_number):
        try:
            if phone_number == '':  # Сообщаем, что если номер не передан, присвоим значению ячейки NULL
                cur.execute(f'''
                INSERT INTO client_phone(client_id, phone_number) VALUES({client_id}, NULL);
                ''')
            elif phone_number != '':
                cur.execute(f'''
                INSERT INTO client_phone(client_id, phone_number) VALUES({client_id}, '{phone_number}');
                ''')
        except psycopg2.errors.ForeignKeyViolation:
            print(f'Клиент с client_id {client_id} отсутствует в таблице client')
        except psycopg2.errors.UniqueViolation:
            print(f'Номер {phone_number} был добавлен в БД ранее')

        return conn.commit()

    add_phone(cur, 1, '8(915)250-76-37')
    add_phone(cur, 8, '8(915)250-76-38')  # Попытка добавить номер для клиента, который не существует в таблице клиентов (будет обработана через исключение)
    add_phone(cur, 1, '8(915)250-35-35')
    add_phone(cur, 2, '')  # Передаем пустой номер, чтобы увидеть NULL в таблице
    add_phone(cur, 3, '8(915)250-00-00')
    add_phone(cur, 2, '8-916-321-01-01')
    add_phone(cur, 3, '8(915)250-76-37')  # Попытка добавить телефонный номер, добавленный в БД ранее (будет обработана через исключение, т.к. значение номера должно быть UNIQUE)

    # 4. Создаем ф-цию, позволяющую изменить данные о клиенте
    def update_client(cursor, what_we_gonna_change, value, client_id):
        cur.execute(f'''
        UPDATE client SET {what_we_gonna_change}=%s WHERE client_id=%s;
        ''', (f'{value}', f'{client_id}')
                    )
        return conn.commit()

    update_client(cur, 'name', 'Ameer', 1)
    update_client(cur, 'surname', 'Sadaka', 1)
    update_client(cur, 'email', 'sadaka.amir@mail.ru', 1)
    update_client(cur, 'email', 'o_bul@mail.ru', 2)
    update_client(cur, 'email', 'some_email@mail.ru', 8)  # Попытка изменить данные по первичному ключу (client_id), которого нет в таблице. Однако запрос не возвращает ошибку, как, например, не вернет ее и SELECT-запрос с несуществующим ключом

    # 5. Создаем ф-цию, позволяющую удалить телефон для существующего клиента
    # def del_phone(cursor, client_id):
    #     cur.execute('''
    #     DELETE FROM client_phone WHERE client_id=%s;
    #     ''', (f'{client_id}', ))
    #
    #     return conn.commit()
    #
    # del_phone(cur, 3)
    #
    # # 6. Создаем ф-цию, позволяющую удалить существующего клиента (одновременно удалятся все номера клиента, существующие в таблице client_phone)
    # def del_client(cursor, client_id):
    #     cur.execute('''
    #     DELETE FROM client WHERE client_id=%s;
    #     ''', (f'{client_id}', ))
    #
    #     return conn.commit()
    #
    # del_client(cur, 4)
    # del_client(cur, 2)

    # 7. Создаем ф-цию, позволяющую найти клиента по его данным: имени, фамилии, email или телефону
    def find_client(cursor, search_criterion, value):
        if search_criterion != 'phone_number':
            cur.execute(f'''
            SELECT * FROM client WHERE {search_criterion}=%s;
            ''', (f'{value}', ))
        else:
            cur.execute(f'''
            SELECT * from client WHERE client_id = (
                                       SELECT client_id FROM client_phone WHERE {search_criterion}=%s
                                                   );
            ''', (f'{value}', ))

        return cur.fetchall()

    print(find_client(cur, 'name', 'Oleg'))
    print(find_client(cur, 'surname', 'Sadaka'))
    print(find_client(cur, 'email', 'isverch@mail.ru'))
    print(find_client(cur, 'phone_number', '8(915)250-76-37'))
    print(find_client(cur, 'phone_number', '8(915)250-00-00'))

conn.close()


