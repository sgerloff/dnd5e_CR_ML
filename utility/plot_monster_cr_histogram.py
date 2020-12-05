import pandas as pd
import matplotlib.pyplot as plt


def get_sorted_cr_series(list_of_monsters):
    cr_list = [eval(monster["cr"]) for monster in list_of_monsters]
    return pd.Series(cr_list).value_counts().sort_index()

def plot_monster_cr_histogram(list_of_monsters, output_str):
    cr_series = get_sorted_cr_series(list_of_monsters)
    plt.figure()
    plt.plot = cr_series.plot(kind="bar")
    plt.ylabel("# of monsters per CR")
    plt.savefig(output_str)
    plt.close("all")