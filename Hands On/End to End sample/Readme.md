# California Housing Price Prediction Project 🏠☀️📈

This project aims to predict the median house value for California districts based on various features collected from the 1990 California census data. It follows a typical machine learning workflow, including data loading, exploration, preprocessing, model training, and evaluation. 🤖📊


---

## Table of Contents 🗺️

1.  [Project Goal](#project-goal) 🎯
2.  [Dataset](#dataset) 💾
3.  [Prerequisites](#prerequisites) ✅
4.  [File Structure](#file-structure) 📁
5.  [Usage](#usage) ▶️
6.  [Workflow and Code Explanation](#workflow-and-code-explanation) ⚙️
    * [Setup and Imports](#setup-and-imports) ✨
    * [Get the Data](#get-the-data) 📥
        * [Load Data](#load-data)
        * [Initial Data Exploration](#initial-data-exploration) 👀
        * [Data Visualization](#data-visualization) 🎨
    * [Create a Test Set](#create-a-test-set) ✂️
        * [Simple Random Split (Conceptual)](#simple-random-split-conceptual)
        * [Identifier-Based Split (Conceptual)](#identifier-based-split-conceptual)
        * [Scikit-Learn `train_test_split`](#scikit-learn-train_test_split)
        * [Stratified Sampling](#stratified-sampling) ⚖️
    * [Discover and Visualize Data (EDA on Training Set)](#discover-and-visualize-data-eda-on-training-set) 🔍
        * [Geographical Visualization](#geographical-visualization) 📍
        * [Looking for Correlations](#looking-for-correlations) 🔗
        * [Experimenting with Attribute Combinations](#experimenting-with-attribute-combinations) 🧪
    * [Prepare the Data for Machine Learning Algorithms](#prepare-the-data-for-machine-learning-algorithms) 🛠️
        * [Data Cleaning (Handling Missing Values)](#data-cleaning-handling-missing-values) 🧹
        * [Handling Text and Categorical Attributes](#handling-text-and-categorical-attributes) 🔠
        * [Feature Scaling](#feature-scaling) 📏
        * [Custom Transformers](#custom-transformers) 🧩
        * [Transformation Pipelines](#transformation-pipelines) 〰️
            * [Numerical Pipeline](#numerical-pipeline)
            * [Categorical Pipeline](#categorical-pipeline)
            * [Combined Preprocessing Pipeline](#combined-preprocessing-pipeline)
    * [Select and Train a Model](#select-and-train-a-model) 🧠
        * [Training and Evaluating on the Training Set](#training-and-evaluating-on-the-training-set) 💪
        * [Better Evaluation Using Cross-Validation](#better-evaluation-using-cross-validation) ✔️
7.  [Results (Preliminary)](#results-preliminary) 📊🏆
8.  [Key Concepts Demonstrated](#key-concepts-demonstrated) 🔑💡
9.  [Potential Next Steps](#potential-next-steps) 🚀

---

## Project Goal

The primary objective is to build a regression model that accurately predicts the median housing value 💰 in Californian districts using census data features like population, median income, location, housing age, etc.

---

## Dataset

The dataset used is the California Housing dataset, derived from the 1990 U.S. Census. Each row represents a block group (district) in California ☀️.

**Features:** 📝

* `longitude`: A measure of how far west a house is (higher value = further west) ⬅️
* `latitude`: A measure of how far north a house is (higher value = further north) ⬆️
* `housing_median_age`: Median age of houses within a block ⏳
* `total_rooms`: Total number of rooms within a block 🚪
* `total_bedrooms`: Total number of bedrooms within a block 🛏️
* `population`: Total number of people residing within a block 👨‍👩‍👧‍👦
* `households`: Total number of households within a block 🏘️
* `median_income`: Median income for households within a block (in tens of thousands of US Dollars) 💵
* `ocean_proximity`: Location of the house w.r.t ocean/sea (Categorical) 🌊

**Target Variable:** 🎯

* `median_house_value`: Median house value for households within a block (in US Dollars) 💲

---

## Prerequisites

* **Python:** Version 3.7 or higher is required (checked via `assert sys.version_info >= (3, 7)`). 🐍
* **Scikit-Learn:** Version 1.0.1 or higher is required (checked via `assert version.parse(sklearn.__version__) >= version.parse("1.0.1")`). 🤖
* **Core Libraries:** 📚
    * `pandas`: For data manipulation and loading CSV files.
    * `numpy`: For numerical operations.
    * `matplotlib`: For plotting graphs. 📊
    * `pathlib`: For handling file paths robustly. 📂
* **Optional (for specific cells):**
    * `scipy`: Used for statistical functions (e.g., `binom.cdf`).
    * `urllib`: Used in extra code to download the California map image. 🌐

It's recommended to use a virtual environment and install dependencies using a `requirements.txt` file (not provided, but derivable from the imports). 💻

---

## File Structure

* **`your_notebook_name.ipynb` / `your_script_name.py`:** The main file containing the Python code for the project. 📓 </>
* **`datasets/housing/housing.csv`:** The input dataset file. **IMPORTANT:** The path to this file is currently hardcoded in the `load_housing_data` function (`HOUSING_CSV_PATH`). You **MUST** update this path to match the location on your system. ⚠️
* **`images/end_to_end_project/`:** Directory created by the code to save generated plots (e.g., histograms, scatter plots). 🖼️

---

## Usage

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```
2.  **Set up Environment & Install Dependencies:** ⚙️
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    pip install pandas numpy scikit-learn matplotlib scipy # Add other specific versions if needed
    ```
3.  **Modify Data Path:** ⚠️📂
    * Open the Python script or Jupyter Notebook (`.py` or `.ipynb`).
    * Locate the `HOUSING_CSV_PATH` variable definition within the `load_housing_data` function or near the top of the script.
    * **Change the path string** (`r"C:\Users\Tanlocal\Desktop\..."`) to the **actual path** where you have stored the `housing.csv` file on your computer.
4.  **Run the Code:** ▶️💨
    * If it's a Jupyter Notebook:
        ```bash
        jupyter notebook your_notebook_name.ipynb
        ```
        Then run the cells sequentially within the Jupyter interface.
    * If it's a Python script:
        ```bash
        python your_script_name.py
        ```
5.  **Check Outputs:** Generated plots will be saved in the `images/end_to_end_project/` directory. 🖼️ Numerical outputs and model evaluation results will be printed or displayed in the notebook/console. 🖥️

---

## Workflow and Code Explanation

The code implements a standard machine learning pipeline:

### Setup and Imports

* Checks Python and Scikit-Learn versions for compatibility. ✅
* Imports necessary libraries (Pandas, NumPy, Scikit-Learn modules, Matplotlib, etc.). 📚

### Get the Data

#### Load Data

* A function `load_housing_data` is defined to load the `housing.csv` file using Pandas.
* It includes error handling (`FileNotFoundError`) if the specified path (`HOUSING_CSV_PATH`) is incorrect. ❌
* **Crucially, the `HOUSING_CSV_PATH` is hardcoded and needs user modification.** ⚠️

#### Initial Data Exploration

* Uses Pandas functions to get a first look at the data:
    * `housing.head()`: Displays the first 5 rows.
    * `housing.info()`: Shows column data types and non-null counts (reveals missing values in `total_bedrooms`). ❓
    * `housing["ocean_proximity"].value_counts()`: Counts unique values in the categorical feature.
    * `housing.describe()`: Provides summary statistics for numerical columns. #️⃣

#### Data Visualization

* Sets up Matplotlib default font sizes for better readability.
* Defines a `save_fig` function to save plots as high-resolution PNGs to the `images/end_to_end_project/` directory. 💾🖼️
* Generates histograms for all numerical attributes using `housing.hist()` to understand their distributions. 📊

### Create a Test Set

* Discusses the importance of splitting data into training and testing sets *before* extensive exploration to avoid data snooping bias. 🕵️‍♂️🚫
* **Simple Random Split (Conceptual):** A function `shuffle_and_split_data` using `np.random.permutation` is shown but noted as potentially problematic if the dataset updates.
* **Identifier-Based Split (Conceptual):** Functions `is_id_in_test_set` and `split_data_with_id_hash` demonstrate a more stable splitting method using hashing on a unique identifier.
* **Scikit-Learn `train_test_split`:** The standard Scikit-Learn function is used for a basic random split (`random_state=42` ensures reproducibility). 👍
* **Stratified Sampling:** ⚖️
    * Recognizes that `median_income` is crucial for prediction and its distribution should be similar in train/test sets.
    * Creates an income category feature (`income_cat`) using `pd.cut`.
    * Uses Scikit-Learn's `StratifiedShuffleSplit` (shown conceptually) and `train_test_split` with the `stratify` argument based on `income_cat` to create `strat_train_set` and `strat_test_set`.
    * Compares the income category proportions in the overall dataset, stratified test set, and random test set to demonstrate the benefit of stratification. ✅
    * Removes the temporary `income_cat` feature from the sets.

### Discover and Visualize Data (EDA on Training Set)

* Creates a copy of the *stratified training set* (`strat_train_set`) for exploration to prevent modifying the original set.

#### Geographical Visualization

* Uses scatter plots (`housing.plot(kind="scatter", ...)`) to visualize geographical data:
    * Simple plot of latitude vs. longitude. 📍🗺️
    * Improved plot using `alpha=0.2` to handle point density.
    * Advanced plot incorporating population size (`s`) and median house value (`c`).
    * Extra code shows how to overlay a California map image for better context.

#### Looking for Correlations

* Calculates the standard correlation coefficient (Pearson's r) between numerical features using `housing.corr(numeric_only=True)`. 🔗
* Focuses on correlations with the target variable (`median_house_value`). 🎯
* Uses `pandas.plotting.scatter_matrix` to visualize correlations between promising attributes.
* Creates a detailed scatter plot of `median_income` vs. `median_house_value`.

#### Experimenting with Attribute Combinations

* Creates new features by combining existing ones, hoping to find stronger correlations: 🧪🔬
    * `rooms_per_house`
    * `bedrooms_ratio`
    * `people_per_house`
* Re-calculates the correlation matrix to check the impact of these new features. 🤔

### Prepare the Data for Machine Learning Algorithms

* Separates features (`housing`) and labels (`housing_labels`) from the `strat_train_set`.

#### Data Cleaning (Handling Missing Values)

* Identifies rows with missing values (`isnull().any(axis=1)`), focusing on `total_bedrooms`. ❓🧹✨
* Discusses and demonstrates three options for handling NaNs: `dropna()`, `drop()`, `fillna()`.
* Uses Scikit-Learn's `SimpleImputer(strategy="median")` as the preferred method for numerical features. ✅
* Briefly mentions `IsolationForest` for outlier detection (code provided but commented out).

#### Handling Text and Categorical Attributes

* Isolates the categorical feature `ocean_proximity`. 🌊🔠🔡
* Demonstrates `OrdinalEncoder` but notes its limitations.
* Uses `OneHotEncoder` as the standard approach for nominal categorical features. 👍
* Compares with Pandas `get_dummies`.

#### Feature Scaling

* Discusses the importance of feature scaling for many ML algorithms. 📏
* Demonstrates `MinMaxScaler` and `StandardScaler`.
* Visualizes the effect of `np.log` transformation.
* Discusses scaling the *target variable*. 🎯

#### Custom Transformers

* Shows how to create simple transformers using `FunctionTransformer`. 🧩⚙️
* Demonstrates building custom Scikit-Learn compatible transformers by inheriting from `BaseEstimator` and `TransformerMixin`.

#### Transformation Pipelines

* Combines multiple preprocessing steps into pipelines for better organization and reproducibility. 〰️➡️
* **Numerical Pipeline:** Combines `SimpleImputer` and `StandardScaler`.
* **Categorical Pipeline:** Combines `SimpleImputer` and `OneHotEncoder`.
* **Combined Preprocessing Pipeline:** Uses `ColumnTransformer` to apply different pipelines to different columns. Builds a complex `preprocessing` pipeline with custom steps. ✅

### Select and Train a Model

* *(This section header intentionally kept clean for linking)* 🧠🤖

#### Training and Evaluating on the Training Set

* Creates a full pipeline including preprocessing and a `LinearRegression` model. 💪
* Fits the pipeline on the training data.
* Calculates the Root Mean Squared Error (RMSE) on the *training set*.
* Repeats the process for a `DecisionTreeRegressor`, noting its perfect score (RMSE=0) on the training set, indicating severe overfitting. (Overfitting 🚨)

#### Better Evaluation Using Cross-Validation

* Uses Scikit-Learn's `cross_val_score` to perform K-fold cross-validation (with `cv=10`). ✔️🔄
* Calculates RMSE scores for the `DecisionTreeRegressor` across the 10 folds (`scoring="neg_root_mean_squared_error"`).
* Displays the mean and standard deviation of the cross-validation RMSE scores, showing a more realistic error metric.
* Repeats the cross-validation for the `LinearRegression` model to compare performance.

*(Note: The provided code snippet ends just before training a `RandomForestRegressor`...)*

---

## Results (Preliminary)

Based on 10-fold cross-validation on the training set: 📊🏆

* **Linear Regression:**
    * Mean RMSE: ~$69,000 (example value)
    * Std Dev RMSE: [Value]
* **Decision Tree Regressor:**
    * Mean RMSE: ~$70,000 (example value)
    * Std Dev RMSE: [Value]

**Interpretation:** 🧐 Initial results suggest Linear Regression slightly outperforms a single Decision Tree in generalization. Both models have significant error, indicating room for improvement. 📈

---

## Key Concepts Demonstrated

* **End-to-End ML Workflow:** Loading -> EDA -> Splitting -> Preprocessing -> Training -> Evaluation 🔁🔑💡
* **Data Loading & Handling:** `pandas`, `pathlib` 💾
* **Exploratory Data Analysis (EDA):** `info()`, `describe()`, `value_counts()`, Histograms, Scatter Plots, Correlation 📊🔍
* **Data Splitting:** Train/Test Split, Stratified Sampling ✂️⚖️
* **Data Preprocessing:** Imputation 🧹, Encoding 🔠, Scaling 📏, Feature Engineering 🧪
* **Scikit-Learn Pipelines:** `Pipeline`, `make_pipeline` 〰️
* **Column Transformer:** `ColumnTransformer`, selectors ✅
* **Custom Transformers:** `FunctionTransformer`, custom classes 🧩
* **Model Training:** `LinearRegression`, `DecisionTreeRegressor` 🧠
* **Model Evaluation:** RMSE, Cross-Validation (`cross_val_score`) ✔️📏
* **Reproducibility:** `random_state` 🎲

---

