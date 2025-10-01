rule supervised_learning:
    input:
        features = "results/normalized/combined_normalized.tsv",
        labels = "metadata/merged_soil_env_data.csv",

    output:
        performance = "results/ml/supervised_learning_performance.png",
        features = "results/ml/supervised_learning_features.png",
        metrics = "results/ml/supervised_learning_metrics.json",
        importances = "results/ml/supervised_learning_feature_importances.json",
        report = "results/ml/supervised_learning_results.pdf" 
    params:
        n_iterations = config.get("ml_n_iterations", 100),
        test_size = config.get("ml_test_size", 0.2),
        random_state = config.get("random_state", 42

    conda:"stats_env"
    
    resources:
        mem_gb=8  
    threads: 4
    log:
        "results/ml/supervised_learning.log"
    script:
        "scripts/supervised_learning.py"

