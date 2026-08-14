# Reversly - Reverse Image Search Application

Welcome to the **Reversely** project! This README provides an overview of the project, setup instructions, and other relevant details.

## Table of Contents

- [Visit](#visit)
- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Structure](#structure)
- [Contributors](#contributors)
- [Contributing](#contributing)
- [License](#license)

## Visit

- [Repository](https://github.com/aabubokarr/reversely)

## About

**Reversely** is a desktop reverse image search application that uses AI-powered visual embeddings to find visually similar images in your local media library. Built with Python and PySide6, it provides fast, private, and offline image discovery.

## Features

- Image Upload
- Reverse Image Search
- Image Similarity Check

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aabubokarr/reversely.git
   ```
2. Navigate to the reversely directory:
   ```bash
   cd reversely
   ```
3. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate

   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Structure

```
reversely/
├── media/                    # Images for testing
├── .gitignore                # Git ignore rules
├── app.py                    # Main desktop application
├── LICENSE                   # Project license
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── search_engine.py          # AI image embedding and similarity search
└── utils.py                  # Image processing utilities
```

## Contributors

<p align="center">
  <a href="https://github.com/aabubokarr/reversely/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=aabubokarr/reversely" alt="Contributors" />
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
