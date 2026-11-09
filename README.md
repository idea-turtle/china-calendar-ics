# 中国日历 ICS

中国大陆节假日放假安排、调休上班、常见农历节日和二十四节气。首版覆盖 2026、2027 两个公历年。

## 订阅与导入

把 [ICS 订阅地址](https://idea-turtle.github.io/china-calendar-ics/china.ics) 粘贴到日历应用的「新建日历订阅」或「通过网址添加日历」。订阅客户端会按自己的频率刷新，也可以下载 `docs/china.ics` 并一次性导入。

日历条目使用全天事件。连续假期显示为一段，补班、农历节日和节气逐日显示。节日当天可能同时显示所属假期和农历节日。

## 更新

1. 在 `data/` 添加或修订相应年份的 JSON。放假开始和结束日期均包含在假期中，使用 `YYYY-MM-DD`。补班也使用 `YYYY-MM-DD`。农历节日和节气填写换算后的公历 `MM-DD`。
2. 用国务院办公厅的年度通知核对放假和补班，用香港天文台的公历与农历对照表核对节日和节气。把来源 URL 和核对日期写入年度文件。
3. 运行 `python3 generate.py`，将生成的 `docs/china.ics` 随数据一起发布。发布目录为 `docs/`，订阅路径保持为 `china.ics`。

生成器只使用 Python 3 标准库。假期以国务院公布的年度安排为准，新增年份需要更新数据并重新发布。

## 数据来源

- [2026 年国务院办公厅放假通知](https://big5.www.gov.cn/gate/big5/www.gov.cn/zhengce/zhengceku/202511/content_7047091.htm)
- [2027 年国务院办公厅放假通知](https://big5.www.gov.cn/gate/big5/www.gov.cn/zhengce/content/202611/content_7085101.htm)
- [香港天文台公历与农历对照表](https://www.hko.gov.hk/sc/gts/time/conversion.htm)
