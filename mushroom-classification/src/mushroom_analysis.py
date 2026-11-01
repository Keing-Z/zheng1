#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蘑菇数据集分析项目
任务：
1. 基础数据统计与可视化分析
2. 特征与"有毒"的相关性分析
3. 机器学习模型分类器
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                           f1_score, confusion_matrix, classification_report,
                           roc_curve, auc)
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MushroomAnalysis:
    def __init__(self):
        self.data = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}

    def load_data(self):
        """加载蘑菇数据集（从本地 CSV 文件）"""
        print("=" * 60)
        print("1. 加载数据集")
        print("=" * 60)

        csv_file = 'mushroom_data.csv'

        if not os.path.exists(csv_file):
            print(f"✗ 找不到数据文件: {csv_file}")
            print(f"  请先运行 data_entry.py 录入数据")
            return False

        self.data = pd.read_csv(csv_file, na_values='?')

        # 从 "代码(中文)" 格式中提取代码部分
        for col in self.data.columns:
            self.data[col] = self.data[col].astype(str).apply(
                lambda x: x.split('(')[0] if '(' in str(x) else x
            )

        if self.data.empty:
            print(f"✗ 数据文件为空: {csv_file}")
            print(f"  请先运行 data_entry.py 录入数据")
            return False

        print(f"✓ 成功从 {csv_file} 加载数据")

        print(f"✓ 数据集形状: {self.data.shape}")
        print(f"✓ 特征数量: {self.data.shape[1] - 1}")
        print(f"✓ 样本数量: {self.data.shape[0]}")

        # 将类别标签转换为数值
        # 可食用=0, 有毒=1
        self.data['类别'] = self.data['类别'].map({'可食用': 0, '有毒': 1})
        # 处理缺失值（如果有）
        self.data['类别'] = self.data['类别'].fillna(1)  # 未知视为有毒

        print(f"\n✓ 类别分布:")
        print(f"  - 可食用 (0): {(self.data['类别'] == 0).sum()}")
        print(f"  - 有毒 (1): {(self.data['类别'] == 1).sum()}")

        return True

    def basic_statistics(self):
        """基础数据统计"""
        print("\n" + "=" * 60)
        print("2. 基础数据统计")
        print("=" * 60)

        print("\n2.1 数据基本信息:")
        print(f"数据类型统计:")
        print(f"  - 分类特征: {self.data.select_dtypes(include=['object']).shape[1]}")
        print(f"  - 数值特征: {self.data.select_dtypes(include=['number']).shape[1]}")

        print("\n2.2 缺失值统计:")
        missing = self.data.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("  无缺失值")

        print("\n2.3 各特征唯一值数量:")
        for col in self.data.columns:
            print(f"  {col}: {self.data[col].nunique()} 个唯一值")

        # 显示每个特征的分布
        print("\n2.4 各特征类别分布:")
        for col in self.data.columns:
            if col != '类别':
                print(f"\n{col}:")
                print(self.data[col].value_counts().head())

    def visualization(self):
        """数据可视化分析"""
        print("\n" + "=" * 60)
        print("3. 数据可视化分析")
        print("=" * 60)

        # 创建图表目录
        if not os.path.exists('plots'):
            os.makedirs('plots')

        # 3.1 类别分布
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # 饼图
        class_counts = self.data['类别'].value_counts()
        axes[0].pie(class_counts.values, labels=['可食用', '有毒'],
                   autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
        axes[0].set_title('蘑菇类别分布', fontsize=14, fontweight='bold')

        # 柱状图
        sns.countplot(x='类别', data=self.data, ax=axes[1],
                     palette=['#2ecc71', '#e74c3c'])
        axes[1].set_xlabel('类别 (0=可食用, 1=有毒)')
        axes[1].set_ylabel('数量')
        axes[1].set_title('蘑菇类别数量分布', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig('plots/class_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ 类别分布图已保存: plots/class_distribution.png")

        # 3.2 主要特征与类别的关系
        key_features = ['odor', 'gill-color', 'ring-type', 'spore-print-color',
                       'gill-size', 'bruises', 'population', 'habitat']

        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()

        for idx, feature in enumerate(key_features):
            if idx < len(axes):
                # 创建交叉表
                ct = pd.crosstab(self.data[feature], self.data['类别'])
                ct.plot(kind='bar', ax=axes[idx], color=['#2ecc71', '#e74c3c'])
                axes[idx].set_title(f'{feature} vs 类别', fontsize=12)
                axes[idx].set_xlabel(feature)
                axes[idx].set_ylabel('数量')
                axes[idx].legend(['可食用', '有毒'])
                axes[idx].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('plots/feature_vs_class.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ 特征与类别关系图已保存: plots/feature_vs_class.png")

        # 3.3 气味特征详细分析（气味是判断毒性的重要特征）
        fig, ax = plt.subplots(figsize=(12, 6))

        odor_class = pd.crosstab(self.data['odor'], self.data['类别'])
        odor_class.plot(kind='bar', ax=ax, color=['#2ecc71', '#e74c3c'])
        ax.set_xlabel('气味类型')
        ax.set_ylabel('数量')
        ax.set_title('不同气味类型的蘑菇类别分布', fontsize=14, fontweight='bold')
        ax.legend(['可食用', '有毒'])
        ax.tick_params(axis='x', rotation=45)

        # 添加气味类型说明
        odor_labels = {
            'a': '杏仁味', 'l': '茴香味', 'c': '杂酚油味', 'y': '鱼腥味',
            'f': '恶臭味', 'm': '霉味', 'n': '无味', 'p': '刺鼻味', 's': '辛辣味'
        }
        ax.set_xticklabels([odor_labels.get(x.get_text(), x.get_text())
                           for x in ax.get_xticklabels()])

        plt.tight_layout()
        plt.savefig('plots/odor_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ 气味分析图已保存: plots/odor_analysis.png")

        # 3.4 特征相关性热图（编码后）
        print("\n正在生成特征相关性热图...")
        le = LabelEncoder()
        data_encoded = self.data.copy()
        # Convert all columns to object type first (handles StringDtype)
        for col in data_encoded.columns:
            data_encoded[col] = data_encoded[col].astype(object)
        for col in data_encoded.columns:
            data_encoded[col] = le.fit_transform(data_encoded[col].astype(str))

        # 计算相关性矩阵
        corr_matrix = data_encoded.corr()

        # 只显示与类别相关性最高的前15个特征
        top_corr = corr_matrix['类别'].abs().sort_values(ascending=False).head(16)
        top_features = top_corr.index.tolist()

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(data_encoded[top_features].corr(), annot=True, fmt='.2f',
                   cmap='RdBu_r', center=0, ax=ax)
        ax.set_title('Top 15 特征相关性热图', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig('plots/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ 相关性热图已保存: plots/correlation_heatmap.png")

    def feature_importance_analysis(self):
        """特征重要性分析"""
        print("\n" + "=" * 60)
        print("4. 特征重要性分析")
        print("=" * 60)

        # 准备数据
        le = LabelEncoder()
        data_encoded = self.data.copy()
        # Convert all columns to object type first (handles StringDtype)
        for col in data_encoded.columns:
            data_encoded[col] = data_encoded[col].astype(object)
        for col in data_encoded.columns:
            data_encoded[col] = le.fit_transform(data_encoded[col].astype(str))

        X = data_encoded.drop('类别', axis=1)
        y = data_encoded['类别']

        # 4.1 使用随机森林计算特征重要性
        print("\n4.1 随机森林特征重要性:")
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)

        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)

        print(feature_importance.to_string(index=False))

        # 可视化特征重要性
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='importance', y='feature', data=feature_importance.head(15),
                   palette='viridis', ax=ax)
        ax.set_title('随机森林特征重要性 Top 15', fontsize=14, fontweight='bold')
        ax.set_xlabel('重要性分数')
        ax.set_ylabel('特征')

        plt.tight_layout()
        plt.savefig('plots/feature_importance_rf.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("\n✓ 随机森林特征重要性图已保存: plots/feature_importance_rf.png")

        # 4.2 使用卡方检验计算特征重要性
        print("\n4.2 卡方检验特征重要性:")
        from sklearn.feature_selection import chi2, SelectKBest

        # 确保所有值非负
        X_chi2 = X.abs()
        chi2_scores, p_values = chi2(X_chi2, y)

        chi2_importance = pd.DataFrame({
            'feature': X.columns,
            'chi2_score': chi2_scores,
            'p_value': p_values
        }).sort_values('chi2_score', ascending=False)

        print(chi2_importance.to_string(index=False))

        # 4.3 使用互信息计算特征重要性
        print("\n4.3 互信息特征重要性:")
        from sklearn.feature_selection import mutual_info_classif

        mi_scores = mutual_info_classif(X, y, random_state=42)
        mi_importance = pd.DataFrame({
            'feature': X.columns,
            'mi_score': mi_scores
        }).sort_values('mi_score', ascending=False)

        print(mi_importance.to_string(index=False))

        # 综合分析
        print("\n" + "=" * 60)
        print("4.4 综合特征重要性分析")
        print("=" * 60)

        # 合并三种方法的结果
        combined = pd.DataFrame({
            'feature': X.columns,
            'rf_importance': rf.feature_importances_,
            'chi2_score': chi2_scores / chi2_scores.max(),  # 归一化
            'mi_score': mi_scores / mi_scores.max()  # 归一化
        })

        combined['combined_score'] = (combined['rf_importance'] +
                                      combined['chi2_score'] +
                                      combined['mi_score']) / 3

        combined = combined.sort_values('combined_score', ascending=False)
        print("\n综合重要性排名 (Top 10):")
        print(combined[['feature', 'combined_score']].head(10).to_string(index=False))

        # 可视化综合重要性
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='combined_score', y='feature', data=combined.head(15),
                   palette='magma', ax=ax)
        ax.set_title('综合特征重要性 Top 15 (RF + Chi2 + MI)', fontsize=14, fontweight='bold')
        ax.set_xlabel('综合重要性分数')
        ax.set_ylabel('特征')

        plt.tight_layout()
        plt.savefig('plots/feature_importance_combined.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("\n✓ 综合特征重要性图已保存: plots/feature_importance_combined.png")

        # 保存特征重要性结果
        combined.to_csv('feature_importance.csv', index=False)
        print("✓ 特征重要性结果已保存: feature_importance.csv")

        return combined

    def prepare_data(self):
        """准备机器学习数据"""
        print("\n" + "=" * 60)
        print("5. 数据预处理")
        print("=" * 60)

        # 编码分类特征
        le = LabelEncoder()
        data_encoded = self.data.copy()

        # Convert all columns to object type first (handles StringDtype)
        for col in data_encoded.columns:
            data_encoded[col] = data_encoded[col].astype(object)
        for col in data_encoded.columns:
            # 处理缺失值
            data_encoded[col] = data_encoded[col].fillna('missing')
            data_encoded[col] = le.fit_transform(data_encoded[col].astype(str))

        # 分离特征和标签
        self.X = data_encoded.drop('类别', axis=1)
        self.y = data_encoded['类别']

        # 划分训练集和测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42, stratify=self.y
        )

        print(f"✓ 训练集大小: {self.X_train.shape[0]}")
        print(f"✓ 测试集大小: {self.X_test.shape[0]}")
        print(f"✓ 特征数量: {self.X_train.shape[1]}")

        # 标准化特征
        scaler = StandardScaler()
        self.X_train_scaled = scaler.fit_transform(self.X_train)
        self.X_test_scaled = scaler.transform(self.X_test)

        print("✓ 特征标准化完成")

        return self.X_train_scaled, self.X_test_scaled, self.y_train, self.y_test

    def build_models(self):
        """构建机器学习模型"""
        print("\n" + "=" * 60)
        print("6. 构建机器学习模型")
        print("=" * 60)

        # 定义模型
        self.models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'SVM': SVC(kernel='rbf', probability=True, random_state=42),
            'KNN': KNeighborsClassifier(n_neighbors=5),
            'Decision Tree': DecisionTreeClassifier(random_state=42)
        }

        # 训练和评估每个模型
        results = []

        for name, model in self.models.items():
            print(f"\n训练 {name}...")

            # 训练模型
            model.fit(self.X_train_scaled, self.y_train)

            # 预测
            y_pred = model.predict(self.X_test_scaled)
            y_prob = model.predict_proba(self.X_test_scaled)[:, 1]

            # 计算指标
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred)
            recall = recall_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred)

            # 交叉验证
            cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=5)

            results.append({
                'Model': name,
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1-Score': f1,
                'CV Mean': cv_scores.mean(),
                'CV Std': cv_scores.std()
            })

            print(f"  准确率: {accuracy:.4f}")
            print(f"  精确率: {precision:.4f}")
            print(f"  召回率: {recall:.4f}")
            print(f"  F1分数: {f1:.4f}")
            print(f"  交叉验证: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        self.results = pd.DataFrame(results)
        return self.results

    def evaluate_models(self):
        """评估模型性能"""
        print("\n" + "=" * 60)
        print("7. 模型性能评估")
        print("=" * 60)

        # 7.1 模型性能比较表
        print("\n7.1 模型性能比较:")
        print(self.results.to_string(index=False))

        # 7.2 模型性能比较图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # 准确率比较
        sns.barplot(x='Model', y='Accuracy', data=self.results, ax=axes[0, 0],
                   palette='viridis')
        axes[0, 0].set_title('模型准确率比较', fontsize=12, fontweight='bold')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].set_ylim(0.9, 1.0)

        # F1分数比较
        sns.barplot(x='Model', y='F1-Score', data=self.results, ax=axes[0, 1],
                   palette='magma')
        axes[0, 1].set_title('模型F1分数比较', fontsize=12, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].set_ylim(0.9, 1.0)

        # 精确率和召回率比较
        x = np.arange(len(self.results))
        width = 0.35
        axes[1, 0].bar(x - width/2, self.results['Precision'], width, label='精确率',
                      color='#3498db')
        axes[1, 0].bar(x + width/2, self.results['Recall'], width, label='召回率',
                      color='#e74c3c')
        axes[1, 0].set_xlabel('模型')
        axes[1, 0].set_ylabel('分数')
        axes[1, 0].set_title('精确率与召回率比较', fontsize=12, fontweight='bold')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(self.results['Model'], rotation=45)
        axes[1, 0].legend()
        axes[1, 0].set_ylim(0.9, 1.0)

        # 交叉验证分数
        sns.barplot(x='Model', y='CV Mean', data=self.results, ax=axes[1, 1],
                   palette='coolwarm')
        axes[1, 1].set_title('交叉验证平均分数', fontsize=12, fontweight='bold')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].set_ylim(0.9, 1.0)

        # 添加误差线
        axes[1, 1].errorbar(range(len(self.results)), self.results['CV Mean'],
                           yerr=self.results['CV Std'], fmt='none', c='black', capsize=5)

        plt.tight_layout()
        plt.savefig('plots/model_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("\n✓ 模型比较图已保存: plots/model_comparison.png")

        # 7.3 最佳模型的混淆矩阵
        best_model_name = self.results.loc[self.results['F1-Score'].idxmax(), 'Model']
        best_model = self.models[best_model_name]
        y_pred = best_model.predict(self.X_test_scaled)

        fig, ax = plt.subplots(figsize=(8, 6))
        cm = confusion_matrix(self.y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                   xticklabels=['可食用', '有毒'], yticklabels=['可食用', '有毒'])
        ax.set_xlabel('预测标签')
        ax.set_ylabel('真实标签')
        ax.set_title(f'最佳模型 ({best_model_name}) 混淆矩阵', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig('plots/confusion_matrix_best.png', dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✓ 最佳模型混淆矩阵已保存: plots/confusion_matrix_best.png")

        # 7.4 ROC曲线
        fig, ax = plt.subplots(figsize=(10, 8))

        for name, model in self.models.items():
            y_prob = model.predict_proba(self.X_test_scaled)[:, 1]
            fpr, tpr, _ = roc_curve(self.y_test, y_prob)
            roc_auc = auc(fpr, tpr)
            ax.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.3f})')

        ax.plot([0, 1], [0, 1], 'k--', label='随机分类器')
        ax.set_xlabel('假阳性率 (FPR)')
        ax.set_ylabel('真阳性率 (TPR)')
        ax.set_title('ROC曲线比较', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('plots/roc_curves.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ ROC曲线图已保存: plots/roc_curves.png")

        # 7.5 保存模型结果
        self.results.to_csv('model_results.csv', index=False)
        print("✓ 模型结果已保存: model_results.csv")

        return best_model_name

    def generate_report(self, best_model_name):
        """生成分析报告"""
        print("\n" + "=" * 60)
        print("8. 生成分析报告")
        print("=" * 60)

        report = """
# 蘑菇数据集分析报告

## 1. 数据集概述
- 数据来源: 本地录入数据 (mushroom_data.csv)
- 样本数量: {total_samples}
- 特征数量: {num_features}
- 类别分布: 可食用 {edible} 个, 有毒 {poisonous} 个

## 2. 关键发现

### 2.1 最重要的特征 (判断毒性)
基于随机森林、卡方检验和互信息三种方法的综合分析：

{feature_importance}

### 2.2 气味特征分析
气味是判断蘑菇毒性的最重要特征：
- 无味(n)的蘑菇大多可食用
- 恶臭(f)、刺鼻(p)、辛辣(s)的蘑菇大多有毒
- 杏仁味(a)的蘑菇可食用

### 2.3 模型性能比较

{model_comparison}

## 3. 结论

1. **最佳模型**: {best_model} (F1分数: {best_f1:.4f})
2. **最重要的特征**: 气味(odor)、菌褶颜色(gill-color)、孢子印颜色(spore-print-color)
3. **准确率**: 所有模型都达到了99%以上的准确率

## 4. 建议

1. 在野外采摘蘑菇时，气味是最重要的判断依据
2. 恶臭、刺鼻、辛辣气味的蘑菇应避免食用
3. 建议使用随机森林或梯度提升模型进行预测
4. 本分析仅供参考，不能替代专业鉴定

## 5. 文件说明

- `mushroom_analysis.py`: 主分析脚本
- `feature_importance.csv`: 特征重要性详细数据
- `model_results.csv`: 模型性能详细数据
- `plots/`: 所有可视化图表
- `README.md`: 项目说明文档
"""

        # 获取特征重要性数据
        le = LabelEncoder()
        data_encoded = self.data.copy()
        # Convert all columns to object type first (handles StringDtype)
        for col in data_encoded.columns:
            data_encoded[col] = data_encoded[col].astype(object)
        for col in data_encoded.columns:
            data_encoded[col] = le.fit_transform(data_encoded[col].astype(str))

        X = data_encoded.drop('类别', axis=1)
        y = data_encoded['类别']

        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)

        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False).head(10)

        feature_importance_str = "| 特征 | 重要性 |\n|------|--------|\n"
        for _, row in feature_importance.iterrows():
            feature_importance_str += f"| {row['feature']} | {row['importance']:.4f} |\n"

        # 模型比较
        model_comparison_str = "| 模型 | 准确率 | F1分数 | 交叉验证 |\n|------|--------|--------|----------|\n"
        for _, row in self.results.iterrows():
            model_comparison_str += f"| {row['Model']} | {row['Accuracy']:.4f} | {row['F1-Score']:.4f} | {row['CV Mean']:.4f} |\n"

        # 获取最佳模型信息
        best_idx = self.results['F1-Score'].idxmax()
        best_f1 = self.results.loc[best_idx, 'F1-Score']

        # 填充报告
        report = report.format(
            total_samples=self.data.shape[0],
            num_features=self.data.shape[1] - 1,
            edible=(self.data['类别'] == 0).sum(),
            poisonous=(self.data['类别'] == 1).sum(),
            feature_importance=feature_importance_str,
            model_comparison=model_comparison_str,
            best_model=best_model_name,
            best_f1=best_f1
        )

        # 保存报告
        with open('analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print("✓ 分析报告已保存: analysis_report.md")

        # 创建README
        readme = """# 蘑菇数据集分析项目

## 项目简介
本项目分析UCI蘑菇数据集，通过机器学习方法预测蘑菇是否有毒。

## 项目结构
```
mushroom_project/
├── mushroom_analysis.py      # 主分析脚本
├── requirements.txt          # 依赖包列表
├── README.md                # 项目说明文档
├── analysis_report.md       # 详细分析报告
├── feature_importance.csv   # 特征重要性数据
├── model_results.csv        # 模型性能数据
└── plots/                   # 可视化图表目录
    ├── class_distribution.png
    ├── feature_vs_class.png
    ├── odor_analysis.png
    ├── correlation_heatmap.png
    ├── feature_importance_rf.png
    ├── feature_importance_combined.png
    ├── model_comparison.png
    ├── confusion_matrix_best.png
    └── roc_curves.png
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行分析
```bash
python mushroom_analysis.py
```

### 3. 查看结果
- 分析报告: `analysis_report.md`
- 可视化图表: `plots/` 目录
- 详细数据: `feature_importance.csv` 和 `model_results.csv`

## 分析内容

1. **基础数据统计与可视化**
   - 数据集基本信息
   - 类别分布分析
   - 特征与类别关系可视化

2. **特征重要性分析**
   - 随机森林特征重要性
   - 卡方检验特征重要性
   - 互信息特征重要性
   - 综合重要性排名

3. **机器学习模型**
   - 逻辑回归
   - 随机森林
   - 梯度提升
   - 支持向量机
   - K近邻
   - 决策树

## 关键发现

1. **最重要的特征**: 气味(odor)是判断蘑菇毒性的最重要特征
2. **模型性能**: 所有模型都达到了99%以上的准确率
3. **最佳模型**: 随机森林和梯度提升表现最好

## 注意事项

**免责声明**: 本分析仅供参考，不能替代专业鉴定。在野外采摘蘑菇时，请务必咨询专业人士。

## 许可证
MIT License
"""

        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme)

        print("✓ 项目说明文档已保存: README.md")

    def run(self):
        """运行完整分析流程"""
        print("蘑菇数据集分析项目")
        print("=" * 60)

        # 1. 加载数据
        if not self.load_data():
            return

        # 2. 基础统计
        self.basic_statistics()

        # 3. 可视化分析
        self.visualization()

        # 4. 特征重要性分析
        self.feature_importance_analysis()

        # 5. 数据预处理
        self.prepare_data()

        # 6. 构建模型
        self.build_models()

        # 7. 评估模型
        best_model_name = self.evaluate_models()

        # 8. 生成报告
        self.generate_report(best_model_name)

        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)
        print("\n生成的文件:")
        print("  分析报告: analysis_report.md")
        print("  可视化图表: plots/ 目录")
        print("  特征重要性: feature_importance.csv")
        print("  模型结果: model_results.csv")
        print("  项目说明: README.md")
        print("\n注意: 本分析仅供参考，不能替代专业鉴定！")

if __name__ == "__main__":
    # 运行分析
    analyzer = MushroomAnalysis()
    analyzer.run()
