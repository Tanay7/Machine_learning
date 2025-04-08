# California Housing Price Predictor 🏡

Predicting median house values in California districts using 1990 census data and Scikit-Learn.

---

## 🚀 At a Glance

* **Goal:** Build a regression model for California housing prices.
* **Data:** 1990 California Census data (`housing.csv`).
* **Tech:** Python, Pandas, Scikit-Learn, NumPy, Matplotlib.
* **Core Task:** End-to-end Machine Learning Regression Pipeline.

---

## ✨ Key Features & Techniques

This project demonstrates a comprehensive ML workflow:

* **Data Handling:** Loading, cleaning (imputation), and exploration using Pandas.
* **Visualization:** Understanding data distributions (histograms) and relationships (scatter plots, geographical maps) with Matplotlib.
* **Robust Splitting:** Stratified train/test split based on income categories to ensure representative sets.
* **Feature Engineering:** Creating new features from existing ones (e.g., rooms per household).
* **Advanced Preprocessing:**
    * Handling numerical (`SimpleImputer`, `StandardScaler`) and categorical (`OneHotEncoder`) data.
    * Applying transformations (`log`, `rbf_kernel`).
    * Using custom Scikit-Learn transformers (`ClusterSimilarity`).
* **Pipeline Automation:** Streamlining preprocessing and modeling using `Pipeline` and `ColumnTransformer`.
* **Model Training:** Implementing and comparing `LinearRegression`, `DecisionTreeRegressor`, and `RandomForestRegressor` (partially implemented).
* **Model Evaluation:** Assessing performance using Root Mean Squared Error (RMSE) and Cross-Validation.

---

## 🛠️ Getting Started

### Prerequisites

* Python (>= 3.7 recommended)
* Pip (Python package installer)
* Access to a terminal or command prompt.

### Installation

1.  **Clone (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```
2.  **Setup Environment (Recommended):**
    ```bash
    python -m venv venv
    # Linux/macOS
    source venv/bin/activate
    # Windows
    .\venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install pandas numpy scikit-learn matplotlib packaging scipy
    # Create a requirements.txt for easier installs later:
    # pip freeze > requirements.txt
    # Then install using: pip install -r requirements.txt
    ```

### Dataset Setup ⚠️ **Important** ⚠️

* The script expects `housing.csv` at a **hardcoded path**: `C:\Users\Tanlocal\Desktop\Github Apr 2024\Machine learning 2025\Hands on Scikit\handson-ml3-main\datasets\housing\housing.csv`.
* **You MUST either:**
    1.  Place your `housing.csv` file exactly at that location.
    *OR*
    2.  **Modify the `HOUSING_CSV_PATH` variable** within the script to point to the correct path where you've saved `housing.csv`.

---

## ▶️ How to Run

1.  **Verify Dataset Path:** Double-check that the script can find `housing.csv` (see "Dataset Setup" above).
2.  **Execute:**
    * **Jupyter Notebook (`.ipynb`):**
        ```bash
        jupyter lab  # or jupyter notebook
        ```
        Navigate to the notebook file and run the cells sequentially.
    * **Python Script (`.py`):**
        ```bash
        python your_script_name.py
        ```

---

## 📋 Project Workflow Steps

The script proceeds through the following stages:

1.  **Load Data:** Reads `housing.csv` into a Pandas DataFrame.
2.  **Explore & Visualize:**
    * Initial data checks (`info()`, `describe()`, `head()`).
    * Distribution analysis (histograms).
    * Geographical plotting (scatter plots colored by price/population).
    * Correlation analysis (correlation matrix, scatter matrix).
3.  **Split Data:** Creates stratified train/test sets based on median income to prevent sampling bias.
4.  **Preprocess & Feature Engineer:**
    * Creates combined features (e.g., `rooms_per_house`).
    * Builds a sophisticated `ColumnTransformer` pipeline to:
        * Impute missing numerical values (median).
        * Scale numerical features (`StandardScaler`).
        * One-hot encode categorical features (`ocean_proximity`).
        * Apply custom transformations (log, ratios, geographic clustering similarity).
5.  **Train & Evaluate Models:**
    * Integrates the preprocessing pipeline with models (`LinearRegression`, `DecisionTreeRegressor`, `RandomForestRegressor`).
    * Calculates RMSE on the training set.
    * Performs 10-fold Cross-Validation for more robust RMSE estimates.
    * Compares model performance and identifies overfitting (especially in the Decision Tree).

---

## 📊 Outputs

Running the script will generate:

* **Console/Notebook Output:** Data summaries, shapes, statistics, and RMSE scores.
* **Saved Plots:** Visualizations saved as `.png` files in the `images/end_to_end_project/` directory (created automatically). Includes histograms, scatter plots, geographic maps, etc.

---

## 🔮 Further Exploration

Potential next steps to improve the model:

* **Tune Hyperparameters:** Use `GridSearchCV` or `RandomizedSearchCV`.
* **Experiment with Models:** Try SVR, Gradient Boosting (XGBoost, LightGBM), etc.
* **Refine Features:** Explore more feature interactions or external data sources.
* **Ensemble Methods:** Combine predictions from the best models.
* **Outlier Treatment:** Implement a strategy based on the Isolation Forest findings or other methods.
