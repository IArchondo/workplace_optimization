import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class OutputVisualizer:
    def __init__(self, model_input, model_output):
        self.input = model_input
        self.output = model_output

    def preprocess_output(self, model_input, model_output):
        return pd.DataFrame(
            [
                pd.Series(
                    {
                        "seat": assignment[0],
                        "person": assignment[1],
                        "team": model_input.person_team_dict[assignment[1]],
                        "x_coor": model_input.seat_to_coordinates[assignment[0]][0],
                        "y_coor": model_input.seat_to_coordinates[assignment[0]][1],
                    }
                )
                for assignment in model_output.assignments
            ]
        )

    def plot_solution(self, plot_df):
        """Plot workplace solution."""
        plt.figure(figsize=(12, 8))
        sns.scatterplot(
            x=plot_df["x_coor"],
            y=plot_df["y_coor"],
            hue=plot_df["team"],
            palette="deep",
            s=150,
        )
        plt.xlim((min(plot_df["x_coor"]) - 1.5, max(plot_df["x_coor"]) + 1.5))
        plt.ylim((min(plot_df["y_coor"]) - 1.5, max(plot_df["y_coor"]) + 1.5))
        plt.xlabel("")
        plt.ylabel("")
        plt.title(
            "Workplace Seating Optimal Solution\n",
            fontsize=25,
            fontweight="bold",
            fontname="Trebuchet MS",
            color="#001F5B",
        )
        for i in range(plot_df.shape[0]):
            plt.text(
                x=plot_df["x_coor"][i] + 0.3,
                y=plot_df["y_coor"][i] + 0.3,
                s=plot_df["person"][i],
                fontdict=dict(color="white", size=10),
                bbox=dict(facecolor="#001F5B", alpha=0.5),
            )

        ax = plt.gca()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)

    def visualize_output(self):
        """Visualize model solution in a plot."""
        plot_df = self.preprocess_output(self.input, self.output)
        self.plot_solution(plot_df)
