# 🐶 Lab_gr — 愛犬ラブラドール・レトリバー給餌量計算Webアプリ

愛犬「ろみ」（ラブラドール・レトリバー）の給餌量を科学的計算式（RER / DER）に基づき安全かつ継続的に管理するためのStreamlit Webアプリケーションです。

---

## 🌟 主な機能

1. **RER / DER 科学的エネルギー計算**:
   - 安静時エネルギー要求量: $\text{RER} = 70 \times (\text{体重kg})^{0.75}$
   - 1日あたりエネルギー要求量: $\text{DER} = \text{RER} \times \text{ライフステージ係数}$
   - 体重・年齢・運動量・避妊去勢状態に応じた高精度な目標カロリー算出

2. **Google スプレッドシートリアルタイム連携**:
   - `food_master` (ドッグフード銘柄・カロリー・栄養素)
   - `breed_master` (ライフステージ係数定義)
   - `gspread` および `st.secrets` による安全なスプレッドシートデータ取得 (未設定時はサンプルローカルデータでデモ動作)

3. **2種フードブレンド計算**:
   - メインフードと減量フード・トッピング等の重量比率指定・給餌量(g)の自動分割計算
   - 目標カロリー密度 (kcal/100g) からの最適ブレンド比率逆算シミュレーション

4. **インタラクティブダッシュボード**:
   - BIG KPI カード表示（1日推奨給餌量g, 1回分給餌量g, DER kcal, RER kcal）
   - Plotly を用いたエネルギー要求量ゲージチャート
   - ドッグフードマスターデータ閲覧機能

---

## 📁 ファイル構成

```text
lab_gr/
├── Lab_gr.py                      # Streamlitメインアプリケーション
├── requirements.txt               # 依存ライブラリ一覧
├── README.md                      # 本ドキュメント
├── .gitignore                     # Git除外設定
├── .antigravity/
│   └── rules.md                   # エージェント行動規範
├── .streamlit/
│   ├── config.toml                # UIテーマ設定
│   └── secrets.toml.example        # Secrets設定テンプレート
└── modules/
    ├── __init__.py                # パッケージ宣言
    ├── calc.py                    # RER / DER / フード量 / ブレンド計算ロジック
    ├── google_sheets.py           # Google Sheets (gspread) 連携モジュール
    └── ui_helpers.py              # 免責事項・Plotlyチャート・KPIコンポーネント
```

---

## 🚀 ローカル起動手順

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. Streamlit アプリの起動
```bash
streamlit run Lab_gr.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 🔐 Google スプレッドシート連携手順 (.streamlit/secrets.toml)

Google スプレッドシート連携を行う場合は以下の手順で設定を行ってください。

1. `.streamlit/secrets.toml.example` をコピーして `.streamlit/secrets.toml` を作成します。
2. GCPコンソールから Google Drive API および Google Sheets API を有効化したサービスアカウントを発行し、JSONキーを取得します。
3. `.streamlit/secrets.toml` 内にサービスアカウントのメールアドレス・秘密鍵および対話対象のスプレッドシートIDを記入してください。
4. 対象のスプレッドシートにワークシート `food_master` および `breed_master` を作成し、サービスアカウントのアドレスに閲覧権限を付与してください。
