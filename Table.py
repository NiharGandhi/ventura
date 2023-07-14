import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLineEdit, QTableView, QPushButton, QLabel, \
    QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex
from PyQt5.QtGui import QIcon
import datetime
import os
import copy

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def headerData(self, section, orientation, role=Qt.ItemDataRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except IndexError:
                return QVariant()
        elif orientation == Qt.Orientation.Vertical:
            try:
                return self._df.index.tolist()[section]
            except IndexError:
                return QVariant()

    def rowCount(self, parent=QModelIndex()):
        return self._df.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._df.shape[1]

    def data(self, index, row=Qt.ItemDataRole.DisplayRole):
        if row != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if not index.isValid():
            return QVariant()
        return QVariant(str(self._df.iloc[index.row(), index.column()]))



class Viewer(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 1100, 500
        self.resize(self.window_width, self.window_height)
        self.setWindowTitle('VIEWER')
        self.setWindowIcon(QIcon('icon.png'))
        self.df = None
        self.setStyleSheet('''
            QWidget {
                font-size: 15px;
            }
            QComboBox {
                width: 160px;
            }
            QPushButton {
                width: 100px
            }
        ''')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

    # def getfile(self):
    #     '''This function will get the address of the file'''
    #     self.filename = QFileDialog.getOpenFileName(filter='csv (*.csv)')[0]
    #     print(self.filename)
    #     return self.filename.replace('/', '\\')
    #     # self.readData()

    def retrieveDataset(self):
        try:
            # print(self.filename)
            urlSource = QFileDialog.getOpenFileName(filter='csv (*.csv)')[0]
            self.df = pd.read_csv(urlSource)
            self.df.fillna('')
            self.model = PandasModel(self.df)
            self.table.setModel(self.model)

            self.comboColumns.clear()
            self.comboColumns.addItems(self.df.columns)
        except Exception as e:
            self.statusLabel.setText(str(e))
            return

    def searchItem(self, v):
        if self.df is None:
            return

        column_index = self.df.columns.get_loc(self.comboColumns.currentText())
        for row_index in range(self.model.rowCount()):
            if v in self.model.index(row_index, column_index).data():
                self.table.setRowHidden(row_index, False)
            else:
                self.table.setRowHidden(row_index, True)


    def initUI(self):
        sourceLayout = QHBoxLayout()
        self.layout.addLayout(sourceLayout)

        label = QLabel('Data Source: ')
        # self.dataSourceField = QLineEdit()
        # label.setBuddy(self.dataSourceField)
        label2 = QLabel('Search: ')

        buttonRetrieve = QPushButton('&Open', clicked=self.retrieveDataset)
        # buttonOpen = QPushButton('&Open File', clicked=self.getfile)

        sourceLayout.addWidget(label)
        # sourceLayout.addWidget(self.dataSourceField)
        sourceLayout.addWidget(buttonRetrieve)
        sourceLayout.addWidget(label2)
        # sourceLayout.addWidget(buttonOpen)

        # Search Field
        searchLayout = QHBoxLayout()
        self.layout.addLayout(searchLayout)

        self.seacrhField = QLineEdit()
        self.seacrhField.textChanged.connect(self.searchItem)
        sourceLayout.addWidget(self.seacrhField)

        self.comboColumns = QComboBox()
        searchLayout.addWidget(self.comboColumns)

        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.layout.addWidget(self.table)

        self.statusLabel = QLabel()
        self.statusLabel.setText('')
        self.layout.addWidget(self.statusLabel)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 17px;
        }
    ''')
    myApp = Viewer()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window')
