# Navis

A privacy-focused personal finance management application built with Streamlit.

## Features

- 💰 **Debt Management** - Track all your debts with Snowball and Avalanche payoff strategies
- 💸 **Expense Tracking** - Categorize and monitor your monthly expenses
- 💵 **Income Management** - Track multiple income sources with different frequencies
- 📋 **Budget Planner** - Create monthly budgets with projections
- 📄 **Reports** - Generate PDF and Excel reports
- 🔐 **PIN Protection** - Secure your profile with a 4-digit PIN
- 📊 **Visualizations** - Interactive charts and progress tracking

## Privacy

- ✅ **100% Local** - All data stored on your machine
- ✅ **No Internet Required** - Works completely offline
- ✅ **No External APIs** - Zero external connections
- ✅ **Complete Ownership** - You control your data

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Quick Start

**Windows:**
```bash
# Double-click run.bat or run in terminal:
run.bat
```

**Mac/Linux:**
```bash
# Make the script executable first
chmod +x run.sh

# Run the application
./run.sh
```

### Manual Installation

```bash
# Navigate to the app directory
cd Navis

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Usage

### First Time Setup

1. Run the application
2. Create your profile with a 4-digit PIN
3. Start adding your debts, expenses, and income

### Navigation

- **Dashboard** - Overview of your financial health
- **Debts** - Add and manage debts, view payoff strategies
- **Expenses** - Track monthly expenses by category
- **Income** - Manage income sources
- **Budget Planner** - Monthly budget and projections
- **Reports** - Export data to PDF or Excel
- **Settings** - Manage profile and goals

## Data Storage

All data is stored locally in CSV files:

```
Navis/
└── users/
    └── [your_profile]/
        ├── debts.csv
        ├── expenses.csv
        ├── income.csv
        └── settings.json
```

## Features Details

### Debt Strategies

**Snowball Method:**
- Pay smallest balance first
- Quick psychological wins
- Builds momentum

**Avalanche Method:**
- Pay highest interest first
- Mathematically optimal
- Saves more money over time

### Budget Projections

- Monthly surplus calculations
- Emergency fund timeline
- Savings growth projections
- Visual progress tracking

### Reports

**Excel Export:**
- Multiple sheets for each data type
- Easy to analyze in spreadsheet software

**PDF Report:**
- Comprehensive financial summary
- Ready for printing or sharing

## Technology Stack

- **Frontend & Backend:** Streamlit
- **Data Processing:** Pandas
- **Visualizations:** Plotly
- **PDF Generation:** ReportLab
- **Excel Export:** XlsxWriter

## Requirements

```
streamlit==1.31.0
pandas==2.2.0
plotly==5.18.0
openpyxl==3.1.2
reportlab==4.0.8
python-dateutil==2.8.2
xlsxwriter==3.1.9
Pillow==10.2.0
```

## Future Enhancements

- Multi-user authentication
- Bank statement import
- Investment tracking
- Bill reminders
- Mobile app support

## License

This project is for personal use. Feel free to modify and extend it for your needs.

## Support

For issues or questions, check the Settings page for data location and troubleshooting information.

---

**Built with ❤️ for personal financial planning**
