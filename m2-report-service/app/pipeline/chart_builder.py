"""Daily time-series chart ("Tracks Over Date Range") as PNG bytes.

Colors follow the Pronatura system: Tide (#1b5c5a) for total registros,
Amber (#e07c2a) for alertas — amber is the attention color in the dashboard.
"""

import calendar
import io
from datetime import date

import matplotlib

matplotlib.use("Agg")  # headless backend — must be set before pyplot import
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

COLOR_TOTAL = "#1b5c5a"   # Tide
COLOR_ALERTS = "#e07c2a"  # Amber
COLOR_GRID = "#e8e4df"    # Fog
COLOR_TEXT = "#6b6760"    # Stone


def build_daily_chart(daily_total: dict, daily_alerts: dict,
                      year: int, month: int) -> bytes:
    last_day = calendar.monthrange(year, month)[1]
    days = [date(year, month, d) for d in range(1, last_day + 1)]
    totals = [daily_total.get(d, 0) for d in days]
    alerts = [daily_alerts.get(d, 0) for d in days]

    fig, ax = plt.subplots(figsize=(9, 3.4), dpi=160)

    ax.plot(days, totals, color=COLOR_TOTAL, linewidth=1.8,
            marker="o", markersize=3, label="Registros totales")
    ax.fill_between(days, totals, color=COLOR_TOTAL, alpha=0.08)
    ax.plot(days, alerts, color=COLOR_ALERTS, linewidth=1.8,
            marker="o", markersize=3, label="Alertas")

    ax.set_xlim(days[0], days[-1])
    ax.set_ylim(bottom=0, top=max(max(totals), 1) * 1.1)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d"))
    ax.tick_params(colors=COLOR_TEXT, labelsize=8)
    ax.grid(axis="y", color=COLOR_GRID, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(COLOR_GRID)

    ax.legend(loc="upper right", frameon=False, fontsize=8, labelcolor=COLOR_TEXT)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    return buffer.getvalue()
