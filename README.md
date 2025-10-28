# Reversly - Reverse Image Search Application

Welcome to the **Reversely** project! This README provides an overview of the project, setup instructions, and other relevant details.

## Table of Contents

- [Visit](#visit)
- [About](#about)
- [Features](#features)
- [Technology](#technology)
- [Installation](#installation)
- [Usage](#usage)
- [Structure](#structure)
- [Contributors](#contributors)
- [Contributing](#contributing)
- [License](#license)

## Visit

- [Vercel](https://reversely0.vercel.app/)

## About

**Reversely** is a reverse image search application where user can upload their images and search using similar images.

## Technology
- *Frontend*: HTML, CSS
- *Backend*: Flask

## Features

- Image Upload
- Reverse Image Search

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/woabu0/reversely.git
   ```
2. Navigate to the reversely directory:
   ```bash
   cd reversely
   ```
3. Install requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Structure

    ```
    server/
    ├── app.py
    ├── utils.py
    ├── requirements.txt
    ├── templates/
    │   ├── index.html
    │   ├── upload.html
    │   ├── search.html
    │   └── search_results.html
    └── static/
        ├── uploads/
        └── features/
    ```

## Contributors

<p align="center">
  <a href="https://github.com/woabu0/reversely/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=woabu0/reversely" alt="Contributors" />
  </a>
</p>

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
