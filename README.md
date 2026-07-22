# misa-public-media

Instagram投稿時にMeta APIから取得できる、公開済みの完成メディアだけを一時保管するリポジトリです。

## 公開するもの

- Instagramの画像1枚投稿・カルーセル投稿に使う最終版JPG画像
- Instagramのカルーセル投稿・Reels投稿に使う最終版MP4動画
- 投稿IDを含む、重複しにくいファイル名
- GitHub Releasesの `instagram-media` Releaseに添付したファイル

非公開側の自動投稿コードは、画像1枚、画像・動画2～10件のカルーセル、Reelsに対応しています。カルーセルとReelsはコードと単体テストまで完了しており、実アカウントでの投稿テストはこれからです。ReelsへのInstagram音源指定は未対応です。

## 公開しないもの

- Instagram・Threadsのアクセストークン
- 投稿前の下書き、没画像、動画プレビュー
- 個人情報
- noteの有料部分
- 元画像、PSD、動画プロジェクトなどの編集データ

秘密情報、投稿キュー、制作途中のデータは、非公開リポジトリ `misa-social-automation` で管理します。

## URL形式

```text
https://github.com/misa-yoru/misa-public-media/releases/download/instagram-media/<filename>.<jpg-or-mp4>
```

JPGはInstagram Content Publishing APIの `image_url`、MP4は `video_url` に渡します。カルーセルでは各メディアのURLを並べ、Reelsでは公開MP4のURLを指定します。

## 自動整理

GitHub Actionsが毎日、`instagram-media` のRelease Assetを確認します。

- 作成から30日を超えたメディアを削除
- 合計5GBを超えた場合は、4GB以下になるまで古いメディアから削除
- 手動実行は初期状態でドライランになり、実際には削除しない

JPGやMP4を通常のGitファイルとしてコミットしないため、削除後もGit履歴だけが肥大化する問題を避けられます。

## 運用の流れ

1. 完成メディアを書き出す
2. JPGまたはMP4を投稿ID入りの一意なファイル名にする
3. `instagram-media` Releaseへアップロードする
4. 公開URLがログインなしで取得できることを確認する
5. URLを非公開側の投稿キューへ保存する
6. 人の明示的な承認後に予約投稿する
7. 公開後30日が経過したメディアを自動整理する

このリポジトリは公開です。完成メディア以外は追加しません。
