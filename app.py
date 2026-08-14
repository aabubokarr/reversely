import os
import sys
import subprocess

from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QSize,
    QUrl,
)

from PySide6.QtGui import (
    QPixmap,
    QDesktopServices,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSlider,
    QProgressBar,
    QMessageBox,
    QScrollArea,
    QFrame,
    QMenu,
    QSizePolicy,
)

from search_engine import ImageSearchEngine


# ============================================================
# INDEX THREAD
# ============================================================

class IndexThread(QThread):

    progress = Signal(int, int, str)
    completed = Signal(int)
    failed = Signal(str)

    def __init__(
        self,
        engine,
        folder
    ):

        super().__init__()

        self.engine = engine
        self.folder = folder

    def run(self):

        try:

            count = self.engine.build_index(
                self.folder,
                self.send_progress
            )

            self.completed.emit(count)

        except Exception as e:

            self.failed.emit(
                str(e)
            )

    def send_progress(
        self,
        current,
        total,
        path
    ):

        self.progress.emit(
            current,
            total,
            path
        )


# ============================================================
# SEARCH THREAD
# ============================================================

class SearchThread(QThread):

    completed = Signal(list)
    failed = Signal(str)

    def __init__(
        self,
        engine,
        query,
        threshold
    ):

        super().__init__()

        self.engine = engine
        self.query = query
        self.threshold = threshold

    def run(self):

        try:

            results = self.engine.search(
                self.query,
                threshold=self.threshold,
                top_k=50
            )

            self.completed.emit(
                results
            )

        except Exception as e:

            self.failed.emit(
                str(e)
            )


# ============================================================
# DROP AREA
# ============================================================

