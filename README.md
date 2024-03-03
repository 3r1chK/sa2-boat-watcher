# SA2 Boat Watcher

![Banner](doc/sa2-watcher-cover.png)

## About

SA2 Boat Watcher is a collection of Python scripts designed to help Sailaway2 players monitor their boats efficiently. These scripts use game data to provide real-time updates and statistics about the status of your boats in Sailaway2.

**Note:** the software is still under development and is not complete. Some features may not work. 

## Features

- **Polar files generation/manipulation;**
- **SA2 GRIB Time Finder & Converter;**
- **Race Route Diagram Generator;**
- NMEA server (to be fixed).

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

* **Web App:** a user-friendly web interface to access all the features of the _SA2 Boat Watcher_.
* **Improved polar file generator** by using multiple boats

## Contributing

Contributions to SA2 Boat Watcher are welcome.
