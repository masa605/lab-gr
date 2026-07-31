"""
modules/google_sheets.py
gspread & google-auth を用いた Google スプレッドシート連携モジュール
st.secrets が未設定の場合はサンプルデータ (Fallback DataFrame) を返します。
"""

import streamlit as st
import pandas as pd
from typing import Tuple, Dict, Any, Optional

# デモ用フォールバックデータ
FALLBACK_FOOD_MASTER = pd.DataFrame([
    {
        "brand_name": "ロイヤルカナン",
        "food_name": "ラブラドールレトリバー 成犬・高齢犬用",
        "kcal_per_100g": 362.0,
        "protein_pct": 30.0,
        "fat_pct": 13.0,
        "description": "ラブラドールの関節・体重管理に配慮した専用フード"
    },
    {
        "brand_name": "ヒルズ",
        "food_name": "サイエンス・ダイエット 減量サポート 成犬用",
        "kcal_per_100g": 317.0,
        "protein_pct": 28.5,
        "fat_pct": 11.5,
        "description": "カロリーオフで健康的かつリバウンドのない減量をサポート"
    },
    {
        "brand_name": "ニュートロ",
        "food_name": "ナチュラルチョイス 減量用 全犬種用 成犬用 ラム＆玄米",
        "kcal_per_100g": 310.0,
        "protein_pct": 23.0,
        "fat_pct": 7.0,
        "description": "低脂質・低カロリーで満腹感を保つフード"
    },
    {
        "brand_name": "アカナ (ACANA)",
        "food_name": "ヘリテージ アダルトラージブリード",
        "kcal_per_100g": 337.5,
        "protein_pct": 31.0,
        "fat_pct": 15.0,
        "description": "大型成犬用。高タンパク・低炭水化物"
    },
    {
        "brand_name": "オリジン (ORIJEN)",
        "food_name": "オリジナル ドッグ",
        "kcal_per_100g": 394.0,
        "protein_pct": 38.0,
        "fat_pct": 18.0,
        "description": "高タンパクでアクティブなラブラドール向け"
    }
])

FALLBACK_BREED_MASTER = pd.DataFrame([
    {
        "stage_name": "避妊・去勢済み成犬",
        "factor": 1.6,
        "description": "標準的な成犬の維持エネルギー (適正体重の維持)"
    },
    {
        "stage_name": "未避妊・未去勢成犬",
        "factor": 1.8,
        "description": "未手術の活発な成犬用"
    },
    {
        "stage_name": "肥満傾向・減量中 (おすすめ)",
        "factor": 1.0,
        "description": "ラブラドールで最も多い減量目標用 (体重コントロール)"
    },
    {
        "stage_name": "体重維持 (太りやすい体質)",
        "factor": 1.2,
        "description": "太りやすい体質の成犬用維持エネルギー"
    },
    {
        "stage_name": "高齢犬 (7歳〜)",
        "factor": 1.4,
        "description": "代謝速度低下に対応したシニア向け"
    },
    {
        "stage_name": "幼犬・パピー (4ヶ月未満)",
        "factor": 3.0,
        "description": "急速成長期の非常に高いエネルギー要求"
    },
    {
        "stage_name": "幼犬・パピー (4ヶ月〜成犬)",
        "factor": 2.0,
        "description": "離乳後から骨格が完成するまでの成長期"
    }
])


@st.cache_data(ttl=600)
def load_masters_from_sheets() -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
    """
    Googleスプレッドシートから food_master および breed_master を読み込みます。
    secretsが設定されていないか認証失敗時はフォールバックデータを返します。

    :return: (food_master_df, breed_master_df, is_live_connection)
    """
    # Secrets チェック
    try:
        if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
            return FALLBACK_FOOD_MASTER, FALLBACK_BREED_MASTER, False
    except Exception:
        # secrets.toml が存在しないか読み込めない場合はフォールバック
        return FALLBACK_FOOD_MASTER, FALLBACK_BREED_MASTER, False

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
        
        service_account_info = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes
        )
        
        gc = gspread.authorize(credentials)
        spreadsheet_id = st.secrets["spreadsheet_id"]
        sh = gc.open_by_key(spreadsheet_id)

        # food_master 取得
        food_worksheet = sh.worksheet("food_master")
        food_records = food_worksheet.get_all_records()
        food_df = pd.DataFrame(food_records)
        
        # 数値型キャスト
        if "kcal_per_100g" in food_df.columns:
            food_df["kcal_per_100g"] = pd.to_numeric(food_df["kcal_per_100g"], errors="coerce")
        if "protein_pct" in food_df.columns:
            food_df["protein_pct"] = pd.to_numeric(food_df["protein_pct"], errors="coerce")
        if "fat_pct" in food_df.columns:
            food_df["fat_pct"] = pd.to_numeric(food_df["fat_pct"], errors="coerce")

        # breed_master 取得
        breed_worksheet = sh.worksheet("breed_master")
        breed_records = breed_worksheet.get_all_records()
        breed_df = pd.DataFrame(breed_records)
        if "factor" in breed_df.columns:
            breed_df["factor"] = pd.to_numeric(breed_df["factor"], errors="coerce")

        return food_df, breed_df, True

    except Exception as e:
        # エラー発生時はメッセージをスタックせずにフォールバックを返す
        st.sidebar.warning(f"Google Sheets接続エラー（デモ用ローカルデータを使用中）: {e}")
        return FALLBACK_FOOD_MASTER, FALLBACK_BREED_MASTER, False
