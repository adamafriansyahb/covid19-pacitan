import telebot
from telebot import types
import mysql.connector
from datetime import datetime, timedelta

mydb = mysql.connector.connect(
  host="localhost",
  port = 8889,
  user="root",
  password="root",
  database="covid_pacitan"
)

sql = mydb.cursor()

token = '1427628129:AAGCb2r1lYS91x8AgkqeMfE1tv6rmBF2yKQ'
bot = telebot.TeleBot(token)

query_max_date = "SELECT MAX(tanggal) FROM kabupaten"
sql.execute(query_max_date)
result_latest_date = sql.fetchone()
latest_date = result_latest_date[0]
yesterday_date = latest_date - timedelta(days=1)

def log(message, cmd):
    current_date = datetime.now()
    name = message.from_user.first_name

    insert = "INSERT INTO log (tanggal, user, perintah) VALUES (%s, %s, %s)"
    val = (current_date, name, cmd)

    sql.execute(insert, val)
    mydb.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # print(message)
    # print(message.chat.id)
    # print(message.from_user.id)

    log(message, 'start')

    # print(message)

    chat_id = message.chat.id
    name = message.from_user.first_name

    custom = types.ReplyKeyboardMarkup()
    a = types.KeyboardButton('Info sekabupaten')
    b = types.KeyboardButton('Info seluruh kecamatan')
    c = types.KeyboardButton('Info per kecamatan')

    custom.row(a)
    custom.row(b)
    custom.row(c)

    text = "Hai {}, apa yang ingin Anda cari tahu?\n".format(name)
    msg = bot.send_message(chat_id, text, reply_markup=custom)

    bot.register_next_step_handler(msg, step1)

def step1(message):
    chat_id = message.chat.id
    pesan = message.text
    custom = types.ReplyKeyboardRemove()

    if (pesan == 'Info sekabupaten'):

        log(message, 'Info sekabupaten')

        sql.execute("SELECT * FROM kabupaten WHERE tanggal='{}'".format(latest_date))
        result = sql.fetchone()

        sql.execute("SELECT * FROM kabupaten WHERE tanggal='{}'".format(yesterday_date))
        result_yesterday = sql.fetchone()

        kasus_baru = result[2] - result_yesterday[2]
        sembuh_baru = result[3] - result_yesterday[3]
        meninggal_baru = result[5] - result_yesterday[5]

        text = "Info Covid-19 Kabupaten Pacitan\n\n"\
            "---------Kumulatif---------\n"\
            "Total Kasus: {}\n"\
            "Total Sembuh: {}\n"\
            'Total kasus aktif: {}\n'\
            "Total Meninggal: {}\n"\
            "---------Harian---------\n"\
            "Kasus baru: +{}\n"\
            "Sembuh: +{}\n"\
            "Meninggal: +{}\n"\
            "------------------\n"\
            "Diupdate terakhir pada: {}\n"\
            "Sumber: https://covid19.pacitankab.go.id".format(result[2], result[3], result[4], result[5], kasus_baru, sembuh_baru, meninggal_baru, result[1])

        bot.send_message(chat_id, text, reply_markup=custom)

    elif (pesan == 'Info seluruh kecamatan'):

        log(message, 'Info seluruh kecamatan')

        sql.execute("SELECT * FROM kecamatan WHERE tanggal='{}'".format(latest_date))
        result = sql.fetchall()
        text = 'Jumlah Kasus Aktif per Kecamatan\n----------------------\n'

        for i in result:
            text += i[2].capitalize() + ': ' + str(i[3]) + '\n'
        text += "----------------------\nDiupdate terakhir pada: {}\nSumber: https://covid19.pacitankab.go.id".format(latest_date)

        bot.send_message(chat_id, text, reply_markup=custom)

    elif (pesan == 'Info per kecamatan'):

        log(message, 'Info per kecamatan')

        kec_button = types.ReplyKeyboardMarkup()

        arjosari = types.KeyboardButton('Arjosari')
        bandar = types.KeyboardButton('Bandar')
        donorojo = types.KeyboardButton('Donorojo')
        kebonagung = types.KeyboardButton('Kebonagung')
        nawangan = types.KeyboardButton('Nawangan')
        ngadirojo = types.KeyboardButton('Ngadirojo')
        pacitan = types.KeyboardButton('Pacitan')
        pringkuku = types.KeyboardButton('Pringkuku')
        punung = types.KeyboardButton('Punung')
        sudimoro = types.KeyboardButton('Sudimoro')
        tegalombo = types.KeyboardButton('Tegalombo')
        tulakan = types.KeyboardButton('Tulakan')

        kec_button.row(arjosari, bandar)
        kec_button.row(donorojo, kebonagung)
        kec_button.row(nawangan, ngadirojo)
        kec_button.row(pacitan, pringkuku)
        kec_button.row(punung, sudimoro)
        kec_button.row(tegalombo, tulakan)

        text = "Kecamatan manakah yang ingin Anda ketahui?\n"
        msg = bot.send_message(chat_id, text, reply_markup=kec_button)

        bot.register_next_step_handler(msg, step2)

    else:
        text = "Mohon maaf, bot tidak mengerti '{}'\n"\
            "/start untuk memulai menggunakan bot.".format(message.text)

        bot.send_message(chat_id, text, reply_markup=custom)

