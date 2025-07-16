import streamlit as st
import google.generativeai as genai
# Streamlit Secretsから読み込み
api_key = st.secrets["GEMINI_API_KEY"]
model = genai.GenerativeModel('gemini-2.5-flash')


if "story" not in st.session_state:
    st.session_state.story = ""
if "continuation_count" not in st.session_state:
    st.session_state.continuation_count = 0
if "base_prompt" not in st.session_state:
    st.session_state.base_prompt = ""
if "story_parts" not in st.session_state:
    st.session_state.story_parts = []

# Streamlit UI設定
st.set_page_config(page_title="AI小説生成サイト", layout="centered")
st.title("AI小説生成サイト")
st.markdown("テーマ・内容・季節、登場人物などを選んで、AIに短編小説を書いてもらおう！")

# --- チェックボックス ---
st.subheader("✅ 文体を選択")
writingstyle = ["通常", "ライトノベル", "純文学", "絵本", "台本","ゲームシナリオ"]
selected_writingstyle = [writingstyle for writingstyle in writingstyle if st.checkbox(writingstyle, key=f"theme_{writingstyle}")]
if st.checkbox("その他（自分で入力）", key="style_other"):
    custom_style = st.text_input("読みたい文体を入力してください", key="style_input")
    if custom_style:
        selected_writingstyle.append(custom_style)

st.subheader("✅ テーマを選択")
themes = ["恋愛", "冒険", "ミステリー", "ホラー", "ファンタジー", "SF"]
selected_themes = [theme for theme in themes if st.checkbox(theme, key=f"theme_{theme}")]
if st.checkbox("その他（自分で入力）", key="theme_other"):
    custom_theme = st.text_input("読みたいテーマを入力してください", key="theme_input")
    if custom_theme:
        selected_themes.append(custom_theme)
        

st.subheader("✅ 内容を選択")
contents = ["切ない", "感動的", "笑える", "哲学的", "ダーク", "ハートフル"]
selected_contents = [content for content in contents if st.checkbox(content, key=f"content_{content}")]
if st.checkbox("その他（自分で入力）", key="content_other"):
    custom_content = st.text_input("読みたい内容を入力してください", key="content_input")
    if custom_content:
        selected_contents.append(custom_content)

st.subheader("✅ 季節を選択")
seasons = ["春", "夏", "秋", "冬"]
selected_seasons = [season for season in seasons if st.checkbox(season, key=f"season_{season}")]
if st.checkbox("その他（自分で入力）", key="season_other"):
    custom_season = st.text_input("物語の季節を入力してください", key="season_input")
    if custom_season:
        selected_seasons.append(custom_season)

# --- 登場人物と舞台設定 ---
st.subheader("👥 登場人物・舞台設定ファイルのアップロード（任意）")
st.markdown(
    "💡 **二次創作を読みたい場合や凝った設定を作りたい場合は、テキストファイルに細かく書いてからアップロードすると　その内容に沿った小説が生成される可能性が高くなります。**"
)
uploaded_file = st.file_uploader("テキストファイル(.txt)をアップロードしてください", type=["txt"])
uploaded_text = ""
if uploaded_file is not None:
    uploaded_text = uploaded_file.read().decode("utf-8")
    st.success("✅ ファイルを読み込みました。")

# --- 登場人物と舞台設定（テキスト入力）---
st.subheader("👤 登場人物の設定（手動入力）")
character_count = st.number_input("登場人物の人数（例：2）", min_value=1, max_value=10, value=2, step=1)
character_traits = st.text_area("登場人物の名前・性格・性別（例：「ひなた」名前とは裏腹にどこか陰った印象のある女子高校生）")

st.subheader("🌍 舞台設定（手動入力）")
setting = st.text_area("物語の舞台（例：近未来の東京、因習が残る村 など）")

char_count = st.slider("希望の文字数を選んでください", min_value=1000, max_value=5000, step=200, value=1000)
# --- 小説を生成 ------

if st.button("🖊 小説を生成"):
    if not selected_themes or not selected_contents or not selected_seasons:
        st.warning("テーマ・内容・季節をすべて1つ以上選んでください。")
    else:
        st.session_state.story = ""
        st.session_state.continuation_count = 0
        st.session_state.story_parts = []

        # アップロードテキストがあればそちらを優先（併用も可）
        if uploaded_text.strip():
            setting_info = uploaded_text.strip()
        else:
            setting_info = (
                f"登場人物: {character_count}人（性格・性別・名前: {character_traits}）\n"
                f"舞台: {setting}"
            )

        prompt = f"""
以下の条件に沿って、日本語で短編小説を書いてください。

- 文体: {', '.join(selected_writingstyle)}
- テーマ: {', '.join(selected_themes)}
- 内容の特徴: {', '.join(selected_contents)}
- 季節: {', '.join(selected_seasons)}

以下の登場人物と舞台設定を必ず反映してください。
{setting_info}

- 文字数: およそ {char_count} 字程度

登場人物の描写が丁寧で、情景や感情が伝わるようなストーリーにしてください。
できるだけキャラクターを際立たせ、読み手が続きを読みたいと思わせるようなストーリーにしてください。
「」のついたセリフが多く続く場合は必ずそれぞれに改行を入れてください。
一直線に話が進むのではなく、なにかハプニングなど、全体的なテーマに捻りを入れることで面白い物語になります。
続きがある場合も、生成された小説の最後に(続く)などは絶対に表示しないでください。
また、句読点は多すぎないようにしてください。指定された文字数で物語が終わらなくても構いません。
大体三回の生成で物語がきれいに終わるように調整してください。
入力された登場人物の内容を崩す、改変するなどは絶対に行わないでください。
"""

        st.session_state.base_prompt = prompt

        with st.spinner("小説を生成中..."):
            try:
                response = model.generate_content(prompt)
                story = response.text.strip()
                st.session_state.story_parts.append(story)
                st.success("✅ 小説が生成されました！")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# --- 物語表示 ---
for idx, part in enumerate(st.session_state.get("story_parts", [])):
    if idx == 0:
        st.markdown("### 🖊小説")
    else:
        st.markdown(f"### 📖 続き {idx}")
    st.write(part)

# --- 続きを書くボタン（最大3回） ---
if st.session_state.story_parts:
    if st.session_state.continuation_count < 3:
        if st.button("📖 物語の続きを書く"):
            with st.spinner("続きの物語を生成中..."):
                try:
                    # 最新の物語全文を基に続き生成
                    full_story = "\n\n".join(st.session_state.story_parts)
                    continuation_prompt = (
                        f"{full_story}\n\n"
                        "この物語の続きを自然につなげて書いてください。"
                    )
                    if st.session_state.continuation_count == 2:
                        continuation_prompt += "\nなお、今回が完結編です。物語を美しく締めくくってください。"

                    response = model.generate_content(continuation_prompt)
                    new_part = response.text.strip()

                    st.session_state.story_parts.append(new_part)
                    st.session_state.continuation_count += 1
                    st.success("✅ 続きが生成されました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
    else:
        st.info("✅ この物語は完結しました。これ以上の続きは存在しません")