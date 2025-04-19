
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

