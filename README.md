# ECショップと簡単な販売管理機能のDjangoデモサイト

## 必要な序ジュールのインストール

```console
pip install -r requirements.txt
```

## その他の前提条件と仕様

- staffというグループをadminサイトで作成して、管理者にstaffグループを付与する。
- staffグループに所属しているユーザのみ販売管理サイトへアクセスできる。
- ユーザ登録時にショッピングカートのレコードが自動生成される。
- ログインはアドレス＋パスワード（カスタムユーザを定義）

## Paypalキーの設定

`templates\ec_site\order_confirmation.html`の以下の`<your_client_key>`を自分のPaypalクライアントIDに置き換える。

```html
<script src="https://www.paypal.com/sdk/js?client-id=<your_client_key>&currency=JPY"></script>
```


## URLパターン概要


| URL  | 機能  |
| ------------ | ------------ |
|/top/  | ECショップサイト |
|/sales_management/dashboard/ | 分析ダッシュボード  |
|sales_management/unshipped/ | 未出荷一覧  |
|sales_management/order_management/ | 注文データ管理  |
|sales_management/sales_analysis/ |売上分析  |

## サンプルデータのロード

```console
python manage.py loaddata --format=yaml ec_site/fixtures/sample_data.yaml
```


## ECショップ

以下のようなECショップサイト機能

## Paypalを使った決済機能


## 出荷状態を管理する管理機能



## 簡単な売上分析機能
描画にはplotly exporessを利用

