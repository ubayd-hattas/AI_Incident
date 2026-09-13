from fractions import Fraction
from ebe.x13_reporting import *
def test_all_primary_labels_and_exact_threshold():
    assert primary_label(Fraction(10),admissible=True)==PRIMARY_LABELS[0]
    assert primary_label(Fraction(1),admissible=True)==PRIMARY_LABELS[1]
    assert primary_label(Fraction(0),admissible=True)=="TIE"
    assert primary_label(Fraction(-1),admissible=True)=="PCD_BETTER_ON_PRIMARY_ESTIMAND"
    assert primary_label(Fraction(2),admissible=False)=="PRIMARY_UNMATCHED"
def test_linear_n_minus_one_quantiles_and_na():
    values=list(range(60)); s=phase_summary(values)
    assert s["p10"]==Fraction(59,10) and s["median"]==Fraction(59,2)
    assert exact_percentage(0,0) is None

