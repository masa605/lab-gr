"""
Lab_gr.py
# 愛犬ラブラドール・レトリバー「ろみ」のための給餌量計算・栄養管理 Streamlit Web アプリケーション
"""

import streamlit as st
import pandas as pd

# モジュールインポート
from modules.calc import (
    calculate_rer,
    calculate_der,
    calculate_daily_gram,
    calculate_blend_grams,
)
from modules.google_sheets import load_masters_from_sheets, add_new_food_to_sheet
from modules.ui_helpers import (
    render_disclaimer,
    render_kpi_metrics,
    render_calorie_gauge,
    render_blend_pie_chart
)

# 1. ページ基本設定
st.set_page_config(
    page_title="Lab_gr - ラブラドール給餌量計算",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSSスタイリング
st.markdown("""
<style>
    /* メインヘッダー */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    /* カード風スタイル */
    .stMetric {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


def main():
    # データ読み込み (breed_df を lifestage_df に変更)
    food_df, lifestage_df, is_live = load_masters_from_sheets()

    # ヘッダー
    st.markdown('<div class="main-header">🐶 Lab_gr — 愛犬給餌量計算</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">愛犬ろみ（ラブラドール・レトリバー）のための科学的カロリー＆フード量シミュレーター</div>',
        unsafe_allow_html=True
    )
    
    # ライブ接続ステータス表示
    if is_live:
        st.caption("🟢 **Google Sheets ライブ連携中** (food_master / lifestage_master)")
    else:
        st.caption("ℹ️ **デモモード動作中** (ローカルマスターデータを使用中)")

    render_disclaimer()
    st.markdown("---")

    # ----------------------------------------------------
    # サイドバー: プロフィール＆フード設定
    # ----------------------------------------------------
    st.sidebar.header("🐾 愛犬プロフィール")
    
    dog_name = st.sidebar.text_input("愛犬のお名前", value="ろみ")
    weight_kg = st.sidebar.number_input(
        "現在の体重 (kg)",
        min_value=1.0,
        max_value=60.0,
        value=30.0,
        step=0.5,
        help="ラブラドールレトリバーの標準体重目安: 25kg〜36kg"
    )

    # ライフステージ選択 (lifestage_dfより)
    stage_options = lifestage_df["lifestage"].tolist() if "lifestage" in lifestage_df.columns else []
    selected_lifestage = st.sidebar.selectbox(
        "ライフステージ / 状態",
        options=stage_options,
        index=2 if len(stage_options) > 2 else 0, # デフォルト「肥満傾向・減量中」
        help="生活環境や体調に応じた係数を選択してください"
    )
    
    # 選択されたステージの係数取得 (der_factorに変更)
    selected_stage_row = lifestage_df[lifestage_df["lifestage"] == selected_lifestage].iloc[0]
    stage_factor = float(selected_stage_row["der_factor"])
    st.sidebar.info(f"💡 係数: **{stage_factor:.1f}** ({selected_stage_row.get('description', '')})")

    meals_per_day = st.sidebar.slider(
        "1日の食事回数",
        min_value=1,
        max_value=4,
        value=2,
        help="1回あたりの給餌量を自動計算します"
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🥣 フード設定")

    # フードブレンド切り替え
    is_blend_mode = st.sidebar.toggle("2種類のフードをブレンドする", value=False)

    # フード選択肢作成 (ブランド名 + フード名)
    food_df["full_name"] = (
        food_df["brand_name"].fillna("").astype(str) +
        " - " + 
        food_df["product_name"].fillna("").astype(str)
    )
    
    food_list = food_df["full_name"].tolist()

    if not is_blend_mode:
        # 単一フードモード
        selected_food_a_name = st.sidebar.selectbox("メインフード", options=food_list, index=0)
        food_a_row = food_df[food_df["full_name"] == selected_food_a_name].iloc[0]
        kcal_a = float(food_a_row["calories_per_100g"])
        
        st.sidebar.caption(f"エネルギー: **{kcal_a} kcal/100g**")
        if "protein_pct" in food_a_row and pd.notna(food_a_row["protein_pct"]):
            st.sidebar.caption(f"タンパク質: {food_a_row['protein_pct']}% / 脂質: {food_a_row['fat_pct']}%")

    else:
        # ブレンドモード
        selected_food_a_name = st.sidebar.selectbox("メインフード (フードA)", options=food_list, index=0)
        food_a_row = food_df[food_df["full_name"] == selected_food_a_name].iloc[0]
        kcal_a = float(food_a_row["calories_per_100g"])

        selected_food_b_name = st.sidebar.selectbox("サブフード / トッピング (フードB)", options=food_list, index=1 if len(food_list) > 1 else 0)
        food_b_row = food_df[food_df["full_name"] == selected_food_b_name].iloc[0]
        kcal_b = float(food_b_row["calories_per_100g"])

        ratio_a_pct = st.sidebar.slider(
            "フードAの重量割合 (%)",
            min_value=0,
            max_value=100,
            value=70,
            step=5,
            help="フードAの配合パーセンテージ"
        )
        
    # ------------------------------------
    # ⚙️ 管理者専用：データ入力自動化UI
    # ------------------------------------
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    st.sidebar.markdown("---")
    admin_mode_toggle = st.sidebar.checkbox("⚙️ 管理者モードを起動", value=st.session_state.admin_authenticated)
    
    if admin_mode_toggle:
        if not st.session_state.admin_authenticated:
            input_password = st.sidebar.text_input("管理者パスワードを入力", type="password")
            if st.sidebar.button("認証"):
                correct_password = st.secrets.get("admin", {}).get("password", "")
                if input_password == correct_password and correct_password != "":
                    st.session_state.admin_authenticated = True
                    st.sidebar.success("✅認証成功！Adminモードを起動しました。")
                    st.rerun()
                else:
                    st.sidebar.error("パスワードが正しくありません")
        else:
            st.sidebar.info("🔓 管理者認証済み")
            if st.sidebar.button("ログアウト"):
                st.session_state.admin_authenticated = False
                st.rerun()
    else:
        st.session_state.admin_authenticated = False
    
    # ⚠️ ここがバグ修正のポイント：if文の中（管理者のみ）にフォームを移動しました
    if st.session_state.admin_authenticated:
        st.subheader("⚙️ 管理者専用：データ入力自動化UI")
        
        with st.form("admin_data_entry"):
            col1, col2 = st.columns(2)
            with col1:
                input_brand_name = st.text_input("ブランド名 (Brand)", placeholder="例: Royal Canin")
                input_product = st.text_input("商品名 (Product Name)", placeholder="例: 消化器サポート")
                input_price = st.number_input("価格 (Price)", min_value=0, value=0)
            with col2:
                input_kcal = st.number_input("カロリー/100g (kcal)", min_value=0.0, value=350.0)
                input_protein = st.number_input("タンパク質 % (Protein)", min_value=0.0, value=20.0)
                input_fat = st.number_input("脂質 % (Fat)", min_value=0.0, value=10.0)

            submit_btn = st.form_submit_button("🚀 スプレッドシートに登録")

            if submit_btn:
                if input_brand_name and input_product:
                    new_row = [input_brand_neme, input_product, input_price, input_kcal, input_protein, input_fat]
                    with st.spinner("スプレッドシートへ書き込み中..."):
                        success = add_new_food_to_sheet(new_row)
                    if success:
                        st.success(f"✅ 「{input_product}」をマスターDBに登録しました！")
                else:
                    st.warning("ブランド名と商品名は必須です。")
    else:
        st.info("※データ入力機能は管理者のみ利用可能です。")
        
    # ----------------------------------------------------
    # 👑 プレミアム機能へのアップグレード（Stripe決済への導線）
    # ----------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("👑 プレミア版へのアップグレード")
    st.sidebar.captionn("高度なブレンド逆算やデータの保存機能を利用するには、プレミアムプラン（月額500円）への登録が必要です。)
                        
    # マスターが取得したtest_ から始まるStripeのURLに際変えて下さい
    stripe_payment_link = "https://buy.stripe.com/test_eVq14meRz8nud5t29adZ600"
    
    st.sidebar.link_button("プレミアム機能を開放する", stripe_payment_link, type="primary")
    

    # ----------------------------------------------------
    # 計算処理実行 (新関数に差し替え)
    # ----------------------------------------------------
    rer = calculate_rer(weight_kg)
    der = calculate_der(rer, stage_factor)

    if not is_blend_mode:
        total_gram = calculate_daily_gram(der, kcal_a)
        gram_per_meal = total_gram / meals_per_day
    else:
        gram_a, gram_b = calculate_blend_grams(der, kcal_a, kcal_b, ratio_a_pct / 100.0)
        total_gram = gram_a + gram_b
        gram_per_meal = total_gram / meals_per_day

    # ----------------------------------------------------
    # メイン画面: BIG KPI
    # ----------------------------------------------------
    st.subheader(f"📊 {dog_name}ちゃんの給餌シミュレーション結果")
    render_kpi_metrics(total_gram, der, rer, meals_per_day, gram_per_meal)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # タブ切り替え表示
    # ----------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📈 カロリー＆給餌分析", "🔀 ブレンドシミュレーター", "🗂️ マスターデータ"])

    with tab1:
        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.markdown("#### 1日エネルギー要求量 (DER) ゲージ")
            gauge_fig = render_calorie_gauge(der, rer)
            st.plotly_chart(gauge_fig, use_container_width=True)

        with col_right:
            st.markdown("#### 📋 1日あたりの給餌サマリー")
            st.write(f"- **対象愛犬**: {dog_name} (体重 {weight_kg} kg)")
            st.write(f"- **選択ライフステージ**: {selected_lifestage}")
            st.write(f"- **安静時エネルギー要求量 (RER)**: `{rer:.1f} kcal/日`")
            st.write(f"- **1日必要エネルギー量 (DER)**: `{der:.1f} kcal/日`")
            st.write(f"- **1日合計推奨給餌量**: **`{total_gram:.1f} g`**")
            st.write(f"- **1回あたり給餌量 ({meals_per_day}回/日)**: **`{gram_per_meal:.1f} g`**")

            if is_blend_mode:
                st.markdown("---")
                st.write(f"• **フードA ({food_a_row['product_name']})**: `{gram_a:.1f} g`")
                st.write(f"• **フードB ({food_b_row['product_name']})**: `{gram_b:.1f} g`")

    with tab2:
        st.markdown("### 🔀 2種フードのブレンド給餌詳細")
        
        if not is_blend_mode:
            st.info("💡 サイドバーの「2種類のフードをブレンドする」トグルをオンにすると、ここで詳細なシミュレーションが行えます。")
        else:
            col_b1, col_b2 = st.columns([1, 1])

            with col_b1:
                pie_fig = render_blend_pie_chart(
                    food_a_row['product_name'],
                    gram_a,
                    food_b_row['product_name'],
                    gram_b
                )
                st.plotly_chart(pie_fig, use_container_width=True)

            with col_b2:
                st.markdown("#### 🎯 目標カロリー密度からの自動逆算")
                st.caption("特定のリハビリ・ダイエット用目標カロリー密度 (kcal/100g) からブレンド比率を逆算します。")
                
                min_kcal = min(kcal_a, kcal_b)
                max_kcal = max(kcal_a, kcal_b)
                default_target = round((kcal_a + kcal_b) / 2.0, 1)

                target_kcal = st.slider(
                    "目標カロリー密度 (kcal/100g)",
                    min_value=float(min_kcal),
                    max_value=float(max_kcal),
                    value=float(default_target),
                    step=1.0
                )

                # 逆算ロジック (関数を呼ばずにインライン計算で処理)
                if kcal_a != kcal_b:
                    calculated_ratio_a = (target_kcal - kcal_b) / (kcal_a - kcal_b)
                    calculated_ratio_a = max(0.0, min(1.0, calculated_ratio_a))
                else:
                    calculated_ratio_a = 0.5
                
                target_gram_a, target_gram_b = calculate_blend_grams(der, kcal_a, kcal_b, calculated_ratio_a)

                st.success(
                    f"**逆算結果**: 目標 `{target_kcal} kcal/100g` を達成するためのフードA割合は "
                    f"**`{calculated_ratio_a * 100:.1f} %`** です。\n\n"
                    f"- フードA ({food_a_row['product_name']}): **{target_gram_a:.1f} g**\n"
                    f"- フードB ({food_b_row['product_name']}): **{target_gram_b:.1f} g**\n"
                    f"- 1日合計: **{target_gram_a + target_gram_b:.1f} g**"
                )

    with tab3:
        st.markdown("### 🗂️ マスターデータ（food_master / lifestage_master）")
        
        tab_sub1, tab_sub2 = st.tabs(["🍖 ドッグフードマスター", "🐕 ライフステージマスター"])
        
        with tab_sub1:
            st.dataframe(food_df, use_container_width=True)
            
        with tab_sub2:
            st.dataframe(lifestage_df, use_container_width=True)


if __name__ == "__main__":
    main()