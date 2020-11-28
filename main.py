import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit
from project_bank import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Настройка окна
        self.setupUi(self)
        self.login_account = ''  # Логин аккаунта в котором находится пользователь
        self.account_money = None  # Деньги аккаунта в котором находится пользователь
        self.pushButton_3.hide()
        self.pushButton_4.hide()
        self.pushButton_5.hide()
        self.pushButton_6.hide()
        self.pushButton_7.hide()
        self.label_3.hide()
        self.pushButton.clicked.connect(self.log_in)
        self.pushButton_2.clicked.connect(self.register)
        self.pushButton_3.clicked.connect(self.deposit)
        self.pushButton_4.clicked.connect(self.get)
        self.pushButton_5.clicked.connect(self.transfer_by_username)
        self.pushButton_6.clicked.connect(self.log_out)
        self.pushButton_7.clicked.connect(self.delete_account)

    # Функция удаление аккаунта
    def delete_account(self):
        con = sqlite3.connect('Bankdb.db')
        cur = con.cursor()
        confirm, ok_pressed = QInputDialog.getText(self, 'Удаление аккаунта',
                                                   'Вы уверены что хотите удалить аккаунт?\n'
                                                   'Все средства будут утеряны, напишите "Подтверждаю"')
        if ok_pressed:
            if confirm == 'Подтверждаю':
                cur.execute('''DELETE FROM bank_data
                                   WHERE login = ?''', (self.login_account,))
                con.commit()
                self.show_authorization()
                QMessageBox.information(self, 'Аккаунт удален', 'Аккаунт удалён успешно')
            else:
                QMessageBox.information(self, 'Удаление аккаунта',
                                        'Чтобы удалить аккаунт введите "Подтверждаю" без кавычек')
        con.close()

    # Функция перевода по логину
    def transfer_by_username(self):
        transfer_login, ok_pressed = QInputDialog.getText(self, 'Перевод денег',
                                                          'Кому хотите перевести деньги?', QLineEdit.Normal, '')
        con = sqlite3.connect('Bankdb.db')
        cur = con.cursor()
        check_logins = cur.execute('''SELECT login FROM bank_data
                                                   WHERE login = ?''', (transfer_login,)).fetchall()
        if ok_pressed:
            if self.account_money != 0:
                if check_logins:
                    transfer_money, ok_pressed = QInputDialog.getInt(self, 'Перевод средств',
                                                                     'Сколько хотите перевести?', 100, 1,
                                                                     self.account_money, 100)
                    if ok_pressed:
                        self.account_money -= transfer_money
                        cur.execute('''UPDATE bank_data
                                           SET money = ?
                                               WHERE login = ?''', (self.account_money, self.login_account))

                        # transfer_account_money - Деньги аккаунта на который выполняется перевод
                        transfer_account_money = cur.execute('''SELECT money FROM bank_data
                                                                    WHERE login = ?''', (transfer_login,)).fetchone()[0]
                        transfer_account_money += transfer_money
                        cur.execute('''UPDATE bank_data
                                           SET money = ?
                                               WHERE login = ?''', (transfer_account_money, transfer_login))
                        con.commit()
                        self.label_3.setText(f'На вашем счету: {self.account_money}')
                        QMessageBox.information(self, 'Перевод выполнен', 'Средства переведены успешно')
                else:
                    QMessageBox.warning(self, 'Аккаунт не найден', 'Аккаунта с таким логином не существует')
            else:
                QMessageBox.information(self, 'На счету нет средств',
                                        'На вашем счету нет денег', QMessageBox.Ok)
        con.close()

    # Функция вывода денег
    def get(self):
        get_money, ok_pressed = QInputDialog.getInt(self, 'Вывод средств',
                                                    'Сколько хотите вывести?', 100, 1, self.account_money, 100)
        if ok_pressed:
            if self.account_money != 0:
                con = sqlite3.connect('Bankdb.db')
                cur = con.cursor()
                self.account_money -= get_money
                cur.execute('''UPDATE bank_data
                                   SET money = ?
                                       WHERE login = ?''', (self.account_money, self.login_account))
                self.label_3.setText(f'На вашем счету: {self.account_money}')
                QMessageBox.information(self, 'Средства выведены',
                                        'Средства успешно выведены с вашего счёта', QMessageBox.Ok)
                con.commit()
                con.close()
            else:
                QMessageBox.information(self, 'На счету нет средств',
                                        'На вашем счету нет денег', QMessageBox.Ok)

    # Функция внесения денег
    def deposit(self):
        deposit_money, ok_pressed = QInputDialog.getInt(self, 'Внести деньги на счёт',
                                                        'Сколько хотите внести?', 100, 1, 100000, 100)
        if ok_pressed:
            con = sqlite3.connect('Bankdb.db')
            cur = con.cursor()
            self.account_money += deposit_money
            cur.execute('''UPDATE bank_data
                               SET money = ?
                                   WHERE login = ?''', (self.account_money, self.login_account))
            self.label_3.setText(f'На вашем счету: {self.account_money}')
            QMessageBox.information(self, 'Счёт пополнен',
                                    'Средства успешно зачислены на ваш счёт', QMessageBox.Ok)
            con.commit()
            con.close()

    # Функция регистрации аккаунта
    def register(self):
        self.setWindowTitle('Регистрация')
        self.statusbar.clearMessage()
        log = self.lineEdit.text()
        passw = self.lineEdit_2.text()
        if not log or not passw:
            self.statusbar.showMessage('Для регистрации введите новый логин и пароль')
        else:
            nametxt = ''
            ok_pressed = True
            while not nametxt and ok_pressed:
                nametxt, ok_pressed = QInputDialog.getText(self, 'Введитя своё имя', 'Имя:', QLineEdit.Normal, '')
                if nametxt:
                    if nametxt.isalpha():
                        if ok_pressed:
                            con = sqlite3.connect('Bankdb.db')
                            cur = con.cursor()
                            check_log = cur.execute('''SELECT login FROM bank_data
                                                           WHERE login = ?''', (log,)).fetchone()
                            if not check_log:
                                cur.execute('''INSERT INTO bank_data(login, passwd, name) VALUES(?, ?, ?)''',
                                            (log, passw, nametxt))
                                con.commit()
                                self.account_money = cur.execute('''SELECT money FROM bank_data
                                                                        WHERE login = ?''', (log,)).fetchone()[0]
                                self.show_account(log, nametxt, self.account_money)
                                self.login_account = log
                                con.close()
                                QMessageBox.information(self, 'Регистрация',
                                                        'Аккаунт успешно зарегистрирован', QMessageBox.Ok)
                            else:
                                self.statusbar.showMessage('Аккаунт с таким логином уже существует')
                        else:
                            self.setWindowTitle('Авторизация')
                            self.statusbar.clearMessage()
                    else:
                        self.statusbar.showMessage('Введены некорректные данные')
                        nametxt = ''
                else:
                    if not ok_pressed:
                        self.statusbar.clearMessage()
                    else:
                        self.statusbar.showMessage('Введите имя')

    # Функция входа в аккаунт
    def log_in(self):
        self.setWindowTitle('Авторизация')
        log = self.lineEdit.text()
        passw = self.lineEdit_2.text()
        self.statusbar.clearMessage()
        if log and passw:
            con = sqlite3.connect('Bankdb.db')
            cur = con.cursor()
            nametxt = cur.execute('''SELECT name FROM bank_data
                                     WHERE login = ? AND passwd = ?''', (log, passw)).fetchall()
            if not nametxt:
                check_account = cur.execute('''SELECT login, passwd FROM bank_data
                                                   WHERE login = ?''', (log,)).fetchall()
                if not check_account:
                    self.statusbar.showMessage('Аккаунта с таким логином не существует')
                elif passw != check_account[0][1]:
                    self.statusbar.showMessage('Неверный пароль')
                con.close()
            else:
                self.account_money = cur.execute('''SELECT money FROM bank_data
                                                        WHERE login = ?''', (log,)).fetchone()[0]
                self.show_account(log, nametxt[0][0], self.account_money)
                self.login_account = log
                con.close()
        else:
            if not log and not passw:
                self.statusbar.showMessage('Введите логин и пароль')
            elif not log:
                self.statusbar.showMessage('Введите логин')
            elif not passw:
                self.statusbar.showMessage('Введите пароль')

    # Функция выхода из аккаунта
    def log_out(self):
        self.show_authorization()
        self.statusbar.showMessage('Вы вышли из аккаунта')

    # Функция показа окна авторизации
    def show_authorization(self):
        self.statusbar.clearMessage()
        self.setWindowTitle('Авторизация')
        self.login_account = ''
        self.account_money = None
        self.pushButton.show()
        self.pushButton_2.show()
        self.label.show()
        self.label_2.show()
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit.show()
        self.lineEdit_2.show()
        self.label_3.hide()
        self.pushButton_3.hide()
        self.pushButton_4.hide()
        self.pushButton_5.hide()
        self.pushButton_6.hide()
        self.pushButton_7.hide()

    # Функция показа окна личного кабинета
    def show_account(self, log, nametxt, account_money):
        self.pushButton.hide()
        self.pushButton_2.hide()
        self.label.hide()
        self.label_2.hide()
        self.label_3.show()
        self.lineEdit.hide()
        self.lineEdit_2.hide()
        self.pushButton_3.show()
        self.pushButton_4.show()
        self.pushButton_5.show()
        self.pushButton_6.show()
        self.pushButton_7.show()
        self.setWindowTitle(f'Личный кабинет - {log}')
        self.statusbar.showMessage(f'Здравствуйте, {nametxt}')
        self.label_3.setText(f'На вашем счету: {account_money}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.setFixedSize(361, 298)
    w.show()
    sys.exit(app.exec_())
