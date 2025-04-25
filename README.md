
# Chatbot Project

This project is a chatbot application powered by Django and ASGI, served using Daphne.

## Requirements

- Python 3.x
- Django
- Daphne

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd chatbot_project
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

Start the server using Daphne:
```bash
daphne -b 0.0.0.0 -p 5000 chatbot_project.asgi:application
```

The server will be accessible at `http://localhost:5000`.

## Notes

- Ensure that your ASGI application is correctly configured in `chatbot_project/asgi.py`.
- Update the `ALLOWED_HOSTS` in your Django settings for production use.

## License

This project is licensed under the MIT License.

## Troubleshooting

If you encounter issues with Django environment variables, ensure that the `DJANGO_SETTINGS_MODULE` is correctly set. You can set it in the terminal using the following command:

```bash
export DJANGO_SETTINGS_MODULE='chatbot_project.settings'
```

This will allow Django to locate and use the appropriate settings module.

## Populating the Database

To insert fake data into the database for testing purposes, you can use the following command:

```bash
python manage.py insert_fake_data
```

> **Note:** Ensure that the `insert_fake_data` management command is implemented in your Django project to generate and populate the database with fake data.





## Overview

The Chatbot Project is designed to provide an interactive and intelligent chatbot application that can be integrated into various platforms. The primary goal of this project is to create a scalable, efficient, and user-friendly chatbot system that leverages modern web technologies and frameworks.

### Why This Project Was Made

The motivation behind this project stems from the increasing demand for automated conversational agents in various industries, such as customer support, e-commerce, and education. Chatbots can significantly reduce response times, improve user engagement, and provide 24/7 support. This project aims to address these needs by offering a robust solution that can be customized and deployed easily.

### What Was Used

To achieve the project's objectives, the following technologies and tools were utilized:

- **Django**: A high-level Python web framework that simplifies the development of web applications by providing built-in features for database management, routing, and authentication.
- **ASGI (Asynchronous Server Gateway Interface)**: Enables asynchronous communication, making the chatbot capable of handling real-time interactions efficiently.
- **Daphne**: A lightweight ASGI server used to serve the Django application, ensuring compatibility with asynchronous features.
- **Python**: The core programming language used for its simplicity, versatility, and extensive library support.

### What This Project Does

The chatbot application provides the following functionalities:

- Real-time communication with users through a web interface or other integrated platforms.
- Scalable architecture to handle multiple concurrent users.
- Easy customization to adapt to specific use cases or industries.
- Support for database operations to store and retrieve user interactions or other relevant data.

### Why It Was Made

This project was created to:

1. Explore the capabilities of modern web frameworks and asynchronous programming.
2. Provide a practical solution for businesses and developers looking to implement chatbot functionality.
3. Serve as a learning resource for understanding the integration of Django with ASGI and Daphne.
4. Demonstrate the use of Python for building scalable and efficient web applications.

By combining these technologies, the Chatbot Project offers a comprehensive solution that is both powerful and easy to deploy, making it suitable for a wide range of applications.
