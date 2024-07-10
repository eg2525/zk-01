import pandas as pd
import re
import streamlit as st

# 日付変換の関数
def convert_date(date_str):
    pattern = r'(\d{2})/(\d{2})\([日月火水木金土]\)'
    match = re.match(pattern, date_str)
    if match:
        month, day = match.groups()
        year = 2024  # 年を指定
        return f'{year:04d}/{int(month):02d}/{int(day):02d}'
    return None

# 新しいデータフレームを作成する関数
def create_new_df(row, col, 貸方科目, 貸方補助, 消費税税率, 摘要):
    new_df = pd.DataFrame(columns=new_columns)
    new_df.loc[0, '貸方科目'] = 貸方科目
    new_df.loc[0, '貸方補助'] = 貸方補助
    new_df.loc[0, '貸方金額'] = row[col]
    new_df.loc[0, '貸方消費税コード'] = 2
    new_df.loc[0, '貸方消費税税率'] = 消費税税率
    new_df.loc[0, '伝票日付'] = row['日付']
    new_df.loc[0, '摘要'] = 摘要
    new_df.loc[0, '形式'] = 3
    return new_df

# 新しいDataFrameのカラム
new_columns = [
    "月種別", "種類", "形式", "作成方法", "付箋", "伝票日付", "伝票番号", "伝票摘要", "枝番",
    "借方部門", "借方部門名", "借方科目", "借方科目名", "借方補助", "借方補助科目名", "借方金額",
    "借方消費税コード", "借方消費税業種", "借方消費税税率", "借方資金区分", "借方任意項目１",
    "借方任意項目２", "借方インボイス情報", "貸方部門", "貸方部門名", "貸方科目", "貸方科目名",
    "貸方補助", "貸方補助科目名", "貸方金額", "貸方消費税コード", "貸方消費税業種", "貸方消費税税率",
    "貸方資金区分", "貸方任意項目１", "貸方任意項目２", "貸方インボイス情報", "摘要", "期日", "証番号",
    "入力マシン", "入力ユーザ", "入力アプリ", "入力会社", "入力日付"
]

# Streamlitアプリの設定
st.title('じこう売上取込')
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    if st.button('Start'):
        # Excelファイルを読み込む
        df = pd.read_excel(uploaded_file)

        # パターンに一致する行をフィルタリングして変換
        df = df[df['当日日付'].str.contains(r'(\d{2})/(\d{2})\([日月火水木金土]\)', regex=True)]
        df['日付'] = df['当日日付'].apply(lambda x: convert_date(x) if re.match(r'(\d{2})/(\d{2})\([日月火水木金土]\)', x) else None)

        # 不要な列を削除
        df = df.drop(['時間帯', '当年売上予算', '当年売上実績', '当年売上達成率', '前年売上予算', '前年売上実績',
                      '前年売上達成率', '当年売上(累計)', '前年売上(累計)', '組数', '来店者数（合計：男/女）', '客単価（全体）',
                      '客単価（男性）', '客単価（女性）', '伝票数', '値引金額', 'サービス料金', '深夜料金'], axis=1)

        # 結果を格納するリスト
        all_new_dfs = []

        # 各行をループ処理
        for idx, row in df.iterrows():
            # 各列をチェックし、値が入っている場合に新しいDataFrameを作成
            for col, 貸方科目, 貸方補助, 消費税税率, 摘要 in [
                ('テイクアウト', 811, 3, 'K8', 'テイクアウト'),
                ('仕出し', 812, 4, 10, '仕出し'),
                ('容器', 812, 3, 10, '容器'),
                ('まぐろきっぷ', 811, 1, 10, 'まぐろきっぷ'),
                ('仕出し8％', 812, 4, 'K8', '仕出し8%'),
                ('慈こうコース', 811, 4, 10, '慈こうコース'),
                ('てん心', 811, 1, 10, 'てん心')
            ]:
                if row[col] != 0:
                    new_df = create_new_df(row, col, 貸方科目, 貸方補助, 消費税税率, 摘要)
                    all_new_dfs.append(new_df)

            for col, 借方科目, 借方補助, 摘要 in [
                ('現金', 100, 0, '現金'),
                ('カード', 1069, 0, 'カード'),
                ('電子マネー', 132, 4, '電子マネー'),
                ('釣無商品券', 132, 11, '釣無商品券')
            ]:
                if row[col] != 0:
                    new_df = pd.DataFrame(columns=new_columns)
                    new_df.loc[0, '借方科目'] = 借方科目
                    new_df.loc[0, '借方補助'] = 借方補助
                    new_df.loc[0, '借方金額'] = row[col]
                    new_df.loc[0, '伝票日付'] = row['日付']
                    new_df.loc[0, '摘要'] = 摘要
                    new_df.loc[0, '形式'] = 3
                    all_new_dfs.append(new_df)

        # 全ての新しいDataFrameを結合
        result_df = pd.concat(all_new_dfs, ignore_index=True)

        # 結果を表示
        st.dataframe(result_df)

        # 結果をCSVファイルとしてダウンロード
        csv = result_df.to_csv(index=False, encoding='cp932').encode('cp932')
        st.download_button(
            label="Download data",
            data=csv,
            file_name='import_r4.csv',
            mime='text/csv',
        )
        st.snow()