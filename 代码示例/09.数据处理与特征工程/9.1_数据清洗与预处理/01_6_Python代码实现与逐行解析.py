import pandas as pd                   # 数据处理库
import numpy as np                    # 数值计算
from typing import List, Union, Optional

class DataCleaner:
    """数据清洗工具类"""
    
    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = "mean",
        fill_value=None
    ) -> pd.DataFrame:
        """处理缺失值
        
        参数:
            df: 输入数据框
            strategy: 填充策略 (mean/median/mode/constant/drop)
            fill_value: 当strategy='constant'时的填充值
        返回:
            处理后的数据框
        """
        df_clean = df.copy()
        
        # 显示缺失值统计
        missing_stats = df_clean.isnull().sum()
        missing_stats = missing_stats[missing_stats > 0]
        if len(missing_stats) > 0:
            print("缺失值统计:")
            print(missing_stats)
        
        if strategy == "drop":
            # 删除包含缺失值的行
            df_clean = df_clean.dropna()
        elif strategy == "mean":
            # 用均值填充数值列（pandas 3.x 已移除链式 inplace 赋值，改为直接赋值）
            for col in df_clean.select_dtypes(include=[np.number]).columns:
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        elif strategy == "median":
            # 用中位数填充数值列
            for col in df_clean.select_dtypes(include=[np.number]).columns:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        elif strategy == "mode":
            # 用众数填充
            for col in df_clean.columns:
                if not df_clean[col].mode().empty:
                    df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])
        elif strategy == "constant":
            # 用固定值填充
            df_clean = df_clean.fillna(fill_value)
        elif strategy == "ffill":
            # 前向填充（fillna(method=...) 在 pandas 2.1+ 弃用、3.0 移除）
            df_clean = df_clean.ffill()
        elif strategy == "bfill":
            # 后向填充
            df_clean = df_clean.bfill()
        
        return df_clean
    
    @staticmethod
    def remove_outliers(
        df: pd.DataFrame,
        columns: List[str],
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pd.DataFrame:
        """删除异常值
        
        参数:
            df: 输入数据框
            columns: 要处理的列
            method: 检测方法 (iqr/zscore)
            threshold: 阈值
        返回:
            处理后的数据框
        """
        df_clean = df.copy()
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            if method == "iqr":
                # IQR方法
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # 标记异常值
                outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
                print(f"{col}: 发现 {outliers.sum()} 个异常值")
                
                # 删除异常值
                df_clean = df_clean[~outliers]
            
            elif method == "zscore":
                # Z-score方法
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                outliers = z_scores > threshold
                print(f"{col}: 发现 {outliers.sum()} 个异常值")
                df_clean = df_clean[~outliers]
        
        return df_clean
    
    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
        subset: Optional[List[str]] = None,
        keep: str = "first"
    ) -> pd.DataFrame:
        """删除重复值
        
        参数:
            df: 输入数据框
            subset: 仅考虑特定列
            keep: 保留哪个 (first/last/False)
        返回:
            处理后的数据框
        """
        duplicates = df.duplicated(subset=subset).sum()
        print(f"发现 {duplicates} 个重复记录")
        
        return df.drop_duplicates(subset=subset, keep=keep)
    
    @staticmethod
    def standardize_text(
        df: pd.DataFrame,
        columns: List[str],
        lowercase: bool = True,
        remove_punctuation: bool = False,
        remove_whitespace: bool = True
    ) -> pd.DataFrame:
        """标准化文本
        
        参数:
            df: 输入数据框
            columns: 文本列
            lowercase: 转为小写
            remove_punctuation: 删除标点
            remove_whitespace: 删除多余空白
        返回:
            处理后的数据框
        """
        df_clean = df.copy()
        import string
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            # 转为字符串类型
            df_clean[col] = df_clean[col].astype(str)
            
            if lowercase:
                df_clean[col] = df_clean[col].str.lower()
            
            if remove_punctuation:
                df_clean[col] = df_clean[col].apply(
                    lambda x: x.translate(str.maketrans('', '', string.punctuation))
                )
            
            if remove_whitespace:
                df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True).str.strip()
        
        return df_clean

if __name__ == "__main__":
    # 创建示例数据
    np.random.seed(42)
    data = {
        'A': [1, 2, np.nan, 4, 5, 100, 7, 8],           # 包含缺失值和异常值
        'B': [10, 20, 30, 40, 50, 60, 70, np.nan],      # 包含缺失值
        'C': ['Hello', 'World', 'hello', 'WORLD', None, '  Test  ', 'Test', 'test'],
    }
    df = pd.DataFrame(data)
    
    print("原始数据:")
    print(df)
    print()
    
    # 创建清洗器
    cleaner = DataCleaner()
    
    # 1. 处理缺失值
    df_clean = cleaner.handle_missing_values(df, strategy="mean")
    print("\n处理缺失值后:")
    print(df_clean)
    
    # 2. 处理异常值
    df_clean = cleaner.remove_outliers(df_clean, columns=['A'], method="iqr")
    print("\n处理异常值后:")
    print(df_clean)
    
    # 3. 标准化文本
    df_clean = cleaner.standardize_text(
        df_clean,
        columns=['C'],
        lowercase=True,
        remove_whitespace=True
    )
    print("\n标准化文本后:")
    print(df_clean)
