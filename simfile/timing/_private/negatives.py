from .. import BeatValue, TimingData
from ..engine import TimingEngine


def negatives_to_warps(timing_data: TimingData):
    if all(bpm.value > 0 for bpm in timing_data.bpms):
        return timing_data
    
    engine = TimingEngine(timing_data)
    engine._use_linear_search = True
    
    for bpm_ in timing_data.bpms:
        bpm: BeatValue = bpm_
        if bpm.value < 0:
            engine.time_at(bpm)
            engine.beat_at()