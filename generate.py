import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


ROOT = Path(__file__).resolve().parent
CALENDAR_NAME = "中国节假日、农历节日和节气"
UNPREFIXED_TITLE_REVISION = "20261109T073543Z"
HOLIDAY_TITLE_REVISION = "20261109T074458Z"
DAY = timedelta(days=1)


@dataclass(frozen=True)
class Event:
    year: int
    category: str
    name: str
    start: date
    end: date
    source: str
    updated: date

    def lines(self):
        key = f"{self.year}/{self.category}/{self.name}"
        if self.category == "调休上班":
            key += f"/{self.start.isoformat()}"
        uid = uuid5(NAMESPACE_URL, f"https://china-calendar-ics.invalid/{key}")
        stamp = self.updated.strftime("%Y%m%dT000000Z")
        if self.category in ("农历节日", "节气"):
            summary = self.name
            stamp = max(stamp, UNPREFIXED_TITLE_REVISION)
        else:
            suffix = "放假" if self.category == "放假" else "补班"
            summary = f"{self.name}{suffix}"
            stamp = max(stamp, HOLIDAY_TITLE_REVISION)
        return [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"LAST-MODIFIED:{stamp}",
            f"DTSTART;VALUE=DATE:{self.start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{self.end:%Y%m%d}",
            f"SUMMARY:{escape_text(summary)}",
            f"CATEGORIES:{escape_text(self.category)}",
            f"DESCRIPTION:{escape_text(f'日期来源：{self.source}')}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]


def escape_text(value):
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def fold(line):
    physical = bytearray()
    for character in line:
        encoded = character.encode("utf-8")
        if len(physical) + len(encoded) > 75:
            yield bytes(physical)
            physical = bytearray(b" ")
        physical.extend(encoded)
    yield bytes(physical)


def load_events(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    year = int(path.stem)
    updated = date.fromisoformat(data["updated"])

    notice = data["sources"]["holidays"]
    almanac = data["sources"]["almanac"]
    holidays = []
    makeup_days = []
    for holiday in data["holidays"]:
        name = holiday["name"]
        start = date.fromisoformat(holiday["start"])
        end = date.fromisoformat(holiday["end"])
        if end < start:
            raise ValueError(f"{year} {name} 的假期结束日期早于开始日期")
        holidays.append(Event(year, "放假", name, start, end + DAY, notice, updated))
        for value in holiday["makeup"]:
            workday = date.fromisoformat(value)
            makeup_days.append(Event(year, "调休上班", name, workday, workday + DAY, notice, updated))

    occupied = set()
    for event in holidays + makeup_days:
        for offset in range((event.end - event.start).days):
            current = event.start + offset * DAY
            if current in occupied:
                raise ValueError(f"{current} 的放假或补班安排重叠")
            occupied.add(current)

    yield from holidays
    yield from makeup_days
    if len(data["solar_terms"]) != 24:
        raise ValueError(f"{year} 应有 24 个节气")
    for category, dates in [("农历节日", data["festivals"]), ("节气", data["solar_terms"])]:
        for name, value in dates.items():
            start = date.fromisoformat(f"{year:04d}-{value}")
            yield Event(year, category, name, start, start + DAY, almanac, updated)


def main():
    paths = sorted((ROOT / "data").glob("[0-9][0-9][0-9][0-9].json"))
    if not paths:
        raise SystemExit("data 目录没有年度日历数据")
    events = sorted(
        (event for path in paths for event in load_events(path)),
        key=lambda event: (event.start, event.category, event.name),
    )
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//China Calendar ICS//China Calendar//ZH-CN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{escape_text(CALENDAR_NAME)}",
    ]
    for event in events:
        lines.extend(event.lines())
    lines.append("END:VCALENDAR")
    payload = b"\r\n".join(part for line in lines for part in fold(line)) + b"\r\n"
    output = ROOT / "docs" / "china.ics"
    output.write_bytes(payload)
    print(f"{output}（{len(events)} 条日历事件）")


if __name__ == "__main__":
    main()
