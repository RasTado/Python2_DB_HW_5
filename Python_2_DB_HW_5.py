import psycopg2
from pprint import pprint


def main():
    with psycopg2.connect(database="netology_db", user="postgres", password="postgres") as conn:
        create_t(conn)
        while True:
            command_w = input('\nAnyKey\t - Enable DB (Work with DB)'
                              '\nq\t\t - Disable DB (delete DB) '
                              '\nInput command: ')
            if command_w != 'q':
                print('Create data base!')
                while True:
                    with conn.cursor() as cur:
                        command = input('\n1 - Client list '
                                        '\na - Add new client '
                                        '\ns - Search client '
                                        '\nc - Change client'
                                        '\ng - Add new number for client '
                                        '\nd - Delete phone'
                                        '\nf - Delete client'
                                        '\nq - Exit '
                                        '\nInput command: ')
                        if command == '1':
                            sh_all_client_with_numbers(cur)
                        if command == 'a':
                            add_new_client(cur)
                        elif command == 's':
                            search_client(cur)
                        elif command == 'c':
                            change_client_data(cur)
                        elif command == 'g':
                            add_new_number_for_client(cur)
                        elif command == 'd':
                            delete_phone(cur)
                        elif command == 'f':
                            delete_client(cur)
                        elif command == 'q':
                            print('exit')
                            break

            elif command_w == 'q':
                delete_t(conn)
                print('Delete data base!')
                break

    conn.close()


def delete_t(conn):
    # удаление таблиц
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE phone_base;
        DROP TABLE client_base;
        """)


# Функция, создающая структуру БД (таблицы)
def create_t(conn):
    # создание таблицы клиентов и телефонов
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client_base
        (id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        second_name VARCHAR(100),
        email VARCHAR(100) UNIQUE NOT NULL);
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone_base
        (id SERIAL PRIMARY KEY,
        client_owner INTEGER REFERENCES client_base(id),
        phone VARCHAR(16));
        """)

        conn.commit()


# Вспомогательная функция, для поиска по почте
def __search_client(cursor, email=None):
    cursor.execute("""
    SELECT * FROM client_base
    WHERE email = %s;
    """, (email,))

    return cursor.fetchone()


# Вспомогательная функция, для поиска по id
def __search_client_id(cursor, id_cl=0):
    if id_cl != '':

        cursor.execute("""
        SELECT * FROM client_base
        WHERE id = %s;
        """, (id_cl,))

        return cursor.fetchone()
    else:
        return


# Функция, для вывода всего списка клиентов
def sh_all_client_with_numbers(cursor):
    cursor.execute("""
    SELECT client_base.id, first_name, second_name, email, phone_base.phone FROM client_base
    LEFT JOIN phone_base ON client_base.id = phone_base.client_owner
    GROUP BY client_base.id, phone_base.phone;
    """)

    print('\nClient list')
    pprint(cursor.fetchall())


# Функция, позволяющая добавить нового клиента
def add_new_client(cursor):
    new_client_em = input('Input email (required): ')
    if new_client_em != '':
        new_client_fn = input('Input first name (optional): ')
        new_client_sn = input('Input second name (optional): ')
        new_client_nm = input('Input phone numeric (optional): ')
        if __search_client(cursor, new_client_em.lower()) is None:

            cursor.execute("""
            INSERT INTO client_base(first_name, second_name, email)
            VALUES(%s, %s, %s);
            """, (new_client_fn.capitalize(), new_client_sn.capitalize(), new_client_em.lower()))
            client_id = __search_client(cursor, new_client_em.lower())

            cursor.execute("""
            INSERT INTO phone_base(client_owner, phone)
            VALUES(%s, %s);
            """, (client_id[0], new_client_nm))

            print('* Add client:', client_id[1],
                  'Email:', client_id[3],
                  'Phone:', new_client_nm)
        else:
            print('* Error! Email address already taken!')
    else:
        print('* Error! Email should not be empty!')


# Функция, позволяющая добавить телефон для существующего клиента
def add_new_number_for_client(cursor):
    old_client_id = input('Enter Id: ')
    new_number = input('Input new number: ')
    client_id = __search_client_id(cursor, old_client_id)
    if client_id is not None:

        cursor.execute("""
        INSERT INTO phone_base(client_owner, phone)
        VALUES(%s, %s);
        """, (client_id[0], new_number))

        print('* Add number:', new_number, 'for', client_id[1])
    else:
        print('* Error! Client not found!')


# Функция, позволяющая изменить данные о клиенте
def change_client_data(cursor):
    old_client_id = input('Enter Id: ')
    new_fn_client = input('Enter new first name (optional): ')
    new_sn_client = input('Enter new second name (optional): ')
    new_email_client = input('Enter new email (required): ')
    if new_email_client.lower() != '':
        client_id = __search_client_id(cursor, old_client_id)
        if client_id is not None:

            cursor.execute("""
            UPDATE client_base
            SET first_name = %s, second_name = %s, email = %s
            WHERE id = %s;
            """, (new_fn_client.capitalize(), new_sn_client.capitalize(), new_email_client.lower(), client_id[0]))

        else:
            print('* Error! Client not found!')
    else:
        print('* Error! Email should not be empty!')


# Функция, позволяющая удалить телефоны для существующего клиента
def delete_phone(cursor):
    old_client_id = input('Enter Id: ')
    client_id = __search_client_id(cursor, old_client_id)
    if client_id is not None:

        cursor.execute("""
        DELETE FROM phone_base 
        WHERE client_owner = %s;
        """, (client_id[0],))

    else:
        print('* Error! Client not found!')


# Функция, позволяющая удалить существующего клиента
def delete_client(cursor):
    old_client_id = input('Enter Id: ')
    client_id = __search_client_id(cursor, old_client_id)
    if client_id is not None:

        cursor.execute("""
        DELETE FROM phone_base 
        WHERE client_owner = %s;
        """, (client_id[0],))

        cursor.execute("""
        DELETE FROM client_base
        WHERE id = %s;
        """, (client_id[0],))

    else:
        print('* Error! Client not found!')


# Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
def search_client(cursor):
    search = input('Input request: ')

    cursor.execute("""
    SELECT client_base.id, first_name, second_name, email, phone_base.phone FROM client_base
    LEFT JOIN phone_base ON client_base.id = phone_base.client_owner
    WHERE first_name like %s or second_name like %s or email like %s or phone_base.phone like %s;
    """, (search.capitalize(), search.capitalize(), search.lower(), search))

    print(f'''Request '{search}':''')
    pprint(cursor.fetchall())


if __name__ == '__main__':
    main()
