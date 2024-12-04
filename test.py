import unittest
from io import StringIO
import sys

# Redirect standard output to capture emitted WebAssembly
class TestEmitter(unittest.TestCase):
    def setUp(self):
        # Capture the output during tests
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        # Restore original stdout
        sys.stdout = self.original_stdout

    def test_simple_function(self):
        src = """
        int main() {
            return 42;
        }
        """
        compile(src)
        output = self.held_output.getvalue()

        # Check the output contains expected WebAssembly instructions
        self.assertIn('(func $main', output)
        self.assertIn('(result i32)', output)
        self.assertIn('i32.const 42', output)
        self.assertIn('return', output)

    def test_variable_declaration(self):
        src = """
        int main() {
            int x = 10;
            return x;
        }
        """
        compile(src)
        output = self.held_output.getvalue()

        # Check the output for the correct memory handling and return of x
        self.assertIn('(func $main', output)
        self.assertIn('(result i32)', output)
        self.assertIn('i32.const 10', output)  # Initializing x
        self.assertIn('return', output)

    def test_control_flow_if_else(self):
        src = """
        int main() {
            int x = 10;
            if (x > 5) {
                return 1;
            } else {
                return 0;
            }
        }
        """
        compile(src)
        output = self.held_output.getvalue()

        # Check for if-else structure
        self.assertIn('(func $main', output)
        self.assertIn('i32.const 10', output)  # Initialization of x
        self.assertIn('i32.const 5', output)  # Comparison
        self.assertIn('br_if', output)        # Conditional branching
        self.assertIn('i32.const 1', output)  # Return 1 in if
        self.assertIn('i32.const 0', output)  # Return 0 in else

    def test_while_loop(self):
        src = """
        int main() {
            int x = 0;
            while (x < 5) {
                x = x + 1;
            }
            return x;
        }
        """
        compile(src)
        output = self.held_output.getvalue()

        # Check for while loop structure
        self.assertIn('(func $main', output)
        self.assertIn('block ;; while', output)
        self.assertIn('loop', output)
        self.assertIn('i32.const 1', output)  # Increment x
        self.assertIn('i32.add', output)      # Addition operation
        self.assertIn('br 0 ;; repeat loop', output)  # Loop repetition

    def test_string_handling(self):
        src = """
        int main() {
            char* str = "hello";
            return 0;
        }
        """
        compile(src)
        output = self.held_output.getvalue()

        # Check for string pooling and memory management
        self.assertIn('(data $.rodata', output)  # String pool
        self.assertIn('"hello\\00"', output)    # Null-terminated string
        self.assertIn('(func $main', output)

if __name__ == "__main__":
    unittest.main()
