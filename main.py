import sys
import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QDialog, QLabel, QProgressBar, QWidget, QPushButton, QTextEdit, 
                             QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget, QTreeView, QSplitter,
                             QMainWindow, QAction, QMessageBox, QLineEdit, QComboBox, QSystemTrayIcon, QMenu)
from PyQt5.QtGui import QClipboard, QIcon
from PyQt5.QtCore import QDir, QModelIndex, QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.Qt import QFileSystemModel

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class ParsingToolMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.initUI()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Error initializing UI: {str(e)}")

    def initUI(self):
        try:
            self.setWindowIcon(QtGui.QIcon(resource_path("app_icon.ico")))    
            self.setWindowTitle('TSTP:Parsing Tool')
            self.setGeometry(100, 100, 1200, 800)

            # Initialize System Tray
            self.initSystemTray()

            # Central widget and main layout
            centralWidget = QWidget()
            self.setCentralWidget(centralWidget)
            mainLayout = QHBoxLayout(centralWidget)

            # Left side (folder structure)
            leftLayout = QVBoxLayout()
            self.folderSearchBar = QLineEdit()
            self.folderSearchBar.setPlaceholderText("Search folders...")
            self.folderSearchBar.textChanged.connect(self.filterFolderTree)
            self.folderView = QTreeView()
            self.folderModel = QFileSystemModel()
            self.folderModel.setRootPath(QDir.rootPath())
            self.folderModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
            self.folderView.setModel(self.folderModel)
            self.folderView.setRootIndex(self.folderModel.index(QDir.rootPath()))
            self.folderView.clicked.connect(self.onFolderClicked)
            self.folderView.setHeaderHidden(True)

            leftLayout.addWidget(self.folderSearchBar)
            leftLayout.addWidget(self.folderView)

            # Middle (file list and text area)
            middleLayout = QVBoxLayout()
            
            self.searchBar = QLineEdit()
            self.searchBar.setPlaceholderText("Search files...")
            self.searchBar.textChanged.connect(self.filterFileList)
            self.fileTypeFilter = QComboBox()
            self.fileTypeFilter.addItem("All Files")
            self.fileTypeFilter.addItem(".txt")
            self.fileTypeFilter.addItem(".log")
            self.fileTypeFilter.addItem(".xml")
            self.fileTypeFilter.currentTextChanged.connect(self.filterFileList)
            
            self.fileList = QListWidget()
            self.fileList.setSelectionMode(QListWidget.MultiSelection)
            self.fileList.itemSelectionChanged.connect(self.onFileSelectionChanged)
            
            self.textArea = QTextEdit()
            self.textArea.setReadOnly(True)

            self.toggleSelectButton = QPushButton('Select All Files')
            self.toggleSelectButton.setCheckable(True)
            self.toggleSelectButton.clicked.connect(self.toggleSelectFiles)

            buttonLayout = QHBoxLayout()
            self.selectFolderButton = QPushButton('Select Folder')
            self.selectFolderButton.clicked.connect(self.selectFolder)
            self.parseButton = QPushButton('Parse')
            self.parseButton.clicked.connect(self.parseSelectedFolder)
            self.saveButton = QPushButton('Save')
            self.saveButton.clicked.connect(self.saveToFile)
            self.copyButton = QPushButton('Copy to Clipboard')
            self.copyButton.clicked.connect(self.copyToClipboard)
            self.copyStructureButton = QPushButton('Copy File Structure')
            self.copyStructureButton.clicked.connect(self.copyFileStructure)
            buttonLayout.addWidget(self.selectFolderButton)
            buttonLayout.addWidget(self.parseButton)
            buttonLayout.addWidget(self.saveButton)
            buttonLayout.addWidget(self.copyButton)
            buttonLayout.addWidget(self.copyStructureButton)
            buttonLayout.addWidget(self.toggleSelectButton)

            middleLayout.addWidget(self.searchBar)
            middleLayout.addWidget(self.fileTypeFilter)
            middleLayout.addWidget(self.fileList)
            middleLayout.addWidget(self.textArea)
            middleLayout.addLayout(buttonLayout)

            # Add layouts to main layout
            splitter = QSplitter()
            folderWidget = QWidget()
            folderWidget.setLayout(leftLayout)
            splitter.addWidget(folderWidget)
            middleWidget = QWidget()
            middleWidget.setLayout(middleLayout)
            splitter.addWidget(middleWidget)

            mainLayout.addWidget(splitter)

            # Menu
            menuBar = self.menuBar()
            helpMenu = menuBar.addMenu('Help')
            
            aboutAction = QAction('About', self)
            aboutAction.triggered.connect(self.showAbout)
            helpMenu.addAction(aboutAction)
            
            donateAction = QAction('Donate', self)
            donateAction.triggered.connect(self.showDonate)
            helpMenu.addAction(donateAction)

            tutorialAction = QAction('Tutorial', self)
            tutorialAction.triggered.connect(self.show_tutorial_dialog)
            helpMenu.addAction(tutorialAction)

            # Options
            optionsMenu = menuBar.addMenu('Options')
            
            selectFolderAction = QAction('Select Folder', self)
            selectFolderAction.triggered.connect(self.selectFolder)
            optionsMenu.addAction(selectFolderAction)
            
            parseAction = QAction('Parse', self)
            parseAction.triggered.connect(self.parseSelectedFolder)
            optionsMenu.addAction(parseAction)
            
            saveAction = QAction('Save', self)
            saveAction.triggered.connect(self.saveToFile)
            optionsMenu.addAction(saveAction)
            
            copyAction = QAction('Copy to Clipboard', self)
            copyAction.triggered.connect(self.copyToClipboard)
            optionsMenu.addAction(copyAction)
            
            copyStructureAction = QAction('Copy File Structure', self)
            copyStructureAction.triggered.connect(self.copyFileStructure)
            optionsMenu.addAction(copyStructureAction)

            self.selected_folder = None
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Error initializing UI: {str(e)}")

    def initSystemTray(self):
        try:
            self.trayIcon = QSystemTrayIcon(self)
            self.trayIcon.setIcon(QtGui.QIcon(resource_path("app_icon.ico")))

            trayMenu = QMenu(self)

            # Add actions to tray menu
            selectFolderAction = QAction("Select Folder", self)
            selectFolderAction.triggered.connect(self.selectFolder)
            trayMenu.addAction(selectFolderAction)

            parseAction = QAction("Parse", self)
            parseAction.triggered.connect(self.parseSelectedFolder)
            trayMenu.addAction(parseAction)

            saveAction = QAction("Save", self)
            saveAction.triggered.connect(self.saveToFile)
            trayMenu.addAction(saveAction)

            copyAction = QAction("Copy to Clipboard", self)
            copyAction.triggered.connect(self.copyToClipboard)
            trayMenu.addAction(copyAction)

            copyStructureAction = QAction("Copy File Structure", self)
            copyStructureAction.triggered.connect(self.copyFileStructure)
            trayMenu.addAction(copyStructureAction)

            aboutAction = QAction("About", self)
            aboutAction.triggered.connect(self.showAbout)
            trayMenu.addAction(aboutAction)

            donateAction = QAction("Donate", self)
            donateAction.triggered.connect(self.showDonate)
            trayMenu.addAction(donateAction)

            tutorialAction = QAction("Tutorial", self)
            tutorialAction.triggered.connect(self.show_tutorial_dialog)
            trayMenu.addAction(tutorialAction)

            exitAction = QAction("Exit", self)
            exitAction.triggered.connect(QApplication.quit)
            trayMenu.addAction(exitAction)

            self.trayIcon.setContextMenu(trayMenu)
            self.trayIcon.show()
        except Exception as e:
            QMessageBox.critical(self, "System Tray Error", f"Error initializing system tray: {str(e)}")

    def onFolderClicked(self, index):
        try:
            self.selected_folder = self.folderModel.filePath(index)
            self.populateFileList(self.selected_folder)
        except Exception as e:
            QMessageBox.critical(self, "Folder Selection Error", f"Error selecting folder: {str(e)}")

    def selectFolder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Select Directory")
            if folder:
                self.selected_folder = folder
                index = self.folderModel.index(folder)
                self.folderView.setCurrentIndex(index)
                self.populateFileList(folder)
        except Exception as e:
            QMessageBox.critical(self, "Folder Selection Error", f"Error selecting folder: {str(e)}")

    def populateFileList(self, folder):
        try:
            self.fileList.clear()
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.filterFileType(file):
                        self.fileList.addItem(file_path)
            self.filterFileList()
        except Exception as e:
            QMessageBox.critical(self, "File Population Error", f"Error populating file list: {str(e)}")

    def filterFolderTree(self):
        try:
            search_term = self.folderSearchBar.text().lower()
            self.folderView.setRootIndex(self.folderModel.index(QDir.rootPath()))
            self.filterFolderModel(self.folderModel.index(QDir.rootPath()), search_term)
        except Exception as e:
            QMessageBox.critical(self, "Folder Filter Error", f"Error filtering folder tree: {str(e)}")

    def filterFolderModel(self, parent, search_term):
        for row in range(self.folderModel.rowCount(parent)):
            index = self.folderModel.index(row, 0, parent)
            if not self.folderModel.isDir(index):
                continue
            folder_name = self.folderModel.fileName(index).lower()
            match = search_term in folder_name
            self.folderView.setRowHidden(row, parent, not match)
            if match or search_term in self.folderModel.filePath(index).lower():
                self.filterFolderModel(index, search_term)

    def filterFileType(self, file):
        try:
            selected_type = self.fileTypeFilter.currentText()
            if selected_type == "All Files":
                return True
            return file.endswith(selected_type)
        except Exception as e:
            QMessageBox.critical(self, "File Filter Error", f"Error filtering file type: {str(e)}")

    def filterFileList(self):
        try:
            search_term = self.searchBar.text().lower()
            for i in range(self.fileList.count()):
                item = self.fileList.item(i)
                item.setHidden(search_term not in item.text().lower())
        except Exception as e:
            QMessageBox.critical(self, "File Filter Error", f"Error filtering file list: {str(e)}")

    def parseSelectedFolder(self):
        try:
            if self.selected_folder and os.path.isdir(self.selected_folder):
                selected_items = self.fileList.selectedItems()
                if selected_items:
                    files_to_parse = [item.text() for item in selected_items]
                else:
                    files_to_parse = []
                    for root, dirs, files in os.walk(self.selected_folder):
                        for file in files:
                            if self.filterFileType(file):
                                files_to_parse.append(os.path.join(root, file))
                self.parseFiles(files_to_parse)
            else:
                QMessageBox.warning(self, "Warning", "Please select a valid folder first.")
        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Error parsing folder: {str(e)}")

    def parseFiles(self, files):
        try:
            self.textArea.clear()
            self.textArea.append('#' * 50)
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.textArea.append(f"\n\n{'#' * 4} {os.path.basename(file_path)}:\n\n")
                    self.textArea.append(content)
                    self.textArea.append("\n")
                    self.textArea.append('#' * 50)
                except Exception as e:
                    QMessageBox.critical(self, "File Read Error", f"Error reading {file_path}: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Error parsing files: {str(e)}")

    def saveToFile(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.textArea.toPlainText())
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Error saving file: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Save Dialog Error", f"Error opening save dialog: {str(e)}")

    def copyToClipboard(self):
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.textArea.toPlainText())
            QMessageBox.information(self, "Success", "Text copied to clipboard.")
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Error copying to clipboard: {str(e)}")

    def copyFileStructure(self):
        try:
            if not self.selected_folder:
                QMessageBox.warning(self, "Warning", "Please select a folder first.")
                return
            
            structure = []
            for root, dirs, files in os.walk(self.selected_folder):
                level = root.replace(self.selected_folder, '').count(os.sep)
                indent = ' ' * 4 * (level)
                structure.append('{}{}/'.format(indent, os.path.basename(root)))
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    structure.append('{}{}'.format(subindent, f))
            
            try:
                clipboard = QApplication.clipboard()
                clipboard.setText('\n'.join(structure))
                QMessageBox.information(self, "Success", "File structure copied to clipboard.")
            except Exception as e:
                QMessageBox.critical(self, "Copy Error", f"Error copying file structure to clipboard: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Copy Structure Error", f"Error copying file structure: {str(e)}")

    def onFileSelectionChanged(self):
        try:
            selected_items = self.fileList.selectedItems()
            if selected_items:
                file_path = selected_items[0].text()
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.textArea.setPlainText(content)
                    self.highlightSearchResults()
                except Exception as e:
                    QMessageBox.critical(self, "File Read Error", f"Error reading {file_path}: {str(e)}")
            self.updateToggleSelectButton()
        except Exception as e:
            QMessageBox.critical(self, "File Selection Error", f"Error handling file selection: {str(e)}")

    def highlightSearchResults(self):
        try:
            cursor = self.textArea.textCursor()
            cursor.movePosition(cursor.Start)
            search_term = self.searchBar.text()
            format = QtGui.QTextCharFormat()
            format.setBackground(QtGui.QBrush(Qt.yellow))

            while not cursor.isNull() and not cursor.atEnd():
                cursor = self.textArea.document().find(search_term, cursor)
                if not cursor.isNull():
                    cursor.mergeCharFormat(format)
        except Exception as e:
            QMessageBox.critical(self, "Highlight Error", f"Error highlighting search results: {str(e)}")

    def toggleSelectFiles(self):
        try:
            if self.toggleSelectButton.isChecked():
                self.fileList.selectAll()
                self.toggleSelectButton.setText("Deselect All Files")
            else:
                self.fileList.clearSelection()
                self.toggleSelectButton.setText("Select All Files")
        except Exception as e:
            QMessageBox.critical(self, "Toggle Error", f"Error toggling file selection: {str(e)}")

    def updateToggleSelectButton(self):
        try:
            if self.fileList.selectedItems():
                self.toggleSelectButton.setChecked(True)
                self.toggleSelectButton.setText("Deselect All Files")
            else:
                self.toggleSelectButton.setChecked(False)
                self.toggleSelectButton.setText("Select All Files")
        except Exception as e:
            QMessageBox.critical(self, "Update Toggle Error", f"Error updating toggle select button: {str(e)}")

    def show_tutorial_dialog(self):
        try:
            tutorialWindow = ParsingToolTutorialWindow(self)
            tutorialWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "Tutorial Error", f"Error opening tutorial: {str(e)}")

    def showAbout(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("About")
            dialog.setFixedSize(400, 300)

            layout = QVBoxLayout()

            message = QLabel("This is a Parsing Tool application that allows you to select a folder and parse its files.\n\nFor more information, check out the Tutorial in the Help menu.\n\nFor support, email us at Support@TSTP.xyz.\n\nThank you for your support and for downloading the Parsing Tool!")
            message.setWordWrap(True)
            message.setAlignment(Qt.AlignCenter)
        
            layout.addWidget(message)
        
            button_layout = QHBoxLayout()
        
            btn_yes = QPushButton("Yes")
            btn_yes.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QUrl("https://tstp.xyz/programs/parsing-tool/")))
        
            btn_ok = QPushButton("OK")
            btn_ok.clicked.connect(dialog.close)
        
            button_layout.addWidget(btn_yes)
            button_layout.addWidget(btn_ok)
        
            layout.addLayout(button_layout)
        
            dialog.setLayout(layout)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "About Error", f"Error showing about dialog: {str(e)}")

    def showDonate(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Donate")
            dialog.setFixedSize(400, 200)

            layout = QVBoxLayout()

            message = QLabel("Thank you for considering a donation!\n\nYou do not have to donate, as this program is free and we will continue to provide free programs and projects for the public, but your donation is greatly appreciated if you still choose to.\n\nThank you for supporting us by downloading the program!\n\nWe appreciate it over at TSTP.")
            message.setWordWrap(True)
            message.setAlignment(Qt.AlignCenter)
        
            layout.addWidget(message)
        
            button_layout = QHBoxLayout()
        
            btn_yes = QPushButton("Yes")
            btn_yes.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QUrl("https://www.tstp.xyz/donate")))
        
            btn_ok = QPushButton("OK")
            btn_ok.clicked.connect(dialog.close)
        
            button_layout.addWidget(btn_yes)
            button_layout.addWidget(btn_ok)
        
            layout.addLayout(button_layout)
        
            dialog.setLayout(layout)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Donate Error", f"Error showing donate dialog: {str(e)}")

