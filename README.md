# NL2SQL-Converter

NL2SQL-Converter is a versatile tool that converts natural language sentences from any language into SQL queries, allowing users to query their databases effortlessly. Simply enter your question in your preferred language, and NL2SQL-Converter will generate the corresponding SQL query to fetch the data you need. This tool simplifies database interactions, making data retrieval accessible to everyone, regardless of SQL proficiency or language preference.

Currently, NL2SQL-Converter supports PostgreSQL as the database and utilizes Anthropic's Large Language Model for natural language processing. This combination ensures robust and accurate query generation for diverse and complex database interactions.

## Features

- Multi-Language Support: Convert natural language sentences from any language into SQL queries.
- Effortless Query Generation: Simply enter your question in plain language, and get the corresponding SQL query.
- PostgreSQL Integration: Seamlessly interact with PostgreSQL databases for data retrieval and management.
- Powered by Anthropic: Utilizes Anthropic's advanced Large Language Model for precise natural language processing.
- Robust Performance: Handles diverse and complex queries efficiently, ensuring reliable database operations.

## Installation

To run the project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/samitugal/aiworkspace.git
    ```
2. Navigate to the project directory::
    ```bash
    cd aiworkspace
    ```
3. Start the application and build the necessary components using Docker Compose::
    ```bash
    docker-compose up --build
    ```
## Configuration
In the configs/DatabaseConfigs directory, you can choose from various database types and enter your database information according to your preferences. Ensure that the following environment variables are set in the .env file:

- DATABASE_CONNECTION_PATH
- LLM_CONFIG_PATH
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION

## Usage
The application runs on port 8000. To send a request, make a POST request to the /generate_response API endpoint. The request should include a parameter called request where users can write their desired query.
```bash
curl -X POST http://localhost:8000/generate_response -d '{"request": "Show me all records from the users table"}' -H "Content-Type: application/json"
```
## Testing
A sample Northwind database is available within the PostgreSQL container. You can use this for testing your queries.

## UI Development
The UI is still under development. If you would like to contribute, your support is welcome.

### Example Requests and Responses
![image](https://github.com/samitugal/aiworkspace/assets/57317518/fc936258-f5d5-4625-b914-1576c2112cde)
-----
![image](https://github.com/samitugal/aiworkspace/assets/57317518/ca1a1a50-0d7e-47bd-945f-6ee1adb0d1c4)
-----
![image](https://github.com/samitugal/aiworkspace/assets/57317518/9776dbfc-8cd9-4ce6-8ba2-6ddd31759f8d)


