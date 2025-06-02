import sys
import os
import platform
import json
from PyQt6 import QtWidgets, QtGui, QtCore
import paho.mqtt.client as mqtt

CONFIG_FILE = "config.json"

# === Проверка/загрузка конфигурации ===
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "MQTT_BROKER": "",
            "MQTT_PORT": 1883,
            "MQTT_TOPIC_COMMAND": "",
            "MQTT_TOPIC_STATUS": "",
            "CLIENT_ID": ""
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return None  # Конфиг только что создан, значения отсутствуют

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    if not all(config.get(key) for key in ["MQTT_BROKER", "MQTT_PORT", "MQTT_TOPIC_COMMAND", "MQTT_TOPIC_STATUS", "CLIENT_ID"]):
        return None  # Не все поля заполнены



            
    return config

# === Функция для сна ===
def go_to_sleep():
    if platform.system() == "Windows":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif platform.system() == "Linux":
        os.system("systemctl suspend")
    elif platform.system() == "Darwin":
        os.system("pmset sleepnow")

# === Главное окно ===
class MainWindow(QtWidgets.QWidget):
    def __init__(self, tray_icon):
        super().__init__()
        self.tray_icon = tray_icon
        self.setWindowTitle("MQTT Контроль")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "MQTT Контроль",
            "Программа свернута в трей",
            QtWidgets.QSystemTrayIcon.MessageIcon.Information
        )

# === Трей-приложение ===
class TrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, config, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("MQTT ПК Контроль")
        self.debug_mode = False
        self.config = config

        self.window = MainWindow(self)
        layout = QtWidgets.QVBoxLayout()

        self.debug_switch = QtWidgets.QCheckBox("Режим отладки")
        self.debug_switch.stateChanged.connect(self.toggle_debug)
        layout.addWidget(self.debug_switch)

        self.btn_online = QtWidgets.QPushButton("Симулировать Online")
        self.btn_offline = QtWidgets.QPushButton("Симулировать Offline")
        self.btn_online.clicked.connect(lambda: self.simulate_status("online"))
        self.btn_offline.clicked.connect(lambda: self.simulate_status("offline"))
        layout.addWidget(self.btn_online)
        layout.addWidget(self.btn_offline)
        self.btn_online.hide()
        self.btn_offline.hide()

        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.window.setLayout(layout)

        menu = QtWidgets.QMenu(parent)
        show_action = menu.addAction("Показать окно")
        exit_action = menu.addAction("Выход")
        show_action.triggered.connect(self.window.show)
        exit_action.triggered.connect(self.quit_app)
        self.setContextMenu(menu)

        self.client = mqtt.Client(client_id=config["CLIENT_ID"], callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config["MQTT_BROKER"], config["MQTT_PORT"], 60)

        self.keepalive_timer = QtCore.QTimer()
        self.keepalive_timer.timeout.connect(lambda: self.client.publish(config["MQTT_TOPIC_STATUS"], "online", retain=True))
        self.keepalive_timer.start(30_000)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.client.loop(timeout=0.1))
        self.timer.start(100)

    def log(self, text):
        self.log_output.append(text)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        self.log(f"[MQTT] Подключено: {rc}")
        client.subscribe(self.config["MQTT_TOPIC_COMMAND"])
        client.publish(self.config["MQTT_TOPIC_STATUS"], "online", retain=True)

    def on_message(self, client, userdata, msg):
        command = msg.payload.decode().strip().lower()
        self.log(f"[MQTT] Команда: {command} (retain={msg.retain})")

        if msg.retain and command == "sleep":
            self.log("[MQTT] Пропущено retain-сообщение sleep при старте.")
            return

        if command == "sleep":
            if self.debug_mode:
                self.log("[DEBUG] Получена команда sleep - симуляция")
            else:
                self.log("[MQTT] Получена команда sleep - переход в сон")
                go_to_sleep()

    def toggle_debug(self, state):
        self.debug_mode = bool(state)
        self.btn_online.setVisible(self.debug_mode)
        self.btn_offline.setVisible(self.debug_mode)
        self.log(f"[UI] Режим отладки: {'включен' if self.debug_mode else 'выключен'}")

    def simulate_status(self, status):
        self.client.publish(self.config["MQTT_TOPIC_STATUS"], status, retain=True)
        self.log(f"[DEBUG] Симулирован статус: {status}")

    def quit_app(self):
        self.client.publish(self.config["MQTT_TOPIC_STATUS"], "offline", retain=True)
        self.client.disconnect()
        QtWidgets.QApplication.quit()

# === Точка входа ===
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    if config is None:
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка конфигурации",
            f"Файл {CONFIG_FILE} не настроен.\nПожалуйста, заполните параметры и перезапустите программу."
        )
        sys.exit(1)

    icon = QtGui.QIcon("icon.ico")
    tray = TrayApp(icon, config)
    tray.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
