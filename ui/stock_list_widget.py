from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal


class StockListWidget(QWidget):
    stock_selected = Signal(str)

    def __init__(self, stocks):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self.list_widget)
        self.stocks = stocks
        self._populate()

    def _populate(self):
        for s in self.stocks:
            item = QListWidgetItem(f"{s['code']} {s['name']}")
            item.setData(256, s["code"])
            self.list_widget.addItem(item)

    def _on_selection(self, current, _previous):
        if current:
            code = current.data(256)
            self.stock_selected.emit(code)

    def select_stock(self, code):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(256) == code:
                self.list_widget.setCurrentItem(item)
                break