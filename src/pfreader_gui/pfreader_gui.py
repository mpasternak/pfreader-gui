import os
import sys
import tempfile
from pathlib import Path

from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtCore import QDir, QSortFilterProxyModel, QCoreApplication
from PyQt5.QtWidgets import QFileSystemModel, QMessageBox, QProgressDialog
from pfreader.core import get_loxfile_data, dir_contains_pflex_data, get_machines, get_year_dirs
from pfreader.output import get_databook

from pfreader_gui.util import autofit_databook
from .__version__ import VERSION
from .exceptions import UnsupportedPlatform
from .mainwindow_ui import Ui_MainWindow

QFileDialog_platform_kwargs = {}
if sys.platform == 'darwin':
    # QFileDialog_platform_kwargs = dict(
    #     options=QtWidgets.QFileDialog.DontUseNativeDialog)
    pass

class ExcludeSomeNamesModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, p_int, idx):
        index = self.sourceModel().index(p_int, 0, idx)
        s = self.sourceModel().data(index)

        if sys.platform == 'darwin':
            if s.startswith("Preboot"):
                return False

            if s.startswith("Volumes"):
                return True

        path = self.sourceModel().filePath(index)

        contains = dir_contains_pflex_data(path)
        if contains:
            return True

        older_prisma = get_year_dirs(path)
        for elem in older_prisma:
            # There may be year dirs in the root directory for older machines
            return True

        return False

    pass


_ = QCoreApplication.translate


class PFReaderGUI(Ui_MainWindow):
    def __init__(self, win):
        Ui_MainWindow.__init__(self)
        self.window = win
        self.setupUi(win)

        qfs = QFileSystemModel(self.treeView)
        exclude = ExcludeSomeNamesModel()
        exclude.setSourceModel(qfs)
        self.treeView.setModel(exclude)

        if sys.platform == 'darwin':
            qfs.setRootPath("/Volumes")
            self.treeView.setRootIndex(exclude.mapFromSource(qfs.index("/Volumes")))
            qfs.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
        else:
            raise UnsupportedPlatform(sys.platform)

        self.treeView.doubleClicked.connect(self.volumeDoubleClicked)

        self.qfs = qfs
        self.exclude = exclude

        self.treeView.setSortingEnabled(True)
        self.treeView.setColumnWidth(0, 300)
        self.treeView.setItemsExpandable(False)
        self.treeView.setRootIsDecorated(False)

        self.openFileButton.clicked.connect(self.openFileButtonClicked)
        self.aboutButton.clicked.connect(self.aboutButtonClicked)

        for elem in range(1, 4):
            self.treeView.hideColumn(elem)

    def directoryChanged(self, *args, **kw):
        print("CHANGE " * 50, args)
        pass

    def aboutButtonClicked(self, *args, **kw):
        QMessageBox.about(
            self.window,
            "pfreader-gui",
            f"pfreader-gui {VERSION}\r\n\r\n"
            "(C) 2018 Michał Pasternak <michal.dtz@gmail.com>\r\n\r\n"
            "(C) 2018 IPLweb, http://www.iplweb.pl/\r\n\r\n"
            "Open source software, not affiliated with Baxter® Inc., provided for "
            "educational purposes. Do not use with any real data. MIT license. "
        )

    def volumeDoubleClicked(self, idx):
        fn = self.qfs.filePath(self.exclude.mapToSource(idx))

        # "New" PrismaFlex software on USB stick: creates MachineID/Year/LOX files
        m = list(get_machines(fn))
        if len(m) == 1:
            path = os.path.join(fn, m[0])
            yd = list(get_year_dirs(path))
            if len(yd) == 1:
                path = os.path.join(path, str(yd[0]))
            self._openFileDialog(path)
            return

        # "Old" PrismaFlex machines on CF card: year/LOX files
        for elem in get_year_dirs(fn):
            self._openFileDialog(fn)
            return

        QMessageBox.warning(
            self.window,
            "No PrismaFlex® data detected",
            'This device most likely does not contain PrismaFlex® data. If you would like '
            'to open individual LOX files, use "Open file" button. '
        )

    def openFileButtonClicked(self, *args, **kw):
        path = QtCore.QStandardPaths.locate(
            QtCore.QStandardPaths.DocumentsLocation, "",
            QtCore.QStandardPaths.LocateDirectory)
        self._openFileDialog(path)

    def _openFileDialog(self, path):
        fn = QtWidgets.QFileDialog.getOpenFileName(
            self.window, _("Open", "Choose file"), path,
            _("Open", "LOX files (*.lox)"),

            **QFileDialog_platform_kwargs)
        if fn[0]:
            self.openLOXFile(fn[0])

    def openLOXFile(self, path):
        if not path.lower().endswith(".lox"):
            QMessageBox.error(
                self.window,
                _("Err", "Error"),
                _("Err", "The filename must end with .LOX extension.")
            )
            return

        wait = QProgressDialog(_("Progress", 'Reading LOX file data...'), None, 0, 0)
        wait.setWindowTitle(" ")
        wait.setMaximum(5)
        wait.show()

        def updateProgressBar(msg, value):
            wait.setValue(value)
            wait.setLabelText(msg)
            QCoreApplication.processEvents()

        updateProgressBar(_("Progress", "Reading LOX file..."), 0)
        r = get_loxfile_data(path)

        updateProgressBar(_("Progress", "Creating initial XLSX file..."), 1)
        db = get_databook(r)

        updateProgressBar(_("Progress", "Resizing columns..."), 2)
        xl_out = autofit_databook(db)

        updateProgressBar(_("Progress", "Writing XLSX file..."), 3)
        with tempfile.NamedTemporaryFile(
                prefix=os.path.splitext(os.path.basename(path))[0],
                suffix='.xlsx',
                delete=False) as fp:
            xl_out.save(fp)

        updateProgressBar(_("Progress", "Opening XLSX file..."), 4)
        if sys.platform == "darwin":
            os.system('open "%s"' % fp.name)

        else:
            # TODO: platform-independetn way of XLS opening
            raise UnsupportedPlatform(sys.platform)

        updateProgressBar(_("Progress", "Done!"), 5)


def entry_point():
    app = QtWidgets.QApplication(sys.argv)

    qtranslator = QtCore.QTranslator()
    locale = QtCore.QLocale.system().name()
    translations_path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)
    qtranslator.load('qt_%s' % locale, translations_path)
    qtranslator.load("qtbase_%s" % locale, translations_path)
    app.installTranslator(qtranslator)

    win = QtWidgets.QMainWindow()

    icon_path = (Path(__file__) / ".." / "pfreader_gui.svg").resolve()
    icon = QtGui.QIcon(str(icon_path))
    win.setWindowIcon(icon)
    app.setWindowIcon(icon)

    prog = PFReaderGUI(win)
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    entry_point()
