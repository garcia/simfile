from simfile.timing import TimingData
from simfile.ssc import SSCSimfile


def testing_timing_data():
    return TimingData(
        SSCSimfile(
            string="#VERSION:0.83;\n"
            "#OFFSET:-0.009;\n"
            "#BPMS:0.000=120.000,\n"
            "1.000=150.000,\n"
            "2.000=200.000,\n"
            "3.000=300.000;\n"
            "#STOPS:2.500=0.500,\n"
            "3.000=0.100;\n"
        )
    )


def testing_timing_data_with_delays_warps_and_fakes():
    # Test cases:
    # 1. delay
    # 2. warp
    # 3. stop on delay
    # 4. stop on warp start
    # 5. stop inside warp
    # 6. stop on warp end
    # 7. delay on warp start
    # 8. delay inside warp
    # 9. delay on warp end
    # 10. consecutive warps
    # 11. partially overlapping warps
    # 12. warp inside warp
    # 13. fake region
    return TimingData(
        SSCSimfile(
            string="#VERSION:0.83;\n"
            "#OFFSET:0.000;\n"
            "#BPMS:0.000=120.000;\n"
            "#STOPS:3.000=0.250,\n"
            "4.000=0.250,\n"
            "5.250=0.250,\n"
            "6.500=0.250;\n"
            "#DELAYS:1.000=0.250,\n"
            "3.000=0.500,\n"
            "7.000=0.250,\n"
            "8.250=0.250,\n"
            "9.500=0.250;\n"
            "#WARPS:2.000=0.500,\n"
            "4.000=0.500,\n"
            "5.000=0.500,\n"
            "6.000=0.500,\n"
            "7.000=0.500,\n"
            "8.000=0.500,\n"
            "9.000=0.500,\n"
            "10.000=0.250,\n"
            "10.250=0.500,\n"
            "11.000=0.500,\n"
            "11.250=0.500,\n"
            "12.000=0.750,\n"
            "12.250=0.250;\n"
            "#FAKES:13.000=0.500;\n"
        )
    )
