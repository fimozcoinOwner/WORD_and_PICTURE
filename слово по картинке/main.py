import sys
import json
import random
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent, QPixmap


# диалоговое окно покупки подсказок
class HintDialog(QDialog):
    def __init__(self, parent=None, message="Вы уверены, что хотите потратить 25 звёзд на подсказку?", has_yes_no=True):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Подсказка")
        self.setFixedSize(400, 180)
        self.setStyleSheet("background-color: white;")
        self.result = False

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # текст сообщения
        title = QLabel(message)
        title.setStyleSheet("color: black; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

        buttons_layout = QHBoxLayout()

        if has_yes_no:
            # кнопка "нет" - закрыть окно без подсказки
            no_btn = QPushButton("Нет")
            no_btn.setFixedSize(120, 45)
            no_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            no_btn.clicked.connect(self.reject)
            buttons_layout.addWidget(no_btn)

            # кнопка "да" - потратить звёзды и получить подсказку
            yes_btn = QPushButton("Да")
            yes_btn.setFixedSize(120, 45)
            yes_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            yes_btn.clicked.connect(self.accept)
            buttons_layout.addWidget(yes_btn)
        else:
            # кнопка "понятно"
            ok_btn = QPushButton("Понятно")
            ok_btn.setFixedSize(150, 45)
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            ok_btn.clicked.connect(self.accept)
            buttons_layout.addStretch()
            buttons_layout.addWidget(ok_btn)
            buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

    # подтверждение действия
    def accept(self):
        self.result = True
        super().accept()

    # отклонение действия
    def reject(self):
        self.result = False
        super().reject()


# окно игры
class GameWindow(QWidget):
    def __init__(self, level_data, current_level_num, stars, main_window_callback):
        super().__init__()
        self.level_data = level_data
        self.current_level_num = current_level_num
        self.stars = stars
        self.main_window_callback = main_window_callback

        # массив с буквами, которые уже ввёл пользователь
        self.current_input = []
        self.word_length = len(level_data["correct_word"])
        self.revealed_letters = []

        self.setWindowTitle("Слово по картинке – Уровень")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        self.showFullScreen()

        # главное вертикальное выравнивание
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)

        top_layout = QHBoxLayout()

        # круглая зелёная кнопка для выхода в главное меню
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
        self.back_button.clicked.connect(self.exit_to_menu)

        # текстовое поле с номером текущего уровня
        self.level_label = QLabel(f"УРОВЕНЬ {self.current_level_num}")
        self.level_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet("color: black;")

        # зелёная рамка с количеством звёзд у игрока
        self.stars_frame = QFrame()
        self.stars_frame.setFixedSize(100, 60)
        self.stars_frame.setStyleSheet("background-color: #2ecc71; border-radius: 15px;")
        stars_layout = QHBoxLayout()
        stars_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stars_label = QLabel(f"⭐ {self.stars}")
        self.stars_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.stars_label.setStyleSheet("color: white; background-color: transparent;")
        stars_layout.addWidget(self.stars_label)
        self.stars_frame.setLayout(stars_layout)

        top_layout.addWidget(self.back_button)
        top_layout.addStretch()
        top_layout.addWidget(self.level_label)
        top_layout.addStretch()
        top_layout.addWidget(self.stars_frame)

        # место для отображения картинки-коллажа
        self.image_label = QLabel()
        self.image_label.setFixedSize(350, 350)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #ecf0f1;
            border: 2px solid #bdc3c7;
        """)

        # загрузка изображения из папки с проектом
        self.load_image()

        images_container = QHBoxLayout()
        images_container.addStretch()
        images_container.addWidget(self.image_label)
        images_container.addStretch()

        # поле для ввода букв (ячейки под каждую букву слова)
        word_widget = QWidget()
        self.word_letters_layout = QHBoxLayout(word_widget)
        self.word_letters_layout.setSpacing(10)
        self.word_letters_layout.setContentsMargins(0, 0, 0, 0)

        self.letter_cells = []
        for i in range(self.word_length):
            cell = QLabel("")
            cell.setFixedSize(55, 55)
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

        # панель с кнопками-буквами (8 штук, 2 ряда по 4)
        letters_widget = QWidget()
        letters_layout = QVBoxLayout(letters_widget)
        letters_layout.setSpacing(15)

        # получение строки с буквами из json и перемешивание
        letters_str = level_data.get("letters", "")
        letters_list = list(letters_str.replace(" ", ""))
        random.shuffle(letters_list)

        # разбивка на два ряда по 4 буквы
        row1_letters = letters_list[:4]
        row2_letters = letters_list[4:8] if len(letters_list) > 4 else []

        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)

        self.letter_buttons = []

        # создание кнопок для первого ряда
        for letter in row1_letters:
            letter_btn = QPushButton(letter)
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
            letter_btn.clicked.connect(self.on_letter_clicked)
            self.letter_buttons.append(letter_btn)
            row1_layout.addWidget(letter_btn)

        # создание кнопок для второго ряда
        for letter in row2_letters:
            letter_btn = QPushButton(letter)
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
            letter_btn.clicked.connect(self.on_letter_clicked)
            self.letter_buttons.append(letter_btn)
            row2_layout.addWidget(letter_btn)

        while row1_layout.count() < 4:
            dummy_btn = QPushButton("")
            dummy_btn.setFixedSize(70, 70)
            dummy_btn.setEnabled(False)
            dummy_btn.setStyleSheet("background-color: #ecf0f1; border-radius: 15px;")
            row1_layout.addWidget(dummy_btn)

        while row2_layout.count() < 4:
            dummy_btn = QPushButton("")
            dummy_btn.setFixedSize(70, 70)
            dummy_btn.setEnabled(False)
            dummy_btn.setStyleSheet("background-color: #ecf0f1; border-radius: 15px;")
            row2_layout.addWidget(dummy_btn)

        letters_layout.addLayout(row1_layout)
        letters_layout.addLayout(row2_layout)

        letters_container = QHBoxLayout()
        letters_container.addStretch()
        letters_container.addWidget(letters_widget)
        letters_container.addStretch()

        # нижние кнопки управления
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setContentsMargins(0, 20, 0, 0)

        # серая кнопка для очистки всего введённого слова
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
        self.cancel_button.clicked.connect(self.clear_input)

        # оранжевая кнопка для вызова подсказки
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
        self.hint_button.clicked.connect(self.hint_dialog)

        bottom_buttons_layout.addWidget(self.cancel_button)
        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self.hint_button)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addStretch()
        center_layout.addLayout(images_container)
        center_layout.addSpacing(15)
        center_layout.addLayout(word_container)
        center_layout.addSpacing(15)
        center_layout.addLayout(letters_container)
        center_layout.addSpacing(15)
        center_layout.addLayout(bottom_buttons_layout)
        center_layout.addStretch()

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(center_layout, 1)

        source_label = QLabel("Изображения сгенерированы нейросетью")
        source_label.setFont(QFont("Arial", 8))
        source_label.setStyleSheet("color: #cccccc; background-color: transparent;")

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(source_label)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # загрузка картинки из файла
    def load_image(self):
        image_data = self.level_data.get("image")

        if isinstance(image_data, list) and len(image_data) > 0:
            image_file = image_data[0]
        else:
            image_file = image_data

        if image_file and os.path.exists(image_file):
            try:
                pixmap = QPixmap(image_file)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        380, 380,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(pixmap)
                else:
                    self.image_label.setStyleSheet(
                        "background-color: #ffcccc; border-radius: 20px; border: 2px solid #ff0000;"
                    )
            except Exception as e:
                print(f"ошибка загрузки: {e}")
        else:
            print(f"файл не найден: {image_file}")
            self.image_label.setStyleSheet(
                "background-color: #ffcccc; border-radius: 20px; border: 2px solid #ff0000;"
            )

    # обработчик клика по кнопке с буквой
    def on_letter_clicked(self):
        button = self.sender()
        letter = button.text()

        if letter and len(self.current_input) < self.word_length:
            self.current_input.append(letter)
            button.setEnabled(False)
            self.update_word_display()

    # обновление отображения введённых букв в ячейках
    def update_word_display(self):
        for i, cell in enumerate(self.letter_cells):
            if i < len(self.current_input):
                cell.setText(self.current_input[i])
            else:
                cell.setText("")

        if len(self.current_input) == self.word_length:
            self.check_answer()

    # полная очистка всех введённых букв
    def clear_input(self):
        self.current_input = []
        self.update_word_display()

    # проверка правильности ответа
    def check_answer(self):
        user_word = "".join(self.current_input)
        correct_word = self.level_data["correct_word"]

        if user_word == correct_word:
            self.stars += 10

            self.save_progress()
            self.next_level()
        else:
            QMessageBox.warning(self, "Неверно", f"Неправильно. Попробуй ещё раз!")
            self.clear_input()

    # переход к следующему уровню
    def next_level(self):
        next_level_num = self.current_level_num + 1

        game_window = self.main_window_callback(next_level_num, self.stars)

        if game_window is not None:
            self.next_window = game_window

            self.close()
            self.next_window.show()
        else:
            QMessageBox.information(None, "Поздравляю!", "Ты прошёл все уровни!")
            self.exit_to_menu()

    # сохранение прогресса (номер уровня и количество звёзд)
    def save_progress(self):
        progress = {
            "current_level": self.current_level_num + 1,
            "stars": self.stars
        }
        try:
            with open("progress.json", "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=4)
        except:
            pass

    # возврат в главное окно
    def exit_to_menu(self):
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()

    # обработка нажатий клавиш (ввод букв, backspace, esc)
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exit_to_menu()
            return

        key_text = event.text().upper()

        if key_text and key_text.isalpha() and len(key_text) == 1:
            available_letters = []
            for btn in self.letter_buttons:
                if btn.text():
                    available_letters.append(btn.text())

            if key_text in available_letters and len(self.current_input) < self.word_length:
                self.current_input.append(key_text)
                self.update_word_display()

        if event.key() == Qt.Key.Key_Backspace:
            if self.current_input:
                self.current_input.pop()
                self.update_word_display()

    # открытие диалогового окна подсказки
    def hint_dialog(self):
        if self.stars < 25:
            dialog = HintDialog(self, "Недостаточно звёзд! Нужно 25 звёзд для подсказки.", has_yes_no=False)
            dialog.exec()
            return

        dialog = HintDialog(self, "Вы уверены, что хотите потратить 25 звёзд на подсказку?", has_yes_no=True)
        if dialog.exec() and dialog.result:
            self.stars -= 25
            self.stars_label.setText(f"⭐ {self.stars}")

            correct_word = self.level_data["correct_word"]

            for i in range(len(correct_word)):
                if i not in self.revealed_letters:
                    self.revealed_letters.append(i)
                    if i >= len(self.current_input):
                        self.current_input.append(correct_word[i])
                    else:
                        self.current_input[i] = correct_word[i]
                    self.update_word_display()
                    break


# главное окно с кнопкой запуска игры
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Слово по картинке")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        self.showFullScreen()

        self.levels = self.load_levels()
        self.current_level = 1
        self.stars = self.load_stars()

        main_layout = QVBoxLayout()

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # крупное название игры в центре главного окна
        title_label = QLabel("СЛОВО ПО КАРТИНКЕ")
        title_label.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: black;")
        center_layout.addWidget(title_label)

        center_layout.addSpacing(40)

        # большая круглая зелёная кнопка с треугольником для старта
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
        self.play_button.clicked.connect(self.start_game)

        center_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        # надпись об источнике изображений
        source_label = QLabel("Изображения сгенерированы нейросетью")
        source_label.setFont(QFont("Arial", 8))
        source_label.setStyleSheet("color: #cccccc; background-color: transparent;")

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(source_label)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    # загрузка массива уровней из json-файла
    def load_levels(self):
        try:
            with open("levels.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data["levels"]
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл levels.json не найден!")
            return []
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Ошибка", "Ошибка в файле levels.json!")
            return []

    # загрузка сохранённого прогресса (текущий уровень и звёзды)
    def load_stars(self):
        try:
            with open("progress.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.current_level = data.get("current_level", 1)
                return data.get("stars", 0)
        except:
            return 0

    # запуск игры с текущего уровня
    def start_game(self):
        if not self.levels:
            QMessageBox.critical(self, "Ошибка", "Нет загруженных уровней!")
            return

        if self.current_level <= len(self.levels):
            self.hide()
            level_data = self.levels[self.current_level - 1]
            self.game_window = GameWindow(level_data, self.current_level, self.stars, self.load_next_level)
            self.game_window.show()
        else:
            QMessageBox.information(self, "Поздравляю!", "Ты прошёл все уровни!")
            self.current_level = 1
            self.stars = 0
            self.start_game()

    # получение следующего уровня для продолжения игры
    def load_next_level(self, next_level_num, stars):
        if next_level_num <= len(self.levels):
            level_data = self.levels[next_level_num - 1]
            return GameWindow(level_data, next_level_num, stars, self.load_next_level)
        else:
            return None

    # выход из игры по клавише esc
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())