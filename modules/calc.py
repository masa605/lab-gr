"""
modules/calc.py
犬の給餌量・エネルギー計算モジュール (RER, DER, 給餌量, ブレンド計算)
"""

from typing import Dict, Tuple, Any

def calculate_rer(weight_kg: float) -> float:
    """
    安静時エネルギー要求量 (RER: Resting Energy Requirement) を計算します。
    公式: RER = 70 * (体重kg)^0.75
    """
    if weight_kg <= 0:
        raise ValueError("体重は0より大きい数値を指定してください。")
    return 70.0 * (weight_kg ** 0.75)


def calculate_der(rer: float, stage_factor: float) -> float:
    """
    1日あたりエネルギー要求量 (DER: Daily Energy Requirement) を計算します。
    公式: DER = RER * ライフステージ係数
    """
    if rer <= 0 or stage_factor <= 0:
        raise ValueError("RERおよびライフステージ係数は正の数値を指定してください。")
    return rer * stage_factor


def calculate_food_gram(der: float, kcal_per_100g: float) -> float:
    """
    単一フードの1日あたり必要給餌量 (g) を計算します。
    公式: 給餌量(g) = (DER / 100gあたりkcal) * 100
    """
    if der <= 0 or kcal_per_100g <= 0:
        return 0.0
    return (der / kcal_per_100g) * 100.0


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


def calculate_blend_amounts(
    der: float,
    kcal_a: float,
    kcal_b: float,
    ratio_a_pct: float
) -> Dict[str, float]:
    """
    指定されたフードAの重量割合 (%) に基づき、フードAおよびフードBの必要量(g)と摂取カロリーを計算します。

    :param der: 1日あたり目標カロリー (DER kcal)
    :param kcal_a: フードAの100gあたりカロリー (kcal)
    :param kcal_b: フードBの100gあたりカロリー (kcal)
    :param ratio_a_pct: フードAの重量割合 (0 ～ 100 %)
    :return: 辞書 {
        "total_gram": 総給餌量 (g),
        "gram_a": フードA給餌量 (g),
        "gram_b": フードB給餌量 (g),
        "kcal_a": フードA由来カロリー (kcal),
        "kcal_b": フードB由来カロリー (kcal),
        "blend_kcal_per_100g": ブレンド後の100gあたりカロリー (kcal)
    }
    """
    ratio_a = max(0.0, min(100.0, ratio_a_pct)) / 100.0
    ratio_b = 1.0 - ratio_a
    
    # ブレンド後の100gあたりカロリー密度
    blend_kcal_per_100g = (ratio_a * kcal_a) + (ratio_b * kcal_b)
    
    if blend_kcal_per_100g <= 0:
        return {
            "total_gram": 0.0,
            "gram_a": 0.0,
            "gram_b": 0.0,
            "kcal_a": 0.0,
            "kcal_b": 0.0,
            "blend_kcal_per_100g": 0.0
        }
    
    total_gram = (der / blend_kcal_per_100g) * 100.0
    gram_a = total_gram * ratio_a
    gram_b = total_gram * ratio_b
    
    kcal_a_val = (gram_a * kcal_a) / 100.0
    kcal_b_val = (gram_b * kcal_b) / 100.0
    
    return {
        "total_gram": round(total_gram, 1),
        "gram_a": round(gram_a, 1),
        "gram_b": round(gram_b, 1),
        "kcal_a": round(kcal_a_val, 1),
        "kcal_b": round(kcal_b_val, 1),
        "blend_kcal_per_100g": round(blend_kcal_per_100g, 1)
    }
