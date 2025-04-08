# California Housing Price Prediction

**Project Objective:** To predict the median house value for Californian districts using various features from those districts based on 1990 census data. This project demonstrates a complete machine learning workflow, including data loading, exploration, visualization, preprocessing, model training, and evaluation using Scikit-Learn.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Dataset](#dataset)
3.  [Dependencies](#dependencies)
4.  [Installation](#installation)
5.  [Usage](#usage)
6.  [Workflow](#workflow)
    * [Data Acquisition](#data-acquisition)
    * [Data Exploration & Visualization](#data-exploration--visualization)
    * [Test Set Creation](#test-set-creation)
    * [Feature Engineering](#feature-engineering)
    * [Data Preprocessing](#data-preprocessing)
    * [Model Selection & Training](#model-selection--training)
    * [Evaluation](#evaluation)
7.  [File Structure](#file-structure)
8.  [Results](#results)
9.  [Potential Improvements](#potential-improvements)

## Project Overview

This project implements a regression model to predict the median housing price in California districts. It leverages the California Housing dataset and employs various data science and machine learning techniques provided by Python libraries like Pandas, NumPy, Matplotlib, and Scikit-Learn. The goal is to build a robust pipeline that cleans and prepares the data, trains different regression models, and evaluates their performance.

## Dataset

* **Source:** The dataset is based on data from the 1990 California census.
* **File:** `housing.csv`
* **Location:** The script currently expects the dataset to be located at a specific hardcoded path: `C:\Users\Tanlocal\Desktop\Github Apr 2024\Machine learning 2025\Hands on Scikit\handson-ml3-main\datasets\housing\housing.csv`. **You will likely need to update the `HOUSING_CSV_PATH` variable in the script to point to the correct location of your `housing.csv` file.** Alternatively, place the dataset in the expected directory structure relative to where you run the script.
* **Features:**
    * `longitude`: District longitude
    * `latitude`: District latitude
    * `housing_median_age`: Median age of houses in the district
    * `total_rooms`: Total number of rooms in the district
    * `total_bedrooms`: Total number of bedrooms in the district (contains missing values)
    * `population`: Total population in the district
    * `households`: Total number of households in the district
    * `median_income`: Median income for households in the district (in tens of thousands of US Dollars)
    * `ocean_proximity`: Categorical feature describing proximity to the ocean/sea
* **Target Variable:**
    * `median_house_value`: Median house value for households in the district (in US Dollars)

## Dependencies

* Python (>= 3.7 recommended)
* Pandas
* NumPy
* Scikit-Learn (>= 1.0.1 recommended, code uses features available from this version onwards, some features might require >= 1.2 or >=1.3)
* Matplotlib
* Pathlib (standard library)
* Packaging (used for version check)
* SciPy (used for statistical calculations like binomial distribution)
* zlib (standard library, used for hashing)

## Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install the required packages:** It's best practice to have a `requirements.txt` file. If you don't have one, you can create it or install packages individually:
    ```bash
    pip install pandas numpy scikit-learn matplotlib packaging scipy
    # Or if requirements.txt exists:
    # pip install -r requirements.txt
    ```

## Usage

1.  **Ensure the Dataset is Accessible:** Make sure the `housing.csv` file is available and the `HOUSING_CSV_PATH` variable in the script points to its correct location.
2.  **Run the Script/Notebook:**
    * If it's a Jupyter Notebook (`.ipynb`):
        ```bash
        jupyter lab # or jupyter notebook
        ```
        Then open the notebook file and run the cells sequentially.
    * If it's a Python script (`.py`):
        ```bash
        python your_script_name.py
        ```
3.  **Outputs:**
    * Descriptive statistics and data info will be printed to the console/notebook output.
    * Data visualizations (histograms, scatter plots) will be displayed and saved as high-resolution PNG files in the `images/end_to_end_project/` directory (created automatically if it doesn't exist).
    * Model performance metrics (RMSE) will be printed.

## Workflow

The script follows a standard machine learning pipeline:

### Data Acquisition

* Loads the `housing.csv` dataset using Pandas.
* Includes error handling for `FileNotFoundError`.

### Data Exploration & Visualization

* **Initial Inspection:** Uses `.head()`, `.info()`, `.describe()`, and `.value_counts()` to understand the data structure, data types, presence of missing values, and basic statistics.
* **Histograms:** Plots histograms for all numerical features to visualize their distributions.
* **Geographical Visualization:** Creates scatter plots using latitude and longitude:
    * A basic scatter plot.
    * A plot with transparency (`alpha`) to show density.
    * A detailed plot where point size represents population and color represents median house value, overlaid on a map of California (requires downloading `california.png`).
* **Correlation Analysis:**
    * Calculates the standard correlation coefficient (Pearson's r) between features and the target variable (`median_house_value`).
    * Uses `scatter_matrix` to visualize correlations between promising attributes.
    * Plots a scatter plot specifically for `median_income` vs. `median_house_value`.

### Test Set Creation

* **Importance:** Emphasizes the need for a separate test set to avoid data snooping bias.
* **Methods Explored:**
    * Simple random shuffling (`shuffle_and_split_data`).
    * Hash-based splitting using identifiers (`split_data_with_id_hash`) for stable splits across runs.
    * Using `sklearn.model_selection.train_test_split`.
* **Stratified Sampling:**
    * Creates an income category feature (`income_cat`) by binning `median_income`.
    * Uses `sklearn.model_selection.StratifiedShuffleSplit` and `train_test_split` with the `stratify` option to ensure the test set is representative of the overall income distribution, which is crucial given its correlation with the target variable.
    * The `income_cat` feature is dropped after splitting.

### Feature Engineering

* Combines existing attributes to create potentially more informative features:
    * `rooms_per_house` (`total_rooms` / `households`)
    * `bedrooms_ratio` (`total_bedrooms` / `total_rooms`)
    * `people_per_house` (`population` / `households`)
* Re-evaluates correlations with these new features.

### Data Preprocessing

This is a major part, preparing the data for machine learning algorithms using Scikit-Learn transformers and pipelines:

* **Data Cleaning (Handling Missing Values):**
    * Identifies missing values (primarily in `total_bedrooms`).
    * Demonstrates three options: dropping rows, dropping the column, or imputing.
    * Uses `sklearn.impute.SimpleImputer` with the `median` strategy to fill missing numerical values.
* **Outlier Handling (Optional):**
    * Includes code (commented out) using `sklearn.ensemble.IsolationForest` to identify and potentially remove outliers.
* **Handling Text and Categorical Attributes:**
    * Identifies the `ocean_proximity` feature.
    * Explores `OrdinalEncoder` but notes its limitations for nominal categories.
    * Uses `sklearn.preprocessing.OneHotEncoder` to convert the categorical feature into numerical one-hot vectors. Handles unknown categories encountered during transformation.
* **Feature Scaling:**
    * Discusses the need for scaling.
    * Applies `MinMaxScaler` and `StandardScaler`. `StandardScaler` is primarily used in the final pipeline.
    * Demonstrates log transformation for skewed distributions (e.g., population).
* **Custom Transformers:**
    * Uses `sklearn.preprocessing.FunctionTransformer` for applying arbitrary functions like `np.log`, `rbf_kernel` (for similarity features based on age or geographic location).
    * Defines custom transformer classes inheriting from `BaseEstimator` and `TransformerMixin`:
        * `StandardScalerClone`: A demonstration of building a Scikit-Learn compatible transformer.
        * `ClusterSimilarity`: Creates features based on the similarity of samples to cluster centers found using `KMeans` on geographical coordinates.
* **Transformation Pipelines:**
    * Uses `sklearn.pipeline.Pipeline` and `make_pipeline` to chain sequential transformations (e.g., imputing then scaling numerical features).
    * Uses `sklearn.compose.ColumnTransformer` and `make_column_transformer` to apply different transformations to different columns (numerical vs. categorical) concurrently.
    * Builds a complex `preprocessing` pipeline incorporating:
        * Ratio calculations (`ratio_pipeline`).
        * Log transformations (`log_pipeline`).
        * Geographical clustering similarity (`ClusterSimilarity`).
        * One-hot encoding for categorical features (`cat_pipeline`).
        * Standard imputation and scaling for remaining numerical features (`default_num_pipeline` via `remainder`).
* **Target Transformation:** Demonstrates scaling the target variable (`median_house_value`) using `StandardScaler` and `sklearn.compose.TransformedTargetRegressor`.

### Model Selection & Training

* **Linear Regression:**
    * Trains a `LinearRegression` model within a pipeline that includes the full preprocessing steps.
* **Decision Tree Regressor:**
    * Trains a `DecisionTreeRegressor` model within the same preprocessing pipeline.
* **Random Forest Regressor:**
    * Starts setting up a `RandomForestRegressor` (the provided code snippet ends here, implying this is the next model to be trained and evaluated).

### Evaluation

* **Metrics:** Uses Root Mean Squared Error (RMSE) as the primary evaluation metric. Includes code to handle potential `ImportError` for `root_mean_squared_error` in older Scikit-Learn versions.
* **Training Set Evaluation:** Calculates RMSE on the full training set. Notes that the Decision Tree achieves 0 RMSE, indicating severe overfitting.
* **Cross-Validation:**
    * Uses `sklearn.model_selection.cross_val_score` with 10 folds (`cv=10`) to get a more robust estimate of model performance.
    * Calculates cross-validated RMSE scores for both Linear Regression and the Decision Tree Regressor.
    * Compares the performance and variability of the models based on cross-validation scores.

## File Structure

.
├── your_script_name.py # or .ipynb
├── datasets
│   └── housing
│       └── housing.csv # <-- Make sure this path is correct or update HOUSING_CSV_PATH
└── images
└── end_to_end_project # <-- Directory for saved plots
├── attribute_histogram_plots.png
├── bad_visualization_plot.png
├── better_visualization_plot.png
├── housing_prices_scatterplot.png
├── california_housing_prices_plot.png
├── scatter_matrix_plot.png
├── income_vs_house_value_scatterplot.png
├── long_tail_plot.png
├── age_similarity_plot.png
├── district_cluster_plot.png
└── housing_income_cat_bar_plot.png
# (potentially california.png if downloaded)

## Results

* **Linear Regression:** Achieves a certain RMSE on the training set and cross-validation (specific values depend on the exact run but are typically around $68,000-$69,000).
* **Decision Tree Regressor:** Achieves an RMSE of 0 on the training set, clearly indicating overfitting. Cross-validation reveals a much higher and more realistic RMSE (typically around $70,000-$71,000), confirming overfitting.
* **Random Forest Regressor:** The evaluation for this model is expected next (based on the code structure) and often provides better performance than individual decision trees or simple linear models.

*(Note: The exact RMSE values might slightly differ based on library versions and the non-determinism inherent in some algorithms if `random_state` is not fixed everywhere, although the script makes good use of `random_state=42`.)*

## Potential Improvements

* **Hyperparameter Tuning:** Use `GridSearchCV` or `RandomizedSearchCV` to find the optimal hyperparameters for models like Decision Tree, Random Forest, or potentially more advanced models.
* **Try More Models:** Experiment with other regression algorithms like Support Vector Machines (SVR), Gradient Boosting models (e.g., XGBoost, LightGBM), or even simple Neural Networks.
* **Advanced Feature Engineering:** Explore more complex feature combinations or interactions. Investigate domain-specific feature engineering.
* **Outlier Analysis:** Perform a more thorough investigation and handling of outliers identified by Isolation Forest or other methods.
* **Ensemble Methods:** Combine predictions from multiple models (stacking, blending).
