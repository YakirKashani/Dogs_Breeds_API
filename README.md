# Dogs Data API

## Overview

The Dogs Data API provides access to detailed information about various dog breeds. This includes breed name, height, weight, age range, life expectancy, temperament, origin, and images. The API is designed to allow the addition, retrieval, updating, and deletion of dog breed data, with all data stored in a MongoDB database. It provides a set of RESTful endpoints for easy interaction with the database.

## Features

- **Create a new dog breed's data.**
- **Retrieve data for all dog breeds.**
- **Retrieve data for a specific dog breed by ID.**
- **Update data for an existing dog breed.**
- **Delete data for a specific dog breed.**

## Requirements

- **Node.js** and **npm** (Node Package Manager)
- **MongoDB** (for data storage)
- API client like Postman or any HTTP client to interact with the API.

## Installation

1. Clone this repository to your local machine:
   ```
   git clone https://github.com/yourusername/dogs-data-api.git
   ```

2. Install the necessary dependencies:
   ```
   cd dogs-data-api
   npm install
   ```

3. Set up MongoDB:
   - Install MongoDB on your local machine or use a cloud service like MongoDB Atlas.
   - Configure the connection string to your MongoDB database.

4. Run the API server:
   ```
   npm start
   ```
   The API should now be running locally at `http://localhost:3000`.

## API Endpoints

### POST `/dogs_data`

Create a new dog breed's data.

**Request Body:**
```
{
  "breed_name": "Golden Retriever",
  "height": 55,
  "weight": 30,
  "age_range": "10-12 years",
  "life_expectancy": 12,
  "temperament": "Friendly, Intelligent, Devoted",
  "origin": "United States",
  "image_url": "https://example.com/golden-retriever.jpg"
}
```

**Response:**
- Status Code: `201 Created`
- Body:
  ```
  {
    "message": "Dog breed data created successfully."
  }
  ```

### GET `/dogs_data`

Get a list of all dog breeds and their data.

**Response:**
- Status Code: `200 OK`
- Body:
  ```
  [
    {
      "breed_name": "Golden Retriever",
      "height": 55,
      "weight": 30,
      "age_range": "10-12 years",
      "life_expectancy": 12,
      "temperament": "Friendly, Intelligent, Devoted",
      "origin": "United States",
      "image_url": "https://example.com/golden-retriever.jpg"
    },
    ...
  ]
  ```

### GET `/dogs_data/{id}`

Get data for a specific dog breed by its unique identifier.

**Response:**
- Status Code: `200 OK`
- Body:
  ```
  {
    "breed_name": "Golden Retriever",
    "height": 55,
    "weight": 30,
    "age_range": "10-12 years",
    "life_expectancy": 12,
    "temperament": "Friendly, Intelligent, Devoted",
    "origin": "United States",
    "image_url": "https://example.com/golden-retriever.jpg"
  }
  ```

### PUT `/dogs_data/{id}`

Update data for a specific dog breed.

**Request Body:**
```
{
  "breed_name": "Golden Retriever",
  "height": 60,
  "weight": 32,
  "age_range": "10-12 years",
  "life_expectancy": 13,
  "temperament": "Friendly, Intelligent, Loyal",
  "origin": "United States",
  "image_url": "https://example.com/golden-retriever-updated.jpg"
}
```

**Response:**
- Status Code: `200 OK`
- Body:
  ```
  {
    "message": "Dog breed data updated successfully."
  }
  ```

### DELETE `/dogs_data/{id}`

Delete data for a specific dog breed.

**Response:**
- Status Code: `200 OK`
- Body:
  ```
  {
    "message": "Dog breed data deleted successfully."
  }
  ```

## Error Handling

The API provides standard HTTP error codes for various issues:
- `400 Bad Request` – The request was malformed or missing required data.
- `404 Not Found` – The specified dog breed data does not exist.
- `500 Internal Server Error` – Something went wrong on the server.


