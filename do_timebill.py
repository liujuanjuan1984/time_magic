"""
记录 24H 时间开销，生成一条条时间开销记录。
当有了这些数据后，按天，周等统计各个维度的时间开销；并生成图片。
这个脚本主要处理的就是时间开销的统计。
"""

import logging

from time_magic import TimeBill

logging.basicConfig(level=logging.INFO)

count_types = ["0-其它", "1-健康", "2-成长", "3-家庭", "4-工作", "5-财富", "6-人际", "7-休闲"]
origin_file = "D:\my_timedata\data\alldata.txt"
image_dir = r"D:\my_timedata\images"

bot = TimeBill(count_types, origin_file, image_dir)
bot.update_counts()
bot.update_draws(2016, 9, 10)
