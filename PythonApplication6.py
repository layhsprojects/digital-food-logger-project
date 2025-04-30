import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QMessageBox, QDialog, QGridLayout,
                            QDateEdit, QCheckBox, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QColor 