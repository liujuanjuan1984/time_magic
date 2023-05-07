import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def progress_bar(percent, width=30):
    """根据百分比生成进度条"""
    if percent < 1:
        percent *= 100
    bar_length = int(width * percent / 100)
    bar_chars = "█" * bar_length + "▁" * (width - bar_length)
    return f"{bar_chars}{percent:.1f}%"


@dataclass
class CircleStatus:
    today: str
    birthday: str
    age: int
    passed_days: int
    this_circle_number: int
    this_circle_begin: str
    this_circle_passed_days: int
    this_circle_remain_days: int
    this_circle_passed_percent: float

    def __str__(self):
        return "\n".join(
            [
                f"今天是 {self.today}，出生于 {self.birthday} 的我正好 {self.age} 岁。我在地球上已经度过 {self.passed_days} 天，这相当于 {1+self.passed_days//7} 周。",
                f"如果说七年就是一辈子，那么现在是我的第 {self.this_circle_number} 辈子。它开始于 {self.this_circle_begin}，已流逝了 {self.this_circle_passed_days} 天，还剩下 {self.this_circle_remain_days} 天。",
                progress_bar(self.this_circle_passed_percent),
            ]
        )


class SevenYearsCircle:
    def __init__(self, birthday: str = "1970-1-1"):
        born_year, born_month, born_day = birthday.split("-")
        self.born_year = int(born_year)
        self.born_month = int(born_month)
        self.born_day = int(born_day)
        self.birthday = self.circle_begin(1)
        self.this_circle = self.__this_circle()

    def circle_begin(self, circle_number=1):
        day = (
            f"{self.born_year + 7*(circle_number-1)}-{self.born_month}-{self.born_day}"
        )
        return datetime.datetime.strptime(day, "%Y-%m-%d").date()

    def __this_circle(self):
        today = datetime.date.today()
        passed = today - self.birthday
        guess = 1 + passed.days // (365 * 7)
        circle_number = 1
        for i in range(guess - 2, guess + 3):
            if self.circle_begin(i) >= today:
                circle_number = i - 1
                break

        this_circle = self.circle_begin(circle_number)
        next_circle = self.circle_begin(circle_number + 1)
        total_days = (next_circle - this_circle).days

        age = 1 + passed.days // 365
        this_birthday = f"{today.year}-{self.born_month}-{self.born_day}"
        this_birthday = datetime.datetime.strptime(this_birthday, "%Y-%m-%d").date()
        if this_birthday <= today:
            age += 1

        data = CircleStatus(
            **{
                "today": str(today),
                "birthday": str(self.birthday),
                "age": 1 + passed.days // 365,
                "passed_days": passed.days,
                "this_circle_number": circle_number,
                "this_circle_begin": str(this_circle),
                "this_circle_passed_days": (today - this_circle).days,
                "this_circle_remain_days": (next_circle - today).days,
                "this_circle_passed_percent": round(
                    (today - this_circle).days / total_days, 4
                ),
            }
        )
        return data