def step2(message):
    chat_id = message.chat.id
    pesan = message.text
    lowered_pesan = pesan.lower()
    kec_button = types.ReplyKeyboardRemove()

    kecamatan = []
    sql.execute("SELECT DISTINCT nama FROM kecamatan")
    result_kec = sql.fetchall()
    for i in result_kec:
        kecamatan.append(i[0])
    
    # print(kecamatan)

    if (lowered_pesan not in kecamatan):

        text = "Mohon maaf, bot tidak mengerti '{}'\n"\
            "/start untuk memulai menggunakan bot.".format(message.text)

        bot.send_message(chat_id, text, reply_markup=kec_button)

    else:

        log(message, pesan)

        sql.execute("SELECT kasus_aktif FROM kecamatan WHERE tanggal='{}' AND nama='{}'".format(latest_date, lowered_pesan))
        result = sql.fetchone()

        if not result:

            text = "Jumlah kasus aktif di kecamatan {}\n"\
                "----------------------\n"\
                "Kasus aktif: {} kasus\n"\
                "----------------------\n"\
                "Diupdate terakhir pada: {}\n"\
                "Sumber: https://covid19.pacitankab.go.id".format(pesan, 0, latest_date)

            bot.send_message(chat_id, text, reply_markup=kec_button)

        else:

            result = result[0]

            text = "Jumlah kasus aktif di kecamatan {}\n"\
                "----------------------\n"\
                "Kasus aktif: {} kasus\n"\
                "----------------------\n"\
                "Diupdate terakhir pada: {}\n"\
                "Sumber: https://covid19.pacitankab.go.id".format(pesan, result, latest_date)

            bot.send_message(chat_id, text, reply_markup=kec_button)

@bot.message_handler(commands=['infokab'])
def send_allstat(message):

    log(message, 'infokab')

    sql.execute("SELECT * FROM kabupaten WHERE tanggal='{}'".format(latest_date))
    result = sql.fetchone()

    text = "Info Covid-19 Kabupaten Pacitan\n"\
        "------------------\n"\
        "Total Kasus: {}\n"\
        "Sembuh: {}\n"\
        'Kasus aktif: {}\n'\
        "Meninggal: {}\n"\
        "------------------\n"\
        "Diupdate terakhir pada: {}\n"\
        "Sumber: https://covid19.pacitankab.go.id/".format(result[2], result[3], result[4], result[5], result[1])

    bot.reply_to(message, text)

@bot.message_handler(commands=['infokecamatan'])
def send_infostat(message):

    log(message, 'infokec')

    texts = message.text.split(' ')
    kecamatan = texts[1].lower()

    sql.execute("SELECT kasus_aktif FROM kecamatan WHERE nama='{}' AND tanggal='{}'".format(kecamatan, latest_date))
    result = sql.fetchone()

    msg = "Jumlah kasus aktif di kec. {} adalah: {}".format(kecamatan, result[0])
    bot.reply_to(message, msg)

@bot.message_handler(commands=['infokec'])
def send_infokec(message):
    log(message, 'infokec')

    query_max_date = "SELECT MAX(tanggal) FROM kabupaten"
    sql.execute(query_max_date)
    result_latest_date = sql.fetchone()
    latest_date = result_latest_date[0]

    sql.execute("SELECT * FROM kecamatan WHERE tanggal='{}'".format(latest_date))
    result = sql.fetchall()
    text = 'Jumlah Kasus Aktif per Kecamatan\n----------------------\n'
    for i in result:
        text += i[2].capitalize() + ': ' + str(i[3]) + '\n'
    text += "----------------------\nDiupdate terakhir pada: {}\nSumber: https://covid19.pacitankab.go.id".format(latest_date)

    bot.reply_to(message, text)


print(mydb)
print('Bot is running...')
bot.polling()