import datetime
import io

import matplotlib.pyplot as plt
import numpy as np


class LifeInWeeks:
    def __init__(
        self,
        birthday: str = "1970-1-1",
        figure_scale=1.0,
        dpi=100,
        edgecolor="black",
        years=90,
        weeks_per_year=52,
    ):
        self.years = years
        self.weeks_per_year = weeks_per_year
        self.figure_scale = figure_scale
        self.dpi = dpi
        self.edgecolor = edgecolor
        self.birthday = datetime.datetime.strptime(birthday, "%Y-%m-%d").date()

    def _patch(self, week, age, color):
        return plt.Rectangle(
            (week, age),
            1,
            1,
            linewidth=1,
            edgecolor=self.edgecolor,
            facecolor=color,
        )

    def draw(self):
        fig, ax = plt.subplots(
            figsize=(8.27 * self.figure_scale, 11.69 * self.figure_scale), dpi=self.dpi
        )

        ax.set_title("A 90-Year Human Life in Weeks", fontsize=16)
        ax.set_xlabel("Week of Year", fontsize=12)
        ax.set_ylabel("Age", fontsize=12)

        ax.set_xlim([0, self.weeks_per_year])
        ax.set_ylim([0, self.years])
        ax.set_xticks(np.arange(0, self.weeks_per_year + 1, 13))
        ax.set_yticks(np.arange(0, self.years + 1, 20))

        ax.invert_yaxis()
        ax.tick_params(
            axis="x",
            which="both",
            bottom=False,
            top=True,
            labelbottom=False,
            labeltop=True,
        )
        ax.xaxis.set_label_coords(0.5, 1.05)

        weeks_passed = (datetime.date.today() - self.birthday).days // 7
        current_week = int(datetime.datetime.now().strftime("%U"))
        years_passed = weeks_passed // self.weeks_per_year

        for age in range(0, self.years + 1):
            for week in range(0, self.weeks_per_year + 1):
                if age <= years_passed:
                    color = (0.9, 0.9, 0.9, 1.0)  # gray
                elif age == years_passed + 1:
                    if week < current_week:
                        color = (0.7, 0.8, 0.9, 1.0)
                    elif week == current_week:
                        color = (1.0, 1.0, 0.0, 1.0)  # yellow
                    else:
                        color = (0.9, 0.8, 0.7, 1.0)
                else:
                    color = (0.8, 1.0, 0.8, 1.0)  # light green
                ax.add_patch(self._patch(week, age, color))

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=self.dpi)  # , bbox_inches="tight")
        imgbytes = buffer.getvalue()
        plt.close(fig)

        return imgbytes

    def save(self, filepath="life_in_weeks.png", imgbytes=None):
        imgbytes = imgbytes or self.draw()
        with open(filepath, "wb") as f:
            f.write(imgbytes)
