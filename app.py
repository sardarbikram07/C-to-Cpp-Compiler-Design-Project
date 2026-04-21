import streamlit as st
import os
from c_cpp import CToCppTranslator

def main():
    st.set_page_config(
        page_title="✨ C2pp ✨ - C to C++ Transformer",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for vibrant UI
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Montserrat:wght@900&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }

    h1 {
        font-family: 'Montserrat', sans-serif;
        color: #00ff9d !important;
        text-shadow: 0 0 10px rgba(0, 255, 157, 0.5);
        text-align: center;
    }

    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        font-family: 'Fira Code', monospace !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #ff4d4d, #f9cb28) !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(249, 203, 40, 0.4);
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 203, 40, 0.6) !important;
    }

    .stMarkdown {
        color: #ffffff !important;
    }

    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("✨ C2pp 🔮")
    # Centered subtitle with custom styling
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>Transform your <span style='color: #ff4d4d; font-weight: bold;'>C</span> to <span style='color: #00ff9d; font-weight: bold;'>C++</span> instantly!</h3>", unsafe_allow_html=True)

    # Feature list in a container with custom styling
    with st.container():
        st.markdown("""
        ### C2pp converts:
        - C-style includes to C++ equivalents
        - #define directives to const declarations
        - structs to classes
        - printf/scanf to cout/cin
        - malloc/free to new/delete
        - And many other C constructs to their C++ counterparts
        """)

    # Create two columns for input and output
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("Input C Code")
        c_code = st.text_area(
            "🧙‍♂️ Enter your C spell below:",
            height=400,
            placeholder="// Enter your C code here...\n#include <stdio.h>\n\nint main() {\n    printf(\"Hello, World!\\n\");\n    return 0;\n}",
            help="Paste your C code to transform it into beautiful C++"
        )

        translate_button = st.button("✨ Cast Translation Spell ✨", type="primary", use_container_width=True)

        # Example code section
        with st.expander("📜 Ancient C Scrolls (Examples)", expanded=False):
            example_code = '''#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 100
#define PI 3.14159

// A simple structure
struct Point {
    int x;
    int y;
};

// Function to initialize a point
void initPoint(struct Point *p, int x, int y) {
    p->x = x;
    p->y = y;
}

// Function to print a point
void printPoint(struct Point *p) {
    printf("Point: (%d, %d)\\n", p->x, p->y);
}

// Calculate distance between two points
float distance(struct Point *p1, struct Point *p2) {
    int dx = p1->x - p2->x;
    int dy = p1->y - p2->y;
    return sqrt(dx*dx + dy*dy);
}

int main() {
    struct Point *p1 = (struct Point *)malloc(sizeof(struct Point));
    struct Point *p2 = (struct Point *)malloc(sizeof(struct Point));

    initPoint(p1, 10, 20);
    initPoint(p2, 30, 40);

    printPoint(p1);
    printPoint(p2);

    printf("Distance between points: %.2f\\n", distance(p1, p2));

    free(p1);
    free(p2);

    return 0;
}'''
            st.code(example_code, language="c")
            if st.button("🔮 Summon Example", key="example_button"):
                st.session_state.c_code = example_code
                st.rerun()

    with col2:
        st.subheader("🌟 C++ Magic Output")

        if 'cpp_code' not in st.session_state:
            st.session_state.cpp_code = ""

        # Display translated code if available
        if st.session_state.cpp_code:
            st.code(st.session_state.cpp_code, language="cpp")

            # Download button for the translated code
            st.download_button(
                label="📥 Capture Magic Code",
                data=st.session_state.cpp_code,
                file_name="translated_code.cpp",
                mime="text/plain"
            )

    # Store the example code in session state if button is clicked
    if 'c_code' in st.session_state:
        c_code = st.session_state.c_code
        del st.session_state.c_code

    # Perform translation when button is clicked
    if translate_button and c_code:
        with st.spinner("🔮 Brewing your C++ potion..."):
            try:
                translator = CToCppTranslator()
                cpp_code = translator.translate(c_code)
                st.session_state.cpp_code = cpp_code
                st.rerun()
            except Exception as e:
                st.error(f"Error during translation: {str(e)}")

    # Add information about the translator
    st.markdown("---")
    st.markdown("""
    ### 🌈 The Magic Behind the Curtain

    The translator analyzes your C code and performs the following transformations:

    1. **Header Conversion**: Changes C headers like `stdio.h` to C++ equivalents like `iostream`
    2. **Struct to Class**: Converts C structs to C++ classes with methods
    3. **Memory Management**: Replaces `malloc`/`free` with `new`/`delete`
    4. **I/O Operations**: Converts `printf`/`scanf` to `cout`/`cin`
    5. **Constants**: Transforms `#define` constants to C++ `const` declarations

    For best results, ensure your C code is syntactically correct before translation.
    """)

if __name__ == "__main__":
    main()
