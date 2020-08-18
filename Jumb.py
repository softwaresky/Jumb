import os
import sys
import random
import pprint
import copy
from functools import partial
import datetime
import time

try:
    from PySide import QtGui, QtCore
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtSvg import *
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtSvg import *

def find_data_file(filename=""):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

this_dir = find_data_file("")
img_dir = os.path.join(this_dir, "imgs", "dice")

DICT_DICE_IMG = {}
DICT_DICE_IMG[0] = os.path.join(img_dir, "Dice-0-b.png")
DICT_DICE_IMG[1] = os.path.join(img_dir, "Dice-1-b.png")
DICT_DICE_IMG[2] = os.path.join(img_dir, "Dice-2-b.png")
DICT_DICE_IMG[3] = os.path.join(img_dir, "Dice-3-b.png")
DICT_DICE_IMG[4] = os.path.join(img_dir, "Dice-4-b.png")
DICT_DICE_IMG[5] = os.path.join(img_dir, "Dice-5-b.png")
DICT_DICE_IMG[6] = os.path.join(img_dir, "Dice-6-b.png")


HAND_TURNS = 3
NUMBER_OF_DICE = 6
MAXIMUM_NUMBER_OF_PLAYERS= 4
NUMBER_OF_ROWS = 13
WIDTH_DICE_SIZE = 50

DICT_ROW_HEADER = {}
for i in range(6):
    DICT_ROW_HEADER[i] = "{0}".format(i+1)

DICT_ROW_HEADER[6] = "Max"
DICT_ROW_HEADER[7] = "Min"
DICT_ROW_HEADER[8] = "Trilling"
DICT_ROW_HEADER[9] = "Full House"
DICT_ROW_HEADER[10] = "Straight"
DICT_ROW_HEADER[11] = "Poker"
DICT_ROW_HEADER[12] = "Jamb"

DICT_COL_HEADER = {}
DICT_COL_HEADER[0] = "Free"
DICT_COL_HEADER[1] = "Up"
DICT_COL_HEADER[2] = "Down"
DICT_COL_HEADER[3] = "Max/Min"
DICT_COL_HEADER[4] = "Announcement"
DICT_COL_HEADER[5] = "Checkout"

q_style = """
QLabel#lblPlayerName {font-weight: bold; }
QLabel#lblTotalHeader {font-weight: bold; }
QLabel#lblColTotal {font-weight: bold; }
QLabel#lblTotal {font-weight: bold; font-size: 20px; color: DarkGreen;}
QLabel#lblColHeader {font-weight: bold; }
QLabel#lblRowHeader {font-weight: bold; }
"""

class DiceWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.held = False
        self.dice_value = 0

        self.set_value(0)

        self.build_ui()
        self.fill_dice()
        self.colorized_dice()

    def set_value(self, dice_value=None):
        if not self.held:
            if dice_value is None:
                self.dice_value = random.randint(1,6)
            else:
                self.dice_value = dice_value

    def fill_dice(self):
        self.stackedWdg.setCurrentIndex(self.dice_value)

    def get_value(self):
        return self.dice_value

    def set_held(self, state=True):
        self.held = state
        self.colorized_dice()

    def get_held(self):
        return self.held

    def hold_switch(self):
        self.set_held(not self.held)

    def colorized_dice(self):
        self.stackedWdg.setStyleSheet("QStackedWidget {background-color: %s}" % ("blue" if self.held else "transparent"))

    def mouse_press_event(self, event):

        if event.type() == QEvent.Type.MouseButtonPress or event.type() == QEvent.Type.MouseButtonDblClick:
            if event.button() == Qt.MouseButton.LeftButton:
                self.hold_switch()


    def build_ui(self):

        self.setContentsMargins(0,0,0,0)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignLeft)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.stackedWdg = QStackedWidget()
        # self.stackedWdg.setContentsMargins(5, 5, 5, 5)
        self.stackedWdg.setAutoFillBackground(True)

        self.stackedWdg.setFixedSize(WIDTH_DICE_SIZE, WIDTH_DICE_SIZE)

        main_layout.addWidget(self.stackedWdg)

        for dice in DICT_DICE_IMG:

            lblImg = QLabel()

            lblImg.mousePressEvent = self.mouse_press_event
            lblImg.setObjectName("lblDice")
            lblImg.setContentsMargins(5,5,5,5)

            img_path = DICT_DICE_IMG.get(dice)
            if img_path:
                pixmap = QPixmap(img_path)
                pixmap.scaledToWidth(WIDTH_DICE_SIZE, Qt.FastTransformation)
                lblImg.setPixmap(pixmap)

            lblImg.setFixedSize(WIDTH_DICE_SIZE, WIDTH_DICE_SIZE)

            lblImg.setScaledContents(True)

            self.stackedWdg.insertWidget(dice, lblImg)

        self.setLayout(main_layout)

class DicesTableWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.lst_diceWdg = []
        self.build_ui()

    def create_layout(self):
        item_layout = QHBoxLayout()

        for i in range(NUMBER_OF_DICE):
            diceWdg = DiceWdg()
            diceWdg.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            item_layout.addWidget(diceWdg)
            self.lst_diceWdg.append(diceWdg)

        return item_layout

    def reset_dice(self):
        for diceWdg in self.lst_diceWdg:
            if isinstance(diceWdg, DiceWdg):
                diceWdg.set_held(False)
                diceWdg.set_value(0)
                diceWdg.fill_dice()

    def roll_dice(self):

        end_dt = datetime.datetime.now() + datetime.timedelta(seconds=1)

        while datetime.datetime.now() < end_dt:
            for diceWdg in self.lst_diceWdg:
                if isinstance(diceWdg, DiceWdg):
                    diceWdg.set_value()
                    diceWdg.fill_dice()

            QApplication.processEvents()

    def get_dice_value(self):
        dict_result = {}
        for diceWdg in self.lst_diceWdg:
            if isinstance(diceWdg, DiceWdg):
                value = diceWdg.get_value()

                if value not in dict_result:
                    dict_result[value] = 0
                dict_result[value] += 1

        return dict_result

    def get_sign_dict(self):

        """
        [7] = "Max"
        [8] = "Min"
        [9] = "Trilling"
        [10] = "Full House"
        [11] = "Straight"
        [12] = "Poker"
        [13] = "Jamb"

        :return:
        """

        dict_result = {}

        for i in range(len(DICT_ROW_HEADER)):
            dict_result[i] = 0

        dict_dices = self.get_dice_value()

        lst_dice = []

        for dice in sorted(dict_dices):
            dice_count = dict_dices.get(dice)
            value = dice_count * dice

            for i in range(dice_count):
                lst_dice.append(dice)

            sign_index = dice
            dict_result[sign_index] = value
            add_value = 0

            if dice_count >= 3:  # Trilling
                sign_index = 9
                add_value = 30
                dict_result[sign_index] = value + add_value

                for dice_other in sorted(dict_dices):
                    other_dice_count = dict_dices.get(dice_other)
                    if dice != dice_other and other_dice_count and other_dice_count == 2:
                        sign_index = 10
                        add_value = 40
                        dict_result[sign_index] = value + (dice_other * other_dice_count) + add_value

                if dice_count >= 4:  # Poker
                    add_value = 50
                    sign_index = 12
                    dict_result[sign_index] = value + add_value

                    if dice_count >= 5:  # Low jamb
                        sign_index = 13
                        add_value = 60
                        if dice == 1:
                            value = 100
                            add_value = 0

                        if dice_count == 6:  # Height jamb
                            sign_index = 13
                            add_value = 0
                            value = 100
                            if dice == 1:
                                value = 150
                                add_value = 0

                        dict_result[sign_index] = value + add_value

        dict_result[7] = 0 if not lst_dice else sum(lst_dice)
        dict_result[8] = 0 if not lst_dice else sum(sorted(lst_dice[:-1]))

        if len(dict_dices.keys()) >= NUMBER_OF_DICE - 1:  # Low or Middle Kenta
            sign_index = 0
            value = 0

            if len(list(set(dict_dices.keys()) & set([1, 2, 3, 4 ,5]))) == 5:
                sign_index = 11
                value = 45

            if len(list(set(dict_dices.keys()) & set([2, 3, 4 ,5, 6]))) == 5:
                sign_index = 11
                value = 50

            if len(dict_dices.keys()) == NUMBER_OF_DICE:  # Height Kenta
                sign_index = 11
                value = 100

            if sign_index:
                dict_result[sign_index] = value

        return dict_result

    def build_ui(self):

        main_layout = QVBoxLayout()
        main_layout.addItem(self.create_layout())
        self.setLayout(main_layout)

        pass

