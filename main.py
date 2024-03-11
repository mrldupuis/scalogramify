from pathlib import Path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from scipy.signal import spectrogram

import pywt


def load_aaa(ffp: Path):
    """Loads an .aaa file"""
    # Get the data
    df = pd.read_csv(ffp, header=None, skiprows=1, usecols=[0])

    # Ensure only single column
    assert df.shape[1] == 1

    # Get dt and number of entries
    with ffp.open(mode="r", encoding="ascii") as f:
        header_line = f.readline().split(",")
    dt = float(header_line[-1].strip())
    n_entries = int(header_line[-2].strip())

    # Sanity check
    assert df.shape[0] == n_entries

    # Compute the time steps
    time_values = np.arange(0.0, n_entries * dt, dt)[:n_entries]

    # Create and return the time series
    return time_values, df.iloc[:, 0].values

def generate_scalogram(
    x:np.array, 
    y:np.array,
    wavelet='morl',
    scales=None,
    sampling_period=1,
    output_folder:str='out',
    filename:str='spectrogram.png',
    **kwargs,
    ):

    """
    Performs a Continuous Wavelet Transform (CWT) on the input time series data (x, y),
    and plots the scalogram of the transformed data.
    
    Parameters:
    - time: Array of time data points.
    - acceleration: Array of acceleration data points in g.
    - wavelet: String, the name of the wavelet to use.
    - scales: Array of scales to use for the CWT. If None, automatically determined.
    - sampling_period: Sampling period of the time series data.
    - out: (Optional) The folder to save the output PNG file. Default is 'out'.
    - filename: (Optional) The name of the output PNG file. Default is 'spectrogram.png'.
    
    Additional keyword arguments can be passed to customize the plot, such as:
    - title: The title of the plot.
    - xlabel: Label for the X-axis.
    - ylabel: Label for the Y-axis.
    - cmap: Colormap of the spectrogram.
    """
    
    # If scales are not provided, automatically generate them.
    if scales is None:
        scales = np.arange(1, 128)

    # Perform Continuous Wavelet Transform
    coefficients, frequencies = pywt.cwt(y, scales, wavelet, sampling_period=sampling_period)

    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Plot the scalogram
    plt.figure(figsize=(10, 4))
    plt.pcolormesh(x, scales, np.abs(coefficients), shading='gouraud', cmap=kwargs.get('cmap', 'Greys'))

    # Customizing the plot
    plt.xlabel(kwargs.get('xlabel','Time (s)'))
    plt.ylabel(kwargs.get('ylabel','Scale'))
    plt.colorbar(label=kwargs.get('colorbar_label', 'Magnitude'))
    plt.title(kwargs.get('title',filename.split('.')[0]))
    # plt.yscale('log')
    
    # Save the figure
    plt.savefig(os.path.join(output_folder, filename.split('.')[0]))
    plt.close()

def process_aaa_files(input_directory:str):
    """
    Loops through every .aaa file in the specified input directory and processes them.

    Parameters:
    - input_directory: The directory to search for .aaa files.
    """
    # Ensure the input directory exists
    if not os.path.exists(input_directory):
        print(f"The directory {input_directory} does not exist.")
        return

    # Loop through all files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".aaa"):
            file_path = os.path.join(input_directory, filename)
            print(f"Processing file: {file_path}")
            x, y = load_aaa(Path(file_path))
            generate_scalogram(x=x,y=y,filename=f'{Path(file_path).name}.png')


if __name__ == "__main__":
    process_aaa_files("in")
