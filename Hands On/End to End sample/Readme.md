# California Housing Price Prediction

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Scikit-Learn Version](https://img.shields.io/badge/scikit--learn-1.0.1+-blue.svg)](https://scikit-learn.org/stable/)

## Project Overview

This project aims to predict the median house value in Californian districts using various features from those districts. It utilizes the California Housing dataset and employs Scikit-Learn for data preprocessing, feature engineering, model training, and evaluation.

The script follows a typical machine learning workflow:

1.  **Data Loading:** Fetches the housing data from a CSV file.
2.  **Data Exploration:** Performs an initial analysis of the data structure, distributions (histograms), and potential correlations.
3.  **Data Splitting:** Creates training and test sets, emphasizing the importance of stratified splitting based on median income categories to ensure representative samples.
4.  **Data Visualization:** Uses scatter plots to visualize geographical data and relationships between features (e.g., median income vs. median house value).
5.  **Feature Engineering:** Creates new, potentially more informative features from existing ones (e.g., rooms per household, bedrooms ratio).
6.  **Data Preprocessing:** Implements comprehensive preprocessing steps for machine learning:
    * Handling missing numerical values using `SimpleImputer`.
    * Encoding categorical features (`ocean_proximity`) using `OneHotEncoder`.
    * Feature scaling using `StandardScaler`.
    * Applying transformations like logarithm (`FunctionTransformer`) and calculating cluster similarity (`ClusterSimilarity`) based on geographical coordinates.
    * Organizing these steps into reusable `Pipeline` and `ColumnTransformer` objects.
7.  **Model Training:** Trains different regression models:
    * Linear Regression
    * Decision Tree Regressor
    * (Intends to train) Random Forest Regressor
8.  **Model Evaluation:** Evaluates models using Root Mean Squared Error (RMSE) and Cross-Validation (`cross_val_score`).

## Dependencies

* Python >= 3.7
* Scikit-Learn >= 1.0.1
* Pandas
* NumPy
* Matplotlib
* SciPy (for statistical functions like `binom`)
* Packaging (for version checking)

## Setup

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Required Libraries:**
    ```bash
    pip install pandas numpy scikit-learn matplotlib scipy packaging
    ```

4.  **Obtain the Dataset:**
    * The script currently expects the `housing.csv` file at a **hardcoded absolute path**: `C:\Users\Tanlocal\Desktop\Github Apr 2024\Machine learning 2025\Hands on Scikit\handson-ml3-main\datasets\housing\housing.csv`.
    * **IMPORTANT:** You **must** either:
        * Place the `housing.csv` file exactly at that location on your system.
        * **OR (Recommended)** Modify the `HOUSING_CSV_PATH` variable in the script to point to the correct location of your `housing.csv` file. A common practice is to place it in a relative path, e.g., `datasets/housing/housing.csv` within the project directory.
        ```python
        # Example modification in the script:
        # from pathlib import Path
        # SCRIPT_DIR = Path(__file__).parent # Get directory of the script
        # HOUSING_CSV_PATH = SCRIPT_DIR / "datasets" / "housing" / "housing.csv"
        ```
    * The dataset is commonly available online (e.g., within the Hands-On Machine Learning GitHub repository).

5.  **Image Directory:**
    * The script saves plots to an `images/end_to_end_project/` directory relative to where the script is run. It will create this directory if it doesn't exist.
    * It also attempts to download `california.png` into this directory for one of the visualizations if it's not found. Ensure you have an internet connection the first time you run the relevant cell if you don't have the image.


## Key Components & Code Structure

* **`load_housing_data()`:** Function to load the CSV data, including error handling for file not found.
* **Data Splitting Functions:** `shuffle_and_split_data`, `split_data_with_id_hash`, and usage of `train_test_split` and `StratifiedShuffleSplit`.
* **Data Cleaning:** Use of `SimpleImputer` to handle missing values (median strategy).
* **Attribute Handling:** `OrdinalEncoder`, `OneHotEncoder` for categorical data.
* **Feature Scaling:** `MinMaxScaler`, `StandardScaler`.
* **Custom Transformers:**
    * `FunctionTransformer`: Used for log transformations, ratio calculations, and RBF kernel similarity features.
    * `StandardScalerClone`: A custom implementation example (though `StandardScaler` is used primarily).
    * `ClusterSimilarity`: Creates features based on similarity to cluster centers found by K-Means.
* **Pipelines:**
    * `Pipeline`/`make_pipeline`: Chains transformers.
    * `ColumnTransformer`/`make_column_transformer`: Applies different transformations to different columns. The main `preprocessing` object combines numerical and categorical pipelines along with custom feature engineering steps.
* **Model Training & Evaluation:** Uses Scikit-Learn models (`LinearRegression`, `DecisionTreeRegressor`, `RandomForestRegressor`) integrated with the preprocessing pipeline and evaluates using `root_mean_squared_error` and `cross_val_score`.

## Notes

* The script sets `random_state` or `np.random.seed` in various places to ensure reproducibility.
