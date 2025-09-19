# ===== Streamlit ライブラリをインポート =====
import streamlit as st            # st: Streamlit を簡単に使うためのモジュール
import requests                   # requests: HTTP リクエスト（API通信）用ライブラリ
from PIL import Image             # Image: 画像ファイル操作用
import io                          # io: バイト列に変換するためのモジュール

# ===== タイトル表示 =====
st.title("Waste Classification App")               # アプリのタイトルを表示
st.write("画像をアップロードすると、リサイクル可能かどうかを判定します。")  # 説明文を表示

# ===== ファイルアップロードUI =====
uploaded_file = st.file_uploader(                # st.file_uploader: ファイル選択ボタン
    "画像を選択してください",                   # ボタンの説明
    type=["jpg", "jpeg", "png"]                 # アップロード可能なファイル形式
)

# ===== ファイルがアップロードされた場合 =====
if uploaded_file is not None:
    image = Image.open(uploaded_file)           # PILで画像を開く
    st.image(image, caption="アップロードした画像", use_container_width=True)  # 画像表示

    # ===== 画像をバイト列に変換 =====
    buf = io.BytesIO()                          # バイト列用のバッファを作成
    image.save(buf, format="PNG")               # 画像をPNG形式で保存（バイト列に）
    byte_im = buf.getvalue()                    # バイト列データを取得

    # ===== FastAPI のエンドポイントURL =====
    # api_url = "http://127.0.0.1:8000/predict"  # backend.py の /predict に送信
    # api_url = "https://waste-backend-6cn4.onrender.com" 
    import os

    # Render上かローカルかで切り替え
    if os.getenv("RENDER") == "1":
        backend_url = "https://waste-backend-6cn4.onrender.com"
    else:
        backend_url = "http://127.0.0.1:8000/predict"

    files = {"file": ("image.png", byte_im, "image/png")}  # 送信データの形式を指定

    # ===== 送信中のスピナー表示 =====
    with st.spinner("判定中..."):               # 処理中のスピナーを表示
        try:
            response = requests.post(api_url, files=files)  # POSTリクエストで画像送信
            result = response.json()                         # JSON形式で結果取得
            st.success(f"予測結果: {result['prediction']}") # 予測結果を画面に表示
        except Exception as e:                                # エラー処理
            st.error(f"APIへの接続に失敗しました: {e}")     # エラー表示
