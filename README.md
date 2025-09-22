# Smart-Budgets
Smart Budget is a user-friendly desktop application designed to help individuals effectively manage their personal finances.

**Smart Budget** is a desktop personal finance application that helps you track your income and expenses, set savings goals, and visualize your financial health. Built with Python and `tkinter`, it's a simple yet powerful tool for managing your money.

## Features

- **User Authentication**: Secure user registration and login with hashed passwords.
- **Guided Setup Wizard**: A step-by-step wizard to easily set up your income streams, expenses, and savings targets.
- **Interactive Dashboard**: A clean and intuitive dashboard that displays a summary of your finances.
- **Data Visualization**: Includes a pie chart of your expense distribution and a bar chart comparing income, expenses, and savings.
- **Personalized Recommendations**: Get actionable tips based on your spending habits to help you stay on track.
- **Data Export**: Export your budget data to CSV and PDF files for easy sharing and record-keeping.

## Installation

### Prerequisites

- Python 3.6 or newer
- `pip` (Python package installer)

### Setup

1.  **Clone the Repository**
    Start by cloning the project from GitHub to your local machine.

    ```sh
    git clone [https://github.com/Elenor180/Smart-Budgets.git](https://github.com/Elenor180/Smart-Budgets.git)
    cd Smart-Budgets
    ```

2.  **Install Dependencies**
    Install the required Python libraries using `pip`.

    ```sh
    pip install -r requirements.txt
    ```

    *If you don't have a `requirements.txt` file yet, you can create one by running `pip freeze > requirements.txt` from your project's root directory.*

## Usage

1.  **Run the Application**
    From the project's root directory, execute the `main.py` file to start the application.

    ```sh
    python main.py
    ```

2.  **Sign Up & Log In**
    When the application window opens, click "Sign Up" to create a new user account. Once registered, log in to access the setup wizard.

3.  **Complete the Setup Wizard**
    Follow the steps in the wizard to input your income, expenses, dependents, and savings goals. This will populate your budget dashboard.

4.  **Explore the Dashboard**
    Use the dashboard to view your budget, filter expenses, and check out the charts and recommendations. You can also export your data or run the wizard again to make adjustments.

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