class LineEditWdg(QLineEdit):

    sig_press = Signal()

    def __init__(self, parent=None, col_name="", col_id=0, row_name="", row_id=0):
        super(self.__class__, self).__init__(parent)
        self.col_name = col_name
        self.col_id = col_id
        self.row_name = row_name
        self.row_id = row_id
        self.assigned = False
        self.value = 0

    def fill_value(self):
        self.setText("{0}".format(self.value))

    def get_index(self):
        return self.col_id, self.row_id

    def set_enable_state(self, state=True):

        if state:
            self.setEnabled(state)

        if not state and not self.assigned:
            self.setEnabled(state)

    def assign_value(self, str_value=""):

        self.value = int(str_value) if str_value and "{0}".format(str_value).isnumeric() else 0
        self.assigned = True
        self.fill_value()
        self.setReadOnly(True)

    def get_object_name(self):
        return "[{0}, {1}] = {2}".format(self.col_name, self.row_name, self.value)

    def __repr__(self):
        return self.get_object_name()

    def __le__(self, other):
        return self.value < other.value

    def __lt__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            event.ignore()
            return None
        else:
            super(self.__class__, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        super(self.__class__, self).mousePressEvent(event)
        self.sig_press.emit()

class LabelWdg(QLabel):

    def __init__(self, parent=None, col_name=""):
        super(self.__class__, self).__init__(parent)
        self.col_name = col_name
        self.value = 0

    def set_value(self, value=0):
        self.value = value

    def fill_value(self):
        self.setText("{0}".format(self.value))

class JambPlayerTable(QWidget):

    def __init__(self, parent=None, player_name=""):
        super(self.__class__, self).__init__(parent)
        self.dict_cols = {}
        self.checkout = False
        self.checkout_row_index = -1
        self.checkout_col_index = 5
        self.player_name = player_name
        self.matrixWdg = []
        self.lstTotalWdg = []
        self.dict_dice_values = {}
        self.txtLineEditWdg = LineEditWdg()
        self.index_element = [-1, -1]
        self.validator = QRegExpValidator()
        self.build_ui()

    def create_content_layout(self):
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        self.matrixWdg = [[LineEditWdg(col_name=col_name, row_name=row_name, row_id=row_index, col_id=col_index) for row_index, row_name in DICT_ROW_HEADER.items()] for col_index, col_name in DICT_COL_HEADER.items()]

        row = 1
        for key in DICT_ROW_HEADER:
            lblRowHeader = QLabel(DICT_ROW_HEADER[key])
            lblRowHeader.setAlignment(Qt.AlignRight)
            lblRowHeader.setObjectName("lblRowHeader")
            grid_layout.addWidget(lblRowHeader, row, 0)
            row += 1

        col = 1
        for key in DICT_COL_HEADER:
            lblColHeader = QLabel(DICT_COL_HEADER[key])
            lblColHeader.setAlignment(Qt.AlignCenter)
            lblColHeader.setObjectName("lblColHeader")
            grid_layout.addWidget(lblColHeader, 0, col)
            col += 1

        for col_ in range(len(self.matrixWdg)):
            for row_ in range(len(self.matrixWdg[col_])):
                grid_layout.addWidget(self.matrixWdg[col_][row_], row_+1, col_+1)
                if isinstance(self.matrixWdg[col_][row_], QLineEdit):

                    self.matrixWdg[col_][row_].setValidator(self.validator)
                    self.matrixWdg[col_][row_].sig_press.connect(partial(self.matrixWdg_sig_update, col_, row_))

        row += 1

        col = 0

        lblRowHeader = QLabel("Total")
        lblRowHeader.setObjectName("lblTotalHeader")
        lblRowHeader.setAlignment(Qt.AlignRight)
        grid_layout.addWidget(lblRowHeader, row, col)

        col += 1

        for col_id, col_name in DICT_COL_HEADER.items():
            lblTotalWdg = LabelWdg(col_name=col_name)
            lblTotalWdg.setObjectName("lblColTotal")
            lblTotalWdg.setAlignment(Qt.AlignCenter)
            lblTotalWdg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.lstTotalWdg.insert(col_id, lblTotalWdg)
            grid_layout.addWidget(lblTotalWdg, row, col)
            col += 1

        return grid_layout

    def create_total_layout(self):
        item_layout = QHBoxLayout()

        self.lblTotals = LabelWdg()
        self.lblTotals.setAlignment(Qt.AlignCenter)
        self.lblTotals.setText("")
        self.lblTotals.setObjectName("lblTotal")
        item_layout.addWidget(self.lblTotals)
        return item_layout

    def calculate_totals(self):
        totals = 0
        for col_index in range(len(self.matrixWdg)):
            lst_row = self.matrixWdg[col_index]
            total_col = 0

            # Numbers total
            for item_ in lst_row[0:6]:
                total_col += item_.value

            # Bonus +30
            if total_col >= 60:
                total_col += 30

            # Min Max sub
            if lst_row[7].value > 0:
                total_col += ((lst_row[6].value - lst_row[7].value) * lst_row[0].value)

            # Signs totals
            for item_ in lst_row[8:]:
                total_col += item_.value

            totals += total_col
            lblTotalWdg = self.lstTotalWdg[col_index]
            if isinstance(lblTotalWdg, LabelWdg):
                lblTotalWdg.set_value(total_col)
                lblTotalWdg.fill_value()

        self.lblTotals.set_value(totals)
        self.lblTotals.fill_value()

    def fill_matrixWdg_values(self):

        for col_ in range(len(DICT_COL_HEADER.keys())):
            for row_ in range(len(DICT_ROW_HEADER.keys())):
                txtEl = self.matrixWdg[col_][row_]
                if isinstance(txtEl, LineEditWdg):
                    if txtEl.assigned:
                        txtEl.fill_value()

    def write_value(self):

        if self.txtLineEditWdg and isinstance(self.txtLineEditWdg, LineEditWdg):
            self.txtLineEditWdg.assign_value(self.txtLineEditWdg.text())
            col = self.txtLineEditWdg.col_id
            self.txtLineEditWdg = None

            if self.checkout:
                self.reset_checkout()
            return True

        return False

    def get_lineEditWdg(self, column=-1, row=-1):

        if column > -1 and row > -1:
            if column < len(self.matrixWdg):
                if row < len(self.matrixWdg[column]):
                    return self.matrixWdg[column][row]
        return None

    def lineEditWdg_update(self):

        if self.checkout:
            self.txtLineEditWdg = self.get_lineEditWdg(column=self.checkout_col_index, row=self.checkout_row_index)

        if self.txtLineEditWdg and isinstance(self.txtLineEditWdg, LineEditWdg):
            self.txtLineEditWdg.setFocus()
            if not (self.txtLineEditWdg.assigned or self.txtLineEditWdg.isReadOnly()):
                value = self.dict_dice_values.get(self.txtLineEditWdg.row_id + 1)
                self.txtLineEditWdg.setText("{0}".format(value))


    def matrixWdg_sig_update(self, col, row):

        if self.txtLineEditWdg and isinstance(self.txtLineEditWdg, LineEditWdg):
            self.txtLineEditWdg.setText("")

        txtEl = self.get_lineEditWdg(col, row)

        if isinstance(txtEl, LineEditWdg):
            self.index_element = txtEl.get_index()

            if not txtEl.isReadOnly():
                value = self.dict_dice_values.get(row+1)
                regex = QRegExp("[{0}-{0}]".format(value))
                self.validator.setRegExp(regex)
                txtEl.setValidator(self.validator)
                txtEl.setText("{0}".format(value))
                self.txtLineEditWdg = txtEl

    def reset_checkout(self):
        self.checkout = False
        self.checkout_row_index = -1

    def fill_columns_rules(self):
        self.set_table_rules()

    def set_table_rules(self):

        if self.checkout:
            self.set_all_disable_except_one(col=self.checkout_col_index, row=self.checkout_row_index)
        else:
            for col in range(len(self.matrixWdg)):
                self.set_column_rules(col)

    def set_column_enabled(self, column=-1, state=False):

        if column > -1 and column < len(self.matrixWdg):
            for row in range(0, len(self.matrixWdg[column])):
                lineEdigWdg = self.matrixWdg[column][row]
                if isinstance(lineEdigWdg, LineEditWdg):
                    lineEdigWdg.setEnabled(state)

    def set_column_rule_direction(self, column=0, row_start=0, row_end=0, direction=0):
        """

        :param column: column index
        :param row_start: start or stop index row
        :param direction: column go from Top to Bottom if direction is 1,
                        column go from Bottom to Top if direction is 0
        :return: None
        """

        if column < len(self.matrixWdg):
            if row_end <= len(self.matrixWdg[column]):
                lst_index = list(range(row_start, row_end+1))
                if direction == 1:
                    lst_index.sort(reverse=True)

                row_edit = lst_index[0]

                for i in range(len(lst_index)):
                    row = lst_index[i]
                    lineEditWdg = self.get_lineEditWdg(column, row)
                    if isinstance(lineEditWdg, LineEditWdg):
                        lineEditWdg.set_enable_state(False)

                        if lineEditWdg.assigned:
                            if i < len(lst_index) - 1:
                                row_edit = lst_index[i+1]

                lineEditWdg = self.get_lineEditWdg(column, row_edit)
                if lineEditWdg:
                    lineEditWdg.set_enable_state(True)

    def set_all_disable_except_one(self, col=5, row=0):

        for col_ in range(0, len(self.matrixWdg)):
            self.set_column_enabled(column=col_, state=False)

        # Line Edit Wdg matrix
        lineEditWdg = self.get_lineEditWdg(col, row)
        if lineEditWdg and isinstance(lineEditWdg, LineEditWdg):
            lineEditWdg.set_enable_state(True)
            lineEditWdg.setFocusPolicy(Qt.StrongFocus)


    def set_column_rules(self, column=-1):

        if column > -1:
            if column < len(self.matrixWdg):
                row_count = len(self.matrixWdg[column])

                if column in [0, 4]: # Free and Announcement column
                    for row in range(len(self.matrixWdg[column])):
                        txtEl = self.matrixWdg[column][row]
                        if txtEl and isinstance(txtEl, LineEditWdg):
                            txtEl.set_enable_state(True)

                if column == 1: # Up column => start from bottom to top
                    self.set_column_rule_direction(column, 0, row_count-1, 1)

                if column == 2: # Down column => start from top to bottom
                    self.set_column_rule_direction(column, 0, row_count-1, 0)

                if column == 3:  # Max/Min column => start from Max to Top and Min to Bottom
                    self.set_column_rule_direction(column, 0, 6, 1)
                    self.set_column_rule_direction(column, 7, row_count-1, 0)

                if column == 5: # Checkout column cell enable if preview Player call announcement
                    for row_ in range(0, row_count):
                        lineEditWdg = self.get_lineEditWdg(column, row_)
                        if lineEditWdg and isinstance(lineEditWdg, LineEditWdg):
                            lineEditWdg.set_enable_state(False)

    def fill_items(self):
        self.fill_matrixWdg_values()
        self.fill_columns_rules()
        self.calculate_totals()

    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addItem(self.create_content_layout())
        main_layout.addItem(self.create_total_layout())
        self.setLayout(main_layout)

class InputWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.lst_txt_wdg = []
        self.build_ui()

    def set_wdgs_enable_state(self, state=True):
        for e in self.lst_txt_wdg:
            e.setEnabled(state)

    def get_players(self):
        return [txtPlayer.text() for txtPlayer in self.lst_txt_wdg if txtPlayer.text()]

    def create_content_layout(self):

        item_layout = QVBoxLayout()
        item_layout.setSpacing(5)
        item_layout.setAlignment(Qt.AlignTop)

        grp_box = QGroupBox("Name of players")
        grp_box_layout = QVBoxLayout()
        grp_box_layout.setSpacing(5)

        for i in range(MAXIMUM_NUMBER_OF_PLAYERS):

            label_name = "Player {0}: ".format(i+1)
            txtWdg = QLineEdit()
            txtWdg.setPlaceholderText(label_name)
            self.lst_txt_wdg.append(txtWdg)
            grp_box_layout.addWidget(self.lst_txt_wdg[-1])

        grp_box.setLayout(grp_box_layout)
        item_layout.addWidget(grp_box)

        self.btnStart = QPushButton("Start")
        self.btnStart.setFixedWidth(100)
        item_layout.addWidget(self.btnStart)
        return item_layout

    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.addItem(self.create_content_layout())
        self.setLayout(main_layout)

class DeckWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.player_index = 0
        self.roll_turn = 0
        self.total_roll_turns = 0

        self.total_game_turns = 5
        self.game_remain_turns = self.total_game_turns
        self.lst_diceWdg = []
        self.lst_players = []
        self.lst_playerTableWdg = []
        self.dict_dice_values = {}
        self.build_ui()
        self.announcement = False

    def create_dice_layout(self):
        item_layout = QHBoxLayout()
        item_layout.setAlignment(Qt.AlignTop)
        item_layout.setStretch(0, 0.5)
        item_layout.setStretch(1, 0.5)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0,0,0,0)
        left_layout.setAlignment(Qt.AlignTop)

        btn_top_layout = QHBoxLayout()
        btn_top_layout.setAlignment(Qt.AlignLeft)

        self.btnRoll = QPushButton("Roll {0}".format(self.get_total_roll_turns() - self.roll_turn))
        self.btnRoll.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnRoll.clicked.connect(self.clicked_btnRoll)
        btn_top_layout.addWidget(self.btnRoll)

        dice_layout = QHBoxLayout()
        dice_layout.setAlignment(Qt.AlignLeft)
        dice_layout.setSpacing(5)

        self.dicesTableWdg = DicesTableWdg()
        dice_layout.addWidget(self.dicesTableWdg)

        btn_bottom_layout = QHBoxLayout()
        btn_bottom_layout.setSpacing(5)
        btn_bottom_layout.setAlignment(Qt.AlignLeft)

        self.btnWrite = QPushButton("Write")
        self.btnWrite.setFixedWidth(100)
        self.btnWrite.clicked.connect(self.clicked_write)
        btn_bottom_layout.addWidget(self.btnWrite)

        self.btnAnnouncement = QPushButton("Announcement")
        self.btnAnnouncement.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnAnnouncement.clicked.connect(self.clicked_btnAnnouncement)
        btn_bottom_layout.addWidget(self.btnAnnouncement)

        left_layout.addItem(btn_top_layout)
        left_layout.addItem(dice_layout)
        left_layout.addItem(btn_bottom_layout)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0,0,0,0)

        self.lblInfo = QLabel()
        self.lblInfo.setAlignment(Qt.AlignTop)
        self.lblInfo.setStyleSheet("QLabel {font-weight: bold; font-size: 12px;}")
        self.lblInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.lblInfo)

        item_layout.addItem(left_layout)
        item_layout.addItem(right_layout)

        return item_layout

    def create_players_layout(self):
        item_layout = QVBoxLayout()

        self.tabPlayer = QTabWidget()

        item_layout.addWidget(self.tabPlayer)

        return item_layout

    def fill_players_tab(self):
        for player_name in self.lst_players:
            playerWdg = JambPlayerTable(player_name=player_name)
            self.lst_playerTableWdg.append(playerWdg)
            self.tabPlayer.addTab(playerWdg, player_name)

    def fill_player_tab_enabled(self):
        if self.player_index < len(self.lst_playerTableWdg) and self.player_index < self.tabPlayer.count():
            self.tabPlayer.setCurrentIndex(self.player_index)
            for playerWdg in self.lst_playerTableWdg:
                if isinstance(playerWdg, JambPlayerTable):
                    playerWdg.setEnabled(False)

            playerWdg = self.get_this_player()
            if playerWdg:
                playerWdg.setEnabled(True)
            self.btnRoll.setEnabled(True)

    def get_total_roll_turns(self):
        return HAND_TURNS + 2 if self.game_remain_turns == 1 else HAND_TURNS

    def get_this_player(self):
        return self.lst_playerTableWdg[self.player_index] if self.player_index < len(self.lst_playerTableWdg) else None

    def get_next_player(self):

        player_index = self.player_index + 1

        if player_index == len(self.lst_playerTableWdg):
            player_index = 0

        return self.lst_playerTableWdg[player_index] if player_index < len(self.lst_playerTableWdg) else None

    def get_prev_player(self):

        player_index = self.player_index - 1

        if player_index < 0:
            player_index = len(self.lst_playerTableWdg)

        return self.lst_playerTableWdg[player_index] if player_index < len(self.lst_playerTableWdg) else None

    def start_player_turn(self):

        self.roll_turn = 0
        playerWdg = self.get_this_player()
        if playerWdg and isinstance(playerWdg, JambPlayerTable):
            playerWdg.dict_dice_values = {}
            reply = QMessageBox.information(self, "Next Player", "{0}'s Turn!".format(playerWdg.player_name), QMessageBox.Ok)

            if reply == QMessageBox.Ok:
                pass

            self.fill_player_tab_enabled()
            playerWdg.fill_items()

        self.dict_dice_values = {}
        self.dicesTableWdg.reset_dice()

        self.btnRoll.setText("Roll {0}".format(self.get_total_roll_turns() - self.roll_turn))

    def next_player(self):

        self.player_index += 1

        if self.player_index == len(self.lst_playerTableWdg):
            self.player_index = 0
            self.game_remain_turns -= 1

        self.start_player_turn()

    def clicked_write(self):

        self.announcement = False

        playerWdg = self.get_this_player()
        if isinstance(playerWdg, JambPlayerTable):
            if isinstance(playerWdg.txtLineEditWdg, LineEditWdg):
                if playerWdg.txtLineEditWdg and playerWdg.txtLineEditWdg.col_id == 4 and not self.announcement:
                    self.clicked_btnAnnouncement()

                if playerWdg.write_value():
                    self.next_player()
                    self.lblInfo.clear()


    def clicked_btnRoll(self):

        total_turn = self.get_total_roll_turns()
        lst_line = []
        player_checkout_state = False
        if self.roll_turn < total_turn:
            self.btnRoll.setEnabled(False)
            self.dicesTableWdg.roll_dice()
            self.btnRoll.setEnabled(True)

            playerWdg = self.get_this_player()
            if isinstance(playerWdg, JambPlayerTable):
                playerWdg.dict_dice_values = copy.deepcopy(self.dicesTableWdg.get_sign_dict())

                dict_dice_value = playerWdg.dict_dice_values

                for sign_id_ in DICT_ROW_HEADER:
                    sign_name = DICT_ROW_HEADER.get(sign_id_)
                    value = dict_dice_value.get(sign_id_+1)
                    if value:
                        lst_line.append("{0} = {1}".format(sign_name, value))

                if self.roll_turn == 1:
                    if not self.announcement:
                        playerWdg.set_column_enabled(column=4, state=False)

                playerWdg.lineEditWdg_update()
                player_checkout_state = playerWdg.checkout

            self.roll_turn += 1
            self.btnRoll.setText("Roll {0}".format(total_turn - self.roll_turn))

        if self.roll_turn == total_turn:
            self.btnRoll.setEnabled(False)

        self.btnAnnouncement.setEnabled(True if self.roll_turn == 1 and not player_checkout_state else False)

        self.lblInfo.setText("\n".join(lst_line))

    def clicked_btnAnnouncement(self):

        self.announcement = True

        thisPlayerWdg = self.get_this_player()

        if thisPlayerWdg and isinstance(thisPlayerWdg, JambPlayerTable):

            col = thisPlayerWdg.index_element[0]
            row = thisPlayerWdg.index_element[1]

            thisPlayerWdg.set_all_disable_except_one(col, row)
            nextPlayerWdg = self.get_next_player()
            if nextPlayerWdg and isinstance(nextPlayerWdg, JambPlayerTable):
                nextPlayerWdg.checkout = True
                nextPlayerWdg.checkout_row_index = row


    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        main_layout.addItem(self.create_dice_layout())
        main_layout.addItem(self.create_players_layout())

        self.setLayout(main_layout)

class JambWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.stackWdg = QStackedWidget()

        self.inputWdg = InputWdg()
        self.inputWdg.btnStart.clicked.connect(self.clicked_inputWdg_btnStart)
        self.deckWdg = DeckWdg()

        self.stackWdg.addWidget(self.inputWdg)
        self.stackWdg.addWidget(self.deckWdg)

        self.build_ui()

    def clicked_inputWdg_btnStart(self):

        self.inputWdg.set_wdgs_enable_state(False)
        self.stackWdg.setCurrentIndex(1)

        self.deckWdg.lst_players = self.inputWdg.get_players()
        self.deckWdg.fill_players_tab()
        self.deckWdg.fill_player_tab_enabled()
        self.deckWdg.start_player_turn()


    def build_ui(self):

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stackWdg)

        self.setLayout(main_layout)

class JambWin(QMainWindow):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setWindowTitle("Jamb")
        self.setWindowIcon(QIcon(DICT_DICE_IMG[5]))
        self.jambWdg = JambWdg()
        self.jambWdg.setStyleSheet(q_style)
        self.setCentralWidget(self.jambWdg)

        self.move_center_position()

    def move_center_position(self):
        fg = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

def main():
    app = QApplication(sys.argv)

    jambWin = JambWin()
    jambWin.resize(750, 600)
    jambWin.show()
    jambWin.move_center_position()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


