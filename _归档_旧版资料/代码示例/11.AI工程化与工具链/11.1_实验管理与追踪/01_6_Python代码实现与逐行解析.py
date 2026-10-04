# MLflow实验管理示例（需要安装: pip install mlflow）
"""
MLflow是一个开源的机器学习生命周期管理平台，核心功能：
1. Tracking: 记录参数、指标、模型
2. Projects: 打包代码以可复现的方式运行
3. Models: 管理模型版本和部署
4. Registry: 模型版本注册中心
"""

def mlflow_tracking_example():
    """MLflow实验追踪示例"""
    try:
        import mlflow
        import mlflow.sklearn
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import load_iris
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score
        import numpy as np
        
        # 设置MLflow跟踪URI（可以是本地或远程服务器）
        mlflow.set_tracking_uri("./mlruns")  # 本地存储
        
        # 创建或获取实验
        experiment_name = "iris_classification"
        mlflow.set_experiment(experiment_name)
        
        # 加载数据
        iris = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(
            iris.data, iris.target, test_size=0.2, random_state=42
        )
        
        # 定义要尝试的超参数组合
        param_grid = [
            {"n_estimators": 50, "max_depth": 3, "min_samples_split": 2},
            {"n_estimators": 100, "max_depth": 5, "min_samples_split": 2},
            {"n_estimators": 100, "max_depth": 10, "min_samples_split": 5},
        ]
        
        for i, params in enumerate(param_grid):
            # 开始一个运行（run）
            with mlflow.start_run(run_name=f"run_{i+1}"):
                print(f"\n运行 {i+1}: {params}")
                
                # 1. 记录参数
                mlflow.log_params(params)
                mlflow.log_param("dataset", "iris")
                mlflow.log_param("test_size", 0.2)
                
                # 2. 训练模型
                model = RandomForestClassifier(**params, random_state=42)
                model.fit(X_train, y_train)
                
                # 3. 评估
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                
                # 4. 记录指标
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                
                # 5. 记录特征重要性
                for idx, importance in enumerate(model.feature_importances_):
                    mlflow.log_metric(f"feature_{idx}_importance", importance)
                
                # 6. 保存模型
                mlflow.sklearn.log_model(model, "model")
                
                # 7. 保存其他文件（如可视化）
                import matplotlib.pyplot as plt
                plt.figure(figsize=(10, 6))
                plt.bar(range(len(model.feature_importances_)), model.feature_importances_)
                plt.xlabel("Feature Index")
                plt.ylabel("Importance")
                plt.title("Feature Importance")
                plt.savefig("feature_importance.png")
                mlflow.log_artifact("feature_importance.png")
                plt.close()
                
                print(f"准确率: {accuracy:.4f}")
                print(f"精确率: {precision:.4f}")
                print(f"召回率: {recall:.4f}")
        
        print("\n实验追踪完成！")
        print("查看结果: mlflow ui --backend-store-uri ./mlruns")
        
    except ImportError:
        print("请先安装MLflow: pip install mlflow")

def simple_experiment_tracker():
    """简单的实验追踪器（无外部依赖）"""
    import json
    from datetime import datetime
    
    class ExperimentTracker:
        """轻量级实验追踪器"""
        def __init__(self, experiment_name):
            self.experiment_name = experiment_name
            self.runs = []
            self.current_run = None
        
        def start_run(self, run_name=None):
            """开始新的运行"""
            self.current_run = {
                "run_name": run_name or f"run_{len(self.runs)+1}",
                "start_time": datetime.now().isoformat(),
                "params": {},
                "metrics": {},
                "artifacts": []
            }
            print(f"开始运行: {self.current_run['run_name']}")
        
        def log_param(self, key, value):
            """记录参数"""
            if self.current_run:
                self.current_run["params"][key] = value
        
        def log_params(self, params):
            """记录多个参数"""
            if self.current_run:
                self.current_run["params"].update(params)
        
        def log_metric(self, key, value, step=None):
            """记录指标"""
            if self.current_run:
                if key not in self.current_run["metrics"]:
                    self.current_run["metrics"][key] = []
                self.current_run["metrics"][key].append({
                    "value": value,
                    "step": step,
                    "timestamp": datetime.now().isoformat()
                })
        
        def end_run(self):
            """结束当前运行"""
            if self.current_run:
                self.current_run["end_time"] = datetime.now().isoformat()
                self.runs.append(self.current_run)
                print(f"结束运行: {self.current_run['run_name']}")
                self.current_run = None
        
        def save(self, filepath):
            """保存实验记录"""
            data = {
                "experiment_name": self.experiment_name,
                "runs": self.runs
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"实验记录已保存至: {filepath}")
        
        def get_best_run(self, metric, mode="max"):
            """获取最佳运行"""
            if not self.runs:
                return None
            
            best_run = None
            best_value = float('-inf') if mode == "max" else float('inf')
            
            for run in self.runs:
                if metric in run["metrics"] and run["metrics"][metric]:
                    value = run["metrics"][metric][-1]["value"]
                    if mode == "max" and value > best_value:
                        best_value = value
                        best_run = run
                    elif mode == "min" and value < best_value:
                        best_value = value
                        best_run = run
            
            return best_run
    
    # 使用示例
    tracker = ExperimentTracker("my_experiment")
    
    # 运行1
    tracker.start_run("baseline")
    tracker.log_params({"lr": 0.001, "epochs": 10, "batch_size": 32})
    tracker.log_metric("accuracy", 0.85, step=1)
    tracker.log_metric("accuracy", 0.87, step=2)
    tracker.log_metric("loss", 0.45, step=1)
    tracker.end_run()
    
    # 运行2
    tracker.start_run("improved")
    tracker.log_params({"lr": 0.0001, "epochs": 20, "batch_size": 64})
    tracker.log_metric("accuracy", 0.88, step=1)
    tracker.log_metric("accuracy", 0.91, step=2)
    tracker.log_metric("loss", 0.35, step=1)
    tracker.end_run()
    
    # 保存和查看最佳运行
    tracker.save("experiment_log.json")
    best = tracker.get_best_run("accuracy", mode="max")
    if best:
        print(f"\n最佳运行: {best['run_name']}")
        print(f"最佳准确率: {best['metrics']['accuracy'][-1]['value']}")

if __name__ == "__main__":
    simple_experiment_tracker()
