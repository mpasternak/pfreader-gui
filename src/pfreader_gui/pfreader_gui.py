import os
import sys
import tempfile
from pathlib import Path

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QDir, QSortFilterProxyModel, QCoreApplication
from PyQt5.QtWidgets import QFileSystemModel
from pfreader.core import get_loxfile_data, dir_contains_pflex_data, get_machines, get_year_dirs
from pfreader.output import get_databook

from src.pfreader_gui.exceptions import UnsupportedPlatform
from .mainwindow_ui import Ui_MainWindow

QFileDialog_platform_kwargs = {}
if sys.platform == 'darwin':
    QFileDialog_platform_kwargs = dict(
        options=QtWidgets.QFileDialog.DontUseNativeDialog)


class ExcludeSomeNames(QSortFilterProxyModel):
    def filterAcceptsRow(self, p_int, idx):
        index = self.sourceModel().index(p_int, 0, idx)
        s = self.sourceModel().data(index)

        if s.startswith("Preboot"):
            return False

        if s.startswith("Volumes"):
            return True

        path = self.sourceModel().filePath(index)
        contains = dir_contains_pflex_data(path)

        if contains:
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
        if sys.platform == 'darwin':
            qfs.setRootPath("/Volumes")
        else:
            raise UnsupportedPlatform(sys.platform)

        qfs.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)

        exclude = ExcludeSomeNames(self.window)
        exclude.setSourceModel(qfs)

        self.treeView.setModel(exclude)
        self.treeView.setRootIndex(exclude.mapFromSource(qfs.index("/Volumes")))

        self.treeView.doubleClicked.connect(self.volumeDoubleClicked)

        self.qfs = qfs
        self.exclude = exclude

        self.treeView.setSortingEnabled(True)
        self.treeView.setColumnWidth(0, 300)

        self.openFileButton.clicked.connect(self.openFileButtonClicked)

    def volumeDoubleClicked(self, idx):
        fn = self.qfs.filePath(self.exclude.mapToSource(idx))
        m = list(get_machines(fn))
        if len(m) == 1:
            path = os.path.join(fn, m[0])
            yd = list(get_year_dirs(path))
            if len(yd) == 1:
                path = os.path.join(path, str(yd[0]))
            self._openFileDialog(path)
        else:
            self._openFileDialog(fn)

    def openFileButtonClicked(self, *args, **kw):
        path = QtCore.QStandardPaths.locate(
            QtCore.QStandardPaths.DocumentsLocation, "",
            QtCore.QStandardPaths.LocateDirectory)
        self.openFileDialog(path)

    def _openFileDialog(self, path):
        fn = QtWidgets.QFileDialog.getOpenFileName(
            self.window, _("Open", "Choose file"), path,
            _("Open", "LOX files (*.lox);;All files (*.*)"),

            **QFileDialog_platform_kwargs)
        if fn[0]:
            self.openLOXFile(fn[0])

    def openLOXFile(self, path):
        if path.lower().endswith(".lox"):
            r = get_loxfile_data(path)
            db = get_databook(r)
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as fp:
                fp.write(db.xlsx)
            import os
            os.system('open "%s"' % fp.name)


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
