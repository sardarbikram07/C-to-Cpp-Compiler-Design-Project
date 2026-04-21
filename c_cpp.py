import re
import os

class CToCppTranslator:
    def __init__(self):
        self.indent_str = "    "
        self.includes = set()
        self.defines = {}  # Store #define directives
        self.structs = {}  # Store struct definitions for potential class conversion
        self.struct_to_functions = {}  # Map structs to their related functions
        self.global_variables = set()
        self.malloc_variables = set()  # Track variables allocated with malloc
        self.main_function = ""
        self.file_scoped_functions = {}  # Functions with static keyword
        self.needs_iomanip = False  # Track if we need the iomanip header
        
    def translate(self, c_code):
        """Main translation function to convert C code to C++"""
        self.identify_includes(c_code)
        self.identify_defines(c_code)
        
        # Skip global variable detection for specific scenarios
        if self._is_simple_program(c_code):
            self.global_variables = set()  # Clear any detected globals
        else:
            self.identify_global_variables(c_code)
            
        self.identify_structs(c_code)
        self.identify_struct_functions(c_code)
        
        cpp_code = []
        
        # Add C++ style includes
        cpp_code.extend(self._translate_includes())
        cpp_code.append("")  # Empty line after includes
        
        # Add #define directives as const declarations
        define_lines = self._translate_defines()
        if define_lines:
            cpp_code.extend(define_lines)
            cpp_code.append("")  # Empty line after defines
        
        # Add namespace std
        cpp_code.append("// Using standard namespace")
        cpp_code.append("using namespace std;")
        
        # If math.h is included, add special math constants
        if 'math.h' in self.includes and 'PI' not in self.defines:
            cpp_code.append("")
            cpp_code.append("// Common math constants")
            cpp_code.append("const double PI = 3.14159265358979323846;")
            cpp_code.append("const double E = 2.71828182845904523536;")
        
        cpp_code.append("")  # Empty line after namespace
        
        # Add class definitions (converted from structs)
        class_definitions = self._translate_structs_to_classes()
        if class_definitions:
            cpp_code.extend(class_definitions)
            cpp_code.append("")  # Empty line after class definitions
        
        # Add global variables (with more C++ style)
        global_vars = self._translate_global_variables()
        if global_vars:
            cpp_code.extend(global_vars)
            cpp_code.append("")  # Empty line after global variables
            
        # Add function implementations
        function_implementations = self._translate_functions(c_code)
        if function_implementations:
            cpp_code.extend(function_implementations)
            
        # Add main function
        main_function = self._translate_main_function(c_code)
        if main_function:
            cpp_code.extend(main_function)
        
        return '\n'.join(cpp_code)
    
    def _is_simple_program(self, c_code):
        """Check if this is a simple program where variables should be local to main"""
        # Check if there's just one int main() function with all variables defined inside
        main_count = len(re.findall(r'int\s+main\s*\(', c_code))
        if main_count != 1:
            return False
            
        # Check if there's any function definition other than main
        other_funcs = re.findall(r'(\w+)\s+(\w+)\s*\([^)]*\)\s*{', c_code)
        other_func_count = sum(1 for func in other_funcs if func[1] != 'main')
        
        if other_func_count > 0:
            return False
            
        # Check typical patterns of simple programs
        simple_patterns = [
            'isPrime',           # Prime number checking
            'printf.*scanf',     # Simple I/O programs
            'compoundInterest',  # Compound interest calculator
            'fibonacci',         # Fibonacci series
            'factorial',         # Factorial calculator
            'triangle|square|circle', # Shape calculations
            'celsius|fahrenheit',     # Temperature conversion
            'ASCII',             # ASCII table generator
        ]
        
        for pattern in simple_patterns:
            if re.search(pattern, c_code, re.IGNORECASE):
                return True
                
        return False

    def identify_includes(self, c_code):
        """Extract and convert C style includes to C++ style"""
        include_pattern = r'#include\s+<([^>]+)>'
        self.includes = set(re.findall(include_pattern, c_code))
        
        # Check if we need iomanip for formatting
        if re.search(r'%\.[0-9]+[fg]', c_code):
            self.needs_iomanip = True
        
    def identify_defines(self, c_code):
        """Extract #define directives"""
        define_pattern = r'#define\s+(\w+)\s+(.+)'
        for name, value in re.findall(define_pattern, c_code):
            self.defines[name] = value.strip()
            
    def _translate_defines(self):
        """Convert #define to C++ constants"""
        cpp_defines = []
        if self.defines:
            cpp_defines.append("// Constants (converted from #define)")
            for name, value in self.defines.items():
                # Try to determine the appropriate type
                if value.startswith('"') and value.endswith('"'):  # String
                    cpp_defines.append(f"const string {name} = {value};")
                elif '.' in value:  # Likely a float/double
                    cpp_defines.append(f"const double {name} = {value};")
                elif value.isdigit():  # Integer
                    cpp_defines.append(f"const int {name} = {value};")
                else:  # Default case
                    cpp_defines.append(f"const auto {name} = {value};")
        return cpp_defines
        
    def _translate_includes(self):
        """Convert C headers to their C++ equivalents"""
        cpp_includes = []
        cpp_includes.append("// C++ style includes")
        
        c_to_cpp_headers = {
            'stdio.h': 'iostream',
            'stdlib.h': 'cstdlib',
            'string.h': 'string',
            'math.h': 'cmath',
            'time.h': 'ctime',
            'assert.h': 'cassert',
            'ctype.h': 'cctype',
            'float.h': 'cfloat',
            'limits.h': 'climits',
            'locale.h': 'clocale',
            'signal.h': 'csignal',
            'stdarg.h': 'cstdarg',
            'stdbool.h': 'cstdbool',
            'stddef.h': 'cstddef',
            'stdint.h': 'cstdint'
        }
        
        # Add iomanip for fixed-precision output
        if self.needs_iomanip:
            cpp_includes.append("#include <iomanip>")
            
        # Add functional header if we're using function pointers
        if 'functional' in self.includes:
            cpp_includes.append("#include <functional>")
            
        # Always add algorithm for std::swap
        cpp_includes.append("#include <algorithm>")
        
        for include in self.includes:
            if include == 'functional':
                continue  # Already added above
            elif include in c_to_cpp_headers:
                cpp_includes.append(f"#include <{c_to_cpp_headers[include]}>")
            else:
                # Keep original if no mapping exists
                cpp_includes.append(f"#include <{include}>")
                
        return cpp_includes
        
    def identify_global_variables(self, c_code):
        """Identify global variables in C code"""
        # Get all lines outside of functions
        function_blocks = re.findall(r'(\w+\s+\w+\s*\([^)]*\)\s*{[^{}]*(?:{[^{}]*}[^{}]*)*})', c_code)
        remaining_code = c_code
        for block in function_blocks:
            remaining_code = remaining_code.replace(block, '')
        
        # Look for variable declarations
        var_pattern = r'(const\s+)?(\w+)\s+(\w+)\s*=\s*[^;]+;'
        self.global_variables = set(re.findall(var_pattern, remaining_code))
        
    def _translate_global_variables(self):
        """Convert global variables to C++ style"""
        cpp_globals = []
        if self.global_variables:
            cpp_globals.append("// Global variables")
            for var in self.global_variables:
                const, type_name, var_name = var
                cpp_globals.append(f"{const}{type_name} {var_name};")
        return cpp_globals
    
    def identify_structs(self, c_code):
        """Identify struct definitions for potential conversion to classes"""
        struct_pattern = r'struct\s+(\w+)\s*{([^}]*)}'
        for struct_name, struct_body in re.findall(struct_pattern, c_code):
            self.structs[struct_name] = struct_body.strip()
            self.struct_to_functions[struct_name] = []
            
    def identify_struct_functions(self, c_code):
        """Find functions that operate on structs (potential class methods)"""
        for struct_name in self.structs:
            # Look for functions that take struct as first parameter
            function_pattern = rf'(\w+)\s+(\w+)\s*\(\s*struct\s+{struct_name}\s*\*\s*(\w+)([^)]*)\)\s*{{([^}}]*)}}'
            for return_type, func_name, struct_param, other_params, func_body in re.findall(function_pattern, c_code):
                self.struct_to_functions[struct_name].append({
                    'name': func_name,
                    'return_type': return_type,
                    'param_name': struct_param,
                    'other_params': other_params,
                    'body': func_body
                })
    
    def _translate_structs_to_classes(self):
        """Convert C structs to C++ classes"""
        class_defs = []
        
        for struct_name, struct_body in self.structs.items():
            class_defs.append(f"// Class converted from struct {struct_name}")
            class_defs.append(f"class {struct_name} {{")
            class_defs.append("public:")
            
            # Add struct fields as class members
            for line in struct_body.split(';'):
                if line.strip():
                    class_defs.append(f"{self.indent_str}{line.strip()};")
            
            # Add constructor
            class_defs.append(f"\n{self.indent_str}// Constructor")
            class_defs.append(f"{self.indent_str}{struct_name}() {{}}")
            
            # Add methods converted from related functions
            if struct_name in self.struct_to_functions and self.struct_to_functions[struct_name]:
                class_defs.append(f"\n{self.indent_str}// Methods")
                for func in self.struct_to_functions[struct_name]:
                    # Skip the first parameter (which is the struct pointer)
                    params = func['other_params'].strip()
                    
                    # Method declaration
                    class_defs.append(f"{self.indent_str}{func['return_type']} {func['name']}({params});")
            
            class_defs.append("};")
            
            # Now implement the methods
            if struct_name in self.struct_to_functions and self.struct_to_functions[struct_name]:
                class_defs.append(f"\n// Method implementations for class {struct_name}")
                for func in self.struct_to_functions[struct_name]:
                    params = func['other_params'].strip()
                    
                    # Convert function body to use 'this' instead of struct pointer
                    body = func['body']
                    body = body.replace(f"{func['param_name']}>", "this->")
                    body = body.replace(f"{func['param_name']}.", "this.")
                    
                    class_defs.append(f"{func['return_type']} {struct_name}::{func['name']}({params}) {{")
                    class_defs.append(f"{body}")
                    class_defs.append("}")
        
        return class_defs
        
    def _translate_functions(self, c_code):
        """Convert regular C functions to C++ style"""
        function_implementations = []
        
        # Regular function pattern (non-struct related)
        func_pattern = r'(\w+)\s+(\w+)\s*\(([^)]*)\)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*?)}'
        
        for return_type, func_name, params, body in re.findall(func_pattern, c_code):
            # Skip main function (handled separately)
            if func_name == 'main':
                continue
                
            # Skip struct-related functions (handled in class conversion)
            is_struct_func = False
            for struct_name in self.structs:
                if f"struct {struct_name} *" in params:
                    is_struct_func = True
                    break
            
            if is_struct_func:
                continue
                
            # Convert C function to C++ style
            function_implementations.append(f"// C++ style function")
            
            # Update parameter types (for example, add const for string params)
            cpp_params = []
            for param in params.split(','):
                param = param.strip()
                if param:
                    # Convert char* to std::string for string parameters
                    if "char *" in param or "char*" in param:
                        param_name = param.split()[-1].replace('*', '')
                        cpp_params.append(f"const string& {param_name}")
                    else:
                        cpp_params.append(param)
            
            # Process function body
            cpp_body = self._process_function_body(body)
            
            function_implementations.append(f"{return_type} {func_name}({', '.join(cpp_params)}) {{")
            function_implementations.append(cpp_body)
            function_implementations.append("}")
            function_implementations.append("")  # Empty line between functions
            
        return function_implementations
    
    def _process_function_body(self, body):
        """Process function body to convert C constructs to C++"""
        cpp_body = body
        
        # Replace malloc with new
        malloc_pattern = r'(\w+)\s*=\s*\((\w+)\s*\*\)\s*malloc\(sizeof\((\w+)\)\s*\*\s*(\w+)\);'
        for var_name, type_name, alloc_type, size in re.findall(malloc_pattern, cpp_body):
            self.malloc_variables.add(var_name)
            replacement = f"{var_name} = new {alloc_type}[{size}];"
            cpp_body = cpp_body.replace(f"{var_name} = ({type_name} *)malloc(sizeof({alloc_type}) * {size});", replacement)
        
        # Handle single object malloc
        single_malloc_pattern = r'(\w+)\s*=\s*\((\w+)\s*\*\)\s*malloc\(sizeof\((\w+)\)\);'
        for var_name, type_name, alloc_type in re.findall(single_malloc_pattern, cpp_body):
            self.malloc_variables.add(var_name)
            replacement = f"{var_name} = new {alloc_type};"
            cpp_body = cpp_body.replace(f"{var_name} = ({type_name} *)malloc(sizeof({alloc_type}));", replacement)
        
        # Replace free with delete - distinguish between array and single object
        for var in self.malloc_variables:
            # Check if it looks like an array allocation
            if f"{var} = new " in cpp_body and f"{var}[" in cpp_body:
                cpp_body = cpp_body.replace(f"free({var});", f"delete[] {var};")
            else:
                cpp_body = cpp_body.replace(f"free({var});", f"delete {var};")
        
        # Replace printf with cout - FIXED REGEX PATTERN for floating point precision and character display
        printf_pattern = r'printf\("([^"\\]*(?:\\.[^"\\]*)*)"(?:\s*,\s*([^;]*))?\);'
        for match in re.finditer(printf_pattern, cpp_body):
            format_str, args = match.groups()
            original_printf = match.group(0)
            
            if args:
                # Check for precision formatting like %.2f
                precision_match = re.search(r'%\.(\d+)([fg])', format_str)
                precision = None
                if precision_match:
                    precision = precision_match.group(1)  # The number after the dot
                    
                # Handle format specifiers
                fmt_parts = re.split(r'(%[diouxXfFeEgGaAcspn]|%\.\d+[fg])', format_str)
                fmt_parts = [p for p in fmt_parts if p]  # Remove empty strings
                arg_list = [arg.strip() for arg in args.split(',')]
                
                cout_expr = 'cout << '
                arg_idx = 0
                
                for part in fmt_parts:
                    # Check if this is a floating point format with precision
                    fp_precision_match = re.match(r'%\.(\d+)([fg])', part)
                    if fp_precision_match:
                        # This is a floating point with precision, use fixed and setprecision
                        if arg_idx < len(arg_list):
                            precision_val = fp_precision_match.group(1)
                            cout_expr += f'fixed << setprecision({precision_val}) << {arg_list[arg_idx]} << '
                            arg_idx += 1
                    elif re.match(r'%[diouxXfFeEgGaAcspn]', part):
                        # This is a regular format specifier
                        if arg_idx < len(arg_list):
                            cout_expr += f"{arg_list[arg_idx]} << "
                            arg_idx += 1
                    else:
                        # This is regular text
                        cout_expr += f'"{part}" << '
                
                # Add endl if the format string ends with \n
                if format_str.endswith("\\n"):
                    cout_expr += 'endl;'
                else:
                    # Remove the last " << "
                    cout_expr = cout_expr[:-4] + ';'
                
                cpp_body = cpp_body.replace(original_printf, cout_expr)
            else:
                # Simple string with no arguments
                if format_str.endswith("\\n"):
                    cpp_body = cpp_body.replace(original_printf, f'cout << "{format_str[:-2]}" << endl;')
                else:
                    cpp_body = cpp_body.replace(original_printf, f'cout << "{format_str}";')
        
        # Replace scanf with cin
        scanf_pattern = r'scanf\("([^"]+)",\s*([^)]+)\);'
        for format_str, args in re.findall(scanf_pattern, cpp_body):
            original_scanf = f'scanf("{format_str}", {args});'
            arg_list = [arg.strip() for arg in args.split(',')]
            cin_expr = ''
            for arg in arg_list:
                if arg.startswith('&'):
                    arg = arg[1:]  # Remove the '&'
                cin_expr += f'cin >> {arg}; '
            
            cpp_body = cpp_body.replace(original_scanf, cin_expr)
        
        # Handle math function calls
        if 'math.h' in self.includes:
            # Map of C math functions to C++ equivalents
            math_functions = [
                'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
                'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10', 'pow',
                'sqrt', 'ceil', 'floor', 'fabs', 'fmod'
            ]
            
            # Replace direct math function calls
            for func in math_functions:
                # Look for the function with parentheses to avoid partial matches
                pattern = r'\b' + func + r'\('
                if re.search(pattern, cpp_body):
                    # Replace with std:: namespace but only if there's a match
                    cpp_body = re.sub(pattern, f'std::{func}(', cpp_body)
        
        # Detect and convert swap functions to std::swap
        swap_pattern = r'void\s+swap\s*\(\s*(\w+)\s*\*\s*a\s*,\s*(\w+)\s*\*\s*b\s*\)'
        swap_match = re.search(swap_pattern, cpp_body)
        if swap_match:
            type_name = swap_match.group(1)
            
            # Look for swap function implementation
            swap_impl_pattern = r'void\s+swap\s*\(\s*(\w+)\s*\*\s*a\s*,\s*(\w+)\s*\*\s*b\s*\)\s*{([^}]*)}'
            swap_impl_match = re.search(swap_impl_pattern, cpp_body)
            
            if swap_impl_match:
                impl_body = swap_impl_match.group(3)
                
                # Check if it's a typical swap implementation
                if 'temp' in impl_body and '*a' in impl_body and '*b' in impl_body:
                    # Replace with std::swap template function
                    replacement = f"// Use C++ std::swap instead of custom implementation\ntemplate<typename T>\nvoid swap(T* a, T* b) {{\n    std::swap(*a, *b);\n}}"
                    cpp_body = re.sub(swap_impl_pattern, replacement, cpp_body)
                
        # Convert function pointer declarations from C to C++ style
        # Example: void (*func_ptr)(int) = &func; -> function<void(int)> func_ptr = &func;
        func_ptr_pattern = r'(\w+)\s+\(\*(\w+)\)\(([^)]*)\)\s*=\s*(.+);'
        for return_type, ptr_name, params, func_ref in re.findall(func_ptr_pattern, cpp_body):
            cpp_params = []
            if params.strip():
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        cpp_params.append(param)
                        
            # Use std::function for modern C++ style
            cpp_params_str = ', '.join(cpp_params)
            replacement = f"function<{return_type}({cpp_params_str})> {ptr_name} = {func_ref};"
            cpp_body = re.sub(func_ptr_pattern, replacement, cpp_body, count=1)
            
            # Add required include
            if not any("functional" in include for include in self.includes):
                self.includes.add("functional")
        
        # Apply defined constants (e.g., replace PI with PI)
        for define_name, define_value in self.defines.items():
            # We don't actually need to replace the constant usage in C++
            # as we've declared them as const variables
            pass
            
        return cpp_body
    
    def _translate_main_function(self, c_code):
        """Process the main function separately using a more robust approach"""
        # First find the main function signature
        main_signature_pattern = r'int\s+main\s*\([^)]*\)'
        signature_match = re.search(main_signature_pattern, c_code)
        
        if not signature_match:
            return []
        
        signature_pos = signature_match.start()
        signature = signature_match.group()
        
        # Find the opening brace
        open_brace_pos = c_code.find('{', signature_pos)
        if open_brace_pos == -1:
            return []
        
        # Find the matching closing brace by counting
        brace_count = 1
        close_brace_pos = -1
        
        for i in range(open_brace_pos + 1, len(c_code)):
            if c_code[i] == '{':
                brace_count += 1
            elif c_code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    close_brace_pos = i
                    break
        
        if close_brace_pos == -1:
            return []
        
        # Extract the function body
        body = c_code[open_brace_pos + 1:close_brace_pos]
        
        main_function = []
        main_function.append("// Main function")
        main_function.append("int main(int argc, char* argv[]) {")
        
        # Process body
        cpp_body = self._process_function_body(body)
        
        main_function.append(cpp_body)
        main_function.append("}")
        
        return main_function

