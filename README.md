# CarX Streets Helper

A sleek and user-friendly tool to modify in-game values (XP, Cash, Gold) in CarX Streets, giving you more control over your gaming experience.

## Features
- Modify XP, Cash, and Gold directly in the game
- Real-time value updates and checks
- Simple, intuitive interface for easy modifications
- Level slider for quick XP adjustments
- Non-resizable window for consistent user experience
- Dark theme for comfortable usage in low-light environments

## Installation & Usage

### For Executable Users:
1. Visit the [Releases](#) page and download the latest version of **CarX Streets Helper**.
2. Run the `.exe` file.
3. Launch **CarX Streets**, then click **Connect** in the helper tool.
4. Use the interface to modify values as desired.

### For Developers (Running from Source):
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CarXStreetsHelper.git
   ```
2. Navigate to the project directory:
   ```bash
   cd CarXStreetsHelper
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the script:
   ```bash
   python CarXHelper.py
   ```

## Usage Instructions

1. **Connecting**: Click the "Connect" button to establish a connection with the game.
2. **Modifying Values**:
   - Enter the desired value in the input field next to XP, Cash, or Gold.
   - Click the "Set" button to apply the change.
3. **Using the Level Slider**:
   - Adjust the slider to select a level.
   - The XP range for the selected level will be displayed.
   - Click "Set XP from Slider" to apply the minimum XP for that level.
4. **Refreshing Values**: Click the "Refresh" button to update the displayed in-game values.

### Important Notes:
- **XP Modification**: To see XP updates in the game, perform a small drift or speed boost.
- **Cash & Gold Modification**: Spend a small amount of the currency in-game for the value to update. If Cash or Gold shows as 0 or 1, restart the game to reflect the correct amount.
- Keep the tool running while playing CarX Streets for real-time monitoring and updates.

## Customization
To change the application icon:
1. Replace the `icon.png` file in the project directory with your desired icon (maintain the same filename).
2. Rebuild the executable using PyInstaller if you're distributing the tool.

## Disclaimer
This tool is for educational purposes only. Use it at your own risk, as modifying game values may conflict with the game's terms of service.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
