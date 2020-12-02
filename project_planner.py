import sys, os
import calendar
import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

from ui.main_window import Ui_MainWindow
from ui.add_project_window import Ui_Add_project

from config import Config
from timeline import Timeline
from database import db
from models import ProjectItem, create_project_items, update_project_items
from custom_widgets import ComboColor


def create_combo_status_widget():
    combo_status = QtWidgets.QComboBox()
    combo_status.addItem("In progress")
    combo_status.addItem("Done")
    combo_status.addItem("Not done")
    return combo_status


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setFixedSize(1220, 538)
        self.setWindowTitle("Project planner")
        self.color = QtGui.QColor(255, 170, 170)
        self.weekend_color = QtGui.QColor(255, 0, 0)
        self.font = Config.MAIN_FONT
        self.setFont(self.font)
        self.setLocale(Config.LOCALE)
        self.header_height = Config.SCALE_HEIGHT + 2 * self.font.pixelSize()
        self.header_offset = 10

        self.add_project_window = AddProjectWindow()

        self.combo_color = ComboColor()
        self.combo_color_item_highlighted(0)

        self.combo_status = create_combo_status_widget()

        self.start_date_widget = QtWidgets.QDateEdit()
        self.start_date_widget.setDate(datetime.date.today())
        self.finish_date_widget = QtWidgets.QDateEdit()
        self.finish_date_widget.setDate(datetime.date.today())
        self.start_date_widget.setCalendarPopup(True)
        self.finish_date_widget.setCalendarPopup(True)

        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.setColumnWidth(0, 440)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.setColumnWidth(4, 120)

        self.tableWidget.setCellWidget(0, 1, self.start_date_widget)
        self.tableWidget.setCellWidget(0, 2, self.finish_date_widget)
        self.tableWidget.setCellWidget(0, 3, self.combo_color)
        self.tableWidget.setCellWidget(0, 4, self.combo_status)

        self.projects_list = db.get_projects()
        timeline = Timeline(self.projects_list)
        self.dates = timeline.generate_timeline()
        self.timeline_scene = self.create_scene()
        self.graphicsView.setScene(self.timeline_scene)

        self.projects = create_project_items(self.projects_list)
        self.projects = update_project_items(self.projects)
        self.show_projects()

        self.timeline_scene.itemClicked.connect(self.project_clicked)
        self.combo_color.currentIndexChanged.connect(self.combo_color_changed)
        self.combo_status.currentIndexChanged.connect(self.combo_status_changed)
        self.start_date_widget.dateChanged.connect(self.date_changed)
        self.finish_date_widget.dateChanged.connect(self.date_changed)
        self.tableWidget.itemChanged.connect(self.project_name_changed)

        self.add_project_button.clicked.connect(self.add_project_clicked)
        self.delete_project_button.clicked.connect(self.delete_project_clicked)

    def create_scene(self):
        scene = TimelineScene()

        for i in range(1, len(self.dates) + 1):
            current_date = self.dates[i - 1]
            if current_date == datetime.date.today():
                pen = QtGui.QPen(self.weekend_color)
                pen.setWidth(3)
                line = scene.addLine(i * Config.SCALE_WIDTH, self.header_height + self.header_offset,
                                     i * Config.SCALE_WIDTH,
                                     Config.LINE_HEIGHT * Config.MAX_LINES + self.header_height + self.header_offset,
                                     pen)
                line.setZValue(100)
            scene.addLine(i * Config.SCALE_WIDTH, 0, i * Config.SCALE_WIDTH, Config.SCALE_HEIGHT - 2)

            date_string = QtWidgets.QGraphicsTextItem(current_date.strftime("%d.%m"))
            date_string.setFont(self.font)
            date_string.adjustSize()
            date_string.setPos((i * Config.SCALE_WIDTH) - date_string.textWidth() // 2, Config.SCALE_HEIGHT)
            if current_date.weekday() in [5, 6]:
                date_string.setDefaultTextColor(self.weekend_color)
            scene.addItem(date_string)

            day_abbr = calendar.day_abbr[calendar.weekday(current_date.year, current_date.month, current_date.day)]
            day_name_item = QtWidgets.QGraphicsTextItem(day_abbr)
            day_name_item.setFont(self.font)
            day_name_item.adjustSize()
            day_name_item.setPos((i * Config.SCALE_WIDTH) - day_name_item.textWidth() // 2,
                                 self.header_height - self.font.pixelSize())
            if current_date.weekday() in [5, 6]:
                day_name_item.setDefaultTextColor(self.weekend_color)
            scene.addItem(day_name_item)

        for i in range(Config.MAX_LINES + 1):
            scene.addLine(0, i * Config.LINE_HEIGHT + self.header_height + 10,
                          (len(self.dates) + 1) * Config.SCALE_WIDTH,
                          i * Config.LINE_HEIGHT + self.header_height + self.header_offset)

        return scene

    def show_projects(self):
        for project in self.projects:
            self.add_project_item(project)

    def add_project_item(self, project):
        try:
            start_pos = self.dates.index(project.start_date) + 1
            finish_pos = self.dates.index(project.finish_date)
            project.setPos(start_pos * Config.SCALE_WIDTH,
                           self.header_height + self.header_offset)
            self.timeline_scene.addItem(project)
            collision = list(filter(lambda x: type(x) == ProjectItem, self.timeline_scene.collidingItems(project)))
            while collision:
                project.moveBy(0, Config.LINE_HEIGHT)
                collision = list(filter(lambda x: type(x) == ProjectItem, self.timeline_scene.collidingItems(project)))
        except ValueError:
            self.graphicsView_reset()

    def graphicsView_reset(self):
        self.projects_list = db.get_projects()
        timeline = Timeline(self.projects_list)
        self.dates = timeline.generate_timeline()
        self.timeline_scene = self.create_scene()
        self.graphicsView.setScene(self.timeline_scene)
        self.projects = create_project_items(self.projects_list)
        self.show_projects()
        self.timeline_scene.itemClicked.connect(self.project_clicked)

    def project_clicked(self, current_project):
        self.tableWidget.blockSignals(True)
        self.start_date_widget.blockSignals(True)
        self.finish_date_widget.blockSignals(True)

        current_project.isClicked = True
        current_project.setZValue(50)
        current_project.redraw_project()

        for project in self.projects:
            if project != current_project:
                project.isClicked = False
                project.setZValue(10)
                project.redraw_project()

        self.tableWidget.item(0, 0).setText(current_project.project_name)
        self.tableWidget.item(0, 0).setData(0x100, current_project.project_id)
        self.tableWidget.item(0, 0).setTextAlignment(QtCore.Qt.AlignCenter)

        self.tableWidget.item(0, 1).setData(0x100, current_project.project_id)
        self.start_date_widget.setDate(current_project.start_date)
        self.tableWidget.item(0, 2).setData(0x100, current_project.project_id)
        self.finish_date_widget.setDate(current_project.finish_date)
        self.start_date_widget.setMaximumDate(self.finish_date_widget.date().addDays(-1))
        self.finish_date_widget.setMinimumDate(self.start_date_widget.date().addDays(1))

        self.tableWidget.item(0, 3).setData(0x100, current_project.project_id)
        self.combo_color.setCurrentIndex(self.combo_color.findData(current_project.hex_color, 0x200))

        self.tableWidget.item(0, 4).setData(0x100, current_project.project_id)
        self.combo_status.setCurrentIndex(current_project.status)
        self.combo_status.update()

        self.tableWidget.blockSignals(False)
        self.start_date_widget.blockSignals(False)
        self.finish_date_widget.blockSignals(False)

    def project_name_changed(self):
        new_name = self.tableWidget.item(0, 0).text()
        for project in self.projects:
            if self.tableWidget.item(0, 0).data(0x100) == project.project_id:
                db.update_name(project.project_id, new_name)
                project.change_name(new_name)

    def combo_color_changed(self):
        color = self.combo_color.currentData(0x200)
        for project in self.projects:
            if self.tableWidget.item(0, 3).data(0x100) == project.project_id:
                project.change_color(color)
                db.update_color(project.project_id, color)
        self.combo_color.setStyleSheet(f"""background: #{color}; 
                                           selection-background-color: #{color};""")

    def combo_color_item_highlighted(self, index):
        color = self.combo_color.itemData(index, 0x200)
        self.combo_color.setStyleSheet(f"""background: #{color}; 
                                           selection-background-color: #{color};""")

    def date_changed(self):
        self.start_date_widget.setMaximumDate(self.finish_date_widget.date().addDays(-1))
        self.finish_date_widget.setMinimumDate(self.start_date_widget.date().addDays(1))
        start_date = self.start_date_widget.date().toPyDate()
        finish_date = self.finish_date_widget.date().toPyDate()

        for project in self.projects:
            if self.tableWidget.item(0, 0).data(0x100) == project.project_id:
                db.update_date(project.project_id, start_date, finish_date)
                self.timeline_scene.removeItem(project)
                project.start_date = start_date
                project.finish_date = finish_date
                if start_date < self.dates[0] or finish_date > self.dates[-1]:
                    self.graphicsView_reset()
                    return
                self.add_project_item(project)

        self.check_for_unnecessary_dates()
        for project in self.projects:
            while self.check_for_empty_space(project):
                pass

    def check_for_empty_space(self, project):
        is_project_moved = False
        if project.scenePos().y() >= self.header_height + self.header_offset + Config.LINE_HEIGHT:
            project.moveBy(0, -Config.LINE_HEIGHT)
            is_project_moved = True
            collision = list(filter(lambda x: type(x) == ProjectItem, self.timeline_scene.collidingItems(project)))
            if collision:
                project.moveBy(0, Config.LINE_HEIGHT)
                is_project_moved = False
        return is_project_moved

    def check_for_unnecessary_dates(self):
        if self.projects and len(self.dates) > 28:
            earliest_date = self.projects[0].start_date
            last_date = self.projects[0].finish_date
            for project in self.projects:
                if earliest_date > project.start_date:
                    earliest_date = project.start_date
                if last_date < project.finish_date:
                    last_date = project.finish_date
                if earliest_date > self.dates[0] or last_date < self.dates[-1]:
                    self.graphicsView_reset()
                    return
        elif len(self.dates) > 28:
            self.graphicsView_reset()
            return

    def combo_status_changed(self):
        status = self.combo_status.currentIndex()
        for project in self.projects:
            if self.tableWidget.item(0, 4).data(0x100) == project.project_id:
                project.status = status
                project.redraw_project()
                db.update_status(project.project_id, status)

    def add_project_clicked(self):
        self.add_project_window.setModal(True)
        self.add_project_window.show()

    def delete_project_clicked(self):
        for project in self.projects:
            if self.tableWidget.item(0, 0).data(0x100) == project.project_id:
                id_ = project.project_id
                self.timeline_scene.removeItem(project)
                self.projects.remove(project)
                db.delete_project(id_)
        self.check_for_unnecessary_dates()
        for project in self.projects:
            while self.check_for_empty_space(project):
                pass

    def wheelEvent(self, event):
        current_pos = self.graphicsView.horizontalScrollBar().sliderPosition()
        if event.angleDelta().y() > 0:
            self.graphicsView.horizontalScrollBar().setSliderPosition(current_pos - 50)
        else:
            self.graphicsView.horizontalScrollBar().setSliderPosition(current_pos + 50)

class TimelineScene(QtWidgets.QGraphicsScene):
    itemClicked = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()


class AddProjectWindow(QtWidgets.QDialog, Ui_Add_project):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(828, 116)
        self.tableWidget.setColumnWidth(0, 440)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.setFont(Config.MAIN_FONT)
        self.setLocale(Config.LOCALE)

        self.start_date_widget = QtWidgets.QDateEdit()
        self.start_date_widget.setDate(datetime.date.today())
        self.finish_date_widget = QtWidgets.QDateEdit()
        self.finish_date_widget.setDate(datetime.date.today())
        self.start_date_widget.setCalendarPopup(True)
        self.finish_date_widget.setCalendarPopup(True)
        self.start_date_widget.setDate(datetime.date.today())
        self.finish_date_widget.setDate(datetime.date.today())

        self.comboColor = ComboColor()
        self.tableWidget.setCellWidget(0, 1, self.start_date_widget)
        self.tableWidget.setCellWidget(0, 2, self.finish_date_widget)
        self.tableWidget.setCellWidget(0, 3, self.comboColor)
        self.tableWidget.item(0, 0).setText("Type here")
        self.tableWidget.item(0, 0).setTextAlignment(QtCore.Qt.AlignCenter)

        self.is_changes_done = False

    def accept(self):
        name = self.tableWidget.item(0, 0).text()
        start_date = self.start_date_widget.date().toPyDate()
        finish_date = self.finish_date_widget.date().toPyDate()
        color = self.comboColor.currentData(0x200)
        if finish_date > start_date and len(name) > 0:
            id_ = db.add_project(name, start_date, finish_date, color)
            new_project_item = ProjectItem(id_, name, start_date, finish_date, color)
            window.projects.append(new_project_item)
            window.add_project_item(new_project_item)
            self.tableWidget.item(0, 0).setText("Type here")
            self.start_date_widget.setDate(datetime.date.today())
            self.finish_date_widget.setDate(datetime.date.today())
            self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
