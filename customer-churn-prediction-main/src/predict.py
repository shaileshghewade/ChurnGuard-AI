
"""
Inference and Explainability Module for Customer Churn Prediction System
Author: ChurnGuard AI Team
Description:
    Loads persisted model and preprocessing pipeline, runs inference,
    categorizes risk level (LOW, MEDIUM, HIGH), and produces interpretable
    feature-level risk drivers and personalized retention recommendations.
"""

import os
import joblib
import numpy as np
import pandas as pd

USD_TO_INR = 83.0


class ChurnPredictor:
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            models_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "models"
            )

        self.models_dir = models_dir
        self.model_path = os.path.join(models_dir, "best_model.pkl")
        self.pipeline_path = os.path.join(
            models_dir,
            "preprocessing_pipeline.pkl"
        )

        if (
            not os.path.exists(self.model_path)
            or not os.path.exists(self.pipeline_path)
        ):
            raise FileNotFoundError(
                f"Trained model or pipeline not found in {models_dir}"
            )

        self.model = joblib.load(self.model_path)
        self.pipeline = joblib.load(self.pipeline_path)

        # Extract feature names from the fitted preprocessing pipeline
        cat_encoder = (
            self.pipeline.named_transformers_["cat"]
            .named_steps["onehot"]
        )

        from preprocessing import CATEGORICAL_COLS, NUMERICAL_COLS

        self.feature_names = (
            NUMERICAL_COLS
            + cat_encoder.get_feature_names_out(
                CATEGORICAL_COLS
            ).tolist()
        )

    def predict_single(self, customer_dict: dict) -> dict:
        """
        Takes a raw customer dictionary, validates the input,
        runs inference, and returns a comprehensive risk assessment.
        """

        # ---------------------------------------------------------
        # 1. Validate required customer fields
        # ---------------------------------------------------------
        required_fields = [
            "gender",
            "SeniorCitizen",
            "Partner",
            "Dependents",
            "tenure",
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaperlessBilling",
            "PaymentMethod",
            "MonthlyCharges",
            "TotalCharges",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in customer_dict
        ]

        if missing_fields:
            raise ValueError(
                "Missing required customer fields: "
                + ", ".join(missing_fields)
            )

        df = pd.DataFrame([customer_dict])

        # ---------------------------------------------------------
        # 2. Validate numerical fields
        # ---------------------------------------------------------
        numerical_fields = [
            "tenure",
            "MonthlyCharges",
            "TotalCharges",
            "SeniorCitizen",
        ]

        for field in numerical_fields:
            df[field] = pd.to_numeric(
                df[field],
                errors="coerce"
            )

            if df[field].isna().any():
                raise ValueError(
                    f"Invalid value for {field}. "
                    "Please enter a valid number."
                )

            if not np.isfinite(df[field].iloc[0]):
                raise ValueError(
                    f"{field} must be a finite number."
                )

        # ---------------------------------------------------------
        # 3. Validate allowed numerical ranges
        # ---------------------------------------------------------
        tenure = float(df["tenure"].iloc[0])
        monthly_charges = float(df["MonthlyCharges"].iloc[0])
        total_charges = float(df["TotalCharges"].iloc[0])
        senior_citizen = float(df["SeniorCitizen"].iloc[0])

        if not 0 <= tenure <= 72:
            raise ValueError(
                "Tenure must be between 0 and 72 months."
            )

        if monthly_charges < 0:
            raise ValueError(
                "Monthly charges cannot be negative."
            )

        if total_charges < 0:
            raise ValueError(
                "Total charges cannot be negative."
            )

        if senior_citizen not in [0, 1]:
            raise ValueError(
                "SeniorCitizen must be either 0 or 1."
            )

        df["SeniorCitizen"] = df["SeniorCitizen"].astype(int)

        # ---------------------------------------------------------
        # 4. Transform input through the fitted preprocessing pipeline
        # ---------------------------------------------------------
        X_transformed = self.pipeline.transform(df)

        X_df = pd.DataFrame(
            X_transformed,
            columns=self.feature_names
        )

        # ---------------------------------------------------------
        # 5. Predict churn probability
        # ---------------------------------------------------------
        # Initialize probability values before prediction.
        # This prevents an uninitialized-variable error.
        churn_prob = 0.0
        churn_prob_pct = 0.0
        stay_prob_pct = 100.0

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_df)[0]

            classes = list(self.model.classes_)

            if 1 not in classes:
                raise ValueError(
                    "The trained model does not contain churn class 1."
                )

            churn_class_index = classes.index(1)

            churn_prob = float(
                probs[churn_class_index]
            )

        else:
            pred = int(
                self.model.predict(X_df)[0]
            )

            churn_prob = 1.0 if pred == 1 else 0.0

        # Always calculate percentages after churn_prob is assigned.
        churn_prob_pct = round(
            churn_prob * 100,
            1
        )

        stay_prob_pct = round(
            (1.0 - churn_prob) * 100,
            1
        )

        # ---------------------------------------------------------
        # 6. Categorize churn risk
        # ---------------------------------------------------------
        if churn_prob_pct < 35.0:
            risk_level = "LOW RISK"
            prediction_label = "LIKELY TO STAY"
            risk_color = "#10B981"
            risk_badge = "success"

        elif churn_prob_pct <= 65.0:
            risk_level = "MEDIUM RISK"
            prediction_label = "MODERATE RISK / WATCHLIST"
            risk_color = "#F59E0B"
            risk_badge = "warning"

        else:
            risk_level = "HIGH RISK"
            prediction_label = "LIKELY TO CHURN"
            risk_color = "#EF4444"
            risk_badge = "danger"

        # ---------------------------------------------------------
        # 7. Analyze customer factors
        # ---------------------------------------------------------
        risk_factors = []
        positive_factors = []
        recommendations = []

        # Contract analysis
        contract = str(
            customer_dict.get("Contract", "")
        )

        if contract == "Month-to-month":
            risk_factors.append({
                "factor": "Month-to-Month Contract",
                "impact": "High Risk Driver (+38% Churn Likelihood)",
                "detail": (
                    "Customer has zero contractual lock-in and can "
                    "cancel without penalty anytime."
                ),
            })

            recommendations.append(
                "Offer a 15% discount incentive to upgrade to a "
                "1-year or 2-year commitment plan."
            )

        elif contract in ["One year", "Two year"]:
            positive_factors.append({
                "factor": f"{contract} Contract",
                "impact": "Strong Retention Anchor",
                "detail": (
                    "Committed agreement significantly reduces "
                    "immediate switching behavior."
                ),
            })

        # Tenure analysis
        if tenure < 12:
            risk_factors.append({
                "factor": f"Low Tenure ({int(tenure)} months)",
                "impact": "Early Lifecycle Vulnerability",
                "detail": (
                    "Customers in their first 12 months experience "
                    "the highest churn rate (~47%)."
                ),
            })

            recommendations.append(
                "Enroll in new-customer onboarding and schedule "
                "a 30-day proactive satisfaction check."
            )

        elif tenure >= 24:
            positive_factors.append({
                "factor": (
                    f"Established Loyalty ({int(tenure)} months tenure)"
                ),
                "impact": "High Brand Affinity",
                "detail": (
                    "Long-term relationships indicate deep service "
                    "integration and high satisfaction."
                ),
            })

        # Internet service and technical support analysis
        internet = str(
            customer_dict.get("InternetService", "")
        )

        tech_support = str(
            customer_dict.get("TechSupport", "")
        )

        online_sec = str(
            customer_dict.get("OnlineSecurity", "")
        )

        if internet == "Fiber optic":
            if tech_support == "No" or online_sec == "No":
                risk_factors.append({
                    "factor": (
                        "Fiber Optic without Technical Support / Security"
                    ),
                    "impact": (
                        "Frequent Service Dissatisfaction Risk"
                    ),
                    "detail": (
                        "Fiber users pay premium rates; without "
                        "security/support, technical glitches can "
                        "contribute to dissatisfaction."
                    ),
                })

                recommendations.append(
                    "Provide a complimentary 6-month Cyber Security "
                    "& Priority Tech Support add-on."
                )

        if tech_support == "Yes":
            positive_factors.append({
                "factor": "Active Tech Support Package",
                "impact": "High Operational Satisfaction",
                "detail": (
                    "Customers receiving rapid assistance are "
                    "associated with lower churn."
                ),
            })

        if online_sec == "Yes":
            positive_factors.append({
                "factor": "Online Security Enabled",
                "impact": "Protective Value Anchor",
                "detail": (
                    "Digital safety features can build stickiness "
                    "and perceived utility."
                ),
            })

        # Payment method analysis
        pay_method = str(
            customer_dict.get("PaymentMethod", "")
        )

        if pay_method == "Electronic check":
            risk_factors.append({
                "factor": "Electronic Check Billing",
                "impact": "High Churn Association (~45% Churn Rate)",
                "detail": (
                    "Manual payment friction can correlate with "
                    "billing disputes and active price shopping."
                ),
            })

            recommendations.append(
                "Promote Auto-pay enrollment via Credit Card or "
                f"Bank Transfer with a ₹{5 * USD_TO_INR:,.0f} monthly bill credit."
            )

        elif "automatic" in pay_method.lower():
            positive_factors.append({
                "factor": f"Automated Billing ({pay_method})",
                "impact": "Frictionless Payment Stream",
                "detail": (
                    "Autopay reduces payment friction and "
                    "unintended non-payment drops."
                ),
            })

        # Pricing burden analysis
        if monthly_charges > 80.0:
            risk_factors.append({
                "factor": (
                    f"High Monthly Charges (₹{monthly_charges * USD_TO_INR:,.2f}/mo)"
                ),
                "impact": "Premium Price Sensitivity",
                "detail": (
                    f"Bills above ₹{80 * USD_TO_INR:,.0f}/month fall into a high pricing "
                    "tier where competitors may target customers."
                ),
            })

            recommendations.append(
                "Conduct a plan audit to bundle entertainment and "
                "streaming services into a cost-optimized package."
            )

        elif monthly_charges < 40.0:
            positive_factors.append({
                "factor": (f"Economical Monthly Bill (₹{monthly_charges * USD_TO_INR:,.2f}/mo)"
                    
                ),
                "impact": "Low Budget Friction",
                "detail": (
                    "Affordable baseline service can reduce "
                    "motivation to switch to competing carriers."
                ),
            })

        # ---------------------------------------------------------
        # 8. Default recommendations by risk category
        # ---------------------------------------------------------
        if risk_level == "HIGH RISK":
            recommendations.append(
                "Dispatch high-priority retention ticket to "
                "Senior Account Management team."
            )

            recommendations.append(
                "Prepare bespoke contract extension package "
                "with guaranteed price freeze."
            )

        elif risk_level == "MEDIUM RISK":
            recommendations.append(
                "Trigger targeted in-app loyalty perks "
                "and engagement surveys."
            )

            recommendations.append(
                "Highlight underutilized features "
                "(backup, cloud storage) to increase perceived value."
            )

        else:
            recommendations.append(
                "Maintain standard service quality and invite "
                "customer to join customer advocacy/referral program."
            )

            recommendations.append(
                "Offer seasonal upgrade previews and "
                "milestone anniversary gifts."
            )

        # ---------------------------------------------------------
        # 9. Return prediction result
        # ---------------------------------------------------------
        return {
            "prediction": int(churn_prob > 0.5),
            "prediction_label": prediction_label,
            "churn_probability": churn_prob,
            "churn_probability_pct": churn_prob_pct,
            "stay_probability_pct": stay_prob_pct,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_badge": risk_badge,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "retention_recommendations": recommendations,
            "customer_summary": {
                "tenure_months": int(tenure),
                "contract": contract,
                "monthly_charges": monthly_charges,
                "internet_service": internet,
                "payment_method": pay_method,
            },
        }


# -------------------------------------------------------------
# Standalone test
# -------------------------------------------------------------
if __name__ == "__main__":
    predictor = ChurnPredictor()

    high_risk_customer = {
        "gender": "Male",
        "SeniorCitizen": 1,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 2,
        "PhoneService": "Yes",
        "MultipleLines": "Yes",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 95.5,
        "TotalCharges": 191.0,
    }

    result = predictor.predict_single(
        high_risk_customer
    )

    print("--- Test High Risk Customer ---")

    print(
        f"Prediction: {result['prediction_label']}"
    )

    print(
        f"Probability: {result['churn_probability_pct']}% "
        f"| Risk Level: {result['risk_level']}"
    )

    print(
        "Top Risk Factors:",
        [
            factor["factor"]
            for factor in result["risk_factors"]
        ]
    )

    print(
        "Recommendations:",
        result["retention_recommendations"][:2]
    )
