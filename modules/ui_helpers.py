"""
modules/ui_helpers.py
Streamlit UI表示補助モジュール（免責事項, カロリーメーター, BIG KPI表示等）
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional

def render_disclaimer():
    """
    医療判断でない旨の免責事項を表示します。
    """
    st.caption(
        "⚠️ **ご注意**: 本アプリの計算結果（RER/DERおよび給餌量）は一般的な獣医栄養学の計算式に基づく推計値です。"
        "実際の必要カロリーは愛犬の個別体質、活動量、生活環境により異なります。"
        "減量や病気療養中、健康状態に懸念がある場合は必ずかかりつけの動物病院・獣医師にご相談ください。"
    )


def render_kpi_metrics(
    total_gram: float,
    der_kcal: float,
    rer_kcal: float,
    meals_per_day: int,
    gram_per_meal: float
):
    """
    BIG KPI メトリクスカードを表示します。
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🍚 1日推奨給餌量",
            value=f"{total_gram:.1f} g",
            delta=None
        )
    
    with col2:
        st.metric(
            label="🥣 1回あたり給餌量",
            value=f"{gram_per_meal:.1f} g",
            delta=f"1日 {meals_per_day} 回給餌"
        )
        
    with col3:
        st.metric(
            label="🔥 1日必要エネルギー(DER)",
            value=f"{der_kcal:.0f} kcal",
            delta=None
        )
        
    with col4:
        st.metric(
            label="💤 安静時要求量(RER)",
            value=f"{rer_kcal:.0f} kcal",
            delta=f"係数 {der_kcal/rer_kcal:.2f}" if rer_kcal > 0 else None
        )


def render_calorie_gauge(
    der_kcal: float,
    rer_kcal: float,
    target_max_kcal: Optional[float] = None
) -> go.Figure:
    """
    Plotly を利用したエネルギー要求量 (RER vs DER) ゲージグラフを生成します。
    """
    max_val = target_max_kcal if target_max_kcal else max(der_kcal * 1.5, 2000.0)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=der_kcal,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "1日必要エネルギー (DER kcal)", 'font': {'size': 18, 'color': "#1F2937"}},
        delta={'reference': rer_kcal, 'increasing': {'color': "#EF4444"}, 'decreasing': {'color': "#10B981"}, 'position': "top"},
        gauge={
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#4B5563"},
            'bar': {'color': "#F59E0B"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, rer_kcal], 'color': "#E0F2FE"},
                {'range': [rer_kcal, der_kcal], 'color': "#FEF3C7"},
                {'range': [der_kcal, max_val], 'color': "#FEE2E2"}
            ],
            'threshold': {
                'line': {'color': "#DC2626", 'width': 4},
                'thickness': 0.75,
                'value': der_kcal
            }
        }
    ))
    
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="sans-serif")
    )
    
    return fig


def render_blend_pie_chart(
    label_a: str,
    gram_a: float,
    label_b: str,
    gram_b: float
) -> go.Figure:
    """
    2種類フードのブレンド給餌割合(g)のパイチャートを生成します。
    """
    fig = go.Figure(data=[go.Pie(
        labels=[label_a, label_b],
        values=[gram_a, gram_b],
        hole=.4,
        marker=dict(colors=["#3B82F6", "#10B981"]),
        textinfo="label+percent+value",
        texttemplate="%{label}<br>%{value:.1f}g (%{percent})"
    )])
    
    fig.update_layout(
        title="🍚 フードブレンド配合比率 (重量 g)",
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig
