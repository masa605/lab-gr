"""
modules/calc.py
犬の給餌量・エネルギー計算モジュール (RER, DER, 給餌量, ブレンド計算)
"""
import math

from typing import Dict, Tuple, Any

def calculate_rer(weight_kg: float) -> float:
    """
    RER (Resting Energy Requirement: 安静時生体維持カロリー) を計算する。
    計算式: 70 * (weight_kg ^ 0.75)
    """
    if weight_kg <= 0:
        raise ValueError("体重は0より大きい数値を指定してください。")
    return 70.0 * math.pow(weight_kg, 0.75)


def calculate_der(rer: float, der_factor: float) -> float:
    """
    DER (Daily Energy Requirement: 1日あたりの目標カロリー) を計算する。
    計算式: RER * der_factor
    """
    if rer <= 0 or der_factor <= 0:
        raise ValueError("RERおよびder_factorは0より大きい数値を指定してください。")
    return rer * der_factor



def calculate_daily_gram(der: float, calories_per_100g: float) -> float:
    """
    1種類フードでの1日あたり必要給餌量(g)を計算する。
    計算式: (DER / calories_per_100g) * 100
    """
    if calories_per_100g <= 0:
        raise ValueError("100gあたりのカロリーは0より大きい数値を指定してください。")
    return (der / calories_per_100g) * 100.0




def calculate_blend_ratio_for_target(kcal_a: float, kcal_b: float, target_kcal_per_100g: float) -> float:
    """
    目標カロリー密度 (target_kcal_per_100g) を満たすためのフードAのブレンド重量割合 (%) を計算します。
    方程式: x * kcal_a + (1 - x) * kcal_b = target_kcal_per_100g
    => x = (target_kcal_per_100g - kcal_b) / (kcal_a - kcal_b)
    
    戻り値: フードAの重量割合 (0.0 ～ 100.0 %)
    """
    if kcal_a == kcal_b:
        return 50.0  # カロリー密度が同じ場合は5:5とする
    
    x = (target_kcal_per_100g - kcal_b) / (kcal_a - kcal_b)
    ratio_a = x * 100.0
    
    # 0% 〜 100% の範囲にクランプ
    return max(0.0, min(100.0, ratio_a))

def calculate_blend_grams(der: float, cal_a: float, cal_b: float, ratio_a: float) -> tuple[float, float]:
    """
    2種類ブレンド時の各フード給餌量(g)を計算する。
    :param der: 1日の目標カロリー (kcal)
    :param cal_a: フードAの100gあたりカロリー (kcal)
    :param cal_b: フードBの100gあたりカロリー (kcal)
    :param ratio_a: フードAの配分比率 (0.0 〜 1.0、例: 70%なら 0.7)
    :return: (gram_a, gram_b)
    """
    if not (0.0 <= ratio_a <= 1.0):
        raise ValueError("比率は0.0から1.0の間で指定してください。")
    if cal_a <= 0 or cal_b <= 0:
        raise ValueError("カロリーは0より大きい数値を指定してください。")

    target_cal_a = der * ratio_a
    target_cal_b = der * (1.0 - ratio_a)

    gram_a = (target_cal_a / cal_a) * 100.0
    gram_b = (target_cal_b / cal_b) * 100.0

    return gram_a, gram_b

