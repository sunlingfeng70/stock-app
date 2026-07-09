from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt


SIGNAL_LABELS = {
    "buy": "买入",
    "add": "加仓",
    "sell": "卖出",
    "hold": "持有",
}


class SignalTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["日期", "信号", "价格", "RSI", "备注"])
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def update_data(self, signals):
        self.setRowCount(len(signals))
        for row, s in enumerate(signals):
            self.setItem(row, 0, QTableWidgetItem(s["date"]))
            label = SIGNAL_LABELS.get(s["signal_type"], s["signal_type"])
            item = QTableWidgetItem(label)
            if s["signal_type"] == "buy":
                item.setForeground(Qt.red)
            elif s["signal_type"] == "add":
                item.setForeground(Qt.blue)
            elif s["signal_type"] == "sell":
                item.setForeground(Qt.darkGreen)
            self.setItem(row, 1, item)
            self.setItem(row, 2, QTableWidgetItem(
                f'{s["price"]:.2f}' if s["price"] else ""
            ))
            self.setItem(row, 3, QTableWidgetItem(
                f'{s["rsi"]:.1f}' if s["rsi"] else ""
            ))
            self.setItem(row, 4, QTableWidgetItem(s.get("note", "")))