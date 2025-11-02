# src/gui/app.py
import os
import json
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QListView, QSplitter, QVBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QPushButton,
    QHBoxLayout, QFileDialog, QInputDialog
)
from PyQt6.QtCore import QDir, Qt, QModelIndex
from PyQt6.QtGui import QFileSystemModel

from src.config import settings
from src.project_managment.manager import ProjectManager

class MainWindow(QWidget):
    """
    Main application window for managing training data.
    This class is responsible for the View logic only. It holds the UI state
    in memory and delegates all core logic (file I/O, PDF generation)
    to the ProjectManager.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Training Data Manager")
        self.setGeometry(100, 100, 1200, 800)

        # --- Logic Handler ---
        self.manager = ProjectManager()

        # --- In-Memory UI State ---
        self.data: Dict[str, Any] = {}
        self.data_compare: Dict[str, Any] = {}

        # --- UI Widget References ---
        self.folder_list_view: QListView
        self.participants_table: QTableWidget
        self.topics_text_edit: QTextEdit
        self.form_widgets: Dict[str, QLineEdit] = {}
        self.file_status_buttons: Dict[str, QPushButton] = {}

        self._setup_ui()

    def _setup_ui(self):
        """Initializes and lays out all UI components."""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self._create_left_pane())
        main_splitter.addWidget(self._create_middle_pane())
        main_splitter.addWidget(self._create_right_pane())
        main_splitter.setSizes([250, 550, 400])

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    def _create_left_pane(self) -> QWidget:
        """Creates the left pane with a new folder button and the directory browser."""
        left_pane_container = QWidget()
        layout = QVBoxLayout(left_pane_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        new_folder_button = QPushButton("＋ New Training Folder")
        new_folder_button.clicked.connect(self._on_new_folder_clicked)
        layout.addWidget(new_folder_button)

        self.folder_list_view = QListView()
        model = QFileSystemModel()
        root_path = str(getattr(settings, 'DEFAULT_TRAINING_ROOT', '.'))
        model.setRootPath(root_path)
        model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self.folder_list_view.setModel(model)
        self.folder_list_view.setRootIndex(model.index(root_path))
        self.folder_list_view.clicked.connect(self._on_directory_selected)
        layout.addWidget(self.folder_list_view)
        return left_pane_container

    def _create_middle_pane(self) -> QSplitter:
        """Creates the middle pane containing the form and the table."""
        middle_splitter = QSplitter(Qt.Orientation.Vertical)
        middle_splitter.addWidget(self._create_form_pane())
        middle_splitter.addWidget(self._create_table_pane())
        middle_splitter.setSizes([280, 520])
        return middle_splitter

    def _create_form_pane(self) -> QWidget:
        """Creates the top part of the middle pane with input fields."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        root_path = str(getattr(settings, 'DEFAULT_TRAINING_ROOT', '.'))
        layout.addWidget(QLabel(f"<b>Current source path: {root_path}</b>"))
        layout.addWidget(QLabel("<b>File Status:</b>"))
        layout.addLayout(self._create_file_status_buttons())
        layout.addWidget(QLabel("<b>Training Information:</b>"))
        for key, placeholder in settings.TRAINING_FIELDS.items():
            line_edit = QLineEdit(placeholderText=placeholder)
            line_edit.editingFinished.connect(self._update_data_from_ui)
            layout.addWidget(line_edit)
            self.form_widgets[key] = line_edit
        layout.addLayout(self._create_action_buttons())
        layout.addStretch(1)
        return widget

    def _create_table_pane(self) -> QTableWidget:
        """Creates the bottom part of the middle pane with the participants table."""
        self.participants_table = QTableWidget()
        self.participants_table.setAlternatingRowColors(True)
        self.participants_table.itemChanged.connect(self._on_cell_changed)
        headers = list(settings.PARTICIPANT_TABLE_HEADERS.values())
        self.participants_table.setColumnCount(len(headers))
        self.participants_table.setHorizontalHeaderLabels(headers)
        return self.participants_table

    def _create_right_pane(self) -> QTextEdit:
        """Creates the right pane with the topics text editor."""
        self.topics_text_edit = QTextEdit(placeholderText="Enter training topics, one per line...")
        self.topics_text_edit.textChanged.connect(self._update_data_from_ui)
        return self.topics_text_edit

    def _on_ankieta_ewaluacyjna_clicked(self):
        if not self.manager.directory:
            QMessageBox.warning(self, "No Directory", "Please select a project directory first.")
            return
        source_file, _ = QFileDialog.getOpenFileName(self, "Select ODS File", "", "ODS Files (*.ods)")
        if not source_file: return
        try:
            ### BALLS
            self.manager.ankieta_work(source_file)
            self._refresh_ui()
            QMessageBox.information(self, "Success", "Ankieta loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize project: {e}")


    def _create_file_status_buttons(self) -> QHBoxLayout:
        """Creates the buttons that show the status of key project files."""
        layout = QHBoxLayout()
        buttons_to_create = {"lista_obecnosci": self._on_lista_obecnosci_button_clicked, "ankieta_ewaluacyjna": self._on_ankieta_ewaluacyjna_clicked, "data.json": None, "data.json.old": None}
        for name, callback in buttons_to_create.items():
            button = QPushButton(name)
            if callback:
                button.clicked.connect(callback)
            self.file_status_buttons[name] = button
            layout.addWidget(button)
        return layout

    def _on_explorer_clicked(self):
        self.manager.open_explorer()

    def _create_action_buttons(self) -> QHBoxLayout:
        """Creates the main action buttons for generating documents."""
        layout = QHBoxLayout()
        open_explorer = QPushButton("Open Exploere")
        open_explorer.clicked.connect(self._on_explorer_clicked)
        layout.addWidget(open_explorer)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._on_save_clicked)
        layout.addWidget(save_button)
        generate_all_btn = QPushButton("Generate Pdfs")
        generate_all_btn.clicked.connect(self._on_generate_clicked)
        layout.addWidget(generate_all_btn)
        return layout

    # --- Event Handlers (Slots) ---
    def _on_new_folder_clicked(self):
        """Prompts the user to create a new training folder."""
        root_path = str(getattr(settings, 'DEFAULT_TRAINING_ROOT', '.'))
        folder_name, ok = QInputDialog.getText(self, "New Training Folder", "Enter the name for the new folder:")
        if not ok or not folder_name.strip(): return
        new_folder_path = os.path.join(root_path, folder_name.strip())
        if os.path.exists(new_folder_path):
            QMessageBox.warning(self, "Folder Exists", f"A folder named '{folder_name}' already exists.")
            return
        try:
            os.makedirs(os.path.join(new_folder_path, settings.ARCHIVE_SUBDIR))
            QMessageBox.information(self, "Success", f"Successfully created folder:\n{new_folder_path}")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")

    def _on_directory_selected(self, index: QModelIndex):
        """Handles selection of a new directory, delegating data loading to the manager."""
        path = index.model().filePath(index)
        if not os.path.isdir(path): return
        self.manager.set_project_directory(path)
        self.data, self.data_compare = self.manager.load_project_data()
        self._refresh_ui()
        print(f"Selected directory: {path}")

    def _on_cell_changed(self, item: QTableWidgetItem):
        """Updates in-memory data when a table cell is edited."""
        if not self.data: return
        row, col = item.row(), item.column()
        header_key = list(settings.PARTICIPANT_TABLE_HEADERS.keys())[col]
        self.data[settings.KEY_PARTICIPANTS][row][header_key] = item.text()
        self._update_data_from_ui()

    def _on_lista_obecnosci_button_clicked(self):
        """Handles the 'Import ODS' action."""
        if not self.manager.directory:
            QMessageBox.warning(self, "No Directory", "Please select a project directory first.")
            return
        source_file, _ = QFileDialog.getOpenFileName(self, "Select ODS File", "", "ODS Files (*.ods)")
        if not source_file: return
        try:
            self.data, self.data_compare = self.manager.initialize_from_ods(source_file)
            self._refresh_ui()
            QMessageBox.information(self, "Success", "Project initialized from ODS file.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize project: {e}")

    def _on_generate_clicked(self):
        """Handles the main 'Generate All' action."""
        if not self._confirm_and_save_changes(): return
        try:
            self.data = self.manager.run_generation(self.data, force=True)
            self.data_compare = json.loads(json.dumps(self.data))
            self._refresh_ui()
            QMessageBox.information(self, "Success", "All documents generated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"An error occurred: {e}")

    def _on_save_clicked(self):
        self._confirm_and_save_changes()

    # --- UI State and Data Sync ---

    def _refresh_ui(self):
        """
        Single source of truth for updating the entire UI based on the current
        in-memory state (self.data, self.data_compare, self.manager.directory).
        """
        if self.data:
            self._populate_ui_from_data()
        else:
            self._clear_ui()
        self._update_file_status_buttons()

    def _update_data_from_ui(self):
        """Updates the in-memory self.data dictionary from form fields."""
        if not self.data: return
        if settings.KEY_TRAINING not in self.data: self.data[settings.KEY_TRAINING] = {}
        for key, widget in self.form_widgets.items():
            self.data[settings.KEY_TRAINING][key] = widget.text()
        self.data[settings.KEY_TRAINING][settings.KEY_TEMATYKA] = self.topics_text_edit.toPlainText()
        # This is a direct consequence of user input, so it's okay to call this here
        # without doing a full refresh, which would be disruptive.
        self._update_file_status_buttons()

    def _populate_ui_from_data(self):
        """(Private) Populates widgets from the in-memory self.data."""
        widgets_to_block = list(self.form_widgets.values()) + [self.topics_text_edit, self.participants_table]
        for widget in widgets_to_block:
            widget.blockSignals(True)
        try:
            training_data = self.data.get(settings.KEY_TRAINING, {})
            for key, widget in self.form_widgets.items():
                widget.setText(str(training_data.get(key, "")))
            self.topics_text_edit.setPlainText(training_data.get(settings.KEY_TEMATYKA, ""))
            self.participants_table.clearContents()
            participants = self.data.get(settings.KEY_PARTICIPANTS, [])
            self.participants_table.setRowCount(len(participants))
            header_keys = list(settings.PARTICIPANT_TABLE_HEADERS.keys())
            for row, person in enumerate(participants):
                for col, key in enumerate(header_keys):
                    item = QTableWidgetItem(str(person.get(key, "")))
                    self.participants_table.setItem(row, col, item)
            self.participants_table.resizeColumnsToContents()
        finally:
            for widget in widgets_to_block:
                widget.blockSignals(False)

    def _clear_ui(self):
        """(Private) Clears all input fields and the table in the UI."""
        for widget in self.form_widgets.values():
            widget.clear()
        self.topics_text_edit.clear()
        self.participants_table.clearContents()
        self.participants_table.setRowCount(0)

    def _update_file_status_buttons(self):
        """(Private) Updates button colors based on file existence and in-memory data changes."""
        if not self.manager.directory: return
        def get_style(state: str) -> str:
            styles = {"found": "background-color: lightgreen;", "missing_crit": "background-color: #FF7F7F;", "missing": "background-color: white;", "changed": "background-color: lightyellow;"}
            return styles.get(state, "")
        paths = {
            "lista_obecnosci": os.path.join(self.manager.directory, settings.ARCHIVE_SUBDIR, settings.LISTA_OBECNOSCI_FILENAME),
            "data.json": os.path.join(self.manager.directory, settings.DATA_FILENAME),
            "data.json.old": os.path.join(self.manager.directory, settings.DATA_COMPARE_FILENAME),
        }
        self.file_status_buttons["lista_obecnosci"].setStyleSheet(get_style("found" if os.path.exists(paths["lista_obecnosci"]) else "missing_crit"))
        self.file_status_buttons["data.json.old"].setStyleSheet(get_style("found" if os.path.exists(paths["data.json.old"]) else "missing"))
        if not os.path.exists(paths["data.json"]):
             self.file_status_buttons["data.json"].setStyleSheet(get_style("missing_crit"))
        elif self.data == self.data_compare:
             self.file_status_buttons["data.json"].setStyleSheet(get_style("found"))
        else:
             self.file_status_buttons["data.json"].setStyleSheet(get_style("changed"))

    def _confirm_and_save_changes(self) -> bool:
        """Prompts the user to save changes before an action, delegating the save to the manager."""
        if not self.manager.directory or not self.data:
            QMessageBox.warning(self, "Warning", "No directory or data loaded.")
            return False
        if self.data == self.data_compare: return True
        reply = QMessageBox.question(self, "Unsaved Changes",
            "You have unsaved changes. Do you want to save them before proceeding?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Save:
            if self.manager.save_project_data(self.data, save_as_compare=True):
                self.data_compare = json.loads(json.dumps(self.data))
                self._refresh_ui() # Refresh after saving to update button colors
                return True
            else:
                QMessageBox.critical(self, "Error", "Failed to save data files.")
                return False
        elif reply == QMessageBox.StandardButton.Discard:
            self.data, self.data_compare = self.manager.load_project_data()
            self._refresh_ui() # Refresh to show the discarded state
            return True
        else: # Cancel
            return False
