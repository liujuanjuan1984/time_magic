"""
人生有 90 年，每年按 52 周计算，展示在一张 A4 纸的图片内。
"""

from time_magic import LifeInWeeks

bot = LifeInWeeks(
    "2012-11-16", figure_scale=1, dpi=100, edgecolor="white", bbox_inches=None
)
bot.save("life_in_weeks.png")
