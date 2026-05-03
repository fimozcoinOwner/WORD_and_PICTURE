import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent


# окно уровня
class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Слово по картинке – Уровень")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        self.showFullScreen()

        # вертикальное выравнивание
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)

        # верхнее горизонтальное выравнивание
        top_layout = QHBoxLayout()

        # кнопка "выйти в главное меню" (стрелка)
        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(60, 60)
        self.back_button.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self.btn_clicked)

        # номер уровня
        self.level_label = QLabel("УРОВЕНЬ 1")
        self.level_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet("color: #2c3e50; background-color: transparent;")

        # баланс звёзд
        self.stars_frame = QFrame()
        self.stars_frame.setFixedSize(100, 60)
        self.stars_frame.setStyleSheet("background-color: #2ecc71; border-radius: 15px;")
        stars_layout = QHBoxLayout()
        stars_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stars_label = QLabel("⭐ 0")
        self.stars_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.stars_label.setStyleSheet("color: white; background-color: transparent;")
        stars_layout.addWidget(self.stars_label)
        self.stars_frame.setLayout(stars_layout)

        top_layout.addWidget(self.back_button)
        top_layout.addStretch()
        top_layout.addWidget(self.level_label)
        top_layout.addStretch()
        top_layout.addWidget(self.stars_frame)

        # картинки
        images_widget = QWidget()
        images_layout = QGridLayout(images_widget)
        images_layout.setSpacing(0)
        images_layout.setContentsMargins(0, 0, 0, 0)

        self.image_buttons = []
        for i in range(4):
            img_btn = QPushButton()
            img_btn.setFixedSize(150, 150)
            img_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border-radius: 15px;
                    border: 2px solid #bdc3c7;
                }
            """)
            img_btn.setEnabled(False)
            self.image_buttons.append(img_btn)

        images_layout.addWidget(self.image_buttons[0], 0, 0)
        images_layout.addWidget(self.image_buttons[1], 0, 1)
        images_layout.addWidget(self.image_buttons[2], 1, 0)
        images_layout.addWidget(self.image_buttons[3], 1, 1)

        images_container = QHBoxLayout()
        images_container.addStretch()
        images_container.addWidget(images_widget)
        images_container.addStretch()

        # поля для ввода букв
        word_widget = QWidget()
        self.word_letters_layout = QHBoxLayout(word_widget)
        self.word_letters_layout.setSpacing(5)
        self.word_letters_layout.setContentsMargins(0, 0, 0, 0)

        self.letter_cells = []
        for i in range(6):
            cell = QLabel("")
            cell.setFixedSize(50, 50)
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setStyleSheet("""
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            """)
            self.letter_cells.append(cell)
            self.word_letters_layout.addWidget(cell)

        word_container = QHBoxLayout()
        word_container.addStretch()
        word_container.addWidget(word_widget)
        word_container.addStretch()

        # кнопки с буквами
        letters_widget = QWidget()
        letters_layout = QVBoxLayout(letters_widget)
        letters_layout.setSpacing(15)

        sample_letters = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж"]

        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)

        self.letter_buttons = []
        for i in range(8):
            letter_btn = QPushButton(sample_letters[i])
            letter_btn.setFixedSize(70, 70)
            letter_btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            letter_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            letter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.letter_buttons.append(letter_btn)

            if i < 4:
                row1_layout.addWidget(letter_btn)
            else:
                row2_layout.addWidget(letter_btn)

        letters_layout.addLayout(row1_layout)
        letters_layout.addLayout(row2_layout)

        letters_container = QHBoxLayout()
        letters_container.addStretch()
        letters_container.addWidget(letters_widget)
        letters_container.addStretch()

        # нижнее горизонтальное выравнивание
        bottom_buttons_layout = QHBoxLayout()

        # кнопка "отменить"
        self.cancel_button = QPushButton("ОТМЕНИТЬ")
        self.cancel_button.setFixedSize(150, 50)
        self.cancel_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # кнопка "подсказка"
        self.hint_button = QPushButton("ПОДСКАЗКА")
        self.hint_button.setFixedSize(150, 50)
        self.hint_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.hint_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.hint_button.setCursor(Qt.CursorShape.PointingHandCursor)

        bottom_buttons_layout.addWidget(self.cancel_button)
        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self.hint_button)

        # общее выравнивание по центру
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addStretch()
        center_layout.addLayout(images_container)
        center_layout.addSpacing(40)
        center_layout.addLayout(word_container)
        center_layout.addSpacing(40)
        center_layout.addLayout(letters_container)
        center_layout.addSpacing(30)
        center_layout.addLayout(bottom_buttons_layout)
        center_layout.addStretch()

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(center_layout, 1)

        # надпись "сгенерировано ии"
        source_label = QLabel("Изображения сгенерированы нейросетью")
        source_label.setFont(QFont("Arial", 8))
        source_label.setStyleSheet("color: #cccccc; background-color: transparent;")

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(source_label)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
    # если кнопка нажата - показывается главное окно
    def btn_clicked(self):
        self.hide()
        self.main_window = MainWindow()
        self.main_window.show()

    # при нажатии на кнопку Esc программа закрывается
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()


# главное окно
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Слово по картинке")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        self.showFullScreen()

        main_layout = QVBoxLayout()

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # название игры
        title_label = QLabel("СЛОВО ПО КАРТИНКЕ")
        title_label.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")
        center_layout.addWidget(title_label)

        center_layout.addSpacing(40)

        # кнопка "начать игру"
        self.play_button = QPushButton()
        self.play_button.setFixedSize(200, 200)
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border-radius: 100px;
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.play_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.play_button.setText("▶")
        self.play_button.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        self.play_button.setStyleSheet(self.play_button.styleSheet() + "color: white;")
        self.play_button.clicked.connect(self.btn_clicked)

        center_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        # надпись "сгенерировано ии"
        source_label = QLabel("Изображения сгенерированы нейросетью")
        source_label.setFont(QFont("Arial", 8))
        source_label.setStyleSheet("color: #cccccc; background-color: transparent;")

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(source_label)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    # если кнопка нажата - показывается окно игры
    def btn_clicked(self):
        self.hide()
        self.game_window = GameWindow()
        self.game_window.show()

    # при нажатии на кнопку Esc программа закрывается
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())