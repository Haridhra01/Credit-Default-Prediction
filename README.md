# Credit Default Prediction

## Machine Learning and Explainable AI Based Credit Default Prediction System
A machine learning and explainable artificial intelligence (XAI) based system for predicting the likelihood of credit card default and providing transparent explanations for model predictions.

The project implements an explainable Business Intelligence workflow that combines dataset preparation, preprocessing, feature selection, machine learning-based prediction, model evaluation, and feature contribution analysis through an interactive web dashboard.

## Project Overview
Credit default prediction is an important problem in financial risk management. Traditional machine learning models can provide accurate predictions, but their decisions may be difficult for business users to understand.

This project addresses this challenge by integrating **Machine Learning** with **Explainable AI** to provide both:

- Credit default predictions
- Interpretable explanations of the factors contributing to those predictions

The system follows the explainable Business Intelligence framework described in the project reference methodology and applies it to the **UCI Default of Credit Card Clients dataset**.

The final system uses **XGBoost** as the selected machine learning model and provides global and local feature contribution analysis using XGBoost's native prediction contribution mechanism.

## Objectives
The main objectives of the project are:

1. To develop a machine learning system for predicting credit card default.
2. To implement a structured dataset preparation and preprocessing workflow.
3. To perform feature selection using the SelectKBest method.
4. To compare multiple classification algorithms and select an appropriate final model.
5. To evaluate the selected model using standard classification metrics.
6. To provide global feature importance and local prediction explanations.
7. To present model results through an interactive Business Intelligence dashboard.
8. To improve transparency and interpretability of machine learning predictions for business users.

## Key Features
### Dataset Management
- Dataset upload support for CSV and Excel files
- Dataset profiling
- Target column specification
- Header row configuration
- Dataset preparation
- Preprocessing analysis
- Application of preprocessing operations

### Machine Learning
- Classification-based credit default prediction
- Comparison of Logistic Regression, Random Forest, and XGBoost
- XGBoost selected as the final model
- 80:20 training and testing split
- Model performance evaluation

### Feature Selection
Feature selection is implemented using:

**SelectKBest with Mutual Information (`mutual_info_classif`)**

The original dataset contains 24 predictor variables after excluding the ID column. The feature-selection stage retains 23 predictor features.

### Explainable AI
The system provides:

- Global feature contribution analysis
- Local prediction explanations
- Increasing and decreasing factors for individual predictions
- Business-oriented interpretation of model outputs

Model contribution values are used to explain how individual features contribute to the model prediction. These explanations represent **model attribution and should not be interpreted as causal relationships**.

### Business Intelligence Dashboard
The React-based dashboard provides:

- Dataset overview
- Customer record selection
- Default probability
- Prediction result
- Model performance
- Local XAI
- Global XAI
- Business insights
- ML model and explainability status

## Dataset
The project uses the:
**UCI Default of Credit Card Clients Dataset**

### Dataset Details

| Property | Description |
|---|---|
| Dataset | Default of Credit Card Clients |
| Source | UCI Machine Learning Repository |
| Records | 30,000 |
| Original Columns | 25 |
| Target Column | `default payment next month` |
| Predictor Variables | 24 |
| Selected Features | 23 |
| Problem Type | Binary Classification |
| Default Class | `1` |
| Non-default Class | `0` |

The original dataset is stored in:
dataset/default of credit card clients.xls

The processed dataset is stored in:
processed/default_of_credit_card_clients_processed.csv

## Methodology
The implemented workflow follows the following sequence:

Dataset Upload
      ↓
Dataset Profiling
      ↓
Dataset Preparation
      ↓
Preprocessing Analysis
      ↓
Apply Preprocessing
      ↓
Feature Selection
      ↓
Candidate Model Comparison
      ↓
XGBoost Model Training
      ↓
Model Evaluation
      ↓
Prediction
      ↓
Global / Local XAI
      ↓
Business Insight

### 1. Dataset Upload
The system accepts the dataset through the web interface and allows configuration of the header row and target column.

### 2. Dataset Profiling
The uploaded dataset is profiled to understand:

* Number of records
* Number of columns
* Column information
* Target variable
* Data quality characteristics

### 3. Dataset Preparation
The dataset is prepared for the machine learning workflow. The ID column is excluded from the predictor variables.