class DropArea(QFrame):

    imageDropped = Signal(str)

    def __init__(self):

        super().__init__()

        self.setAcceptDrops(True)

        self.setObjectName(
            "dropArea"
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        self.label = QLabel(
            "Drop an image here"
        )

        self.label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.label.setObjectName(
            "dropLabel"
        )

        layout.addWidget(
            self.label
        )

        self.preview = QLabel()

        self.preview.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.preview.setVisible(
            False
        )

        layout.addWidget(
            self.preview
        )

    def dragEnterEvent(
        self,
        event
    ):

        if event.mimeData().hasUrls():

            for url in event.mimeData().urls():

                path = url.toLocalFile()

                if os.path.isfile(path):

                    event.acceptProposedAction()
                    return

        event.ignore()

    def dropEvent(
        self,
        event
    ):

        for url in event.mimeData().urls():

            path = url.toLocalFile()

            if os.path.isfile(path):

                self.set_image(
                    path
                )

                self.imageDropped.emit(
                    path
                )

                event.acceptProposedAction()
                return

    def set_image(
        self,
        path
    ):

        pixmap = QPixmap(
            path
        )

        if pixmap.isNull():
            return

        pixmap = pixmap.scaled(
            275,
            275,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview.setPixmap(
            pixmap
        )

        self.preview.setVisible(
            True
        )

        self.label.setVisible(
            False
        )


# ============================================================
# RESULT CARD
# ============================================================

class ResultCard(QFrame):

    def __init__(
        self,
        path,
        similarity
    ):

        super().__init__()

        self.path = path

        self.setObjectName(
            "resultCard"
        )

        self.setFixedSize(
            190,
            220
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            6,
            6,
            6,
            7
        )

        layout.setSpacing(
            5
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        self.image = QLabel()

        self.image.setFixedSize(
            178,
            158
        )

        self.image.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.image.setObjectName(
            "resultImage"
        )

        pixmap = QPixmap(
            path
        )

        if not pixmap.isNull():

            pixmap = pixmap.scaled(
                174,
                154,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.image.setPixmap(
                pixmap
            )

        layout.addWidget(
            self.image
        )

        # ----------------------------------------------------
        # BOTTOM ROW
        # ----------------------------------------------------

        bottom = QHBoxLayout()

        bottom.setSpacing(
            5
        )

        filename = os.path.basename(
            path
        )

        name = QLabel(
            filename
        )

        name.setToolTip(
            path
        )

        name.setObjectName(
            "filename"
        )

        name.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        bottom.addWidget(
            name
        )

        score = QLabel(
            f"{similarity * 100:.1f}%"
        )

        score.setObjectName(
            "score"
        )

        bottom.addWidget(
            score
        )

        layout.addLayout(
            bottom
        )

        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.customContextMenuRequested.connect(
            self.show_context_menu
        )

    def mouseDoubleClickEvent(
        self,
        event
    ):

        if event.button() == Qt.MouseButton.LeftButton:

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(
                    self.path
                )
            )

        super().mouseDoubleClickEvent(
            event
        )

    def show_context_menu(
        self,
        position
    ):

        menu = QMenu(
            self
        )

        open_action = menu.addAction(
            "Open Image"
        )

        reveal_action = menu.addAction(
            "Reveal in Finder"
        )

        action = menu.exec(
            self.mapToGlobal(position)
        )

        if action == open_action:

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(
                    self.path
                )
            )

        elif action == reveal_action:

            if sys.platform == "darwin":

                subprocess.run([
                    "open",
                    "-R",
                    self.path
                ])

            elif sys.platform.startswith(
                "win"
            ):

                subprocess.run([
                    "explorer",
                    "/select,",
                    os.path.normpath(
                        self.path
                    )
                ])


# ============================================================
# MAIN WINDOW
# ============================================================

class ReverselyWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.engine = None
        self.media_folder = None
        self.query_path = None

        self.index_thread = None
        self.search_thread = None

        self.setWindowTitle(
            "Reversely"
        )

        self.resize(
            1280,
            800
        )

        self.setMinimumSize(
            1050,
            650
        )

        self.setup_ui()

        self.load_engine()

    # ========================================================
    # ENGINE
    # ========================================================

    def load_engine(self):

        self.status_text.setText(
            "Loading vision model..."
        )

        QApplication.processEvents()

        try:

            self.engine = ImageSearchEngine()

            count = len(
                self.engine.index
            )

            self.status_text.setText(
                f"{count:,} images indexed"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Startup Error",
                str(e)
            )

            self.status_text.setText(
                "Model failed to load"
            )

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        root = QVBoxLayout(
            central
        )

        root.setContentsMargins(
            18,
            14,
            18,
            14
        )

        root.setSpacing(
            12
        )

        # ====================================================
        # TOOLBAR
        # ====================================================

        toolbar = QFrame()

        toolbar.setObjectName(
            "toolbar"
        )

        toolbar_layout = QHBoxLayout(
            toolbar
        )

        toolbar_layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        toolbar_layout.setSpacing(
            10
        )

        logo = QLabel(
            "Reversely"
        )

        logo.setObjectName(
            "logo"
        )

        toolbar_layout.addWidget(
            logo
        )

        subtitle = QLabel(
            "Reverse image search"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        toolbar_layout.addWidget(
            subtitle
        )

        toolbar_layout.addStretch()

        self.status_dot = QLabel(
            "●"
        )

        self.status_dot.setObjectName(
            "statusDot"
        )

        toolbar_layout.addWidget(
            self.status_dot
        )

        self.status_text = QLabel(
            "Starting..."
        )

        self.status_text.setObjectName(
            "statusText"
        )

        toolbar_layout.addWidget(
            self.status_text
        )

        root.addWidget(
            toolbar
        )

        # ====================================================
        # MAIN CONTENT
        # ====================================================

        content = QHBoxLayout()

        content.setSpacing(
            14
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            330
        )

        side = QVBoxLayout(
            sidebar
        )

        side.setContentsMargins(
            18,
            18,
            18,
            18
        )

        side.setSpacing(
            12
        )

        search_title = QLabel(
            "Search"
        )

        search_title.setObjectName(
            "sectionTitle"
        )

        side.addWidget(
            search_title
        )

        description = QLabel(
            "Choose an image to find visually similar images in your media folder."
        )

        description.setWordWrap(
            True
        )

        description.setObjectName(
            "description"
        )

        side.addWidget(
            description
        )

        # ----------------------------------------------------
        # DROP AREA
        # ----------------------------------------------------

        self.drop_area = DropArea()

        self.drop_area.setFixedHeight(
            290
        )

        self.drop_area.imageDropped.connect(
            self.set_query
        )

        side.addWidget(
            self.drop_area
        )

        # ----------------------------------------------------
        # CHOOSE IMAGE
        # ----------------------------------------------------

        choose_button = QPushButton(
            "Choose Image"
        )

        choose_button.setObjectName(
            "secondaryButton"
        )

        choose_button.clicked.connect(
            self.choose_image
        )

        side.addWidget(
            choose_button
        )

        # ----------------------------------------------------
        # THRESHOLD
        # ----------------------------------------------------

        threshold_header = QHBoxLayout()

        threshold_label = QLabel(
            "Minimum similarity"
        )

        threshold_label.setObjectName(
            "fieldLabel"
        )

        threshold_header.addWidget(
            threshold_label
        )

        threshold_header.addStretch()

        self.threshold_value = QLabel(
            "80%"
        )

        self.threshold_value.setObjectName(
            "thresholdValue"
        )

        threshold_header.addWidget(
            self.threshold_value
        )

        side.addLayout(
            threshold_header
        )

        self.threshold_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.threshold_slider.setRange(
            50,
            95
        )

        self.threshold_slider.setValue(
            80
        )

        self.threshold_slider.valueChanged.connect(
            self.threshold_changed
        )

        side.addWidget(
            self.threshold_slider
        )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        self.search_button = QPushButton(
            "Search Similar Images"
        )

        self.search_button.setObjectName(
            "primaryButton"
        )

        self.search_button.clicked.connect(
            self.search
        )

        side.addWidget(
            self.search_button
        )

        # ----------------------------------------------------
        # FOLDER
        # ----------------------------------------------------

        folder_label = QLabel(
            "MEDIA LIBRARY"
        )

        folder_label.setObjectName(
            "smallHeading"
        )

        side.addWidget(
            folder_label
        )

        self.folder_text = QLabel(
            "No folder selected"
        )

        self.folder_text.setWordWrap(
            True
        )

        self.folder_text.setObjectName(
            "folderText"
        )

        side.addWidget(
            self.folder_text
        )

        self.choose_folder_button = QPushButton(
            "Choose Media Folder"
        )

        self.choose_folder_button.setObjectName(
            "secondaryButton"
        )

        self.choose_folder_button.clicked.connect(
            self.choose_folder
        )

        side.addWidget(
            self.choose_folder_button
        )

        self.reindex_button = QPushButton(
            "↻  Reindex Library"
        )

        self.reindex_button.setObjectName(
            "secondaryButton"
        )

        self.reindex_button.clicked.connect(
            self.reindex
        )

        side.addWidget(
            self.reindex_button
        )

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setVisible(
            False
        )

        self.progress.setTextVisible(
            False
        )

        self.progress.setFixedHeight(
            5
        )

        side.addWidget(
            self.progress
        )

        side.addStretch()

        content.addWidget(
            sidebar
        )

        # ====================================================
        # RESULTS
        # ====================================================

        results_panel = QFrame()

        results_panel.setObjectName(
            "resultsPanel"
        )

        results_layout = QVBoxLayout(
            results_panel
        )

        results_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        results_layout.setSpacing(
            10
        )

        results_header = QHBoxLayout()

        similar_title = QLabel(
            "Similar Images"
        )

        similar_title.setObjectName(
            "sectionTitle"
        )

        results_header.addWidget(
            similar_title
        )

        results_header.addStretch()

        self.results_count = QLabel(
            "No search yet"
        )

        self.results_count.setObjectName(
            "resultsCount"
        )

        results_header.addWidget(
            self.results_count
        )

        results_layout.addLayout(
            results_header
        )

        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.results_container = QWidget()
        self.results_container.setObjectName("results_container")

        self.results_grid = QGridLayout(
            self.results_container
        )

        self.results_grid.setContentsMargins(
            2,
            2,
            2,
            2
        )

        self.results_grid.setHorizontalSpacing(
            12
        )

        self.results_grid.setVerticalSpacing(
            12
        )

        self.results_grid.setAlignment(
            Qt.AlignmentFlag.AlignTop |
            Qt.AlignmentFlag.AlignLeft
        )

        self.scroll.setWidget(
            self.results_container
        )

        results_layout.addWidget(
            self.scroll
        )

        content.addWidget(
            results_panel,
            1
        )

        root.addLayout(
            content,
            1
        )

    # ========================================================
    # THRESHOLD
    # ========================================================

    def threshold_changed(
        self,
        value
    ):

        self.threshold_value.setText(
            f"{value}%"
        )

    # ========================================================
    # QUERY IMAGE
    # ========================================================

    def choose_image(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Search Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff)"
        )

        if path:

            self.set_query(
                path
            )

    def set_query(
        self,
        path
    ):

        if not os.path.isfile(path):
            return

        self.query_path = path

        self.drop_area.set_image(
            path
        )

        self.status_text.setText(
            "Image selected"
        )

    # ========================================================
    # MEDIA FOLDER
    # ========================================================

    def choose_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Media Folder"
        )

        if not folder:
            return

        self.media_folder = folder

        self.folder_text.setText(
            folder
        )

        self.reindex()

    # ========================================================
    # REINDEX
    # ========================================================

    def reindex(self):

        if self.engine is None:
            return

        if not self.media_folder:

            folder = QFileDialog.getExistingDirectory(
                self,
                "Choose Media Folder"
            )

            if not folder:
                return

            self.media_folder = folder

            self.folder_text.setText(
                folder
            )

        self.set_indexing_state(
            True
        )

        self.index_thread = IndexThread(
            self.engine,
            self.media_folder
        )

        self.index_thread.progress.connect(
            self.index_progress
        )

        self.index_thread.completed.connect(
            self.index_finished
        )

        self.index_thread.failed.connect(
            self.index_failed
        )

        self.index_thread.start()

    def set_indexing_state(
        self,
        indexing
    ):

        self.reindex_button.setEnabled(
            not indexing
        )

        self.choose_folder_button.setEnabled(
            not indexing
        )

        self.search_button.setEnabled(
            not indexing
        )

        self.progress.setVisible(
            indexing
        )

        if indexing:

            self.status_dot.setObjectName(
                "statusDotBusy"
            )

            self.status_dot.style().unpolish(
                self.status_dot
            )

            self.status_dot.style().polish(
                self.status_dot
            )

    def index_progress(
        self,
        current,
        total,
        path
    ):

        if total > 0:

            self.progress.setValue(
                int(
                    current / total * 100
                )
            )

        filename = os.path.basename(
            path
        )

        self.status_text.setText(
            f"Indexing {current:,} / {total:,}  •  {filename}"
        )

    def index_finished(
        self,
        count
    ):

        self.set_indexing_state(
            False
        )

        self.status_dot.setObjectName(
            "statusDot"
        )

        self.status_dot.style().unpolish(
            self.status_dot
        )

        self.status_dot.style().polish(
            self.status_dot
        )

        self.status_text.setText(
            f"{count:,} images indexed"
        )

        self.results_count.setText(
            "Ready to search"
        )

    def index_failed(
        self,
        message
    ):

        self.set_indexing_state(
            False
        )

        QMessageBox.critical(
            self,
            "Indexing Error",
            message
        )

        self.status_text.setText(
            "Indexing failed"
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def search(self):

        if self.engine is None:

            QMessageBox.warning(
                self,
                "Not Ready",
                "The image model has not finished loading."
            )

            return

        if not self.query_path:

            QMessageBox.information(
                self,
                "Choose an Image",
                "Choose or drop an image first."
            )

            return

        if not self.engine.index:

            QMessageBox.information(
                self,
                "Library Empty",
                "Choose a media folder and index it first."
            )

            return

        threshold = (
            self.threshold_slider.value()
            / 100
        )

        self.search_button.setEnabled(
            False
        )

        self.search_button.setText(
            "Searching..."
        )

        self.status_text.setText(
            "Searching your library..."
        )

        self.search_thread = SearchThread(
            self.engine,
            self.query_path,
            threshold
        )

        self.search_thread.completed.connect(
            self.search_finished
        )

        self.search_thread.failed.connect(
            self.search_failed
        )

        self.search_thread.start()

    def search_finished(
        self,
        results
    ):

        self.search_button.setEnabled(
            True
        )

        self.search_button.setText(
            "Search Similar Images"
        )

        self.display_results(
            results
        )

        self.status_text.setText(
            f"{len(results)} matching images"
        )

    def search_failed(
        self,
        message
    ):

        self.search_button.setEnabled(
            True
        )

        self.search_button.setText(
            "Search Similar Images"
        )

        QMessageBox.critical(
            self,
            "Search Error",
            message
        )

        self.status_text.setText(
            "Search failed"
        )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    def clear_results(self):

        while self.results_grid.count():

            item = self.results_grid.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

    def display_results(
        self,
        results
    ):

        self.clear_results()

        count = len(
            results
        )

        self.results_count.setText(
            f"{count} match" +
            ("" if count == 1 else "es")
        )

        if not results:

            empty = QLabel(
                "No images meet your similarity threshold."
            )

            empty.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty.setObjectName(
                "emptyResults"
            )

            self.results_grid.addWidget(
                empty,
                0,
                0
            )

            return

        # Four cards on a normal desktop window.
        # Qt will naturally wrap based on available width.
        columns = 4

        for index, result in enumerate(
            results
        ):

            row = index // columns

            column = index % columns

            card = ResultCard(
                result["path"],
                result["similarity"]
            )

            self.results_grid.addWidget(
                card,
                row,
                column
            )


# ============================================================
# APPLICATION
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "Reversely"
    )

    app.setStyle(
        "Fusion"
    )

    # --------------------------------------------------------
    # POLISHED UI
    # --------------------------------------------------------

    app.setStyleSheet(
        """
        /* ==================================================
           GLOBAL
        ================================================== */

        QWidget {
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "SF Pro Display",
                "Helvetica Neue",
                Arial;
            font-size: 13px;
            color: #1d1d1f;
        }

        QMainWindow {
            background: #f5f5f7;
        }


        /* ==================================================
           TOOLBAR
        ================================================== */

        #toolbar {
            background: #ffffff;
            border: 1px solid #e5e5e7;
            border-radius: 12px;
        }

        #logo {
            font-size: 22px;
            font-weight: 700;
            color: #111111;
        }

        #subtitle {
            color: #86868b;
            font-size: 13px;
        }

        #statusText {
            color: #86868b;
            font-size: 12px;
        }

        #statusDot {
            color: #34c759;
            font-size: 11px;
        }

        #statusDotBusy {
            color: #ff9500;
            font-size: 11px;
        }


        /* ==================================================
           SIDEBAR
        ================================================== */

        #sidebar {
            background: #ffffff;
            border: 1px solid #e5e5e7;
            border-radius: 12px;
        }

        #sectionTitle {
            font-size: 18px;
            font-weight: 700;
            color: #1d1d1f;
        }

        #description {
            color: #86868b;
            line-height: 1.4;
        }

        #smallHeading {
            font-size: 10px;
            font-weight: 700;
            color: #86868b;
            letter-spacing: 1px;
            margin-top: 8px;
        }

        #fieldLabel {
            font-size: 12px;
            color: #555555;
        }

        #thresholdValue {
            font-weight: 700;
            color: #007aff;
        }

        #folderText {
            color: #6e6e73;
            font-size: 11px;
        }


        /* ==================================================
           DROP AREA
        ================================================== */

        #dropArea {
            background: #f8f8fa;
            border: 1px dashed #c7c7cc;
            border-radius: 10px;
        }

        #dropArea:hover {
            background: #f2f2f7;
            border-color: #007aff;
        }

        #dropLabel {
            color: #86868b;
            font-size: 13px;
        }


        /* ==================================================
           BUTTONS
        ================================================== */

        QPushButton {
            min-height: 34px;
            padding-left: 13px;
            padding-right: 13px;
            border-radius: 7px;
            border: 1px solid #d1d1d6;
            background: #ffffff;
            color: #1d1d1f;
            font-weight: 600;
        }

        QPushButton:hover {
            background: #f2f2f7;
        }

        QPushButton:pressed {
            background: #e5e5ea;
        }

        QPushButton:disabled {
            color: #a1a1a6;
            background: #f5f5f7;
        }

        #primaryButton {
            background: #007aff;
            color: white;
            border: none;
            min-height: 40px;
            font-size: 13px;
        }

        #primaryButton:hover {
            background: #006ee6;
        }

        #primaryButton:pressed {
            background: #005dcc;
        }

        #secondaryButton {
            min-height: 34px;
        }


        /* ==================================================
           RESULTS
        ================================================== */

        #resultsPanel {
            background: #ffffff;
            border: 1px solid #e5e5e7;
            border-radius: 12px;
        }

        #resultsCount {
            color: #86868b;
            font-size: 12px;
        }

        #emptyResults {
            color: #86868b;
            font-size: 14px;
            padding: 40px;
        }


        /* ==================================================
           RESULT CARD
        ================================================== */

        #resultCard {
            background: #ffffff;
            border: 1px solid #e5e5e7;
            border-radius: 10px;
        }

        #resultCard:hover {
            border-color: #007aff;
            background: #fafcff;
        }

        #resultImage {
            background: #f5f5f7;
            border-radius: 7px;
        }

        #filename {
            color: #424245;
            font-size: 11px;
            font-weight: 500;
            max-width: 112px;
        }

        #score {
            color: #34c759;
            font-size: 11px;
            font-weight: 700;
            background: #eaf8ee;
            border-radius: 5px;
            padding: 3px 5px;
        }


        /* ==================================================
        SCROLL AREA
        ================================================== */

        #resultsPanel {
            background: #ffffff;
            border: 1px solid #e5e5e7;
            border-radius: 12px;
        }

        QScrollArea {
            border: none;
            background: #ffffff;
        }

        QScrollArea > QWidget > QWidget {
            background: #ffffff;
        }

        #results_container {
            background: #ffffff;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 3px;
        }

        QScrollBar::handle:vertical {
            background: #c7c7cc;
            border-radius: 4px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: #a1a1a6;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }


        /* ==================================================
           SLIDER
        ================================================== */

        QSlider::groove:horizontal {
            height: 4px;
            background: #d1d1d6;
            border-radius: 2px;
        }

        QSlider::sub-page:horizontal {
            background: #007aff;
            border-radius: 2px;
        }

        QSlider::handle:horizontal {
            width: 16px;
            height: 16px;
            margin: -6px 0;
            background: #ffffff;
            border: 1px solid #b0b0b5;
            border-radius: 8px;
        }


        /* ==================================================
           PROGRESS
        ================================================== */

        QProgressBar {
            background: #e5e5ea;
            border: none;
            border-radius: 2px;
        }

        QProgressBar::chunk {
            background: #007aff;
            border-radius: 2px;
        }


        /* ==================================================
           CONTEXT MENU
        ================================================== */

        QMenu {
            background: #ffffff;
            border: 1px solid #d1d1d6;
            padding: 5px;
            border-radius: 7px;
        }

        QMenu::item {
            padding: 7px 25px 7px 10px;
            border-radius: 5px;
        }

        QMenu::item:selected {
            background: #007aff;
            color: white;
        }
        """
    )

    window = ReverselyWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
    