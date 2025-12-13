import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def generate_assets():
    try:
        # Load data
        df = pd.read_csv("digital_marketing_dataset.csv")
        
        # 1. Campaign Performance Overview
        metrics = df.groupby("campaign_segment").agg(
            visit_rate=("visit", "mean"),
            conversion_rate=("conversion", "mean"),
            avg_spend=("spend", "mean")
        ).reset_index()

        # Create a subplot figure
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        sns.barplot(data=metrics, x="campaign_segment", y="visit_rate", ax=axes[0], palette="viridis")
        axes[0].set_title("Visit Rate by Campaign")
        axes[0].set_ylabel("Visit Rate")

        sns.barplot(data=metrics, x="campaign_segment", y="conversion_rate", ax=axes[1], palette="coolwarm")
        axes[1].set_title("Conversion Rate by Campaign")
        axes[1].set_ylabel("Conversion Rate")

        sns.barplot(data=metrics, x="campaign_segment", y="avg_spend", ax=axes[2], palette="magma")
        axes[2].set_title("Average Spend by Campaign")
        axes[2].set_ylabel("Average Spend ($)")

        plt.tight_layout()
        plt.savefig("assets/campaign_performance.png")
        print("Generated campaign_performance.png")

        # 2. Conversion by Spend Group (Profiling)
        # Dynamic binning
        df['spend_group'] = pd.qcut(df['history_spend'], q=3, labels=['Low Value', 'Medium Value', 'High Value'])
        spend_metrics = df.groupby(['campaign_segment', 'spend_group']).agg(
            conversion_rate=('conversion', 'mean')
        ).reset_index()

        plt.figure(figsize=(10, 6))
        sns.barplot(data=spend_metrics, x='spend_group', y='conversion_rate', hue='campaign_segment', palette='coolwarm')
        plt.title("Conversion Rate by Historical Spend Tier")
        plt.ylabel("Conversion Rate")
        plt.xlabel("Customer Value Tier")
        plt.legend(title="Campaign")
        plt.tight_layout()
        plt.savefig("assets/spend_profile.png")
        print("Generated spend_profile.png")

    except Exception as e:
        print(f"Error generating assets: {e}")

if __name__ == "__main__":
    if not os.path.exists("assets"):
        os.makedirs("assets")
    generate_assets()
