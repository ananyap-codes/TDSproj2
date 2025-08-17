"""
Chart generator for creating data visualizations
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import base64
import io
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('default')
sns.set_palette("husl")

class ChartGenerator:
    def __init__(self):
        self.figure_size = (10, 6)
        self.dpi = 100
        self.max_size_bytes = 100000  # 100KB limit as per evaluation

    def generate_chart(self, data_files: Dict[str, Any], chart_config: Dict[str, Any]) -> Optional[str]:
        """
        Generate a chart based on configuration and return as base64 encoded PNG
        """
        try:
            chart_type = chart_config.get('type', 'scatter')
            data_source = chart_config.get('data_source')

            if not data_source or data_source not in data_files:
                return None

            data = data_files[data_source]
            if not isinstance(data, pd.DataFrame):
                return None

            # Create the chart based on type
            if chart_type == 'scatter':
                fig = self._create_scatter_plot(data, chart_config)
            elif chart_type == 'bar':
                fig = self._create_bar_chart(data, chart_config)
            elif chart_type == 'line':
                fig = self._create_line_plot(data, chart_config)
            elif chart_type == 'histogram':
                fig = self._create_histogram(data, chart_config)
            elif chart_type == 'heatmap':
                fig = self._create_heatmap(data, chart_config)
            elif chart_type == 'box':
                fig = self._create_box_plot(data, chart_config)
            else:
                # Default to scatter plot
                fig = self._create_scatter_plot(data, chart_config)

            if fig is None:
                return None

            # Convert to base64
            base64_image = self._fig_to_base64(fig)
            plt.close(fig)

            return base64_image

        except Exception as e:
            print(f"Chart generation error: {str(e)}")
            return None

    def _create_scatter_plot(self, data: pd.DataFrame, config: Dict[str, Any]) -> Optional[plt.Figure]:
        """Create a scatter plot with optional regression line"""
        try:
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            title = config.get('title', 'Scatter Plot')

            if not x_col or not y_col or x_col not in data.columns or y_col not in data.columns:
                return None

            # Filter numeric data
            plot_data = data[[x_col, y_col]].dropna()
            if len(plot_data) == 0:
                return None

            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

            # Create scatter plot
            ax.scatter(plot_data[x_col], plot_data[y_col], alpha=0.6)

            # Add regression line if requested
            if config.get('add_regression', True):
                try:
                    z = np.polyfit(plot_data[x_col], plot_data[y_col], 1)
                    p = np.poly1d(z)
                    ax.plot(plot_data[x_col], p(plot_data[x_col]), "r--", alpha=0.8, linewidth=2)
                except:
                    pass

            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(title)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Scatter plot error: {str(e)}")
            return None

    def _create_bar_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> Optional[plt.Figure]:
        """Create a bar chart"""
        try:
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            title = config.get('title', 'Bar Chart')

            if not x_col or not y_col or x_col not in data.columns or y_col not in data.columns:
                return None

            # Aggregate data if needed
            if data[x_col].dtype == 'object':
                plot_data = data.groupby(x_col)[y_col].mean().reset_index()
            else:
                plot_data = data[[x_col, y_col]].dropna()

            if len(plot_data) == 0:
                return None

            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

            ax.bar(plot_data[x_col], plot_data[y_col])
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(title)
            ax.grid(True, alpha=0.3, axis='y')

            # Rotate x labels if needed
            if len(str(plot_data[x_col].iloc[0])) > 10:
                plt.xticks(rotation=45, ha='right')

            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Bar chart error: {str(e)}")
            return None

    def _create_line_plot(self, data: pd.DataFrame, config: Dict[str, Any]) -> Optional[plt.Figure]:
        """Create a line plot"""
        try:
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            title = config.get('title', 'Line Plot')

            if not x_col or not y_col or x_col not in data.columns or y_col not in data.columns:
                return None

            plot_data = data[[x_col, y_col]].dropna().sort_values(x_col)
            if len(plot_data) == 0:
                return None

            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

            ax.plot(plot_data[x_col], plot_data[y_col], marker='o', linewidth=2, markersize=4)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(title)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Line plot error: {str(e)}")
            return None

    def _create_histogram(self, data: pd.DataFrame, config: Dict[str, Any]) -> Optional[plt.Figure]:
        """Create a histogram"""
        try:
            x_col = config.get('x_column')
            title = config.get('title', 'Histogram')
            bins = config.get('bins', 30)

            if not x_col or x_col not in data.columns:
                return None

            plot_data = data[x_col].dropna()
            if len(plot_data) == 0:
                return None

            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

            ax.hist(plot_data, bins=bins, alpha=0.7, edgecolor='black', linewidth=0.5)
            ax.set_xlabel(x_col)
            ax.set_ylabel('Frequency')
            ax.set_title(title)
            ax.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Histogram error: {str(e)}")
            return None

    def _create_heatmap(self, data: pd.DataFrame, config: Dict[str, Any]) -> Optional[plt.Figure]:
        """Create a correlation heatmap"""
        try:
            title = config.get('title', 'Correlation Heatmap')

            # Get numeric columns only
            numeric_data = data.select_dtypes(include=[np.number])
            if numeric_data.shape[1] < 2:
                return None

            corr_matrix = numeric_data.corr()

            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, ax=ax, cbar_kws={'shrink': 0.8})
            ax.set_title(title)

            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Heatmap error: {str(e)}")
            return None

    def _create_box_plot(self, data: pd.DataFrame, config: Dict[str, Any]) -> Optional[plt.Figure]:
        """Create a box plot"""
        try:
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            title = config.get('title', 'Box Plot')

            if not y_col or y_col not in data.columns:
                return None

            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

            if x_col and x_col in data.columns:
                # Grouped box plot
                data.boxplot(column=y_col, by=x_col, ax=ax)
                ax.set_xlabel(x_col)
            else:
                # Single box plot
                ax.boxplot(data[y_col].dropna())
                ax.set_xlabel('Data')

            ax.set_ylabel(y_col)
            ax.set_title(title)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            return fig

        except Exception as e:
            print(f"Box plot error: {str(e)}")
            return None

    def _fig_to_base64(self, fig: plt.Figure) -> str:
        """Convert matplotlib figure to base64 encoded PNG"""
        buffer = io.BytesIO()

        # Save with optimization to keep size under limit
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', optimize=True)
        buffer.seek(0)

        # Check size and reduce quality if needed
        img_data = buffer.getvalue()
        if len(img_data) > self.max_size_bytes:
            buffer.close()
            buffer = io.BytesIO()
            # Reduce DPI and save again
            fig.savefig(buffer, format='png', dpi=50, bbox_inches='tight',
                       facecolor='white', edgecolor='none', optimize=True)
            buffer.seek(0)
            img_data = buffer.getvalue()

        base64_str = base64.b64encode(img_data).decode('utf-8')
        buffer.close()

        return f"data:image/png;base64,{base64_str}"

    def create_multi_chart(self, data: pd.DataFrame, chart_configs: list) -> Optional[str]:
        """Create multiple charts in subplots"""
        try:
            num_charts = len(chart_configs)
            if num_charts == 0:
                return None

            # Determine subplot layout
            if num_charts == 1:
                rows, cols = 1, 1
            elif num_charts == 2:
                rows, cols = 1, 2
            elif num_charts <= 4:
                rows, cols = 2, 2
            else:
                rows, cols = 3, 2

            fig, axes = plt.subplots(rows, cols, figsize=(12, 8), dpi=self.dpi)
            if num_charts == 1:
                axes = [axes]
            elif rows == 1 or cols == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()

            for i, config in enumerate(chart_configs[:len(axes)]):
                self._create_subplot(data, config, axes[i])

            # Hide unused subplots
            for i in range(num_charts, len(axes)):
                axes[i].set_visible(False)

            plt.tight_layout()
            base64_image = self._fig_to_base64(fig)
            plt.close(fig)

            return base64_image

        except Exception as e:
            print(f"Multi-chart error: {str(e)}")
            return None

    def _create_subplot(self, data: pd.DataFrame, config: Dict[str, Any], ax):
        """Create a subplot on given axes"""
        chart_type = config.get('type', 'scatter')
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        title = config.get('title', f'{chart_type.title()} Plot')

        try:
            if chart_type == 'scatter' and x_col and y_col:
                plot_data = data[[x_col, y_col]].dropna()
                ax.scatter(plot_data[x_col], plot_data[y_col], alpha=0.6)
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == 'bar' and x_col and y_col:
                if data[x_col].dtype == 'object':
                    plot_data = data.groupby(x_col)[y_col].mean()
                    ax.bar(range(len(plot_data)), plot_data.values)
                    ax.set_xticks(range(len(plot_data)))
                    ax.set_xticklabels(plot_data.index, rotation=45)
                else:
                    plot_data = data[[x_col, y_col]].dropna()
                    ax.bar(plot_data[x_col], plot_data[y_col])
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == 'histogram' and x_col:
                plot_data = data[x_col].dropna()
                ax.hist(plot_data, bins=20, alpha=0.7)
                ax.set_xlabel(x_col)
                ax.set_ylabel('Frequency')

            ax.set_title(title, fontsize=10)
            ax.grid(True, alpha=0.3)

        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center', transform=ax.transAxes)
