import csv
import logging
import os
from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)


class TimeBill:
    """time bill bot"""

    def __init__(
        self,
        count_types,
        origin_file: str,
        image_dir: str,
        begin_of_week: int = 3,
        is_cover: bool = True,
        bbox_inches=None,
    ):
        """
        origin_file: the file of origin data, each line is a record of time cost
        image_dir: the directory to save images
        begin_of_week: 0-6, 0 is Monday, 6 is Sunday, you can set anyday to your first day of week
        is_cover: if True, the image will cover the old one
        """
        self.count_types = count_types
        self.origin_file = origin_file
        self.image_dir = image_dir
        self.begin_of_week = begin_of_week or 3
        self.is_cover = is_cover
        self.bbox_inches = bbox_inches
        self.files = {
            "DAY": self.origin_file.replace(".txt", "_count_day.txt"),
            "WEEK": self.origin_file.replace(".txt", "_count_week.txt"),
            "WEEK4": self.origin_file.replace(".txt", "_count_4weeks.txt"),
            "DayH": self.origin_file.replace(".txt", "_count_day_hour.txt"),
            "WeekH": self.origin_file.replace(".txt", "_count_week_hour.txt"),
            "Week4H": self.origin_file.replace(".txt", "_count_4weeks_hour.txt"),
        }

    def read_csvfile(self, csvfile: str):
        """read csvfile to list of dict"""
        with open(csvfile, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            data = [row for row in reader]
        return data

    def write_csvfile(self, results: dict, csvfile: str):
        """write results to csvfile"""
        fieldnames = ["date", "total"] + self.count_types
        with open(csvfile, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for date, data in results.items():
                row = {"date": date, "total": data["total"]}
                row.update(data["types"])
                writer.writerow(row)

    def count_by_day(self, to_result_file=None):
        """count by day with the origin data"""
        data = self.read_csvfile(self.origin_file)
        results = {}
        for row in data:
            day_str = datetime.strptime(row["DATE"], "%Y-%m-%d").strftime("%Y-%m-%d")
            if day_str not in results:
                results[day_str] = {
                    "total": 0,
                    "types": {k: 0 for k in self.count_types},
                }
            results[day_str]["total"] += int(row["MINS"])
            results[day_str]["types"][row["TYPE"]] += int(row["MINS"])

        # check if there are missing days
        start_day = datetime.strptime(min(results.keys()), "%Y-%m-%d")
        end_day = datetime.strptime(max(results.keys()), "%Y-%m-%d")
        days = (end_day - start_day).days + 1
        for day in range(days):
            date = start_day + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")
            if date_str not in results:
                results[date_str] = {
                    "total": 0,
                    "types": {k: 0 for k in self.count_types},
                }
        # sort by date
        results = {k: results[k] for k in sorted(results.keys())}

        if to_result_file:
            self.write_csvfile(results, to_result_file)
        return results

    def results_to_hours(self, results, to_hour_file=None, n=60):
        """
        convert results to hours and write to file
        results: the result dict
        to_hour_file: if not None, write the result to file
        n: the number of minutes
        """
        results_hours = {}
        for date_str, data in results.items():
            results_hours[date_str] = {
                "total": round(data["total"] / n, 2),
                "types": {},
            }
            for k in self.count_types:
                results_hours[date_str]["types"][k] = round(data["types"][k] / n, 2)
        if to_hour_file:
            self.write_csvfile(results_hours, to_hour_file)
        return results_hours

    def count_by_week(self, day_results, weeks=1, to_result_file=None):
        """
        count by week
        day_results: the result of count_by_day
        weeks: how many weeks to count
        to_result_file: if not None, write the result to file
        """

        results = {}
        interval_start = None
        sorted_days = sorted(day_results.keys())
        for date_str in sorted_days:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date.weekday()
            if interval_start is None:
                interval_start = date
                interval_end = date
            elif weekday == self.begin_of_week and date > interval_end:
                interval_start = date
                interval_end = (
                    interval_start + timedelta(days=7 * weeks) - timedelta(seconds=1)
                )

            interval_key = interval_start.strftime("%Y-%m-%d")
            if interval_key not in results:
                results[interval_key] = {
                    "total": 0,
                    "types": {k: 0 for k in self.count_types},
                }
            results[interval_key]["total"] += day_results[date_str]["total"]
            for type_name, mins in day_results[date_str]["types"].items():
                results[interval_key]["types"][type_name] += mins

        if to_result_file:
            self.write_csvfile(results, to_result_file)
        return results

    def update_counts(self):
        """update the counts of time cost"""

        day_results = self.count_by_day(self.files["DAY"])
        self.results_to_hours(day_results, self.files["DayH"])

        results = self.count_by_week(day_results, 1, self.files["WEEK"])
        self.results_to_hours(results, self.files["WeekH"])

        results = self.count_by_week(day_results, 4, self.files["WEEK4"])
        self.results_to_hours(results, self.files["Week4H"])

    def draw_area(self, df, title, pngfile):
        """draw area chart"""
        matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
        matplotlib.rcParams["axes.unicode_minus"] = False
        plt.tick_params(axis="x", labelsize=10)

        ax = df.plot(
            kind="area",
            figsize=(20, 10),
            title=title,
            grid=False,
            stacked=True,
        )
        fig = ax.get_figure()
        fig.savefig(pngfile, bbox_inches=self.bbox_inches)
        plt.close()
        logger.info("done %s", pngfile)

    def draw_by_weeks(
        self,
        start_day="2018-5-3",
        default_end_day="2023-4-25",
        weeks=12,
        result_type=None,
    ):
        """
        draw by weeks, each weeks is draw to an image
        start_day: the day to start
        default_end_day: the day to end
        weeks: how many weeks to draw
        result_type: DAY, WEEK, WEEK4
        """
        df = pd.read_csv(self.files[result_type], delimiter="\t")
        df["date"] = pd.to_datetime(df["date"])

        days = 7 * weeks
        start_day = datetime.strptime(start_day, "%Y-%m-%d")
        default_end_day = datetime.strptime(default_end_day, "%Y-%m-%d")

        while start_day < datetime.now() and start_day < default_end_day:
            end_day = start_day + timedelta(days=days - 1)
            if start_day > datetime.now():
                break
            dfx = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
            title = "".join(
                [
                    start_day.strftime("%Y-%m-%d"),
                    " - ",
                    end_day.strftime("%Y-%m-%d"),
                    f" {days} Days TimeBill ({result_type})",
                ]
            )

            pngfile = os.path.join(
                self.image_dir,
                f"{result_type}_{days}",
                f"TimeBill_{days}Days_{start_day.strftime('%Y-%m-%d')}_{result_type}.png",
            )
            if not os.path.exists(os.path.dirname(pngfile)):
                os.makedirs(os.path.dirname(pngfile))
            dfx = dfx.set_index("date")
            dfx = dfx[self.count_types]
            start_day += timedelta(days=days)
            if os.path.exists(pngfile) and not self.is_cover:
                continue
            self.draw_area(dfx, title, pngfile)

    def draw_by_year(self, start_day, end_day, result_type="WEEK"):
        """draw by year, all data in one image
        start_day: the day of the year start
        end_day: the day of next year start
        """
        df = pd.read_csv(self.files[result_type], delimiter="\t")
        df["date"] = pd.to_datetime(df["date"])
        start_day = datetime.strptime(start_day, "%Y-%m-%d")
        if start_day > datetime.now():
            return
        end_day = datetime.strptime(end_day, "%Y-%m-%d")
        days = (end_day - start_day).days
        dfx = df[(df["date"] >= start_day) & (df["date"] < end_day)]
        title = "".join(
            [
                start_day.strftime("%Y-%m-%d"),
                " - ",
                end_day.strftime("%Y-%m-%d"),
                f" {days} Days TimeBill ({result_type})",
            ]
        )
        pngfile = os.path.join(
            self.image_dir,
            f"{result_type}_YEAR",
            f"TimeBill_{start_day.strftime('%Y-%m-%d')}_{end_day.strftime('%Y-%m-%d')}_{result_type}.png",
        )
        if not os.path.exists(os.path.dirname(pngfile)):
            os.makedirs(os.path.dirname(pngfile))
        dfx = dfx.set_index("date")
        dfx = dfx[self.count_types]
        if not os.path.exists(pngfile) or self.is_cover:
            self.draw_area(dfx, title, pngfile)

    def update_draws(self, start_year=2017, month=7, day=20):
        """
        start_year: the year that start to count
        month: the month of the year that start to count
        day: the day of the month that start to count
        month-day can be your birthday or other special day
        """
        year = datetime.now().year
        for y in range(start_year, year + 1):
            start_day = f"{y}-{month}-{day}"
            end_day = f"{y+1}-{month}-{day}"
            self.draw_by_weeks(start_day, end_day, 4, "DayH")
            self.draw_by_weeks(start_day, end_day, 12, "DayH")
            self.draw_by_weeks(start_day, end_day, 12, "WeekH")
            self.draw_by_year(start_day, end_day, "DayH")
            self.draw_by_year(start_day, end_day, "WeekH")
            self.draw_by_year(start_day, end_day, "Week4H")
