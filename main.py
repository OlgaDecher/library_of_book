from flask import Flask, request
import sqlite3
import json



app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/<name_of_table>', methods=['GET', 'POST'])
def all_get_search(name_of_table):
    if name_of_table in ('books', 'authors', 'relate_table'): 
        if request.method == 'GET':
            with sqlite3.connect("library.db") as con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM {name_of_table}")
                data = cur.fetchall()
            return json.dumps(data)
        elif request.method == 'POST':
            json_body = request.get_json()
            try:
                if name_of_table == 'relate_table':
                    table_title = ('book_ID', 'author_ID')
                elif name_of_table == 'authors':
                    table_title = ('name', 'info')
                elif name_of_table == 'books':
                    table_title = ('name', 'descr')
                name = json_body[table_title[0]]
                descr = json_body[table_title[1]]

            except KeyError:
                    return '{"status":"KeyError","status_code":500}'

            with sqlite3.connect("library.db") as con:
                cur = con.cursor()
                if name_of_table == 'books':
                    cur.execute('INSERT INTO books(name,descr) VALUES(?,?)', (name, descr))
                elif name_of_table == 'authors':
                    cur.execute('INSERT INTO authors(name,info) VALUES(?,?)', (name, descr))
                elif name_of_table == 'relate_table':
                    cur.execute('INSERT INTO relate_table(book_ID,author_ID) VALUES(?,?)', (name, descr))
                con.commit()
            return '{"status":"OK","status_code": 200}' 
      
    else:
        return '{"status":"UnboundLocalError","status_code":500}'

@app.route('/<name_of_table>/<int:id>', methods=['GET'])
def alone_get(name_of_table,id):
    if request.method == 'GET':
        with sqlite3.connect("library.db") as con:
            cur = con.cursor()
            if name_of_table == 'books':
                search = """
                    SELECT books.book_id,books.name,books.descr,authors.author_id,authors.name
                    FROM authors
                    INNER JOIN relate_table ON authors.author_id=relate_table.author_ID
                    INNER JOIN books ON relate_table.book_ID=books.book_id
                    WHERE relate_table.book_ID=?"""
            elif name_of_table == 'authors':
                search = """
                    SELECT authors.author_id,authors.name,authors.info,books.book_id,books.name
                    FROM books
                    INNER JOIN relate_table ON books.book_id=relate_table.book_ID
                    INNER JOIN authors ON relate_table.author_ID=authors.author_id
                    WHERE relate_table.author_ID=?"""
        res = cur.execute(search, (str(id)))  
    return res.fetchall()


con = sqlite3.connect('./library.db')
cur = con.cursor()

query_create_table_books = """
CREATE TABLE IF NOT EXISTS books(
book_id     INTEGER         PRIMARY KEY     AUTOINCREMENT,
name        VARCHAR(256)    NOT NULL, 
descr       TEXT            NOT NULL DEFAULT '')"""

query_create_table_authors = """
CREATE TABLE IF NOT EXISTS authors(
author_id   INTEGER         PRIMARY KEY     AUTOINCREMENT,
name        VARCHAR(256)    NOT NULL,
info        TEXT            NOT NULL DEFAULT '')"""

query_create_relate_table = """
CREATE TABLE IF NOT EXISTS relate_table(
book_ID     INTEGER         REFERENCES books,
author_ID   INTEGER          REFERENCES authors
)"""

cur.execute(query_create_table_books)
cur.execute(query_create_table_authors)
cur.execute(query_create_relate_table)

if __name__=="__main__":
    app.run(debug=True, port=5000, host='127.0.0.1')