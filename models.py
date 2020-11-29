import datetime

from PyQt5 import QtWidgets, QtGui, QtCore

from config import Config


def hex_to_rgb(value):
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


class ProjectItem(QtWidgets.QGraphicsItem):

    def __init__(self, project_id, project_name, start_date, finish_date, color, status=0):
        super().__init__()

        self.project_id = project_id

        self.hex_color = color
        self.border_color = QtGui.QColor(0, 0, 0)
        self.border_pen = QtGui.QPen(self.border_color)
        self.text_color = QtGui.QColor(255, 255, 240)

        self.brush_color = QtGui.QColor(*hex_to_rgb(self.hex_color))
        self.brush = QtGui.QBrush(self.brush_color)

        self.isClicked = False
        self.setZValue(10)

        self.project_name = project_name
        self.font = Config.MAIN_FONT
        self.font.setPixelSize(16)

        self.text_options = QtGui.QTextOption(QtCore.Qt.AlignCenter)

        self.start_date = datetime.date.fromisoformat(start_date) if type(start_date) is str else start_date
        self.finish_date = datetime.date.fromisoformat(finish_date) if type(finish_date) is str else finish_date

        self.status = status

        self.rect = QtCore.QRectF(0, 0, Config.SCALE_WIDTH * (self.finish_date - self.start_date).days,
                                  Config.LINE_HEIGHT)

        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QtCore.QRectF(0, 0,
                             Config.SCALE_WIDTH * (self.finish_date - self.start_date).days,
                             Config.LINE_HEIGHT)

    def paint(self, Qpainter, QStyleOptionGraphicsItem, widget=None):
        self.rect = QtCore.QRectF(0, 0, Config.SCALE_WIDTH * (self.finish_date - self.start_date).days,
                                  Config.LINE_HEIGHT)
        if self.isClicked:
            self.border_pen.setWidth(3)
            Qpainter.setPen(self.border_pen)
        else:
            self.border_pen.setWidth(1)
            Qpainter.setPen(self.border_pen)
        Qpainter.setBrush(self.brush)
        Qpainter.drawRoundedRect(self.rect, Config.LINE_HEIGHT // 2, Config.LINE_HEIGHT // 2)

        if self.status == 1:
            Qpainter.setBrush(QtGui.QBrush(QtCore.Qt.BDiagPattern))
            Qpainter.drawRoundedRect(self.rect, Config.LINE_HEIGHT // 2, Config.LINE_HEIGHT // 2)

        if self.status == 2:
            Qpainter.setBrush(QtGui.QBrush(QtCore.Qt.Dense7Pattern))
            Qpainter.drawRoundedRect(self.rect, Config.LINE_HEIGHT // 2, Config.LINE_HEIGHT // 2)

        Qpainter.setFont(self.font)
        Qpainter.setPen(self.text_color)
        Qpainter.drawText(self.rect, self.project_name, self.text_options)

    def change_color(self, color):
        self.hex_color = color
        self.brush_color = QtGui.QColor(*hex_to_rgb(self.hex_color))
        self.brush = QtGui.QBrush(self.brush_color)
        self.redraw_project()

    def change_name(self, project_name):
        self.project_name = project_name
        self.redraw_project()

    def redraw_project(self):
        self.update(self.sceneBoundingRect())
        self.scene().update(self.sceneBoundingRect())

    def hoverMoveEvent(self, move_event):
        hover_brush_color = self.brush_color.darker(125)
        self.brush = QtGui.QBrush(hover_brush_color)
        super().hoverMoveEvent(move_event)

    def hoverLeaveEvent(self, move_event):
        self.brush = QtGui.QBrush(self.brush_color)
        super().hoverLeaveEvent(move_event)

    def mousePressEvent(self, mouse_event):
        self.scene().itemClicked.emit(self)
        super().mousePressEvent(mouse_event)


def create_project_items(projects_list):
    projects_items = []
    for project in projects_list:
        projects_items.append(ProjectItem(*project))
    return projects_items


def update_project_items(project_items):
    for project in project_items:
        if project.finish_date < datetime.date.today() and project.status != 1:
            project.status = 2
        elif project.status != 1:
            project.status = 0
    return project_items