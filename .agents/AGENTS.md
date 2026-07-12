# AI WebAuto Workspace Rules & Knowledge

## 役割分担（Role Division）
- **ロジック・バックエンド開発**: Claude Code に一任する。（例：シフト管理アプリなど）
- **デザイン・フロントエンド開発**: Claude Design (Gemini / Antigravity) が担当する。圧倒的に美しく、プレミアムなUI/UXを提供すること。（例：AI完全自動更新HPのデザイン一新など）

## 開発環境・ツール（Environment & Tools）
- **Git / GitHub連携**: お客様は **GitHub Desktop** を使用して連携を行っている。通常の `git` コマンドはシステムに無い場合があるため、AI側からGitを操作する際は `$env:LOCALAPPDATA\GitHubDesktop\app-*\resources\app\git\cmd\git.exe` を使用すること。

## コミュニケーション方針
- お客様の過去の指示やコンテキストを絶対に忘れないこと。
- お客様に同じことを二度言わせないよう、常にこのファイルの設定を参照して行動すること。
