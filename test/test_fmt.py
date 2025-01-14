from dataclasses import dataclass
from datetime import timedelta

from better_rich_progress.fmt import (
    format_duration_hmms,
    format_duration_human_readable,
    format_large_num_si,
)


@dataclass
class FormatTestCase:
    input: float
    expected_si: str
    expected_hmmss: str
    expected_duration: str

    def assert_large_num_si(self):
        output = format_large_num_si(self.input)
        assert output == self.expected_si

    def assert_duration_simple(self):
        output = format_duration_hmms(self.input)
        assert output == self.expected_hmmss

    def assert_duration_human_readable(self):
        output = format_duration_human_readable(self.input)
        assert output == self.expected_duration


# NOTE: Everything under 0 is really only covered by format_duration_human_redable, but
# the values are still given for the other methods, as that is what the output will be.
# This contains multiples of 10 from 1e-10 to 1e9 plus some additional ones that trigger
# a special case, such as having no seconds.
TEST_CASES = [
    FormatTestCase(
        input=1e-10,
        expected_si="0.00",
        expected_hmmss="00:00",
        expected_duration="0.1ns",
    ),
    FormatTestCase(
        input=1e-9, expected_si="0.00", expected_hmmss="00:00", expected_duration="1ns"
    ),
    FormatTestCase(
        input=1e-8, expected_si="0.00", expected_hmmss="00:00", expected_duration="10ns"
    ),
    FormatTestCase(
        input=1e-7,
        expected_si="0.00",
        expected_hmmss="00:00",
        expected_duration="100ns",
    ),
    FormatTestCase(
        input=1e-6, expected_si="0.00", expected_hmmss="00:00", expected_duration="1μs"
    ),
    FormatTestCase(
        input=1e-5, expected_si="0.00", expected_hmmss="00:00", expected_duration="10μs"
    ),
    FormatTestCase(
        input=1e-4,
        expected_si="0.00",
        expected_hmmss="00:00",
        expected_duration="100μs",
    ),
    FormatTestCase(
        input=1e-3, expected_si="0.00", expected_hmmss="00:00", expected_duration="1ms"
    ),
    FormatTestCase(
        input=1e-2, expected_si="0.01", expected_hmmss="00:00", expected_duration="10ms"
    ),
    FormatTestCase(
        input=1e-1,
        expected_si="0.10",
        expected_hmmss="00:00",
        expected_duration="100ms",
    ),
    FormatTestCase(
        input=0, expected_si="0.00", expected_hmmss="00:00", expected_duration="0s"
    ),
    FormatTestCase(
        input=1e1, expected_si="10.0", expected_hmmss="00:10", expected_duration="10s"
    ),
    FormatTestCase(
        input=1e2, expected_si="100", expected_hmmss="01:40", expected_duration="1m40s"
    ),
    FormatTestCase(
        input=1e3,
        expected_si="1.00k",
        expected_hmmss="16:40",
        expected_duration="16m40s",
    ),
    FormatTestCase(
        input=1e4,
        expected_si="10.0k",
        expected_hmmss="2:46:40",
        expected_duration="2h46m40s",
    ),
    FormatTestCase(
        input=1e5,
        expected_si="100k",
        expected_hmmss="27:46:40",
        expected_duration="1d03h46m40s",
    ),
    FormatTestCase(
        input=1e6,
        expected_si="1.00M",
        expected_hmmss="277:46:40",
        expected_duration="11d13h46m40s",
    ),
    FormatTestCase(
        input=1e7,
        expected_si="10.0M",
        expected_hmmss="2777:46:40",
        expected_duration="115d17h46m40s",
    ),
    FormatTestCase(
        input=1e8,
        expected_si="100M",
        expected_hmmss="27777:46:40",
        expected_duration="1157d09h46m40s",
    ),
    FormatTestCase(
        input=1e9,
        expected_si="1.00G",
        expected_hmmss="277777:46:40",
        expected_duration="11574d01h46m40s",
    ),
    # Special cases, easier to create them with timedelta
    FormatTestCase(
        input=timedelta(minutes=1).total_seconds(),
        expected_si="60.0",
        expected_hmmss="01:00",
        expected_duration="1m",
    ),
    FormatTestCase(
        input=timedelta(minutes=1, seconds=1).total_seconds(),
        expected_si="61.0",
        expected_hmmss="01:01",
        expected_duration="1m01s",
    ),
    FormatTestCase(
        input=timedelta(hours=1).total_seconds(),
        expected_si="3.60k",
        expected_hmmss="1:00:00",
        expected_duration="1h",
    ),
    FormatTestCase(
        input=timedelta(hours=1, minutes=1).total_seconds(),
        expected_si="3.66k",
        expected_hmmss="1:01:00",
        expected_duration="1h01m",
    ),
    FormatTestCase(
        input=timedelta(hours=1, seconds=1).total_seconds(),
        expected_si="3.60k",
        expected_hmmss="1:00:01",
        expected_duration="1h01s",
    ),
    FormatTestCase(
        input=timedelta(hours=1, minutes=1, seconds=1).total_seconds(),
        expected_si="3.66k",
        expected_hmmss="1:01:01",
        expected_duration="1h01m01s",
    ),
    FormatTestCase(
        input=timedelta(days=1).total_seconds(),
        expected_si="86.4k",
        expected_hmmss="24:00:00",
        expected_duration="1d",
    ),
    FormatTestCase(
        input=timedelta(days=1, hours=1).total_seconds(),
        expected_si="90.0k",
        expected_hmmss="25:00:00",
        expected_duration="1d01h",
    ),
    FormatTestCase(
        input=timedelta(days=1, minutes=1).total_seconds(),
        expected_si="86.5k",
        expected_hmmss="24:01:00",
        expected_duration="1d01m",
    ),
    FormatTestCase(
        input=timedelta(days=1, seconds=1).total_seconds(),
        expected_si="86.4k",
        expected_hmmss="24:00:01",
        expected_duration="1d01s",
    ),
    FormatTestCase(
        input=timedelta(days=1, hours=1, minutes=1, seconds=1).total_seconds(),
        expected_si="90.1k",
        expected_hmmss="25:01:01",
        expected_duration="1d01h01m01s",
    ),
]


def test_format_large_num_si():
    for test_case in TEST_CASES:
        test_case.assert_large_num_si()


def test_format_duration_simple():
    for test_case in TEST_CASES:
        test_case.assert_duration_simple()


def test_format_time_human_readable():
    for test_case in TEST_CASES:
        test_case.assert_duration_human_readable()
