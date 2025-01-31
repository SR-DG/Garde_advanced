import datetime
import sqlite3

from PyQt5 import QtWidgets, uic, QtGui, Qt, QtCore
from calendar import monthrange

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QTableWidgetItem, qApp, QMessageBox

import app
import app_inf_urgence
import export_garde
from dialogs import CustomDialog, Saving_progress_dialog, Threading_loading, Auto_plus

import os

from threads import Thread_load_guards, Thread_create_guard, ThreadAutoGuard, Thread_load_guards_inf_urgences, \
    Thread_create_urgence_inf_guard, Thread_create_urgence_surv_guard, Thread_load_guards_surv_urgences
from widgets import Chose_worker


class GuardUi(QtWidgets.QMainWindow):
    def __init__(self, service, month, year):
        super(GuardUi, self).__init__()
        uic.loadUi("./user_interfaces/planing_garde.ui", self)

        self.want_to_close = False
        self.days_of_week = "Dimanche" + "  " + "Lundi" + "  " + "Mardi" + "  " + "Mercredi" + "  " + "Jeudi"

        self.service = service
        self.ttl = self.findChild(QtWidgets.QLabel, "label")
        self.table = self.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.save = self.findChild(QtWidgets.QPushButton, "pushButton")
        self.save.setIcon(QIcon("./asstes/images/save.png"))
        self.exportPd = self.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.exportPd.setIcon(QIcon("./asstes/images/download.png"))
        self.auto = self.findChild(QtWidgets.QPushButton, "pushButton_3")
        self.auto.setIcon(QIcon("./icons/refresh-ccw.png"))
        self.auto_plus = self.findChild(QtWidgets.QPushButton, "pushButton_4")
        self.auto_plus.setIcon(QIcon("./asstes/images/auto.png"))
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 220)
        self.table.setColumnWidth(3, 220)

        if self.service == "inf" or self.service == "radio" or self.service == "labo" or self.service == "admin" or self.service == "pharm" or self.service == "dentiste_inf":
            data = ["Jours", "Date", "De 08h:00 à 16h:00", "De 16h:00 à 08h:00"]
        else:
            data = ["Jours", "Date", "De 08h:00 à 20h:00", "De 20h:00 à 08h:00"]

        self.table.setHorizontalHeaderLabels(data)

        self.month = month
        self.year = year
        self.num_days = monthrange(self.year, self.month)[1]

        if self.month == 1:
            m = "janvier"
        elif self.month == 2:
            m = "février"
        elif self.month == 3:
            m = "mars"
        elif self.month == 4:
            m = "avril"
        elif self.month == 5:
            m = "mai"
        elif self.month == 6:
            m = "juin"
        elif self.month == 7:
            m = "juillet"
        elif self.month == 8:
            m = "août"
        elif self.month == 9:
            m = "septembre"
        elif self.month == 10:
            m = "octobre"
        elif self.month == 11:
            m = "novembre"
        elif self.month == 12:
            m = "décembre"

        if self.service == "urgence":
            self.ttl.setText("Planing de garde urgence mois " + str(m) + "/" + str(self.year) + ":")

            self.load_med()
            self.load_guards()

        elif self.service == "dentiste":
            self.ttl.setText("Planing de garde chirurgie dentaire mois " + str(m) + "/" + str(self.year) + ":")
            self.load_med()
            self.load_guards()

        elif self.service == "labo":
            self.ttl.setText("Planing de garde laboratoire mois " + str(m) + "/" + str(self.year) + ":")

            self.load_med()
            self.load_guards()

        elif self.service == "radio":
            self.ttl.setText("Planing de garde radiologie mois " + str(m) + "/" + str(self.year) + ":")

            self.load_med()
            self.load_guards()

        elif self.service == "admin":
            self.ttl.setText("Planing de garde administration mois " + str(m) + "/" + str(self.year) + ":")
            self.load_med()
            self.load_guards()

        elif self.service == "dentiste_inf":
            self.ttl.setText("Planing de garde infirmiers dentaire mois " + str(m) + "/" + str(self.year) + ":")
            self.load_med()
            self.load_guards()

        elif self.service == "inf":
            self.ttl.setText("Planing de garde infirmiers d'urgences mois " + str(m) + "/" + str(self.year) + ":")

            self.load_groups_inf()
            self.load_guards_inf()

        elif self.service == "surv":
            self.ttl.setText("Planing de garde surveillants d'urgences mois " + str(m) + "/" + str(self.year) + ":")

            self.load_groups_surv()
            self.load_guards_surv()

        elif self.service == "pharm":
            self.ttl.setText("Planing de garde pharmacie mois " + str(m) + "/" + str(self.year) + ":")
            self.load_med()
            self.load_guards()


        self.exportPd.clicked.connect(self.export)

        self.save.clicked.connect(self.save_)
        self.auto.clicked.connect(self.auto_)
        self.auto_plus.clicked.connect(self.auto_plus_)

    def load_guards(self):
        self.dialog = Threading_loading()
        self.dialog.ttl.setText("إنتظر من فضلك")
        self.dialog.progress.setValue(0)
        self.dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.dialog.show()

        self.thr2 = Thread_load_guards(self.service, self.num_days, self.month, self.year)
        self.thr2._signal.connect(self.signal_accepted_load)
        self.thr2._signal_status.connect(self.signal_accepted_load)
        self.thr2._signal_finish.connect(self.signal_accepted_load)
        self.thr2.start()

    def load_med(self):
        connection = sqlite3.connect("database/sqlite.db")
        cur = connection.cursor()
        sql_q = 'SELECT full_name FROM health_worker where service=?'
        cur.execute(sql_q, (self.service,))
        self.medcins = cur.fetchall()
        connection.close()

    def save_(self):
        self.want_to_close = True
        self.dialog = Threading_loading()
        self.dialog.ttl.setText("إنتظر من فضلك")
        self.dialog.progress.setValue(0)
        self.dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.dialog.show()

        if self.service == "inf" :
            self.thr = Thread_create_urgence_inf_guard(self.num_days, self.month, self.year, self.table)
            self.thr._signal.connect(self.signal_accepted)
            self.thr._signal_status.connect(self.signal_accepted)
            self.thr.start()
        elif self.service == "surv":
            self.thr = Thread_create_urgence_surv_guard(self.num_days, self.month, self.year, self.table)
            self.thr._signal.connect(self.signal_accepted)
            self.thr._signal_status.connect(self.signal_accepted)
            self.thr.start()
        else:
            self.thr = Thread_create_guard(self.service, self.num_days, self.month, self.year, self.table)
            self.thr._signal.connect(self.signal_accepted)
            self.thr._signal_status.connect(self.signal_accepted)
            self.thr.start()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        message = "Es-tu sûr de quiter?"
        dialog = CustomDialog(message)
        if dialog.exec():
            if self.service == "inf" or self.service == "surv":
                self.next_page = app_inf_urgence.AppInfUi("inf")
                self.next_page.show()
                self.close()
            else:
                self.next_page = app.AppUi(self.service)
                self.next_page.show()
                self.close()
        else:
            a0.ignore()

    def signal_accepted(self, progress):
        if type(progress) == int:
            self.dialog.progress.setValue(progress)
        elif type(progress) == bool:
            self.dialog.progress.setValue(100)
            self.dialog.ttl.setText("complete")
            self.dialog.close()

    def signal_accepted_load(self, progress):
        if type(progress) == int:
            self.dialog.progress.setValue(progress)
        elif type(progress) == list:
            row = progress[0]
            results_light = progress[1]
            results_night = progress[2]

            day = row + 1
            x = datetime.datetime(self.year, self.month, day)
            m = ""
            if x.strftime("%A") == "Saturday":
                m = "Samedi"
            elif x.strftime("%A") == "Sunday":
                m = "Dimanche"
            elif x.strftime("%A") == "Monday":
                m = "Lundi"
            elif x.strftime("%A") == "Tuesday":
                m = "Mardi"
            elif x.strftime("%A") == "Wednesday":
                m = "Mercredi"
            elif x.strftime("%A") == "Thursday":
                m = "Jeudi"
            elif x.strftime("%A") == "Friday":
                m = "Vendredi"

            self.table.setRowHeight(row, 50)
            self.table.setItem(row, 0, QTableWidgetItem(m))
            self.table.setItem(row, 1, QTableWidgetItem(str(day) + "/" + str(self.month) + "/" + str(self.year)))
            chose_light = Chose_worker(self.medcins)
            chose_night = Chose_worker(self.medcins)

            if self.service == "admin" or self.service == "pharm" or self.service == "dentiste_inf" or self.service == "dentiste" or self.service == "labo":
                if m in self.days_of_week:
                    if results_light:
                        rl = results_light[0]
                        chose_light.chose.setCurrentText(str(rl[0]))
                    else:
                        chose_light.chose.setEnabled(False)
                        chose_light.setStyleSheet("background-color: rgb(162, 153, 153);")
                else:
                    if results_light:
                        rl = results_light[0]
                        chose_light.chose.setCurrentText(str(rl[0]))
                if results_night:
                    rn = results_night[0]
                    chose_night.chose.setCurrentText(str(rn[0]))
            else:
                if results_light:
                    rl = results_light[0]
                    chose_light.chose.setCurrentText(str(rl[0]))
                if results_night:
                    rn = results_night[0]
                    print(results_night)
                    chose_night.chose.setCurrentText(str(rn[0]))


            self.table.setCellWidget(row, 2, chose_light)
            self.table.setCellWidget(row, 3, chose_night)

        elif type(progress) == bool:
            self.dialog.progress.setValue(100)
            self.dialog.ttl.setText("complete")
            self.dialog.close()

    def export(self):
        if self.service == "inf":
            self.want_to_close = True
            self.next_page = export_garde.ExportGardeUi("inf", self.month, self.year)
            self.next_page.show()
        elif self.service == "surv":
            self.want_to_close = True
            self.next_page = export_garde.ExportGardeUi("surv", self.month, self.year)
            self.next_page.show()
        else:
            self.want_to_close = True
            self.next_page = export_garde.ExportGardeUi(self.service, self.month, self.year)
            self.next_page.show()



    def auto_(self):
        try:
            for i in range(self.table.rowCount()):
                if self.table.cellWidget(i, 2).isEnabled():
                    self.table.cellWidget(i, 2).chose.setCurrentIndex(0)
                self.table.cellWidget(i, 3).chose.setCurrentIndex(0)
        except Exception:
            print(Exception.args)


    def alert_(self, message):
        alert = QMessageBox()
        alert.setWindowTitle("alert")
        alert.setText(message)
        alert.exec_()


    def signal_accepted_auto(self, progress):
        if type(progress) == int:
            self.dialog.progress.setValue(progress)
        elif type(progress) == list:
            chose_light = Chose_worker(self.medcins)
            chose_night = Chose_worker(self.medcins)

            if self.table.item(progress[0], 0).text() == "Dimanche" or self.table.item(progress[0],
                                                                                       0).text() == "Lundi" or self.table.item(
                    progress[0], 0).text() == "Mardi" or self.table.item(progress[0],
                                                                         0).text() == "Mercredi" or self.table.item(
                    progress[0], 0).text() == "Jeudi":
                if self.service == "admin" or self.service == "pharm" or self.service == "dentiste_inf" or self.service == "dentiste":
                    chose_night.chose.setCurrentIndex(progress[2])
                    self.table.setCellWidget(progress[0], 3, chose_night)
                else:
                    chose_light.chose.setCurrentIndex(progress[1])
                    chose_night.chose.setCurrentIndex(progress[2])
                    self.table.setCellWidget(progress[0], 2, chose_light)
                    self.table.setCellWidget(progress[0], 3, chose_night)
            else:
                chose_light.chose.setCurrentIndex(progress[1])
                chose_night.chose.setCurrentIndex(progress[2])
                self.table.setCellWidget(progress[0], 2, chose_light)
                self.table.setCellWidget(progress[0], 3, chose_night)
        else:
            self.dialog.progress.setValue(100)
            self.dialog.ttl.setText("complete")
            self.dialog.close()


    def load_groups_inf(self):
        connection = sqlite3.connect("database/sqlite.db")
        cur = connection.cursor()
        sql_q = 'SELECT DISTINCT g FROM groupe'
        cur.execute(sql_q)
        self.medcins = cur.fetchall()
        connection.close()

    def load_groups_surv(self):
        connection = sqlite3.connect("database/sqlite.db")
        cur = connection.cursor()
        sql_q = 'SELECT DISTINCT g FROM groupe_surv'
        cur.execute(sql_q)
        self.medcins = cur.fetchall()
        connection.close()

    def load_guards_inf(self):
        self.dialog = Threading_loading()
        self.dialog.ttl.setText("إنتظر من فضلك")
        self.dialog.progress.setValue(0)
        self.dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.dialog.show()

        self.thr2 = Thread_load_guards_inf_urgences(self.num_days, self.month, self.year)
        self.thr2._signal.connect(self.signal_accepted_load_inf)
        self.thr2._signal_status.connect(self.signal_accepted_load_inf)
        self.thr2._signal_finish.connect(self.signal_accepted_load_inf)
        self.thr2.start()

    def signal_accepted_load_inf(self, progress):
        if type(progress) == int:
            self.dialog.progress.setValue(progress)
        elif type(progress) == list:

            row = progress[0]
            results_light = progress[1]
            results_night = progress[2]

            day = row + 1
            x = datetime.datetime(self.year, self.month, day)
            m = ""
            if x.strftime("%A") == "Saturday":
                m = "Samedi"
            elif x.strftime("%A") == "Sunday":
                m = "Dimanche"
            elif x.strftime("%A") == "Monday":
                m = "Lundi"
            elif x.strftime("%A") == "Tuesday":
                m = "Mardi"
            elif x.strftime("%A") == "Wednesday":
                m = "Mercredi"
            elif x.strftime("%A") == "Thursday":
                m = "Jeudi"
            elif x.strftime("%A") == "Friday":
                m = "Vendredi"

            self.table.setRowHeight(row, 50)
            self.table.setItem(row, 0, QTableWidgetItem(m))
            self.table.setItem(row, 1, QTableWidgetItem(str(day) + "/" + str(self.month) + "/" + str(self.year)))
            chose_light = Chose_worker(self.medcins)
            chose_night = Chose_worker(self.medcins)

            if results_light:
                print(results_light)
                rl = results_light[0]
                chose_light.chose.setCurrentText(str(rl[0]))
            if results_night:
                print(results_night)
                rn = results_night[0]
                chose_night.chose.setCurrentText(str(rn[0]))

            self.table.setCellWidget(row, 2, chose_light)
            self.table.setCellWidget(row, 3, chose_night)

        elif type(progress) == bool:
            self.dialog.progress.setValue(100)
            self.dialog.ttl.setText("complete")
            self.dialog.close()

    def load_guards_surv(self):
        self.dialog = Threading_loading()
        self.dialog.ttl.setText("إنتظر من فضلك")
        self.dialog.progress.setValue(0)
        self.dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.dialog.show()

        self.thr2 = Thread_load_guards_surv_urgences(self.num_days, self.month, self.year)
        self.thr2._signal.connect(self.signal_accepted_load_surv)
        self.thr2._signal_status.connect(self.signal_accepted_load_surv)
        self.thr2._signal_finish.connect(self.signal_accepted_load_surv)
        self.thr2.start()

    def signal_accepted_load_surv(self, progress):
        if type(progress) == int:
            self.dialog.progress.setValue(progress)
        elif type(progress) == list:

            row = progress[0]
            results_light = progress[1]
            results_night = progress[2]

            day = row + 1
            x = datetime.datetime(self.year, self.month, day)
            m = ""
            if x.strftime("%A") == "Saturday":
                m = "Samedi"
            elif x.strftime("%A") == "Sunday":
                m = "Dimanche"
            elif x.strftime("%A") == "Monday":
                m = "Lundi"
            elif x.strftime("%A") == "Tuesday":
                m = "Mardi"
            elif x.strftime("%A") == "Wednesday":
                m = "Mercredi"
            elif x.strftime("%A") == "Thursday":
                m = "Jeudi"
            elif x.strftime("%A") == "Friday":
                m = "Vendredi"

            self.table.setRowHeight(row, 50)
            self.table.setItem(row, 0, QTableWidgetItem(m))
            self.table.setItem(row, 1, QTableWidgetItem(str(day) + "/" + str(self.month) + "/" + str(self.year)))
            chose_light = Chose_worker(self.medcins)
            chose_night = Chose_worker(self.medcins)

            if results_light:
                print(results_light)
                rl = results_light[0]
                chose_light.chose.setCurrentText(str(rl[0]))
            if results_night:
                print(results_night)
                rn = results_night[0]
                chose_night.chose.setCurrentText(str(rn[0]))

            self.table.setCellWidget(row, 2, chose_light)
            self.table.setCellWidget(row, 3, chose_night)

        elif type(progress) == bool:
            self.dialog.progress.setValue(100)
            self.dialog.ttl.setText("complete")
            self.dialog.close()


    def auto_plus_(self):
        dialog = Auto_plus(self.num_days, self.month, self.medcins)
        if self.service == "radio" or self.service == "inf" or self.service == "surv":
            dialog.type.setCurrentIndex(1)
        else:
            dialog.type.setCurrentIndex(0)
        list_med = []
        jf = []
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            print("ok")
            if dialog.classement.count() != 0:
                for i in range(dialog.classement.count()):
                    list_med.append(dialog.classement.item(i).text())


            if dialog.list_jour_fr.count() != 0:

                for i in range(dialog.list_jour_fr.count()):
                    jf.append(dialog.list_jour_fr.item(i).text())

            for j in jf:
                jj = j.split(" ")
                jj = jj[0]

                chose_light = Chose_worker(self.medcins)
                self.table.removeCellWidget(int(jj)-1, 2)
                self.table.setCellWidget(int(jj)-1, 2, chose_light)
                self.table.cellWidget(int(jj)-1, 2).setStyleSheet("background-color: rgb(199, 238, 255);")
            if dialog.type.currentIndex() == 0:
                if len(list_med) == 0:
                    self.alert_("liste des travailleurs est vide")
                else:
                    index = 0
                    if dialog.radio_all.isChecked():
                        days = self.num_days
                        days = days+1

                        for day in range(1, days):
                            row = day - 1
                            if index < len(list_med):
                                if self.table.cellWidget(row, 2).chose.isEnabled():
                                    self.table.cellWidget(row, 2).chose.setCurrentText(list_med[index])
                                    if index == len(list_med) - 1:
                                        index = 0
                                    else:
                                        index = index + 1
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
                                else:
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
                            else:
                                index = 0
                                if self.table.cellWidget(row, 2).chose.isEnabled():
                                    self.table.cellWidget(row, 2).chose.setCurrentText(list_med[index])
                                    index = index + 1
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
                                else:
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1

                    else:
                        st = int(dialog.start_day.text())
                        en = int(dialog.end_day.text())
                        en = en + 1

                        for day in range(st, en):
                            row = day - 1
                            if index < len(list_med):
                                if self.table.cellWidget(row, 2).chose.isEnabled():
                                    self.table.cellWidget(row, 2).chose.setCurrentText(list_med[index])
                                    if index == len(list_med) - 1:
                                        index = 0
                                    else:
                                        index = index + 1
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
                                else:
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
                            else:
                                index = 0
                                if self.table.cellWidget(row, 2).chose.isEnabled():
                                    self.table.cellWidget(row, 2).chose.setCurrentText(list_med[index])
                                    index = index + 1
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
                                else:
                                    if self.table.cellWidget(row, 3).chose.isEnabled():
                                        self.table.cellWidget(row, 3).chose.setCurrentText(list_med[index])
                                        index = index + 1
            else:
                index = 0
                A = list_med
                B = []
                for i in range(len(list_med)):
                    if i == 0:
                        B.append(A[len(list_med) - 1])
                    else:
                        B.append(A[i - 1])

                if dialog.radio_all.isChecked():
                    days = self.num_days
                    days = days + 1

                    for day in range(1, days):
                        row = day - 1

                        if index < len(list_med):

                            self.table.cellWidget(row, 2).chose.setCurrentText(A[index])
                            self.table.cellWidget(row, 3).chose.setCurrentText(B[index])
                            index = index + 1

                        else:
                            index = 0
                            self.table.cellWidget(row, 2).chose.setCurrentText(A[index])
                            self.table.cellWidget(row, 3).chose.setCurrentText(B[index])
                            index = index + 1

                else:
                    st = int(dialog.start_day.text())
                    en = int(dialog.end_day.text())
                    en = en + 1

                    for day in range(st, en):
                        row = day - 1
                        if index < len(list_med):

                            self.table.cellWidget(row, 2).chose.setCurrentText(A[index])
                            self.table.cellWidget(row, 3).chose.setCurrentText(B[index])
                            index = index + 1

                        else:
                            index = 0
                            self.table.cellWidget(row, 2).chose.setCurrentText(A[index])
                            self.table.cellWidget(row, 3).chose.setCurrentText(B[index])
                            index = index + 1


           