class ParsingToolTutorialWindow(QWidget):
    def __init__(self, parent=None):
        super(ParsingToolTutorialWindow, self).__init__(parent)
        try:
            self.setWindowIcon(QtGui.QIcon(resource_path("app_icon.ico")))   
            self.setWindowTitle("Interactive Tutorial")
            self.setGeometry(100, 100, 800, 600)
            self.setWindowFlags(Qt.Window)

            self.layout = QVBoxLayout()

            self.webView = QWebEngineView()
            self.webView.setStyleSheet("background-color: #ffffff;")  # White background for the content
            
            self.layout.addWidget(self.webView)

            self.navigation_layout = QHBoxLayout()
            self.navigation_layout.setContentsMargins(10, 10, 10, 10)  # Margin for cleaner look

            self.back_button = QPushButton("Previous")
            self.back_button.setStyleSheet(self.button_style())
            self.back_button.clicked.connect(self.go_to_previous_page)
            self.navigation_layout.addWidget(self.back_button)

            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setStyleSheet(self.progress_bar_style())
            self.navigation_layout.addWidget(self.progress_bar)

            self.next_button = QPushButton("Next")
            self.next_button.setStyleSheet(self.button_style())
            self.next_button.clicked.connect(self.go_to_next_page)
            self.navigation_layout.addWidget(self.next_button)

            self.start_button = QPushButton("Start Using App")
            self.start_button.setStyleSheet(self.button_style())
            self.start_button.clicked.connect(self.close)
            self.navigation_layout.addWidget(self.start_button)

            self.layout.addLayout(self.navigation_layout)
            self.setLayout(self.layout)

            self.current_page_index = 0
            self.tutorial_pages = [
                self.create_welcome_page(),
                self.create_overview_page(),
                self.create_select_folder_page(),
                self.create_search_filter_page(),
                self.create_parse_files_page(),
                self.create_save_copy_page(),
                self.create_copy_structure_page(),
                self.create_error_handling_page()
            ]

            self.load_tutorial_page(self.current_page_index)
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Error initializing tutorial: {str(e)}")

    def load_tutorial_page(self, index):
        try:
            self.webView.setHtml(self.tutorial_pages[index])
            self.progress_bar.setValue(int((index + 1) / len(self.tutorial_pages) * 100))
        except Exception as e:
            QMessageBox.critical(self, "Loading Error", f"Error loading tutorial page: {str(e)}")

    def go_to_previous_page(self):
        try:
            if self.current_page_index > 0:
                self.current_page_index -= 1
                self.load_tutorial_page(self.current_page_index)
        except Exception as e:
            QMessageBox.critical(self, "Navigation Error", f"Error navigating to previous page: {str(e)}")

    def go_to_next_page(self):
        try:
            if self.current_page_index < len(self.tutorial_pages) - 1:
                self.current_page_index += 1
                self.load_tutorial_page(self.current_page_index)
        except Exception as e:
            QMessageBox.critical(self, "Navigation Error", f"Error navigating to next page: {str(e)}")

    def open_link_in_browser(self, url):
        try:
            QtGui.QDesktopServices.openUrl(url)
        except Exception as e:
            QMessageBox.critical(self, "Link Error", f"Error opening link: {str(e)}")

    def button_style(self):
        return """
        QPushButton {
            background-color: #4CAF50; /* Green */
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            margin: 4px 2px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """

    def progress_bar_style(self):
        return """
        QProgressBar {
            border: 1px solid #bbb;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            width: 20px;
        }
        """

    def create_welcome_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #333; }
                p { font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>Welcome to the Parsing Tool Interactive Tutorial</h1>
            <p>In this tutorial, you will learn how to use the key features of the Parsing Tool application in detail.</p>
            <p>Let's get started!</p>
        </body>
        </html>
        """

    def create_overview_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Overview</h2>
            <p>The Parsing Tool allows you to select a folder and parse its files, displaying the content in a user-friendly interface.</p>
            <p>Key features include:</p>
            <ul>
                <li>File search and filtering</li>
                <li>Parsing and displaying file contents</li>
                <li>Saving and copying parsed content</li>
                <li>Copying file structure</li>
                <li>Advanced error handling</li>
            </ul>
        </body>
        </html>
        """

    def create_select_folder_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Selecting a Folder</h2>
            <p>To begin, select a folder to parse:</p>
            <ol>
                <li>Click on the 'Select Folder' button.</li>
                <li>Browse to the desired directory and select it.</li>
                <li>The folder structure will be displayed on the left side of the application.</li>
            </ol>
        </body>
        </html>
        """

    def create_search_filter_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
                ul { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Search and Filter Files</h2>
            <p>Use the search bar and filter options to narrow down the list of files:</p>
            <ul>
                <li>Type in the search bar to filter files by name.</li>
                <li>Select a file type from the dropdown menu to filter by extension (e.g., .txt, .log, .xml).</li>
                <li>The file list will update in real-time based on your search criteria.</li>
            </ul>
        </body>
        </html>
        """

    def create_parse_files_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
                ul { font-size: 14px; }
                ol { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Parsing Files</h2>
            <p>To parse files:</p>
            <ol>
                <li>Select one or more files from the list.</li>
                <li>Click the 'Parse' button to display their contents in the text area.</li>
            </ol>
            <p>If no files are selected, all files in the folder and subfolders will be parsed.</p>
        </body>
        </html>
        """

    def create_save_copy_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
                ol { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Saving and Copying Parsed Content</h2>
            <p>You can save or copy the parsed content for further use:</p>
            <ol>
                <li>Click 'Save' to save the parsed content to a file.</li>
                <li>Click 'Copy to Clipboard' to copy the parsed content to the clipboard.</li>
            </ol>
        </body>
        </html>
        """

    def create_copy_structure_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
                ol { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Copying File Structure</h2>
            <p>To copy the structure of the selected folder:</p>
            <ol>
                <li>Click the 'Copy File Structure' button.</li>
                <li>The folder structure will be copied to the clipboard in a readable format.</li>
            </ol>
        </body>
        </html>
        """

    def create_error_handling_page(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h2 { color: #333; }
                p { font-size: 14px; }
                ul { font-size: 14px; }
            </style>
        </head>
        <body>
            <h2>Advanced Error Handling</h2>
            <p>The Parsing Tool includes advanced error handling to ensure smooth operation:</p>
            <ul>
                <li>Errors encountered during file parsing will be displayed in a message box.</li>
                <li>Error messages provide detailed information about the issue and possible causes.</li>
                <li>Ensure you have the necessary permissions to read and write files in the selected folder.</li>
            </ul>
        </body>
        </html>
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ParsingToolMainWindow()
    ex.show()
    sys.exit(app.exec_())