### 4. Preprocessing
The preprocessing stage analyzes and applies the required data preparation operations.

### 5. Feature Selection
SelectKBest with mutual information is used for feature selection.

Method: SelectKBest
Score Function: mutual_info_classif
k: all

After excluding the ID column, 24 predictor variables are available. The feature-selection process retains 23 features.

### 6. Candidate Model Comparison
Three classification algorithms were evaluated:

* Logistic Regression
* Random Forest
* XGBoost

XGBoost provided the strongest overall performance for the selected dataset and evaluation setup and was therefore selected as the final model.

### 7. Model Training
The final XGBoost model was trained using an 80:20 train-test split:

Training Records: 24,000
Testing Records: 6,000

### 8. Model Evaluation
The final model was evaluated using:

* Accuracy
* Precision
* Recall
* F1-Score
* ROC-AUC

### 9. Prediction
The trained XGBoost model predicts whether a selected customer is likely to default.

The dashboard displays the predicted class and the estimated default probability.

### 10. Explainable AI
The system provides both:

**Global Explanation**
Identifies the features that contribute most strongly to model predictions across the dataset.

**Local Explanation**
Explains the contribution of individual features for a selected customer prediction.

Due to compatibility considerations between the installed XGBoost and SHAP versions, model-native XGBoost prediction contributions using `pred_contribs=True` are used for the explanation workflow.

## Model Performance
The three candidate classification models were evaluated using the same dataset and evaluation setup.

| Model               |   Accuracy |  Precision |     Recall |   F1-Score |    ROC-AUC |
| ------------------- | ---------: | ---------: | ---------: | ---------: | ---------: |
| Logistic Regression |     80.78% |     68.83% |     23.96% |     35.55% |     70.76% |
| Random Forest       |     81.43% |     65.06% |     34.66% |     45.23% |     75.66% |
| **XGBoost**         | **81.87%** | **66.53%** | **36.25%** | **46.93%** | **77.84%** |

### Final Model
**XGBoost**

The final model achieved:

* **Accuracy:** 81.87%
* **Precision:** 66.53%
* **Recall:** 36.25%
* **F1-Score:** 46.93%
* **ROC-AUC:** 77.84%

## Explainable AI Results
### Global Feature Contributions
The major features identified through global feature contribution analysis include:

| Rank | Feature   | Mean Absolute Contribution |
| ---: | --------- | -------------------------: |
|    1 | PAY_0     |                   0.504984 |
|    2 | LIMIT_BAL |                   0.208830 |
|    3 | BILL_AMT1 |                   0.132401 |
|    4 | PAY_AMT2  |                   0.112601 |
|    5 | PAY_2     |                   0.100909 |

These results indicate that recent repayment status and credit-related variables have strong influence on the model's predictions.

### Local Explanation
For an example customer record, the system provides:

* Predicted class
* Default probability
* Features contributing toward a higher predicted probability
* Features contributing toward a lower predicted probability

The dashboard presents these contributions using business-friendly feature descriptions along with the original dataset feature names.

## System Architecture

The project follows a full-stack architecture consisting of:

                    React Frontend
                         │
                         │ HTTP / REST API
                         ▼
                   FastAPI Backend
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
     Dataset          Machine        Explainable
    Processing        Learning       AI / XAI
          │              │              │
          ▼              ▼              ▼
      Dataset          XGBoost       Feature
     Preparation        Model       Contributions

### Frontend
The frontend provides an interactive dashboard for dataset management, prediction, model evaluation, and explainability.

**Technology:**
* React
* Vite
* JavaScript
* CSS

### Backend
The backend provides REST APIs for dataset processing, authentication, prediction, model evaluation, and explainability.

**Technology:**
* Python
* FastAPI
* SQLite
* Scikit-learn
* XGBoost
* SHAP-compatible model contribution analysis

## Technology Stack
### Programming Languages
* Python
* JavaScript

### Frontend
* React
* Vite
* HTML
* CSS

### Backend
* FastAPI
* Uvicorn

### Machine Learning
* Scikit-learn
* XGBoost

### Explainable AI
* SHAP
* XGBoost native prediction contributions

### Database and Authentication
* SQLite
* JWT-based authentication
* Password hashing

