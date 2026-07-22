# misa-public-media

Instagram投稿時にMeta APIから取得できる、公開済み完成画像だけを一時保管するリポジトリです。

## 公開するもの

- Instagramへ投稿する最終版の画像
- JPG形式を基本とし、投稿IDを含む推測しにくいファイル名
- GitHub Releasesの `instagram-media` リリースに添付したファイル

## 公開しないもの

- Instagram・Threadsのアクセストークン
- 投稿前の下書きや没画像
- 個人情報
- noteの有料部分
- 元画像、PSDなどの編集データ

秘密情報と投稿キューは、非公開リポジトリ `misa-social-automation` で管理します。

## URL形式

画像URLは次の形式です。

```text
https://github.com/misa-yoru/misa-public-media/releases/download/instagram-media/<filename>.jpg
```

このURLをInstagram Content Publishing APIの `image_url` に渡します。

## 自動整理

GitHub Actionsが毎日、`instagram-media` の添付画像を確認します。

- 作成から30日を超えた画像を削除
- 合計500MBを超えた場合は、400MB以下になるまで古い画像から削除
- 手動実行は初期状態でドライランになり、実際には削除しない

Gitの通常ファイルとして画像をコミットしないため、画像を削除したあとにGit履歴だけが肥大化することも避けられます。

## 運用の流れ

1. 完成画像をJPGへ圧縮する
2. ファイル名を `<post-id>-<random>.jpg` にする
3. `instagram-media` Releaseへアップロードする
4. 公開URLを非公開側の投稿キューへ保存する
5. InstagramとThreadsへ予約投稿する
6. 公開後30日が経過した画像を自動削除する

このリポジトリは公開です。完成画像以外は追加しません。
