from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStatusBar, QMessageBox, QSplitter,
)
from PySide6.QtCore import Qt, QThread, Signal
from ui.stock_list_widget import StockListWidget
from ui.detail_panel import DetailPanel
from db.database import get_stocks, init_db, init_stocks, save_price_cache, get_price_cache, save_signal, get_signals
from engine.data_fetcher import fetch_daily
from engine.indicators import compute_all
from engine.strategy import evaluate_current
from engine.backtest import run_backtest
from config import STOCKS
import pandas as pd


class FetchWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, code, name):
        super().__init__()
        self.code = code
        self.name = name

    def run(self):
        try:
            data = fetch_daily(self.code, self.name)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A股盘后分析")
        self.resize(1200, 800)
        init_db()
        init_stocks(STOCKS)

        self.stocks = get_stocks()
        self.current_code = None
        self.current_data = None
        self.current_indicators = None
        self.worker = None

        self._setup_ui()
        self._setup_statusbar()

        if self.stocks:
            self.stock_list.select_stock(self.stocks[0]["code"])

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QWidget()
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 4, 8, 4)

        self.btn_refresh = QPushButton("刷新数据")
        self.btn_refresh.clicked.connect(self.on_refresh)
        self.btn_backtest = QPushButton("策略回测")
        self.btn_backtest.clicked.connect(self.on_backtest)
        tb_layout.addWidget(self.btn_refresh)
        tb_layout.addWidget(self.btn_backtest)
        tb_layout.addStretch()
        layout.addWidget(toolbar)

        splitter = QSplitter(Qt.Horizontal)
        self.stock_list = StockListWidget(self.stocks)
        self.stock_list.stock_selected.connect(self.on_stock_selected)
        self.detail_panel = DetailPanel()
        splitter.addWidget(self.stock_list)
        splitter.addWidget(self.detail_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter)

    def _setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("就绪")

    def on_stock_selected(self, code):
        self.current_code = code
        self.status.showMessage(f"加载 {code} 数据...")
        cached = get_price_cache(code)
        if cached:
            df = pd.DataFrame(cached)
            self._process_data(df)
            self.status.showMessage(f"{code} 数据已加载（缓存）")
        else:
            self._do_fetch(code)

    def _do_fetch(self, code):
        stock = next((s for s in self.stocks if s["code"] == code), None)
        if not stock:
            return
        self.btn_refresh.setEnabled(False)
        self.status.showMessage(f"正在获取 {code} 数据...")
        self.worker = FetchWorker(code, stock["name"])
        self.worker.finished.connect(self._on_fetched)
        self.worker.error.connect(self._on_fetch_error)
        self.worker.start()

    def _on_fetched(self, data):
        self.btn_refresh.setEnabled(True)
        if not data:
            self.status.showMessage("未获取到数据")
            return
        save_price_cache(self.current_code, data)
        df = pd.DataFrame(data)
        self._process_data(df)
        self.status.showMessage(f"{self.current_code} 数据已更新")

    def _on_fetch_error(self, msg):
        self.btn_refresh.setEnabled(True)
        QMessageBox.warning(self, "数据获取失败", str(msg))
        self.status.showMessage("数据获取失败")

    def _process_data(self, df):
        if df.empty:
            return
        df = df.sort_values("date").reset_index(drop=True)
        ind = compute_all(df)
        self.current_data = df
        self.current_indicators = ind

        signal, reason = evaluate_current(df, ind)
        last = df.iloc[-1]
        self.detail_panel.show_stock(
            code=self.current_code,
            price=float(last["close"]),
            pct_chg=float(last.get("pct_chg", 0)),
            signal=signal,
            signal_reason=reason,
            ma20=ind["ma20"][-1],
            ma60=ind["ma60"][-1],
            rsi=ind["rsi"][-1],
            boll_upper=ind["boll_upper"][-1],
            boll_mid=ind["boll_mid"][-1],
            boll_lower=ind["boll_lower"][-1],
        )

        sig_data = {
            "ma20": ind["ma20"][-1],
            "ma60": ind["ma60"][-1],
            "rsi": ind["rsi"][-1],
            "boll_upper": ind["boll_upper"][-1],
            "boll_mid": ind["boll_mid"][-1],
            "boll_lower": ind["boll_lower"][-1],
            "volume_ratio": ind["volume_ratio"][-1],
        }
        save_signal(
            self.current_code, str(last["date"]),
            signal, float(last["close"]), sig_data, reason,
        )

        self.detail_panel.update_chart(df, ind)

        signals = get_signals(self.current_code)
        self.detail_panel.update_signals(signals)

    def on_refresh(self):
        if self.current_code:
            self._do_fetch(self.current_code)

    def on_backtest(self):
        if self.current_data is None or self.current_indicators is None:
            QMessageBox.information(self, "提示", "请先加载股票数据")
            return
        result = run_backtest(self.current_data, self.current_indicators)
        msg = (
            f"总交易次数: {result['total_trades']}\n"
            f"胜率: {result['win_rate']}%\n"
            f"总盈亏: {result['total_profit']}%\n\n"
            f"交易记录:\n"
        )
        for t in result["trades"]:
            arrow = "→" if t["type"] == "sell" else ("↓" if t["type"] == "buy" else "↑")
            profit_str = f" {t['profit_pct']}%" if "profit_pct" in t else ""
            msg += f"  {t['date']} {arrow} {t['type']} @ {t['price']}{profit_str} {t['reason']}\n"
        QMessageBox.information(self, "回测结果", msg)