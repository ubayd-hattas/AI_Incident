import hashlib
from datetime import datetime,timezone,timedelta
from ebe.evaluator import *
T=datetime(2026,1,1,tzinfo=timezone.utc)
def body(page,text,minute=1,seq=1):
    raw=text.encode(); return RetainedBodyRecord(page,T+timedelta(minutes=minute),raw,hashlib.sha256(raw).hexdigest(),seq)
def test_core_absent_context_present_is_incomplete():
    f={"c":Fragment("c","dse~A","body_span",b"core"),"x":Fragment("x","dse~B","body_span",b"ctx")}
    p=Proposition("P",True,(("c",),),(("c","x"),),context_state="required")
    assert not context_covered(p,f,RetainedSnapshot(T+timedelta(hours=1),(body("dse~B","ctx"),),()))[0]
def test_self_contained_equals_core_and_three_way_or():
    core=Fragment("c","dse~A","body_span",b"core")
    fs={"c":core,**{f"x{i}":Fragment(f"x{i}",f"dse~X{i}","body_span",f"ctx{i}".encode()) for i in range(3)}}
    p=Proposition("P",True,(("c",),),tuple(("c",f"x{i}") for i in range(3)),context_state="required")
    snap=RetainedSnapshot(T+timedelta(hours=1),(body("dse~A","core",1,1),body("dse~X1","ctx1",2,2)),())
    assert context_covered(p,fs,snap)[0]
def test_wrong_time_future_and_multiplicity_fail():
    f=Fragment("e","dse~A","observable_feed",feed_action="delete",event_time=T,minimum_multiplicity=2)
    snap=RetainedSnapshot(T+timedelta(minutes=3),(),(RetainedFeedRecord("dse~A","delete",T+timedelta(seconds=1),T+timedelta(minutes=1)),))
    assert not fragment_satisfied(f,snap)[0]
def test_unknown_context_interval():
    f={"c":Fragment("c","dse~A","body_span",b"x")}
    p=Proposition("P",True,(("c",),),context_state="unknown")
    r=compute_context_coverage([p],f,RetainedSnapshot(T+timedelta(minutes=2),(body("dse~A","x"),),()),critical_only=False)
    assert r.percentage is None and (r.lower_numerator,r.upper_numerator)==(0,1)
