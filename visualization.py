'''
A bulk of the visualization code was taken from Gemini's code. A bit sloppy, so I shall clean it up later.
'''
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Tuple
import pandas as pd


def get_feature_importance(model, feature_cols, X_sample):
    """
    Get feature importance for a specific prediction kinda like SHAP-values
    Returns top features that contribute most to the prediction
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        importances = np.abs(X_sample.values[0])
        importances = importances / importances.sum() if importances.sum() > 0 else importances
    
    feature_importance = dict(zip(feature_cols, importances))
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_features


def get_top_strengths(model, feature_cols, X_sample, top_n=3):
    """
    Extract top N strengths (most impactful features) for a roster
    Returns list of (feature_name, importance) tuples
    """
    feature_importance = get_feature_importance(model, feature_cols, X_sample)
    
    # Get top N features
    top_features = feature_importance[:top_n]
    
    strengths = []
    for feat_name, importance in top_features:
        display_name = feat_name.replace("TEAM_", "").replace("_", " ").title()
        display_name = display_name.replace("Avg ", "").replace("Total ", "").replace("Top2 ", "Top 2 ")
        display_name = display_name.replace("P36", "Per 36 Min")
        strengths.append((display_name, importance))
    
    return strengths


def visualize_roster_comparison(roster1_name: str, roster1_wins: float, 
                                roster1_strengths: List[Tuple[str, float]],
                                roster2_name: str, roster2_wins: float,
                                roster2_strengths: List[Tuple[str, float]],
                                save_path: str = "roster_comparison.png"):
    """
    Create a clean, professional visualization comparing two rosters
    
    Args:
        roster1_name: Name of first roster
        roster1_wins: Predicted wins for first roster
        roster1_strengths: List of (strength_name, importance) tuples
        roster2_name: Name of second roster
        roster2_wins: Predicted wins for second roster
        roster2_strengths: List of (strength_name, importance) tuples
        save_path: Path to save the visualization
    """
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except:
        try:
            plt.style.use('seaborn-darkgrid')
        except:
            plt.style.use('default')
    
    fig = plt.figure(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3, 
                          left=0.08, right=0.95, top=0.92, bottom=0.08)
    
    # Color scheme - professional NBA colors
    color1 = '#1f77b4'  # Blue
    color2 = '#ff7f0e'  # Orange
    win_color1 = '#2ecc71' if roster1_wins > roster2_wins else '#95a5a6'
    win_color2 = '#2ecc71' if roster2_wins > roster1_wins else '#95a5a6'
    
    # ========== Plot 1: Predicted Wins Comparison ==========
    ax1 = fig.add_subplot(gs[0, :])
    
    rosters = [roster1_name, roster2_name]
    wins = [roster1_wins, roster2_wins]
    colors = [win_color1, win_color2]
    
    bars = ax1.bar(rosters, wins, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    # Add value labels on bars
    for i, (bar, win) in enumerate(zip(bars, wins)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{win:.1f} wins',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add 82-game reference line
    ax1.axhline(y=41, color='gray', linestyle='--', alpha=0.5, linewidth=1, label='.500 (41 wins)')
    ax1.axhline(y=50, color='green', linestyle='--', alpha=0.5, linewidth=1, label='Playoff Threshold (~50 wins)')
    
    ax1.set_ylabel('Predicted Wins (out of 82)', fontsize=12, fontweight='bold')
    ax1.set_title('Predicted Season Win Totals', fontsize=16, fontweight='bold', pad=5) #THIS ONE
    ax1.set_ylim(0, max(82, max(wins) * 1.2))
    ax1.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # ========== Plot 2: Roster 1 Strengths ==========
    ax2 = fig.add_subplot(gs[1, 0])
    
    strength_names = [s[0] for s in roster1_strengths]
    strength_values = [s[1] for s in roster1_strengths]
    
    # Normalize for better visualization
    max_val = max(strength_values) if strength_values else 1
    strength_values_norm = [v / max_val * 100 for v in strength_values]
    
    bars2 = ax2.barh(range(len(strength_names)), strength_values_norm, 
                     color=color1, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax2.set_yticks(range(len(strength_names)))
    ax2.set_yticklabels(strength_names, fontsize=10)
    ax2.set_xlabel('Relative Impact (%)', fontsize=10, fontweight='bold')
    ax2.set_title(f'{roster1_name}\nTop Strengths', fontsize=12, fontweight='bold')
    ax2.set_xlim(0, 110)
    ax2.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, strength_values_norm)):
        width = bar.get_width()
        ax2.text(width + 2, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%',
                ha='left', va='center', fontsize=9)
    
    # ========== Plot 3: Roster 2 Strengths ==========
    ax3 = fig.add_subplot(gs[1, 1])
    
    strength_names2 = [s[0] for s in roster2_strengths]
    strength_values2 = [s[1] for s in roster2_strengths]
    
    # Normalize for better visualization
    max_val2 = max(strength_values2) if strength_values2 else 1
    strength_values_norm2 = [v / max_val2 * 100 for v in strength_values2]
    
    bars3 = ax3.barh(range(len(strength_names2)), strength_values_norm2,
                     color=color2, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    ax3.set_yticks(range(len(strength_names2)))
    ax3.set_yticklabels(strength_names2, fontsize=10)
    ax3.set_xlabel('Relative Impact (%)', fontsize=10, fontweight='bold')
    ax3.set_title(f'{roster2_name}\nTop Strengths', fontsize=12, fontweight='bold')
    ax3.set_xlim(0, 110)
    ax3.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars3, strength_values_norm2)):
        width = bar.get_width()
        ax3.text(width + 2, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%',
                ha='left', va='center', fontsize=9)
    
    # Add overall title
    fig.suptitle('NBA Roster Comparison Analysis', 
                 fontsize=18, fontweight='bold', y=0.98)    #THIS ONE
    
    # Save figure
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nVisualization saved to: {save_path}")
    
    # Display
    plt.show()

    # fig.savefig("figure.png")
    # plt.savefig("plot.png")
    
    return fig

