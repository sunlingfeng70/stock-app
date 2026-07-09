from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QGridLayout, QFrame,
)
from PySide6.QtCore import Qt
from ui.chart_widget import ChartWidget
from ui.signal_table import SignalTable


SIGNAL_STYLES = {
    "buy": ("买入", "color: white; background-color: #e74c3c; padding: 6px 20px; border-radius: 4px; font-size: 16px; font-weight: bold;"),
    "add": ("加仓", "color: white; background-color: #2ecc71; padding: 6px 20px; border-radius: 4px; font-size: 16px; font-weight: bold;"),
    "sell": ("卖出", "color: white; background-color: #e67e22; padding: 6px 20px; border-radius: 4px; font-size: 16px; font-weight: bold;"),
    "hold": ("持有", "color: white; background-color: #3498db; padding: 6px 20px; border-radius: 4px; font-size: 16px; font-weight: bold;"),
}


def _value_label(text, color="#2c3e50"):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size: 14px; color: {color}; font-weight: bold;")
    return lbl


class DetailPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.signal_label = QLabel()
        self.signal_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.signal_label)

        info_group = QGroupBox("当前指标")
        grid = QGridLayout(info_group)
        grid.addWidget(QLabel("价格:"), 0, 0)
        self.price_label = _value_label("-")
        grid.addWidget(self.price_label, 0, 1)
        grid.addWidget(QLabel("涨跌幅:"), 0, 2)
        self.pct_label = _value_label("-")
        grid.addWidget(self.pct_label, 0, 3)
        grid.addWidget(QLabel("MA20:"), 0, 4)
        self.ma20_label = _value_label("-")
        grid.addWidget(self.ma20_label, 0, 5)

        grid.addWidget(QLabel("MA60:"), 1, 0)
        self.ma60_label = _value_label("-")
        grid.addWidget(self.ma60_label, 1, 1)
        grid.addWidget(QLabel("RSI:"), 1, 2)
        self.rsi_label = _value_label("-")
        grid.addWidget(self.rsi_label, 1, 3)
        grid.addWidget(QLabel("布林上/中/下:"), 1, 4)
        self.boll_label = _value_label("-")
        grid.addWidget(self.boll_label, 1, 5)
        layout.addWidget(info_group)

        self.chart = ChartWidget()
        layout.addWidget(self.chart, stretch=1)

        section_label = QLabel("历史信号记录")
        section_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(section_label)

        self.signal_table = SignalTable()
        layout.addWidget(self.signal_table)

    def show_stock(self, code, price, pct_chg, signal, signal_reason,
                   ma20, ma60, rsi, boll_upper, boll_mid, boll_lower):
        signal_label, signal_style = SIGNAL_STYLES.get(signal, ("-", ""))
        text = f"{code} 当前信号: {signal_label}"
        if signal_reason:
            text += f"  ({signal_reason})"
        self.signal_label.setText(text)
        self.signal_label.setStyleSheet(signal_style)

        self.price_label.setText(f"{price:.2f}")
        pct_color = "#e74c3c" if pct_chg >= 0 else "#2ecc71"
        self.pct_label.setText(f"{pct_chg:+.2f}%")
        self.pct_label.setStyleSheet(f"font-size: 14px; color: {pct_color}; font-weight: bold;")
        self.ma20_label.setText(f"{ma20:.2f}" if ma20 else "-")
        self.ma60_label.setText(f"{ma60:.2f}" if ma60 else "-")
        self.rsi_label.setText(f"{rsi:.1f}" if rsi else "-")
        if boll_upper and boll_mid and boll_lower:
            self.boll_label.setText(f"{boll_upper:.2f} / {boll_mid:.2f} / {boll_lower:.2f}")
        else:
            self.boll_label.setText("-")

    def update_chart(self, df, indicators):
        self.chart.plot_kline(df, indicators)

    def update_signals(self, signals):
        self.signal_table.update_data(signals)