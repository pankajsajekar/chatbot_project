
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