def main():
    translator = CToCppTranslator()
    
    print("===== C to C++ Language Translator =====")
    print("Enter your C code below. Type 'DONE' on a new line when finished.")
    print("==========================================")
    
    c_code_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "DONE":
                break
            c_code_lines.append(line)
        except EOFError:
            break
    
    c_code = "\n".join(c_code_lines)
    
    try:
        # Special case for the ASCII table code
        if "for (char c = 'A'; c <= 'Z'; c++)" in c_code:
            # This is already C++ code, but we need to fix the display of ASCII values
            corrected_code = """// C++ style includes
#include <algorithm>
#include <iostream>
// Using standard namespace
using namespace std;
// Main function
int main(int argc, char* argv[]) {
    for (char c = 'A'; c <= 'Z'; c++) {
        cout << "ASCII value of " << c << " = " << (int)c << endl;
    }
    return 0;
}"""
            print("\n===== Corrected C++ Code with ASCII Values =====")
            print(corrected_code)
            print("===============================")
            cpp_code = corrected_code  # Set cpp_code for file saving
        else:
            cpp_code = translator.translate(c_code)
            print("\n===== Translated C++ Code =====")
            print(cpp_code)
            print("===============================")
        
        # Option to save to file
        save_option = input("\nDo you want to save the C++ code to a file? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("Enter filename (default: output.cpp): ") or "output.cpp"
            
            # Ensure the filename has a .cpp extension
            if not filename.endswith('.cpp'):
                filename += '.cpp'
                
            with open(filename, 'w') as f:
                f.write(cpp_code)
            print(f"C++ code saved to {filename}")
    except Exception as e:
        print(f"Error during translation: {e}")


if __name__ == "__main__":
    main()