from datetime import datetime, timezone, timedelta
from ebe.support_masks import SupportState, compile_stable_support_intervals
T=datetime(2026,1,1,tzinfo=timezone.utc)
def test_interval_endpoints_and_checkpoint():
    states=[SupportState("a","dse~A","1",T,1),SupportState("b","dse~A","2",T+timedelta(seconds=10),1)]
    x=compile_stable_support_intervals(states,checkpoint=T+timedelta(seconds=20))
    assert x[0].start_us==int(T.timestamp()*1e6)+1
    assert x[0].end_us==int((T+timedelta(seconds=10)).timestamp()*1e6)-1
def test_equal_text_and_incompatible():
    x=compile_stable_support_intervals([SupportState("a","dse~A","h",T),SupportState("b","dse~A","h",T+timedelta(seconds=1))])
    assert x[0].eligible
    y=compile_stable_support_intervals([SupportState("x","dse~X",None,T,state="incompatible")])
    assert not y[0].eligible and "INCOMPATIBLE" in y[0].reason

