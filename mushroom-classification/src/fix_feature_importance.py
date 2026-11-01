#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复特征重要性数据并重新生成综合特征重要性图表
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2, mutual_info_classif
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def fix_and_regenerate():
    print("=" * 60)
    print("修复特征重要性数据并重新生成图表")
    print("=" * 60)

    # 1. 加载数据
    print("\n[1/5] 加载数据...")
    data = pd.read_csv('../mushroom_data.csv', na_values='?')

    # 提取代码部分
    for col in data.columns:
        data[col] = data[col].astype(str).apply(
            lambda x: x.split('(')[0] if '(' in str(x) else x
        )

    # 类别标签映射
    data['类别'] = data['类别'].map({'可食用': 0, '有毒': 1})
    data['类别'] = data['类别'].fillna(1)

    print(f"  数据形状: {data.shape}")
    print(f"  类别分布: 可食用 {(data['类别'] == 0).sum()}, 有毒 {(data['类别'] == 1).sum()}")

    # 2. 数据编码
    print("\n[2/5] 数据编码...")
    le = LabelEncoder()
    data_encoded = data.copy()

    for col in data_encoded.columns:
        data_encoded[col] = data_encoded[col].astype(object)
    for col in data_encoded.columns:
        data_encoded[col] = data_encoded[col].fillna('missing')
        data_encoded[col] = le.fit_transform(data_encoded[col].astype(str))

    X = data_encoded.drop('类别', axis=1)
    y = data_encoded['类别']

    print(f"  特征数量: {X.shape[1]}")

    # 3. 计算特征重要性（三种方法）
    print("\n[3/5] 计算特征重要性...")

    # 方法1：随机森林特征重要性
    print("  - 随机森林特征重要性...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    rf_importance = rf.feature_importances_

    # 方法2：卡方检验
    print("  - 卡方检验...")
    X_chi2 = X.abs()  # 确保非负
    chi2_scores, p_values = chi2(X_chi2, y)

    # 方法3：互信息
    print("  - 互信息...")
    mi_scores = mutual_info_classif(X, y, random_state=42)

    # 4. 计算综合得分
    print("\n[4/5] 计算综合得分...")

    # 归一化并处理异常值（NaN/Inf/除以0）
    rf_imp = np.array(rf_importance, dtype=float)
    chi2_s = np.array(chi2_scores, dtype=float)
    mi_s = np.array(mi_scores, dtype=float)

    rf_imp = np.nan_to_num(rf_imp, nan=0.0, posinf=0.0, neginf=0.0)
    chi2_s = np.nan_to_num(chi2_s, nan=0.0, posinf=0.0, neginf=0.0)
    mi_s = np.nan_to_num(mi_s, nan=0.0, posinf=0.0, neginf=0.0)

    rf_max = rf_imp.max() if rf_imp.size and rf_imp.max() != 0 else 1.0
    chi2_max = chi2_s.max() if chi2_s.size and chi2_s.max() != 0 else 1.0
    mi_max = mi_s.max() if mi_s.size and mi_s.max() != 0 else 1.0

    rf_norm = rf_imp / rf_max
    chi2_norm = chi2_s / chi2_max
    mi_norm = mi_s / mi_max

    # 综合得分（三种方法的平均值）
    combined_score = (rf_norm + chi2_norm + mi_norm) / 3

    # 创建DataFrame
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'rf_importance': rf_importance,
        'chi2_score': chi2_scores,
        'mi_score': mi_scores,
        'combined_score': combined_score
    })

    # 按综合得分排序
    feature_importance = feature_importance.sort_values('combined_score', ascending=False)

    # 保存到CSV
    feature_importance.to_csv('feature_importance.csv', index=False)
    print("  特征重要性数据已保存: feature_importance.csv")

    # 显示前10个特征
    print("\n  综合特征重要性排名 (Top 10):")
    print("  " + "-" * 50)
    for i, (_, row) in enumerate(feature_importance.head(10).iterrows(), 1):
        print(f"  {i:2d}. {row['feature']:25s} {row['combined_score']:.4f}")

    # 5. 生成综合特征重要性图表
    print("\n[5/5] 生成综合特征重要性图表...")

    # 图表1：Top 15 特征重要性（水平柱状图）
    fig, ax = plt.subplots(figsize=(12, 8))

    top_15 = feature_importance.head(15)
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(top_15)))

    bars = ax.barh(range(len(top_15)), top_15['combined_score'], color=colors)
    ax.set_yticks(range(len(top_15)))
    ax.set_yticklabels(top_15['feature'], fontsize=11)
    ax.invert_yaxis()  # 最重要的特征在上方

    ax.set_xlabel('综合重要性分数', fontsize=12)
    ax.set_title('综合特征重要性 Top 15\n(随机森林 + 卡方检验 + 互信息)', fontsize=14, fontweight='bold')

    # 添加数值标签
    for i, (idx, row) in enumerate(top_15.iterrows()):
        ax.text(row['combined_score'] + 0.005, i, f'{row["combined_score"]:.3f}',
                va='center', fontsize=10)

    ax.set_xlim(0, 1.15)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('../plots/feature_importance_combined.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  综合特征重要性图已保存: plots/feature_importance_combined.png")

    # 图表2：三种方法对比图（Top 10）
    fig, ax = plt.subplots(figsize=(14, 8))

    top_10 = feature_importance.head(10)
    x = np.arange(len(top_10))
    width = 0.25

    # 归一化后的得分
    rf_norm_top10 = top_10['rf_importance'] / top_10['rf_importance'].max()
    chi2_norm_top10 = top_10['chi2_score'] / top_10['chi2_score'].max()
    mi_norm_top10 = top_10['mi_score'] / top_10['mi_score'].max()

    bars1 = ax.bar(x - width, rf_norm_top10, width, label='随机森林', color='#3498db')
    bars2 = ax.bar(x, chi2_norm_top10, width, label='卡方检验', color='#e74c3c')
    bars3 = ax.bar(x + width, mi_norm_top10, width, label='互信息', color='#2ecc71')

    ax.set_xlabel('特征', fontsize=12)
    ax.set_ylabel('归一化重要性分数', fontsize=12)
    ax.set_title('Top 10 特征重要性 - 三种方法对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(top_10['feature'], rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('../plots/feature_importance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  三种方法对比图已保存: plots/feature_importance_comparison.png")

    # 图表3：雷达图（Top 5 特征）
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    top_5 = feature_importance.head(5)

    # 归一化
    rf_norm_top5 = top_5['rf_importance'] / top_5['rf_importance'].max()
    chi2_norm_top5 = top_5['chi2_score'] / top_5['chi2_score'].max()
    mi_norm_top5 = top_5['mi_score'] / top_5['mi_score'].max()

    # 角度
    angles = np.linspace(0, 2 * np.pi, len(top_5), endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    # 数据
    rf_values = rf_norm_top5.tolist() + [rf_norm_top5.iloc[0]]
    chi2_values = chi2_norm_top5.tolist() + [chi2_norm_top5.iloc[0]]
    mi_values = mi_norm_top5.tolist() + [mi_norm_top5.iloc[0]]

    # 绘制
    ax.plot(angles, rf_values, 'o-', linewidth=2, label='随机森林', color='#3498db')
    ax.fill(angles, rf_values, alpha=0.1, color='#3498db')

    ax.plot(angles, chi2_values, 's-', linewidth=2, label='卡方检验', color='#e74c3c')
    ax.fill(angles, chi2_values, alpha=0.1, color='#e74c3c')

    ax.plot(angles, mi_values, '^-', linewidth=2, label='互信息', color='#2ecc71')
    ax.fill(angles, mi_values, alpha=0.1, color='#2ecc71')

    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(top_5['feature'], fontsize=11)

    ax.set_title('Top 5 特征重要性雷达图', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    plt.savefig('../plots/feature_importance_radar.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  雷达图已保存: plots/feature_importance_radar.png")

    print("\n" + "=" * 60)
    print("完成！已生成以下文件：")
    print("=" * 60)
    print("1. feature_importance.csv - 修复后的特征重要性数据")
    print("2. plots/feature_importance_combined.png - 综合特征重要性图")
    print("3. plots/feature_importance_comparison.png - 三种方法对比图")
    print("4. plots/feature_importance_radar.png - 雷达图")

if __name__ == '__main__':
    fix_and_regenerate()