### Data Processing
* Pandas
* NumPy

### Development Tools
* Visual Studio Code
* Git
* GitHub

## Project Structure

Credit-Default-Prediction/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── dataset.py
│   │   │   ├── prediction.py
│   │   │   └── xai.py
│   │   │
│   │   ├── config/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── xai/
│   │
│   ├── processed/
│   │   └── default of credit card clients_processed.csv
│   └── requirements.txt
│
├── dataset/
│   └── default of credit card clients.xls
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── processed/
│   └── default_of_credit_card_clients_processed.csv
│
├── trained_models/
│   └── explainbi_xgboost_model.joblib
│
├── notebooks/
├── reports/
├── .gitignore
└── README.md

## Installation and Setup
### Prerequisites
Make sure the following software is installed:
* Python 3.10 or compatible Python environment
* Node.js
* npm
* Git

### Clone the Repository
git clone https://github.com/<your-github-username>/Credit-Default-Prediction.git
cd Credit-Default-Prediction

## Backend Setup
Navigate to the backend directory:
cd backend

Create and activate a Python virtual environment if required.

### Windows
python -m venv .venv
.venv\Scripts\activate

Install the backend dependencies:
pip install -r requirements.txt

Start the FastAPI server:
uvicorn app.main:app --reload

The backend will be available at:
http://127.0.0.1:8000

FastAPI interactive API documentation:
http://127.0.0.1:8000/docs

## Frontend Setup
Open another terminal and navigate to the frontend directory:
cd frontend

Install the required packages:
npm install

Start the Vite development server:
npm run dev

The frontend will normally be available at:
http://localhost:5173

## Application Workflow
After starting the application, the general workflow is:

1. Register a user account.
2. Log in to the application.
3. Upload and profile the dataset.
4. Prepare the dataset.
5. Analyze preprocessing requirements.
6. Apply preprocessing.
7. View dataset information and customer records.
8. Select a customer record.
9. Generate a credit default prediction.
10. View the predicted default probability.
11. Examine local feature contributions.
12. Review global feature importance.
13. Interpret the generated business insight.
14. Review model performance.

## API Modules
The FastAPI backend provides APIs for the following major functions:

### Authentication
POST /auth/register
POST /auth/login
GET  /auth/me

### Dataset Management
POST /datasets/upload
GET  /datasets/profile
POST /datasets/prepare
POST /datasets/preprocess
POST /datasets/preprocess/apply
GET  /datasets/rows

### Prediction
POST /prediction
GET  /prediction/performance

### Explainable AI
GET /xai/global
GET /xai/local

## Security
The application includes authentication functionality using:

* User registration
* User login
* Password hashing
* JWT-based authentication
* Authenticated user verification

Sensitive configuration files and local databases are excluded from version control through `.gitignore`.

## Explainability and Business Interpretation
The purpose of the explainability component is to make machine learning predictions easier to understand.

The system provides two levels of explanation:

### Global XAI
Global analysis identifies the features that have the greatest overall contribution to the model predictions.

### Local XAI
Local analysis explains the contribution of individual features for a specific customer prediction.

The explanations are intended to improve model transparency and support business interpretation. Feature contribution values describe how the trained model uses the available information and **should not be interpreted as evidence of causal relationships**.

## Project Reference
The project methodology is based on the framework presented in:

> Chitnis, A. and Tewari, et al. (2024), *Operationalizing Explainable AI in Business Intelligence: A Blueprint for Transparent Enterprise Analytics.*

The framework was adapted and implemented for the credit default prediction problem using the UCI Default of Credit Card Clients dataset.

## Academic Project Information
**Project Title:** Credit Default Prediction

**Program:** M.Sc. Data Analytics

**Institution:** Sri Ramakrishna College of Arts & Science for Women

**Academic Year:** 2026

**Project Type:** Semester / Mini Project

## Future Enhancements
Potential future enhancements include:

* Support for additional financial datasets
* Further model and hyperparameter optimization
* Extended explainability techniques
* Additional visualization options
* More comprehensive business-oriented analytics
* Improved support for different dataset structures

## Author
**Haridhra S**

M.Sc. Data Analytics

Sri Ramakrishna College of Arts & Science for Women

## License
This project is developed as an academic project. No specific open-source license has been applied to this repository.