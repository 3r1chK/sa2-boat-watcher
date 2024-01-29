# SA2 Boat Watcher

![alt text](doc/sa2-watcher-cover.png)

## About

SA2 Boat Watcher is a collection of Python scripts designed to help Sailaway2 players monitor their boats efficiently. These scripts use game data to provide real-time updates and statistics about the status of your boats in Sailaway2.

**Note:** the software is still under development and is not complete. Some features may not work. 

## Features

- **Polar files generation/manipulation**
- **NMEA server**

## Getting Started
### Prerequisites

- Python 3.x
- Sailaway2 game account

### Installation

1. Clone the repository:
    ```bash 
    git clone https://github.com/3r1chK/sa2-boat-watcher.git
    ```
1. Navigate to the cloned directory:
    ```bash 
    cd sa2-boat-watcher
    ```
1. Install Python requirements:
    ```bash 
    pip install -r requirements.txt
    ```

### Usage

1. Configure the `config.ini` file with your Sailaway2 account details.
1. Run the main script to start monitoring:
    ```bash 
    python main.py
    ```

## Future Developments

* **SA2 GRIB Time Finder & Converter:** this tool selects a GRIB file that matches the current time and compares it with your boat's weather in SA2. Once aligned, it allows for the conversion of the GRIB file to match the SA2 timing.
* **Race Route Diagram Generator:** a tool designed to create and modify race route diagrams.
* **Web App:** a user-friendly web interface to access all the features of the _SA2 Boat Watcher_.


## Contributing

Contributions to SA2 Boat Watcher are welcome.
