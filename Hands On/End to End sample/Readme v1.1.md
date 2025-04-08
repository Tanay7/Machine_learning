# 🏠 California Housing Value Prediction Project 📊🤖

This project implements a machine learning pipeline to predict the median house value for Californian districts based on various features available for each district. It follows the end-to-end example often associated with the California Housing dataset, demonstrating key steps in a typical ML workflow.

## 📜 Table of Contents

*   [Project Goal](#project-goal-🎯)
*   [Key Features & Concepts](#key-features--concepts-✅)
*   [Dataset](#dataset-💾)
*   [Prerequisites](#prerequisites-⚙️)
*   [Setup & Installation](#setup--installation-💻)
*   [Usage](#usage-🚀)
*   [Code Workflow Breakdown](#code-workflow-breakdown-🛠️)
    *   [1. Environment Setup](#1-environment-setup)
    *   [2. Data Acquisition](#2-data-acquisition-📂)
    *   [3. Exploratory Data Analysis (EDA) & Visualization](#3-exploratory-data-analysis-eda--visualization-👀)
    *   [4. Test Set Creation](#4-test-set-creation-✂️)
    *   [5. Data Preparation & Preprocessing](#5-data-preparation--preprocessing-🧹)
    *   [6. Model Selection & Training](#6-model-selection--training-🧠)
    *   [7. Model Evaluation (Cross-Validation)](#7-model-evaluation-cross-validation-📈)
    *   [8. Hyperparameter Tuning](#8-hyperparameter-tuning-🔧)
    *   [9. Analysis of Best Model](#9-analysis-of-best-model-🥇)
    *   [10. Final Evaluation on Test Set](#10-final-evaluation-on-test-set-🎯)
    *   [11. Model Persistence](#11-model-persistence-💾)
*   [Exploratory Exercises](#exploratory-exercises-🧪)
*   [Potential Improvements](#potential-improvements-🤔)
*   [Acknowledgements](#acknowledgements-🙏)

## Project Goal 🎯

The primary objective is to build a regression model that accurately predicts the median housing value in California districts using census data features like population, median income, location, etc.

## Key Features & Concepts ✅

This project showcases a comprehensive ML workflow, including:

*   **Data Loading & Handling:** Using `pandas` and `pathlib` for robust data loading.
*   **Exploratory Data Analysis (EDA):** Utilizing `.info()`, `.describe()`, `.value_counts()`, histograms (`matplotlib`), and scatter plots to understand data distributions, correlations, and potential issues.
*   **Data Visualization:** Creating insightful geographical plots, correlation matrices (`pandas.plotting.scatter_matrix`), and attribute combinations plots.
*   **Data Splitting Strategies:** Implementing random splitting and stratified splitting (`StratifiedShuffleSplit`) based on income categories to ensure representative test sets.
*   **Data Cleaning:** Handling missing values using `sklearn.impute.SimpleImputer`.
*   **Feature Engineering:** Creating new, potentially more predictive features from existing ones (e.g., `rooms_per_house`).
*   **Handling Categorical Features:** Using `sklearn.preprocessing.OneHotEncoder` for converting text features to numerical representations.
*   **Feature Scaling:** Applying `sklearn.preprocessing.StandardScaler` and `MinMaxScaler` to standardize numerical features.
*   **Custom Transformers:** Building custom Scikit-Learn compatible transformers using `FunctionTransformer`, `BaseEstimator`, `TransformerMixin`, and `ClusterSimilarity` for specialized preprocessing steps (e.g., log transform, RBF kernels, clustering-based features).
*   **Pipeline Construction:** Using `sklearn.pipeline.Pipeline` and `sklearn.compose.ColumnTransformer` to streamline preprocessing and modeling steps, preventing data leakage.
*   **Model Training:** Implementing various regression algorithms:
    *   `sklearn.linear_model.LinearRegression`
    *   `sklearn.tree.DecisionTreeRegressor`
    *   `sklearn.ensemble.RandomForestRegressor`
    *   `sklearn.svm.SVR` (Support Vector Regressor - explored in exercises)
*   **Model Evaluation:** Using Root Mean Squared Error (RMSE) as the primary metric and employing K-Fold Cross-Validation (`sklearn.model_selection.cross_val_score`) for robust performance estimation.
*   **Hyperparameter Tuning:** Optimizing model performance using:
    *   `sklearn.model_selection.GridSearchCV`
    *   `sklearn.model_selection.RandomizedSearchCV` (with various `scipy.stats` distributions)
*   **Feature Importance Analysis:** Identifying the most influential features using the best-performing model (Random Forest).
*   **Model Persistence:** Saving and loading the trained pipeline using `joblib` for deployment or later use.
*   **Advanced Techniques (Exercises):** Exploring `SelectFromModel` for feature selection and creating meta-estimators (`FeatureFromRegressor`).

## Dataset 💾

The project utilizes the **California Housing Prices dataset**. This dataset contains information derived from the 1990 California census.

*   **Source:** Originally from the StatLib repository. Commonly used in machine learning examples.
*   **Features:** Longitude, Latitude, Housing Median Age, Total Rooms, Total Bedrooms, Population, Households, Median Income, Ocean Proximity.
*   **Target Variable:** `median_house_value` (The variable we aim to predict).
*   **File:** `housing.csv` (Expected location defined in the script, requires adjustment based on user environment).

## Prerequisites ⚙️

*   **Python:** Version 3.7 or higher (`assert sys.version_info >= (3, 7)`).
*   **Core Libraries:**
    *   `scikit-learn`: Version 1.0.1 or higher (`assert version.parse(sklearn.__version__) >= version.parse("1.0.1")`).
    *   `pandas`
    *   `numpy`
    *   `matplotlib`
    *   `scipy`
    *   `joblib`
*   **Jupyter Environment (Recommended):** Jupyter Notebook or JupyterLab for running the `.ipynb` style code.

## Setup & Installation 💻

1.  **Clone the Repository (if applicable):**
    ```
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install Dependencies:** Create a `requirements.txt` file with the libraries listed above (or use one if provided) and install:
    ```
    pip install -r requirements.txt
    # Or install manually:
    # pip install pandas numpy scikit-learn==<version> matplotlib scipy joblib jupyterlab
    ```
4.  **Download the Dataset:** Ensure the `housing.csv` file is available. **Crucially, update the `HOUSING_CSV_PATH` variable in the script** to point to the correct location of your `housing.csv` file. The script currently uses a hardcoded path:
    ```
    # In the script:
    HOUSING_CSV_PATH = Path(r"C:\Users\Tanlocal\Desktop\Github Apr 2024\Machine learning 2025\Hands on Scikit\handson-ml3-main\datasets\housing\housing.csv")
    # --> CHANGE THIS PATH to where your housing.csv is located! <--
    ```

## Usage 🚀

1.  **Activate Virtual Environment:** (If you created one)
    ```
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```
2.  **Start Jupyter:**
    ```
    jupyter lab
    # or
    jupyter notebook
    ```
3.  **Open and Run:** Open the notebook file (if you have it as `.ipynb`) or paste the code from the `paste.txt` into a new notebook. Run the cells sequentially.
4.  **Observe Outputs:** Pay attention to the outputs of each cell, including data summaries, visualizations, model performance metrics (RMSE), and tuning results.

## Code Workflow Breakdown 🛠️

The script follows a structured machine learning workflow:

### 1. Environment Setup

*   Imports necessary libraries (`sys`, `sklearn`, `pandas`, `numpy`, `matplotlib`, etc.).
*   Performs version checks for Python and Scikit-Learn to ensure compatibility.

### 2. Data Acquisition 📂

*   Defines a function `load_housing_data()` using `pandas.read_csv` and `pathlib.Path`.
*   Includes error handling (`FileNotFoundError`) if the specified `housing.csv` path is incorrect.
*   Loads the dataset into a pandas DataFrame named `housing`.

### 3. Exploratory Data Analysis (EDA) & Visualization 👀

*   **Initial Inspection:** Uses `housing.head()`, `housing.info()`, `housing.describe()` to get a first look at the data structure, types, non-null counts, and basic statistics.
*   **Categorical Feature Analysis:** Examines the distribution of `ocean_proximity` using `value_counts()`.
*   **Histograms:** Plots histograms for all numerical features using `housing.hist()` to visualize distributions (identifying skewness, scale differences). Includes a helper function `save_fig()` to save plots.
*   **Geographical Visualization:** Creates scatter plots of `longitude` vs. `latitude`:
    *   Simple scatter plot.
    *   Plot with `alpha` transparency to handle density.
    *   Enhanced plot where point size represents `population` and color represents `median_house_value` (using `cmap="jet"`). Includes overlaying a California map image for context. 🗺️
*   **Correlation Analysis:**
    *   Computes the pairwise correlation matrix using `housing.corr(numeric_only=True)`.
    *   Focuses on correlations with the target variable `median_house_value`.
    *   Uses `pandas.plotting.scatter_matrix` to visualize correlations between promising attributes.

### 4. Test Set Creation ✂️

*   **Importance:** Emphasizes the need for a separate test set to avoid data snooping bias.
*   **Methods Discussed:**
    *   Simple random split (using custom `shuffle_and_split_data`).
    *   Identifier-based split (using `crc32` hash) for stable splits across runs.
    *   Using `sklearn.model_selection.train_test_split`.
*   **Stratified Sampling:**
    *   Identifies `median_income` as crucial for stratification. Creates an income category feature (`income_cat`) using `pd.cut`.
    *   Uses `sklearn.model_selection.StratifiedShuffleSplit` (and the simpler `train_test_split` with `stratify` argument) to ensure the test set distribution of income categories matches the overall dataset distribution. This is crucial for unbiased evaluation.
    *   Removes the temporary `income_cat` feature after splitting.

### 5. Data Preparation & Preprocessing 🧹

*   Creates copies of the stratified training set (`strat_train_set`) for processing. Separates features (`housing`) from labels (`housing_labels`).
*   **Data Cleaning (Handling NaNs):**
    *   Identifies missing values (specifically in `total_bedrooms`).
    *   Discusses three options: drop rows, drop column, impute.
    *   Implements imputation using `sklearn.impute.SimpleImputer(strategy="median")` on numerical features.
*   **Handling Text/Categorical Attributes:**
    *   Selects the `ocean_proximity` column.
    *   Discusses `OrdinalEncoder` (not suitable here) and `OneHotEncoder`.
    *   Applies `OneHotEncoder` to convert categories into binary vectors (sparse and dense formats shown). Discusses `handle_unknown="ignore"`.
*   **Custom Transformers:** 🛠️
    *   Demonstrates `sklearn.preprocessing.FunctionTransformer` for applying simple functions (e.g., `np.log`, `rbf_kernel`).
    *   Implements custom classes `StandardScalerClone` (as an example of `BaseEstimator`, `TransformerMixin`) and `ClusterSimilarity` (using KMeans to create location similarity features).
*   **Feature Scaling:** 📏
    *   Discusses `MinMaxScaler` and `StandardScaler`.
    *   Applies `StandardScaler` within pipelines.
    *   Mentions log transformation for heavy-tailed distributions (e.g., population).
*   **Transformation Pipelines:** 🔗
    *   Builds separate pipelines for numerical (`num_pipeline`) and categorical (`cat_pipeline`) features using `make_pipeline`.
    *   Combines these using `sklearn.compose.ColumnTransformer` (and `make_column_transformer` with `make_column_selector`) to apply appropriate transformations to different columns.
    *   Creates a more complex `preprocessing` pipeline incorporating feature engineering (ratios, log transforms, geo-clustering) and handling remaining columns.

### 6. Model Selection & Training 🧠

*   Trains several regression models within pipelines that include the preprocessing steps:
    *   **Linear Regression:** `make_pipeline(preprocessing, LinearRegression())`
    *   **Decision Tree:** `make_pipeline(preprocessing, DecisionTreeRegressor())`
    *   **Random Forest:** `make_pipeline(preprocessing, RandomForestRegressor())`
*   Fits each model on the preprocessed training data (`housing`, `housing_labels`).
*   Makes initial predictions on the training set to check if the models learned *something*.

### 7. Model Evaluation (Cross-Validation) 📈

*   **Metric:** Uses Root Mean Squared Error (RMSE). Includes a helper check for `root_mean_squared_error` availability or defines it using `mean_squared_error`.
*   **Cross-Validation:** Employs `sklearn.model_selection.cross_val_score` with 10 folds (`cv=10`) and `scoring="neg_root_mean_squared_error"` (negative because `cross_val_score` maximizes score).
*   Evaluates Linear Regression, Decision Tree, and Random Forest using cross-validation to get a more robust estimate of their performance and assess overfitting (comparing training RMSE vs. validation RMSE).

### 8. Hyperparameter Tuning 🔧

*   **Goal:** Optimize the hyperparameters of the most promising model (Random Forest).
*   **Grid Search:**
    *   Uses `sklearn.model_selection.GridSearchCV` with a predefined `param_grid` targeting hyperparameters within the preprocessing steps (`preprocessing__geo__n_clusters`) and the model itself (`random_forest__max_features`).
    *   Fits the `GridSearchCV` object, which explores all combinations using 3-fold CV.
    *   Examines `best_params_`, `best_estimator_`, and `cv_results_`.
*   **Randomized Search:**
    *   Uses `sklearn.model_selection.RandomizedSearchCV` with parameter distributions (`scipy.stats.randint`) for more efficient exploration of larger hyperparameter spaces.
    *   Sets `n_iter` to control the number of combinations sampled.
    *   Fits and examines results similarly to Grid Search.
    *   Includes a bonus section explaining different `scipy.stats` distributions suitable for hyperparameter sampling.

### 9. Analysis of Best Model 🥇

*   Selects the `best_estimator_` found by Randomized Search (`rnd_search.best_estimator_`).
*   Extracts feature importances from the `RandomForestRegressor` component of the final pipeline.
*   Displays the importances alongside their corresponding feature names (obtained using `get_feature_names_out()` from the preprocessing pipeline).

### 10. Final Evaluation on Test Set 🎯

*   Retrieves the held-back test set (`strat_test_set`). Separates features (`X_test`) and labels (`y_test`).
*   Uses the `final_model` (best tuned pipeline) to make predictions on `X_test`.
*   Calculates the final RMSE on the test set. **This provides the estimate of the model's generalization error.**
*   Computes a 95% confidence interval for the test RMSE using `scipy.stats.bootstrap` on the squared errors.

### 11. Model Persistence 💾

*   Saves the entire final pipeline (preprocessing + trained model) to a file (`my_california_housing_model.pkl`) using `joblib.dump`.
*   Demonstrates how to load the model back using `joblib.load` and make predictions on new data.

## Exploratory Exercises 🧪

The final sections of the code explore several advanced exercises:

1.  **Support Vector Machine (SVR):** Tries `sklearn.svm.SVR` with `GridSearchCV` and `RandomizedSearchCV` (using `loguniform` and `expon` distributions) on a subset of data, demonstrating tuning for different model types.
2.  **Feature Selection:** Uses `sklearn.feature_selection.SelectFromModel` within a pipeline to select important features based on a `RandomForestRegressor` before feeding them to an SVR.
3.  **Custom Meta-Estimator:** Implements a `FeatureFromRegressor` transformer that trains a regressor (e.g., `KNeighborsRegressor`) on specific inputs (latitude, longitude) and outputs its predictions as a new feature. Explores adding this KNN-based feature to the pipeline and tuning its hyperparameters.
4.  **Advanced Custom Transformer:** Re-implements `StandardScalerClone` from scratch, adding `inverse_transform` and full feature name support (`feature_names_in_`, `get_feature_names_out`).

## Potential Improvements 🤔

*   **Try More Models:** Experiment with other regression algorithms (e.g., Gradient Boosting variants like XGBoost, LightGBM, CatBoost).
*   **Advanced Feature Engineering:** Explore more sophisticated feature combinations or domain-specific features.
*   **Outlier Handling:** Implement more robust outlier detection and removal strategies (e.g., using Isolation Forest results more formally).
*   **Hyperparameter Optimization:** Use more advanced tuning techniques like Bayesian Optimization (e.g., using `scikit-optimize`).
*   **Ensemble Methods:** Combine predictions from multiple models (stacking, blending).
*   **Deployment:** Package the model and deploy it as an API using frameworks like Flask or FastAPI.

## Acknowledgements 🙏

*   This project closely follows the end-to-end California Housing example from the book "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow" by Aurélien Géron.
*   Dataset sourced from the StatLib repository, originally collected by Pace, R. Kelley and Barry, Ronald.

