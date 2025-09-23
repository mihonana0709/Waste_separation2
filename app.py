# ===== Streamlit ライブラリをインポート =====
import streamlit as st            # st: Streamlit を簡単に使うためのモジュール
import requests                   # requests: HTTP リクエスト（API通信）用ライブラリ
from PIL import Image             # Image: 画像ファイル操作用
import io                          # io: バイト列に変換するためのモジュール

# ===== タイトル表示 =====
st.title("Waste Classification App")               # アプリのタイトルを表示
st.write("画像をアップロードすると、リサイクル可能かどうかを判定します。")  # 説明文を表示

# # ===== サイドバーに郵便番号入力欄を追加 =====
# st.sidebar.title("地域設定")
# zipcode = st.sidebar.text_input("郵便番号を入力（例: 1600001）", max_chars=7)

# # 郵便番号から地域名を取得する関数
# def get_region_from_zip(zipcode):
#     if not zipcode:
#         return None
#     url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if data["results"]:
#             region = data["results"][0]["address1"]  # 都道府県
#             city = data["results"][0]["address2"]    # 市区町村
#             return f"{region} {city}"
#     except:
#         return None

# # 地域名を表示
# region_name = get_region_from_zip(zipcode)
# if region_name:
#     st.sidebar.success(f"地域: {region_name}")
#     # ここで地域ごとの分別情報を取得する処理を追加可能
# else:
#     if zipcode:
#         st.sidebar.error("地域情報を取得できませんでした")


# ===== ファイルアップロードUI =====
st.markdown("### 判定したい写真を選んでください")
uploaded_file = st.file_uploader(                # st.file_uploader: ファイル選択ボタン
    "",                   # ボタンの説明
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
        backend_url = "https://waste-backend-6cn4.onrender.com/predict/"
    else:
        backend_url = "http://127.0.0.1:8000/predict/"

    files = {"file": ("image.png", byte_im, "image/png")}  # 送信データの形式を指定

    # ===== 送信中のスピナー表示 =====
    with st.spinner("判定中..."):               # 処理中のスピナーを表示
        try:
            # response = requests.post(api_url, files=files)  # POSTリクエストで画像送信
            response = requests.post(backend_url, files=files)
            result = response.json()                         # JSON形式で結果取得

            # st.write("ステータスコード:", response.status_code)
            # st.write("レスポンス内容:", response.text)

            prediction = result['prediction']  # ← ここで prediction を定義
            confidence = result['probability']      # 0.9876 などの float 値
            # probability = result.get("probability", None)
            # st.success(f"予測結果: {result['prediction']}") # 予測結果を画面に表示
            # if prediction == "Recyclable":
            #     st.success("♻️ このゴミは **リサイクル可能** です！")
                
            # else:
            #     st.error("🚮 このゴミは **リサイクル不可** です。")
                
            # # 確信度をパーセンテージで表示
            # confidence = result['probability']      # 0.9876 などの float 値
            # st.metric(label="判定の確信度", value=f"{confidence * 100:.1f}%")
            # # リサイクル可能なら風船を飛ばす
            # if prediction == "Recyclable":
            #     # st.balloons() 
            #     st.snow()

            # 背景色を判定に応じて切り替え
            bg_color = "#e6f4ea" if prediction == "Recyclable" else "#fdecea"
            border_color = "#4CAF50" if prediction == "Recyclable" else "#f44336"
            emoji = "♻️" if prediction == "Recyclable" else "🚮"
            label = "リサイクル可能" if prediction == "Recyclable" else "リサイクル不可"

            st.markdown(f"""
            <div style="
                background-color: {bg_color};
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-left: 6px solid {border_color};
                margin-top: 20px;
            ">
            <h3 style="margin-top: 0;">🧾 判定結果カード</h3>
            <p style="font-size: 18px;">{emoji} このゴミは <strong>{label}</strong> です。</p>
            <p style="font-size: 16px;">判定の確信度: <strong>{confidence * 100:.1f}%</strong></p>
            <p style="font-size: 13px; color: #666;">※ この判定はAIによる予測です。地域の分別ルールと異なる場合があります。</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:                                # エラー処理
            st.error(f"APIへの接続に失敗しました: {e}")     # エラー表示

