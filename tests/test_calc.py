import pytest
import math
# マスターのcalc.pyから関数をインポート
# from modules.calc import calculate_rer, calculate_der 

# --- ダミーの関数（マスターのcalc.pyの中身を想定） ---
def calculate_rer(weight_kg):
    if weight_kg <= 0:
        raise ValueError("体重は0より大きい必要があります")
    return 70 * math.pow(weight_kg, 0.75)

def calculate_der(rer, factor):
    if factor <= 0:
        raise ValueError("係数は0より大きい必要があります")
    return rer * factor
# ----------------------------------------------------


class TestDogCalorieCalculator:
    """犬のカロリー計算ロジック（calc.py）のテスト群"""

    def test_calculate_rer_normal(self):
        """【正常系】標準的な体重(例: 10kg)のRER計算が正しいか"""
        weight = 10.0
        # 70 * (10^0.75) ≒ 393.6
        expected_rer = 70 * math.pow(weight, 0.75)
        actual_rer = calculate_rer(weight)
        
        # 浮動小数点の計算なので、pytest.approxで「ほぼ等しい」ことを確認
        assert actual_rer == pytest.approx(expected_rer, rel=1e-3)

    def test_calculate_der_normal(self):
        """【正常系】RERと係数を用いたDER計算が正しいか"""
        rer = 400.0
        factor = 1.6 # 避妊・去勢済みの成犬などの標準係数
        expected_der = 640.0
        
        actual_der = calculate_der(rer, factor)
        assert actual_der == expected_der

    def test_calculate_rer_zero_or_negative_weight(self):
        """【異常系】体重に0やマイナスが入力された時に、安全にエラーを吐くか"""
        with pytest.raises(ValueError):
            calculate_rer(0)
            
        with pytest.raises(ValueError):
            calculate_rer(-5.0)

    def test_calculate_der_invalid_factor(self):
        """【異常系】係数に0やマイナスが入力された時に、安全にエラーを吐くか"""
        with pytest.raises(ValueError):
            calculate_der(400.0, 0)