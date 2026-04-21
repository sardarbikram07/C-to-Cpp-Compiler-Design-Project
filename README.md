# ✨ C2pp 🔮 - C to C++ Code Transformer

![C2pp Banner](https://img.shields.io/badge/C2pp-Transform%20C%20to%20C%2B%2B-00ff9d?style=for-the-badge&logo=c%2B%2B)

C2pp is a powerful tool that magically transforms your C code into modern C++ code. With an intuitive Streamlit interface, you can easily convert legacy C code to take advantage of C++ features and best practices.

## ✨ Features

C2pp intelligently converts:

- **C-style includes** to C++ equivalents (`stdio.h` → `iostream`)
- **#define directives** to const declarations
- **structs** to classes with proper methods
- **printf/scanf** to cout/cin
- **malloc/free** to new/delete
- And many other C constructs to their C++ counterparts

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/c2pp.git
   cd c2pp
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install them directly:
   ```bash
   pip install streamlit
   ```

## 🔮 Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. The app will open in your default web browser.

3. Enter your C code in the left panel or use one of the provided examples.

4. Click the "✨ Cast Translation Spell ✨" button to transform your code.

5. View the translated C++ code in the right panel.

6. Download the translated code using the "📥 Capture Magic Code" button.

## 🧙‍♂️ How It Works

The translator analyzes your C code and performs the following transformations:

1. **Header Conversion**: Changes C headers like `stdio.h` to C++ equivalents like `iostream`
2. **Struct to Class**: Converts C structs to C++ classes with methods
3. **Memory Management**: Replaces `malloc`/`free` with `new`/`delete`
4. **I/O Operations**: Converts `printf`/`scanf` to `cout`/`cin`
5. **Constants**: Transforms `#define` constants to C++ `const` declarations

## 📋 Example

### Input (C Code):
```c
#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 100

struct Point {
    int x;
    int y;
};

void printPoint(struct Point *p) {
    printf("Point: (%d, %d)\n", p->x, p->y);
}

int main() {
    struct Point *p = (struct Point *)malloc(sizeof(struct Point));
    p->x = 10;
    p->y = 20;
    printPoint(p);
    free(p);
    return 0;
}
```

### Output (C++ Code):
```cpp
// C++ style includes
#include <algorithm>
#include <iostream>
#include <cstdlib>

// Using standard namespace
using namespace std;

// Constants (converted from #define)
const int MAX_SIZE = 100;

// Class converted from struct Point
class Point {
public:
    int x;
    int y;

    // Constructor
    Point() {}

    // Methods
    void printPoint();
};

// Method implementations for class Point
void Point::printPoint() {
    cout << "Point: (" << this->x << ", " << this->y << ")" << endl;
}

// Main functions
int main(int argc, char* argv[]) {
    Point *p = new Point;
    p->x = 10;
    p->y = 20;
    p->printPoint();
    delete p;
    return 0;
}
```

## 🛠️ Project Structure

- `app.py` - Streamlit web interface
- `c_cpp.py` - Core translation engine
- `requirements.txt` - Required Python packages

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Streamlit for the amazing web app framework
- The C and C++ communities for their excellent documentation

---

Made with ❤️ by BIKRAM SARDAR, JAYDEEP DAS, ABHIRUP KARMAKAR
