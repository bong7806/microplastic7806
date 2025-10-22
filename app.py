"""
Streamlit app for microplastic intake analysis
Reads the CSV file "섭취량 웹앱 데이터(업로드).csv" placed in the same repository.
Generates summary statistics, histograms, boxplots, and a small download of processed data.
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="미세플라스틱 섭취량 분석", layout="wide")

@st.cache_data
def load_data(path="섭취량 웹앱 데이터(업로드).csv"):
    return pd.read_csv(path)

df = load_data()

st.title("미세플라스틱 섭취량 분석 웹앱")
st.markdown("업로드된 데이터 요약과 시각화를 제공합니다.")

st.sidebar.header("설정")
cols = df.columns.tolist()
selected_cols = st.sidebar.multiselect("분석할 열 선택 (수치형 권장)", cols, default=cols[:3])
group_col = st.sidebar.selectbox("그룹핑 열 (없으면 전체)", ["---"] + cols)

st.header("원본 데이터 미리보기")
st.dataframe(df.head(50))

# Numeric columns
num_df = df.select_dtypes(include=[np.number])
if num_df.empty:
    st.warning("수치형 열이 없습니다. CSV에 수치형 데이터가 포함되어 있는지 확인하세요.")
else:
    st.header("수치형 열 통계")
    stats = num_df.describe().T
    st.dataframe(stats)

    st.header("히스토그램 (4x4 그리드)")
    # choose columns to plot
    plot_cols = selected_cols if selected_cols else num_df.columns.tolist()
    plot_cols = [c for c in plot_cols if c in num_df.columns]
    # limit to up to 16 columns for 4x4 grid
    plot_cols = plot_cols[:16]

    n = len(plot_cols)
    cols_grid = 4
    rows = (n + cols_grid - 1) // cols_grid

    fig, axes = plt.subplots(rows, cols_grid, figsize=(4*cols_grid, 3*rows))
    axes = axes.flatten()
    for i, col in enumerate(plot_cols):
        axes[i].hist(num_df[col].dropna(), bins=20)
        axes[i].set_title(col)
        axes[i].set_xlabel("")
    # hide unused axes
    for j in range(i+1, len(axes)):
        axes[j].axis('off')
    st.pyplot(fig)

    st.header("과목(그룹)별 평균 및 표준편차 (라벨 표시)")
    if group_col != '---' and group_col in df.columns:
        grouped = df.groupby(group_col)[plot_cols].agg(['mean','std'])
        # flatten columns
        grouped.columns = [f"{c}_{stat}" for c,stat in grouped.columns]
        st.dataframe(grouped)
    else:
        overall = df[plot_cols].agg(['mean','std']).T
        st.dataframe(overall)

    st.header("상자 그림 (선택된 열)")
    fig2, ax2 = plt.subplots(figsize=(10,6))
    df[plot_cols].boxplot(ax=ax2, rot=45)
    st.pyplot(fig2)

st.markdown("""---
### 사용법
- 로컬에서 실행: `streamlit run app.py`
- 저장소에 CSV 파일(`섭취량 웹앱 데이터(업로드).csv`)을 함께 업로드하세요.
""")
