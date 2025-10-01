#!/usr/bin/env python3
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import shap

def main():
    # Load input data
    features = pd.read_csv(snakemake.input.features, sep='\t', index_col=0)
    labels = pd.read_csv(snakemake.input.labels, sep='\c', index_col=0)
    
    # Ensure samples align
    common_samples = features.index.intersection(labels.index)
    X = features.loc[common_samples]
    y = labels.loc[common_samples]
    
    # Get parameters
    test_size = float(snakemake.params.test_size)
    random_state = int(snakemake.params.random_state)
    n_iterations = int(snakemake.params.n_iterations)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state)
    
    # Initialize models
    models = {
        "XGBoost": XGBRegressor(random_state=random_state, n_jobs=int(snakemake.threads)),
        "RandomForest": RandomForestRegressor(random_state=random_state, n_jobs=int(snakemake.threads)),
        "ElasticNet": make_pipeline(StandardScaler(), ElasticNet(random_state=random_state))
    }
    
    # Results storage
    metrics = {}
    importances = {}
    shap_values = {}
    
    # Create PDF report
    with PdfPages(snakemake.output.report) as pdf:
        # Train and evaluate each model
        for name, model in models.items():
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train.values.ravel(), 
                                      cv=5, scoring='r2', n_jobs=int(snakemake.threads))
            
            # Final training
            model.fit(X_train, y_train.values.ravel())
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics[name] = {
                "r2_score": r2_score(y_test, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                "cv_mean_r2": np.mean(cv_scores),
                "cv_std_r2": np.std(cv_scores)
            }
            
            # Get feature importances
            if hasattr(model, 'feature_importances_'):
                importances[name] = dict(zip(X.columns, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                importances[name] = dict(zip(X.columns, model[-1].coef_))  # For pipeline
            
            # SHAP analysis (for XGBoost only)
            if name == "XGBoost":
                explainer = shap.Explainer(model)
                shap_values[name] = explainer(X_test).values.mean(0)
                
                # SHAP summary plot
                plt.figure(figsize=(10, 6))
                shap.summary_plot(shap_values[name], X_test, plot_type="bar", show=False)
                plt.title(f"{name} Feature Importance (SHAP)")
                pdf.savefig()
                plt.close()
            
            # Performance plot
            plt.figure(figsize=(10, 6))
            plt.scatter(y_test, y_pred, alpha=0.6)
            plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--')
            plt.xlabel('Actual Values')
            plt.ylabel('Predicted Values')
            plt.title(f'{name} Performance\nR² = {metrics[name]["r2_score"]:.2f}')
            pdf.savefig()
            plt.close()
            
            # Feature importance plot
            if name in importances:
                imp_df = pd.DataFrame.from_dict(importances[name], orient='index', columns=['importance'])
                imp_df.sort_values('importance', ascending=False).head(20).plot.bar(figsize=(10, 6))
                plt.title(f'{name} Top 20 Important Features')
                plt.tight_layout()
                pdf.savefig()
                plt.close()
    
        # Add summary page
        plt.figure(figsize=(10, 6))
        pd.DataFrame(metrics).T[['r2_score', 'rmse', 'cv_mean_r2']].plot.bar(rot=0)
        plt.title('Model Comparison')
        plt.ylabel('Score')
        pdf.savefig()
        plt.close()
    
    # Save metrics JSON
    with open(snakemake.output.metrics, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Save feature importances JSON
    with open(snakemake.output.importances, 'w') as f:
        json.dump(importances, f, indent=2)
    
    # Save individual plots
    for name in models:
        if name in importances:
            imp_df = pd.DataFrame.from_dict(importances[name], orient='index', columns=['importance'])
            imp_df.sort_values('importance', ascending=False).head(20).plot.bar(figsize=(10, 6))
            plt.title(f'{name} Top 20 Important Features')
            plt.tight_layout()
            plt.savefig(f"results/ml/{name.lower()}_feature_importance.png")
            plt.close()

if __name__ == "__main__":
    main()