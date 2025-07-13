import sys
import json
import time
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, QSplitter, QProgressBar)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QUrl, Qt
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

class SessionRecorder:
    def __init__(self):
        self.events = []
        self.is_recording = False
        self.start_time = None
    def start_recording(self):
        self.events = []
        self.is_recording = True
        self.start_time = time.time()
    def stop_recording(self):
        self.is_recording = False
    def add_event(self, event_type, data):
        if self.is_recording:
            event = {'timestamp': time.time() - self.start_time, 'type': event_type, 'data': data}
            self.events.append(event)
    def save_session(self, filename):
        session_data = {'start_time': datetime.fromtimestamp(self.start_time).isoformat(), 'events': self.events}
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
    def load_session(self, filename):
        with open(filename, 'r') as f:
            session_data = json.load(f)
        self.events = session_data['events']
        return session_data

class SessionReplayer(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    def __init__(self, events, web_view):
        super().__init__()
        self.events = events
        self.web_view = web_view
        self.current_index = 0
    def run(self):
        for i, event in enumerate(self.events):
            self.progress_signal.emit(f"Replaying event {i+1}/{len(self.events)}: {event['type']}")
            if event['type'] == 'navigation':
                self.web_view.setUrl(QUrl(event['data']['url']))
            elif event['type'] == 'click':
                js_code = f"""
                var element = document.elementFromPoint({event['data']['x']}, {event['data']['y']});
                if (element) {{
                    element.click();
                }}
                """
                self.web_view.page().runJavaScript(js_code)
            elif event['type'] == 'input':
                js_code = f"""
                var element = document.elementFromPoint({event['data']['x']}, {event['data']['y']});
                if (element && element.tagName === 'INPUT') {{
                    element.value = '{event['data']['value']}';
                    element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                """
                self.web_view.page().runJavaScript(js_code)
            time.sleep(event.get('delay', 0.5))
        self.finished_signal.emit()

class CustomWebPage(QWebEnginePage):
    def __init__(self, recorder):
        super().__init__()
        self.recorder = recorder
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if self.recorder.is_recording:
            self.recorder.add_event('console_message', {'level': level, 'message': message, 'line': lineNumber, 'source': sourceID})
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if self.recorder.is_recording and isMainFrame:
            self.recorder.add_event('navigation_request', {'url': url.toString(), 'type': _type})
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class ToolskitchMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder = SessionRecorder()
        self.replayer = None
        self.init_ui()
        self.apply_dark_theme()
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
    def create_logo_area(self):
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(10, 10, 10, 10)
        
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Toolskitch")
            logo_label.setFont(QFont("Arial", 16, QFont.Bold))
            logo_label.setStyleSheet("color: #2a82da;")
        
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background-color: transparent; border: none;")
        logo_layout.addWidget(logo_label)
        
        return logo_widget
    def init_ui(self):
        self.setWindowTitle("Toolskitch - By Ansh")
        self.setGeometry(100, 100, 1200, 800)
        
        icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.setWindowIcon(icon)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        logo_widget = self.create_logo_area()
        main_layout.addWidget(logo_widget)
        
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        self.loading_progress = QProgressBar()
        self.loading_progress.setVisible(False)
        main_layout.addWidget(self.loading_progress)
        splitter = QSplitter()
        main_layout.addWidget(splitter)
        browser_widget = self.create_browser_area()
        splitter.addWidget(browser_widget)
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        splitter.setSizes([800, 400])
        self.statusBar().showMessage("Ready")
    def create_toolbar(self):
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL (e.g., https://example.com)")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2a82da;
            }
        """)
        toolbar_layout.addWidget(self.url_bar)
        self.enter_btn = QPushButton("Enter")
        self.enter_btn.clicked.connect(self.navigate_to_url)
        self.enter_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e6bb8;
            }
            QPushButton:pressed {
                background-color: #155a9e;
            }
        """)
        toolbar_layout.addWidget(self.enter_btn)
        self.reload_btn = QPushButton("Reload")
        self.reload_btn.clicked.connect(self.refresh_page)
        self.reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
        """)
        toolbar_layout.addWidget(self.reload_btn)
        return toolbar_widget
    def create_browser_area(self):
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        self.web_view = QWebEngineView()
        self.web_page = CustomWebPage(self.recorder)
        self.web_view.setPage(self.web_page)
        self.web_view.urlChanged.connect(self.url_changed)
        self.web_view.loadFinished.connect(self.page_loaded)
        browser_layout.addWidget(self.web_view)
        return browser_widget
    def create_control_panel(self):
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        preview_group = QWidget()
        preview_layout = QVBoxLayout(preview_group)
        preview_label = QLabel("Your Preview Here")
        preview_label.setFont(QFont("Arial", 14, QFont.Bold))
        preview_label.setStyleSheet("color: #2a82da; margin-bottom: 10px;")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setPlaceholderText("Preview area - Your web application will appear here...")
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 10px;
                color: #cccccc;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 2px solid #2a82da;
            }
        """)
        preview_layout.addWidget(self.preview_text)
        control_layout.addWidget(preview_group)
        recording_group = QWidget()
        recording_layout = QVBoxLayout(recording_group)
        recording_label = QLabel("Session Recording")
        recording_label.setFont(QFont("Arial", 12, QFont.Bold))
        recording_label.setStyleSheet("color: white; margin-top: 10px;")
        recording_layout.addWidget(recording_label)
        recording_buttons_layout = QHBoxLayout()
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e6bb8;
            }
            QPushButton:pressed {
                background-color: #155a9e;
            }
        """)
        recording_buttons_layout.addWidget(self.record_btn)
        self.save_btn = QPushButton("Save Session")
        self.save_btn.clicked.connect(self.save_session)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """)
        recording_buttons_layout.addWidget(self.save_btn)
        recording_layout.addLayout(recording_buttons_layout)
        control_layout.addWidget(recording_group)
        replay_group = QWidget()
        replay_layout = QVBoxLayout(replay_group)
        replay_label = QLabel("Session Replay")
        replay_label.setFont(QFont("Arial", 12, QFont.Bold))
        replay_label.setStyleSheet("color: white; margin-top: 10px;")
        replay_layout.addWidget(replay_label)
        replay_buttons_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Session")
        self.load_btn.clicked.connect(self.load_session)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        replay_buttons_layout.addWidget(self.load_btn)
        self.replay_btn = QPushButton("Start Replay")
        self.replay_btn.clicked.connect(self.start_replay)
        self.replay_btn.setEnabled(False)
        self.replay_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """)
        replay_buttons_layout.addWidget(self.replay_btn)
        replay_layout.addLayout(replay_buttons_layout)
        control_layout.addWidget(replay_group)
        log_group = QWidget()
        log_layout = QVBoxLayout(log_group)
        log_label = QLabel("Session Log")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        log_label.setStyleSheet("color: white; margin-top: 10px;")
        log_layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 5px;
                padding: 8px;
                color: #cccccc;
                font-size: 11px;
            }
        """)
        log_layout.addWidget(self.log_text)
        control_layout.addWidget(log_group)
        return control_widget
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.loading_progress.setVisible(True)
        self.loading_progress.setRange(0, 0)
        self.statusBar().showMessage("Loading...")
        self.preview_text.setPlainText(f"Loading: {url}")
        self.web_view.setUrl(QUrl(url))
    def refresh_page(self):
        self.loading_progress.setVisible(True)
        self.loading_progress.setRange(0, 0)
        self.statusBar().showMessage("Reloading...")
        current_url = self.web_view.url().toString()
        self.preview_text.setPlainText(f"Reloading: {current_url}")
        self.web_view.reload()
    def url_changed(self, url):
        self.url_bar.setText(url.toString())
        if self.recorder.is_recording:
            self.recorder.add_event('navigation', {'url': url.toString()})
            self.log_message(f"Navigation: {url.toString()}")
    def page_loaded(self, success):
        self.loading_progress.setVisible(False)
        if success:
            self.statusBar().showMessage("Page loaded successfully")
            current_url = self.web_view.url().toString()
            self.preview_text.setPlainText(f"Loaded successfully: {current_url}")
            if self.recorder.is_recording:
                self.recorder.add_event('page_loaded', {'url': current_url})
                self.log_message("Page loaded")
        else:
            self.statusBar().showMessage("Failed to load page")
            self.preview_text.setPlainText("Failed to load page. Please check the URL and try again.")
    def toggle_recording(self):
        if not self.recorder.is_recording:
            self.recorder.start_recording()
            self.record_btn.setText("Stop Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #cc3333;
                }
            """)
            self.save_btn.setEnabled(False)
            self.log_message("Recording started")
            self.statusBar().showMessage("Recording session...")
            self.preview_text.setPlainText("🔴 Recording session...\n\nAll interactions will be captured.\nClick 'Stop Recording' when finished.")
        else:
            self.recorder.stop_recording()
            self.record_btn.setText("Start Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a82da;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e6bb8;
                }
                QPushButton:pressed {
                    background-color: #155a9e;
                }
            """)
            self.save_btn.setEnabled(True)
            self.log_message("Recording stopped")
            self.statusBar().showMessage("Recording stopped")
            self.preview_text.setPlainText("✅ Recording stopped\n\nSession saved. You can now save the session file.")
    def save_session(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Session", "", "JSON Files (*.json)")
        if filename:
            self.recorder.save_session(filename)
            self.log_message(f"Session saved to {filename}")
            QMessageBox.information(self, "Success", "Session saved successfully!")
    def load_session(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Session", "", "JSON Files (*.json)")
        if filename:
            try:
                session_data = self.recorder.load_session(filename)
                self.replay_btn.setEnabled(True)
                self.log_message(f"Session loaded: {len(session_data['events'])} events")
                QMessageBox.information(self, "Success", "Session loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load session: {str(e)}")
    def start_replay(self):
        if not self.recorder.events:
            QMessageBox.warning(self, "Warning", "No session loaded for replay")
            return
        self.replayer = SessionReplayer(self.recorder.events, self.web_view)
        self.replayer.progress_signal.connect(self.log_message)
        self.replayer.finished_signal.connect(self.replay_finished)
        self.replayer.start()
        self.replay_btn.setEnabled(False)
        self.log_message("Replay started")
    def replay_finished(self):
        self.replay_btn.setEnabled(True)
        self.log_message("Replay finished")
        self.statusBar().showMessage("Replay completed")
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Toolskitch")
    app.setApplicationVersion("1.0.0")
    
    icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
    
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
    
    window = ToolskitchMainWindow()
    window.show()
    
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        window.setWindowIcon(icon)
        window.repaint()
    
    sys.exit(app.exec_())
if __name__ == "__main__":
    main() 