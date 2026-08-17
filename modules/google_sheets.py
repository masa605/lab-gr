"""
modules/google_sheets.py
gspread & google-auth を用いた Google スプレッドシート連携モジュール
本番環境(production)ではエラー時に安全に停止し、
開発環境(development)ではサンプルデータ(Fallback DataFrame)を返します。
"""

import gspread
import os
import streamlit as st
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from google.oauth2.service_account import Credentials
import traceback

# --- デモ用フォールバックデータ ---
FALLBACK_FOOD_MASTER = pd.DataFrame([
    {
        "brand": "ロイヤルカナン",
        "product_name": "ラブラドールレトリバー 成犬・高齢犬用",
        "calories_per_100g": 362.0,
        "protein_pct": 30.0,
        "fat_pct": 13.0,
        "description": "ラブラドールの関節・体重管理に配慮した専用フード"
    },
    {
        "brand": "ヒルズ",
        "product_name": "サイエンス・ダイエット 減量サポート 成犬用",
        "calories_per_100g": 317.0,
        "protein_pct": 28.5,
        "fat_pct": 11.5,
        "description": "カロリーオフで健康的かつリバウンドのない減量をサポート"
    },
    {
        "brand": "ニュートロ",
        "product_name": "ナチュラルチョイス 減量用 全犬種用 成犬用 ラム＆玄米",
        "calories_per_100g": 310.0,
        "protein_pct": 23.0,
        "fat_pct": 7.0,
        "description": "低脂質・低カロリーで満腹感を保つフード"
    },
    {
        "brand": "アカナ (ACANA)",
        "product_name": "ヘリテージ アダルトラージブリード",
        "calories_per_100g": 337.5,
        "protein_pct": 31.0,
        "fat_pct": 15.0,
        "description": "大型成犬用。高タンパク・低炭水化物"
    },
    {
        "brand": "オリジン (ORIJEN)",
        "product_name": "オリジナル ドッグ",
        "calories_per_100g": 394.0,
        "protein_pct": 38.0,
        "fat_pct": 18.0,
        "description": "高タンパクでアクティブなラブラドール向け"
    }
])

FALLBACK_LIFESTAGE_MASTER = pd.DataFrame([
    {
        "stage_name": "避妊・去勢済み成犬",
        "der_factor": 1.6,
        "description": "標準的な成犬の維持エネルギー (適正体重の維持)"
    },
    {
        "stage_name": "未避妊・未去勢成犬",
        "der_factor": 1.8,
        "description": "未手術の活発な成犬用"
    },
    {
        "stage_name": "肥満傾向・減量中 (おすすめ)",
        "der_factor": 1.0,
        "description": "ラブラドールで最も多い減量目標用 (体重コントロール)"
    },
    {
        "stage_name": "体重維持 (太りやすい体質)",
        "der_factor": 1.2,
        "description": "太りやすい体質の成犬用維持エネルギー"
    },
    {
        "stage_name": "高齢犬 (7歳〜)",
        "der_factor": 1.4,
        "description": "代謝速度低下に対応したシニア向け"
    },
    {
        "stage_name": "幼犬・パピー (4ヶ月未満)",
        "der_factor": 3.0,
        "description": "急速成長期の非常に高いエネルギー要求"
    },
    {
        "stage_name": "幼犬・パピー (4ヶ月〜成犬)",
        "der_factor": 2.0,
        "description": "離乳後から骨格が完成するまでの成長期"
    }
])


@st.cache_data(ttl=600)
def load_masters_from_sheets() -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
    """
    Googleスプレッドシートから food_master と lifestage_master を読み込みます。
    本番環境(production)で接続失敗した場合はエラーを発生させて停止します。
    """
    env = st.secrets.get("ENVIRONMENT", "development")

    # Secrets チェック
    try:
        if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
            if env == "production":
                st.error("🚨 【本番エラー】Google Sheets APIの認証情報が設定されていません。")
                st.stop()
            return FALLBACK_FOOD_MASTER, FALLBACK_LIFESTAGE_MASTER, False
    except Exception:
        if env == "production":
            st.error("🚨 【本番エラー】secrets.toml が読み込めません。")
            st.stop()
        return FALLBACK_FOOD_MASTER, FALLBACK_LIFESTAGE_MASTER, False

    try:
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
        if "calories_per_100g" in food_df.columns:
            food_df["calories_per_100g"] = pd.to_numeric(food_df["calories_per_100g"], errors="coerce")
        if "protein_pct" in food_df.columns:
            food_df["protein_pct"] = pd.to_numeric(food_df["protein_pct"], errors="coerce")
        if "fat_pct" in food_df.columns:
            food_df["fat_pct"] = pd.to_numeric(food_df["fat_pct"], errors="coerce")

        # lifestage_master 取得
        lifestage_worksheet = sh.worksheet("lifestage_master")
        lifestage_records = lifestage_worksheet.get_all_records()
        lifestage_df = pd.DataFrame(lifestage_records)
        
        if "der_factor" in lifestage_df.columns:
            lifestage_df["der_factor"] = pd.to_numeric(lifestage_df["der_factor"], errors="coerce")
            
        st.success("✅ スプレッドシートからのデータ読み込みに成功しました！")
        return food_df, lifestage_df, True

    except Exception as e:
        if env == "production":
            # 本番環境では完全に停止させる
            st.error(f"🚨 【本番エラー】Google Sheetsとの連携に失敗しました: {e}")
            st.stop()
        else:
            # 開発環境ではフォールバックに逃がす
            st.error(f"⚠️ スプレッドシート通信エラーの種類: {type(e).__name__}")
            st.sidebar.warning(f"Google Sheets接続エラー（デモ用ローカルデータを使用中）: {e}")
            return FALLBACK_FOOD_MASTER, FALLBACK_LIFESTAGE_MASTER, False
    
    
def add_new_food_to_sheet(new_data: list) -> bool:
    """
    スプレッドシートの food_master に新しいフード情報を追加します。
    """
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
            st.error("⚠️ Google Sheets APIの認証情報が設定されていません。")
            return False

        service_account_info = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes
        )
        
        gc = gspread.authorize(credentials)
        spreadsheet_id = st.secrets["spreadsheet_id"]
        sh = gc.open_by_key(spreadsheet_id)

        # food_master 取得して追記
        food_worksheet = sh.worksheet("food_master")
        food_worksheet.append_row(new_data)
        
        # キャッシュをクリア
        load_masters_from_sheets.clear()
        return True

    except Exception as e:
        st.error(f"⚠️ スプレッドシート書き込みエラー: {e}")
        return False