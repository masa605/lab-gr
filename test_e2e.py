from playwright.sync_api import sync_playwright

def run_e2e_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("🤖 AI：ローカルのLab_grアプリにアクセスします...")
        page.goto("http://localhost:8501", wait_until="networkidle")

        print("⏳ 描画完了を待機中...")
        page.wait_for_selector(".stApp")
        page.wait_for_timeout(3000)

        # ---------------------------------------------------
        # 💡 【追加】ここからAIが数値をチェックします！
        # ---------------------------------------------------
        print("🔍 AI：ろみちゃんの計算結果をテストします...")
        
        # 画面に表示されているテキストをすべて取得
        page_text = page.locator(".stApp").inner_text()
        
        # 期待する数値が画面に存在するかを「assert（断言・検証）」する
        # もし見つからなければ、ここでエラーを出してストップします！
        assert "897 kcal" in page_text, "❌ エラー：カロリー(DER/RER)の計算結果が間違っています！"
        assert "238.6 g" in page_text, "❌ エラー：1日推奨給餌量の計算結果が間違っています！"
        
        print("✅ テスト合格！カロリー（897 kcal）と給餌量（238.6 g）は正確に計算されています！")

        # 最後に記念撮影
        page.screenshot(path="e2e_evidence_final.png")
        browser.close()
        print("🎉 すべてのE2Eテストが完了しました！")

if __name__ == "__main__":
    run_e2e_test()