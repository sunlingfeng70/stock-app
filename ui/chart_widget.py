import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
import numpy as np

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "PingFang SC", "Heiti SC", "WenQuanYi Micro Hei"]
plt.rcParams["axes.unicode_minus"] = False


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def plot_kline(self, df, indicators):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        close = df["close"].values.astype(float)
        dates = df["date"].values
        x = np.arange(len(close))

        ax.plot(x, close, label="收盘价", color="black", linewidth=1)
        ax.plot(x, indicators["ma20"], label="MA20", color="blue", alpha=0.7, linewidth=0.8)
        ax.plot(x, indicators["ma60"], label="MA60", color="orange", alpha=0.7, linewidth=0.8)
        ax.fill_between(x, indicators["boll_upper"], indicators["boll_lower"],
                        alpha=0.1, color="gray", label="布林带")

        n = len(x)
        step = max(1, n // 8)
        tick_positions = list(range(0, n, step))
        if tick_positions[-1] != n - 1:
            tick_positions.append(n - 1)
        tick_labels = [dates[i] for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, fontsize=8)
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()