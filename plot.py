from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as Navi
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import sip

# Need a Canvas for Graph
class MatplotlibCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=120):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MatplotlibCanvas,self).__init__(fig)
        fig.tight_layout()



class Ui_GraphWindoow(object):
    def setupUi(self, GraphWindoow):
        GraphWindoow.setObjectName("GraphWindoow")
        GraphWindoow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(GraphWindoow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.ComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.ComboBox.setObjectName("ComboBox")
        self.horizontalLayout.addWidget(self.ComboBox)
        self.OpenButton = QtWidgets.QPushButton(self.centralwidget)
        self.OpenButton.setObjectName("OpenButton")
        self.horizontalLayout.addWidget(self.OpenButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        GraphWindoow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(GraphWindoow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 18))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        GraphWindoow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(GraphWindoow)
        self.statusbar.setObjectName("statusbar")
        GraphWindoow.setStatusBar(self.statusbar)
        self.actionOpen_CSV = QtWidgets.QAction(GraphWindoow)
        self.actionOpen_CSV.setObjectName("actionOpen_CSV")
        self.actionExit = QtWidgets.QAction(GraphWindoow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen_CSV)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(GraphWindoow)
        QtCore.QMetaObject.connectSlotsByName(GraphWindoow)

        self.filename = ''
        self.canv = MatplotlibCanvas(self)
        self.df = []

        self.toolbar = Navi(self.canv, self.centralwidget)
        self.horizontalLayout.addWidget(self.toolbar)

        self.themes = ['bmh', 'classic', 'dark_background', 'seaborn', 'fast', 'ggplot', 'grascale']
        self.ComboBox.addItems(self.themes)

        self.OpenButton.clicked.connect(self.getFile)
        self.ComboBox.currentIndexChanged['QString'].connect(self.update)

    def update(self, value):
        print("Value from Combo Box: ", value)
        plt.clf()
        plt.style.use(value)
        try:
            self.horizontalLayout.removeWidget(self.toolbar)
            self.verticalLayout.removeWidget(self.canv)

            sip.delete(self.toolbar)
            sip.delete(self.canv)
            self.toolbar = None
            self.canv = None
            self.verticalLayout.removeItem(self.spacerItem1)

        except Exception as e:
            print(e)
            pass
        self.canv = MatplotlibCanvas(self)
        self.toolbar = Navi(self.canv, self.centralwidget)

        self.horizontalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.canv)

        self.canv.axes.cla()
        ax = self.canv.axes
        self.df.plot(ax = self.canv.axes)
        legend = ax.legend()
        legend.set_draggable(True)
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_title('Title')
        self.canv.draw()

    def getFile(self):
        '''This function will get the address of the file'''
        self.filename = QFileDialog.getOpenFileName(filter='csv (*.csv)')[0]
        self.readData()

    def readData(self):
        self.df = pd.read_csv(self.filename, encoding='utf-8').fillna(0)
        self.update(self.themes[0]) # Default Theme : bmh



    def retranslateUi(self, GraphWindoow):
        _translate = QtCore.QCoreApplication.translate
        GraphWindoow.setWindowTitle(_translate("GraphWindoow", "MainWindow"))
        self.label.setText(_translate("GraphWindoow", "Select Theme"))
        self.OpenButton.setText(_translate("GraphWindoow", "Open"))
        self.menuFile.setTitle(_translate("GraphWindoow", "File"))
        self.actionOpen_CSV.setText(_translate("GraphWindoow", "Open CSV"))
        self.actionExit.setText(_translate("GraphWindoow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    GraphWindoow = QtWidgets.QMainWindow()
    ui = Ui_GraphWindoow()
    ui.setupUi(GraphWindoow)
    GraphWindoow.show()
    sys.exit(app.exec_())
