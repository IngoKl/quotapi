from flask import Flask, jsonify, abort, request
from termcolor import colored
import logging
import datetime
import sqlite3
import json
import random

# Quotapi v.1.0; 08.06.2016, MIT License (Ingo Kleiber 2016)

# Disable Console Output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Settings
logfile = './api-log.txt'
logging = True
db_connection = sqlite3.connect("quotes-clean.db3", check_same_thread=False)


def dictionary_factory(cursor, row):
    """
    :param cursor: the cursor object
    :param row: the row
    :type cursor: object
    :type row: list
    :return: d
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def max_quote_id():
    """
    :return: the last quote_id in the database
    """
    db_connection.row_factory = dictionary_factory
    sql = db_connection.cursor()
    sql.execute('SELECT max(id) FROM quotes')

    return sql.fetchone()["max(id)"]


def has_ip_verified(ip, quote_id):
    """
    :param ip: the ip address of the request
    :param quote_id: the quote_id requested
    :type ip: str
    :type quote_id: int
    :return: bool
    """
    sql = db_connection.cursor()
    sql.execute('SELECT * FROM verifications WHERE sender_ip = ? AND quote_id = ?', (ip, quote_id))

    if len(sql.fetchall()) > 0:
        return True
    else:
        return False


def quote_id_exists(quote_id):
    """
    :param quote_id: the quote_id requested
    :type quote_id: int
    :return: bool
    """
    sql = db_connection.cursor()
    sql.execute('SELECT * FROM quotes WHERE id=?', (quote_id,))

    if len(sql.fetchall()) > 0:
        return True
    else:
        return False


def log(level, message):
    """
    :param level: the log-level
    :param message: the message to log
    :type level: str
    :type message: str
    :return: none
    """
    if level == 'success':
        color = 'green'
    elif level == 'hard_error':
        color = 'red'
    elif level == 'soft_error':
        color = 'magenta'
    else:
        color = 'white'

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print colored('[%s] %s' % (time, message), color)

    if logging:
        logfile_object = open(logfile, 'a')
        logfile_object.write('[%s] %s \n' % (time, message))
        logfile_object.close()


app = Flask(__name__)


@app.route('/quotapi/api/v1.0/quotes/<int:quote_id>', methods=['GET'])
def get_quote(quote_id):
    if quote_id_exists(quote_id):
        db_connection.row_factory = dictionary_factory
        sql = db_connection.cursor()
        sql.execute('SELECT quotes.*, SUM(verifications.verification) AS verification_sum FROM quotes INNER JOIN verifications ON quotes.id=verifications.quote_id WHERE quotes.id=?', (quote_id,))
        quote = sql.fetchone()

        log('success', '[GET] [200] [%s] - /quotapi/api/v1.0/quotes/%d' % (request.remote_addr, quote_id))
        return jsonify({'quote': quote})
    else:
        log('soft_error', '[GET] [404] [%s] - /quotapi/api/v1.0/quotes/%d' % (request.remote_addr, quote_id))
        abort(404)


@app.route('/quotapi/api/v1.0/quotes/verify/<int:quote_id>', methods=['POST'])
def post_verify_quote(quote_id):
    verification = int(request.form['verification'])
    sender_ip = request.remote_addr
    log('success', '[POST] [200] [%s] - /quotapi/api/v1.0/quotes/%d' % (request.remote_addr, quote_id))

    if quote_id_exists(quote_id):
        if has_ip_verified(sender_ip, quote_id):
            log('soft_error', '[VERIFICATION-FAILED-REPEATED-VERIFICATION] [409] [Ver.: %s] [%s] - /quotapi/api/v1.0/quotes/%d' % (
                verification, request.remote_addr, quote_id))
            abort(409)
        else:
            if -1 <= verification <= 1:
                log('success', '[VERIFICATION] [%s] [%s] - /quotapi/api/v1.0/quotes/%d' % (
                    verification, request.remote_addr, quote_id))
                sql = db_connection.cursor()
                sql.execute('INSERT INTO verifications (sender_ip, quote_id, verification) VALUES (?, ?, ?)', (
                    sender_ip, quote_id, verification))
                db_connection.commit()
                abort(200)
            else:
                log('soft_error', '[VERIFICATION-FAILED] [Ver.: %s] [%s] - /quotapi/api/v1.0/quotes/%d' % (
                    verification, request.remote_addr, quote_id))
                abort(403)
    else:
        log('soft_error', '[VERIFICATION-FAILED-UNKNOWN-QUOTE-ID] [404] [Ver.: %s] [%s] - /quotapi/api/v1.0/quotes/%d' % (
            verification, request.remote_addr, quote_id))
        abort(404)


@app.route('/quotapi/api/v1.0/quotes/random', methods=['GET'])
def get_random_quote():
    last_quote_id = max_quote_id()

    quote_id = random.randint(0, last_quote_id)
    db_connection.row_factory = dictionary_factory
    sql = db_connection.cursor()
    sql.execute('SELECT quotes.*, SUM(verifications.verification) AS verification_sum FROM quotes INNER JOIN verifications ON quotes.id=verifications.quote_id WHERE quotes.id=?', (quote_id,))
    quote = sql.fetchone()

    log('success', '[GET] [200] [%s] - /quotapi/api/v1.0/quotes/random [%d]' % (request.remote_addr, quote_id))
    return jsonify({'quote': quote})


@app.route('/quotapi/api/v1.0/quotes/search', methods=['POST'])
def post_search_quotes():
    search_term = request.form['search_term']
    db_connection.row_factory = dictionary_factory
    sql = db_connection.cursor()
    sql.execute('SELECT * FROM quotes WHERE quote LIKE ?', ("%" + search_term + "%",))

    log('success', '[GET] [200] [%s] - /quotapi/api/v1.0/quotes/search [%s]' % (request.remote_addr, search_term))
    return jsonify({'search_results': sql.fetchall()})


if __name__ == '__main__':
    app.run(debug=True)
