import os
import json
import urllib.request
import urllib.error
import re
from datetime import datetime, timedelta

try:
    import tweepy
except ImportError:
    print("tweepyがインストールされていません。pip install tweepyを実行してください。")
    tweepy = None

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

# 5. 使用可能なAIモデルを自動で取得する
models_req = urllib.request.Request(
    "https://api.anthropic.com/v1/models",
    headers={
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }
)
try:
    models_response = urllib.request.urlopen(models_req)
    models_data = json.loads(models_response.read().decode("utf-8"))
    
    # 取得した全モデルを出力（デバッグ用）
    all_models = [m["id"] for m in models_data.get("data", [])]
    print(f"あなたのアカウントで利用可能な全モデル: {all_models}")
    
    # fable系は一時的に利用制限がかかっているようなので除外する
    safe_models = [m for m in all_models if "fable" not in m and ("claude" in m or "opus" in m or "sonnet" in m or "haiku" in m)]
    
    # 料金を節約するため、haiku（安価で高速）またはsonnetを最優先する
    haiku_models = [m for m in safe_models if "haiku" in m]
    sonnet_models = [m for m in safe_models if "sonnet" in m]
    
    if haiku_models:
        selected_model = haiku_models[0]
    elif sonnet_models:
        selected_model = sonnet_models[0]
    elif safe_models:
        selected_model = safe_models[0]
    elif all_models:
        selected_model = all_models[0]
    else:
        raise ValueError("使用可能なAIモデルが見つかりません。")
        
    print(f"自動選択されたモデル: {selected_model}")
except urllib.error.HTTPError as e:
    print(f"モデル一覧の取得に失敗しました: {e.read().decode('utf-8')}")
    selected_model = "opus-4.8" # エラーメッセージの推奨モデルを強制指定

# 6. Claude API へのリクエスト準備
data = {
    "model": selected_model,
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

# 7. API通信とHTMLの上書き
try:
    print("Claude APIにリクエストを送信中...")
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode("utf-8"))
    
    try:
        new_html = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                new_html = block.get("text", "")
                break
                
        if not new_html:
            raise ValueError("テキストデータが見つかりませんでした。")
            
        new_html = new_html.strip()
    except Exception as e:
        print(f"APIからの返答形式が予想と異なりました。エラー: {e}")
        print("実際の返答データ:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise

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
    
    # 8. 短い要約文の生成と、自社LP (lp/index.html) のメッセージ枠の更新
    print("LP更新用の短い要約を生成中...")
    # 新しく生成されたHTML(new_html)の中から、AIが報告した内容(result)を抽出する安全な方法を採用
    import re
    summary_text = "本日のアクセス傾向に合わせて数件の微調整を行いました。"
    match = re.search(r'<div class="log-box result">\s*<p>(.*?)</p>', new_html, re.DOTALL)
    if match:
        extracted = match.group(1).strip()
        # HTMLタグが混入している場合は除去
        extracted = re.sub(r'<[^>]+>', '', extracted)
        if extracted:
            summary_text = extracted
    
    # 自社LP (lp/index.html) の更新
    try:
        lp_path = "lp/index.html"
        with open(lp_path, "r", encoding="utf-8") as lp_f:
            lp_content = lp_f.read()
        
        # 日付の更新（実際の実行時刻に関わらず、表示上は常に「09:00」とする）
        now_str = datetime.now().strftime("%Y年%m月%d日 09:00")
        lp_content = re.sub(
            r"(<!-- AI-UPDATE-DATE-START -->\s*)[\s\S]*?(\s*<!-- AI-UPDATE-DATE-END -->)",
            rf"\g<1>最終更新：{now_str}（AIシステム稼働中）\g<2>",
            lp_content
        )
        
        # メッセージの更新
        ai_msg = f"【AI WebAuto 稼働報告】本日もシステムが正常に稼働し、最適化を実行しました。作業内容：「{summary_text}」"
        lp_content = re.sub(
            r"(<!-- AI-UPDATE-MSG-START -->\s*)[\s\S]*?(\s*<!-- AI-UPDATE-MSG-END -->)",
            rf"\g<1>{ai_msg}\g<2>",
            lp_content
        )
        
        with open(lp_path, "w", encoding="utf-8") as lp_f:
            lp_f.write(lp_content)
        print(f"成功: {lp_path} のAIステータス枠も更新しました！")
    except Exception as lp_e:
        print(f"LPの自動更新中にエラーが発生しました: {lp_e}")
        
    # 9. X (Twitter) への自動投稿（設定されている場合のみ）
    twitter_api_key = os.environ.get("TWITTER_API_KEY")
    twitter_api_secret = os.environ.get("TWITTER_API_SECRET")
    twitter_access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    twitter_access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

    if tweepy and twitter_api_key and twitter_access_token:
        print("X(Twitter)への自動投稿を開始します...")
        final_tweet = f"{summary_text}\n#AI自動更新\n\n👇自動更新されるデモサイトはこちら\nhttps://melodic-peony-09bb15.netlify.app/daily-demo/index.html"
        
        try:
            client = tweepy.Client(
                consumer_key=twitter_api_key,
                consumer_secret=twitter_api_secret,
                access_token=twitter_access_token,
                access_token_secret=twitter_access_secret
            )
            
            response = client.create_tweet(text=final_tweet)
            print(f"Xへの投稿が成功しました！ Tweet ID: {response.data['id']}")
        except Exception as e:
            print(f"Xへの投稿中にエラーが発生しました: {e}")

except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8")
    print(f"HTTPエラーが発生しました: {e.code} {e.reason}")
    print(f"エラーの詳細: {error_body}")
    exit(1)
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
    exit(1)
