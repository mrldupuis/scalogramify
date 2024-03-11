from pathlib import Path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from scipy.signal import spectrogram



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

def generate_spectrogram(
    time:np.array, 
    acceleration:np.array,
    output_folder:str='out',
    filename:str='spectrogram.png',
    **kwargs,
    ):
    """
    Generates a spectrogram from time and acceleration data and saves it as a PNG file.
    
    Parameters:
    - time: Array of time data points.
    - acceleration: Array of acceleration data points in g.
    - out: (Optional) The folder to save the output PNG file. Default is 'out'.
    - filename: (Optional) The name of the output PNG file. Default is 'spectrogram.png'.
    
    Additional keyword arguments can be passed to customize the plot, such as:
    - title: The title of the plot.
    - xlabel: Label for the X-axis.
    - ylabel: Label for the Y-axis.
    - cmap: Colormap of the spectrogram.
    """
    
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Calculate the sampling rate
    sampling_rate = 1 / np.mean(np.diff(time))
    
    # Generate the spectrogram
    f, t, Sxx = spectrogram(acceleration, fs=sampling_rate, nperseg=256)
    
    # Apply a logarithmic scale
    Sxx_log = 10 * np.log10(Sxx)
    
    # Plot the spectrogram
    plt.figure(figsize=(10, 4))
    plt.pcolormesh(t, f, Sxx_log, shading='gouraud', cmap=kwargs.get('cmap', 'Greys'))
    plt.colorbar(label=kwargs.get('colorbar_label', 'Intensity (dB)'))
    
    # Customizing the plot
    plt.title(kwargs.get('title',filename.split('.')[0]))
    plt.xlabel(kwargs.get('xlabel','Time (s)'))
    plt.ylabel(kwargs.get('ylabel','Frequency (Hz)'))

    
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
            generate_spectrogram(time=x,acceleration=y,filename=f'{Path(file_path).name}.png')


if __name__ == "__main__":
    process_aaa_files("in")


