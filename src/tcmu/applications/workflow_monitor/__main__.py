import tcmu
from PySide6 import QtWidgets, QtCore, QtGui
import os
import datetime


class StatusTable(QtWidgets.QTableWidget):
    def __init__(self, parent):
        headers = ['Hash', 'Server', 'Status', 'Stage', 'Run Time']
        super().__init__(0, len(headers), parent=parent)
        self.setHorizontalHeaderLabels(headers)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def reset(self):
        self.setRowCount(0)

    def add_row(self, row):
        self.setRowCount(self.rowCount() + 1)
        for i, x in enumerate(row):
            item = QtWidgets.QTableWidgetItem()
            item.setText(x)
            self.setItem(self.rowCount() - 1, i, item)

        self.resizeColumnsToContents()



class WorkFlowMonitorWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        main_frame = QtWidgets.QFrame()
        self.setCentralWidget(main_frame)
        self.main_layout = QtWidgets.QGridLayout(main_frame)
        self.status_table = StatusTable(self)
        self.main_layout.addWidget(self.status_table)
        self.open_connections = []
        # self.update_statuses()

    def open_connection(self, servername: str, username: str = None, key_filename: str = None):
        server = tcmu.connect.Connection(servername, username=username, key_filename=key_filename)
        server.open()
        self.open_connections.append(server)

    def get_status_data(self):
        data = tcmu.workflow_db.read_all()
        for hsh, d in data.items():
            d['server'] = 'Local'

        for connection in self.open_connections:
            new_data = tcmu.workflow_db.read_remote(connection)
            for hsh, d in new_data.items():
                data[hsh] = d
                d['server'] = str(f'{connection.username}@{connection.server}')

        return data

    def update_statuses(self):
        data = self.get_status_data()
        self.status_table.reset()

        for hsh, d in data.items():
            print(hsh, d)
            start_time = d.get('start_time', None)
            if start_time is not None and d['status'] == 'RUNNING':
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d-%H-%M-%S')
                td = datetime.datetime.now() - start_time
                run_time = ''
                if td >= datetime.timedelta(days=1):
                    run_time += f'{td.days}-'
                if td >= datetime.timedelta(hours=1):
                    run_time += f'{td.seconds//(60*60):02}:'
                run_time += f'{td.seconds//60%60:02}:{td.seconds%60:02}'
            else:
                run_time = ''
            self.status_table.add_row((hsh, d['server'], d['status'], d['stage'], run_time))


class WorkFlowMonitor(QtWidgets.QApplication):
    def __init__(self):
        super().__init__()
        fontpath = os.path.split(__file__)[0] + '/../fonts/Inter/Inter-VariableFont_opsz,wght.ttf'
        QtGui.QFontDatabase.addApplicationFont(fontpath)
        fontpath = os.path.split(__file__)[0] + '/../fonts/ibm_plex_mono/IBMPlexMono-Regular.ttf'
        QtGui.QFontDatabase.addApplicationFont(fontpath)
        self.setStyle('Fusion')

        self.window = WorkFlowMonitorWindow()
        self.window.show()

    def exit(self):
        for connection in self.window.open_connections:
            connection.close()

        super().exit()


if __name__ == '__main__':
    app = WorkFlowMonitor()
    # app.window.open_connection('ada.labs.vu.nl', 'yhk800')
    app.window.update_statuses()
    app.exec()
