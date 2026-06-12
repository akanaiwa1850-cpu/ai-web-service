import os
import json
import urllib.request
import re
from datetime import datetime, timedelta

# 1. APIキーの取得（GitHub Secretsから渡される）
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY が設定されていません。")
API_KEY = API_KEY.strip()

HTML_PATH = "daily-demo/index.html"

# 2. 現在のHTMLファイルを読み込む
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

# 3. 日付の計算（昨日の夜に要望が来て、今日の朝に対応したという設定）
today = datetime.now()
yesterday = today - timedelta(days=1)
today_str = today.strftime("%Y年%m月%d日")
yesterday_str = yesterday.strftime("%Y年%m月%d日")

# 4. Claude APIへの指示（プロンプト）
prompt = f"""
あなたは優秀な「AI Webコーダー」です。
現在、以下のHTMLコードで「毎日自動進化するデモサイト」を運用しています。
毎日、あなたがHTMLのコードを直接書き換えることで、自動更新の証明としています。

以下の指示に従って、提供されたHTMLコードを更新し、新しいHTMLコード全体のみを返してください。（Markdownのバッククォート ```html などは絶対に含めないでください）

【指示内容】
1. HTML内の `<!-- 更新履歴 1 (最新) -->` の下にある `<div class="glass-panel changelog-card">` ブロックを見つけてください。
2. `<div class="changelog-date" id="changelog-date-1">` の日付を「📅 {today_str}の更新」に変更してください（JavaScriptで自動更新されますが一応HTML側も書き換えます）。
3. `<div class="log-box request">` 内の `<p>` タグの文章を、架空のクライアントからの新しい要望（例：「少しボタンの色を目立たせて」「テキストをポジティブな言葉に変えて」など、ごく簡単なもの）に書き換えてください。
4. `<div class="log-box result">` 内の `<p>` タグの文章を、「承知いたしました。〇〇を〇〇に変更しました。」という実行報告に書き換えてください。
5. **最重要**: 3で設定した要望の内容通りに、**実際のHTMLコードの一部（CSSのカラーコードや、ヒーローセクションのテキスト等）を本当に書き換えてください**。
   ※大きな構造変更はせず、色、文字、マージンなどの微小な変更にとどめること。

【現在のHTMLコード】
{html_content}
"""

# 5. Claude API へのリクエスト準備
data = {
    "model": "claude-3-haiku-20240307",
    "max_tokens": 4000,
    "system": "You are a professional AI web developer. You strictly output ONLY raw HTML code without any markdown formatting or explanations.",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=json.dumps(data).encode("utf-8"),
    headers={
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    method="POST"
)

# 6. API通信とHTMLの上書き
try:
    print("Claude APIにリクエストを送信中...")
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode("utf-8"))
    new_html = result["content"][0]["text"].strip()
    
    # 万が一Markdown記法が含まれていた場合の除去処理
    if new_html.startswith("```html"):
        new_html = new_html[7:]
    if new_html.startswith("```"):
        new_html = new_html[3:]
    if new_html.endswith("```"):
        new_html = new_html[:-3]
        
    new_html = new_html.strip()

    # 新しいHTMLを保存
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
        
    print(f"成功: {HTML_PATH} を自動更新しました！")
    
except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8")
    print(f"HTTPエラーが発生しました: {e.code} {e.reason}")
    print(f"エラーの詳細: {error_body}")
    exit(1)
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
    exit(1)
