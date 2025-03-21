import ast
import subprocess
import tempfile
import re
from typing import List, Dict

class CodeAutoFixEngine:
    def __init__(self, code: str):
        """Initialize the code auto-fix engine."""
        self.original_code = code

    def auto_fix_syntax_errors(self, code: str) -> str:
        """Fix common syntax errors and ensure colon after function parenthesis."""
        fixed_code = code
        lines = fixed_code.split('\n')
        corrected_lines = []

        for line in lines:
            stripped = line.strip()
            if re.match(r'^def\s+\w+\([^)]*\)', stripped) and not stripped.endswith(':'):
                line += ':'
            elif re.match(r'^(if|elif|for|while|class)\s+[^:]+$', stripped):
                line += ':'
            elif re.match(r'^\s*print\s+[^\(].*', stripped):
                line = re.sub(r'print\s+([^\(].*)', r'print(\1)', line)
            corrected_lines.append(line)

        fixed_code = '\n'.join(corrected_lines)
        fixed_code = re.sub(r'\t', '    ', fixed_code)

        lines = fixed_code.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            if re.match(r'^(\s*)(if|elif|for|while|def|class) .+:$', line):
                if i + 1 >= len(lines) or not lines[i + 1].strip() or lines[i + 1].strip() in ['else:', 'elif']:
                    new_lines.append(line)
                    new_lines.append('    ' * (len(line) - len(line.lstrip())) + '    pass')
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        return '\n'.join(new_lines)

    def fix_missing_brackets(self, code: str) -> str:
        """Fix missing brackets in function calls and expressions."""
        lines = code.split('\n')
        corrected_lines = []
        
        for line in lines:
            open_paren = line.count('(')
            close_paren = line.count(')')
            open_bracket = line.count('[')
            close_bracket = line.count(']')
            
            if open_paren > close_paren:
                line += ')' * (open_paren - close_paren)
            if open_bracket > close_bracket:
                line += ']' * (open_bracket - close_bracket)
                
            corrected_lines.append(line)
        return '\n'.join(corrected_lines)

    def fix_missing_quotes(self, code: str) -> str:
        """Fix missing quotes in string literals."""
        lines = code.split('\n')
        corrected_lines = []
        in_multiline = False
        
        for line in lines:
            if in_multiline:
                if line.strip().endswith('"""'):
                    in_multiline = False
                corrected_lines.append(line)
                continue
            
            line = re.sub(r'""+\)', '")', line)
            
            print_match = re.search(r'print\s*\(([^\'"\s(][^\s)]*)["\']*\)?', line)
            if print_match:
                unquoted = print_match.group(1)
                if not re.search(r'[+\-*/%<>=]', unquoted) and not unquoted.isidentifier():
                    line = re.sub(r'print\s*\(' + unquoted, f'print("{unquoted}"', line)
            
            if line.strip().startswith('"""') and not line.strip().endswith('"""'):
                in_multiline = True
            
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            closing_brackets = [i for i, char in enumerate(line) if char in ')]']
            
            if single_quotes % 2 != 0:
                if closing_brackets:
                    insert_pos = min(closing_brackets)
                    line = line[:insert_pos] + "'" + line[insert_pos:]
                else:
                    line += "'"
                    
            if double_quotes % 2 != 0 and not in_multiline:
                if closing_brackets:
                    insert_pos = min(closing_brackets)
                    line = line[:insert_pos] + '"' + line[insert_pos:]
                else:
                    line += '"'
                    
            corrected_lines.append(line)
        
        if in_multiline:
            corrected_lines.append('"""')
            
        return '\n'.join(corrected_lines)

    def auto_format_with_black(self, code: str) -> str:
        """Auto-format using Black if available."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                temp_file.write(code.encode())
                temp_file.flush()
                subprocess.run(["black", temp_file.name], capture_output=True, text=True)
                with open(temp_file.name, 'r') as f:
                    return f.read()
        except Exception:
            return code

    def fix_undefined_variables(self, code: str) -> str:
        """Define undefined variables and fix reserved words."""
        try:
            tree = ast.parse(code)
            defined_vars = set()
            used_vars = set()
            reserved_words = {'list', 'dict', 'set', 'str', 'int', 'float'}

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_vars.add(target.id)
                elif isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        defined_vars.add(arg.arg)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)

            lines = code.split('\n')
            for i, line in enumerate(lines):
                for reserved in reserved_words:
                    if re.search(rf'\b{reserved}\s*=', line):
                        lines[i] = re.sub(rf'\b{reserved}\b', f'my_{reserved}', line)

            undefined_vars = used_vars - defined_vars - set(dir(__builtins__)) - reserved_words
            if undefined_vars:
                new_lines = []
                in_function = False
                indent_level = 0
                declaration_position = 0
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if re.match(r'^def\s+\w+\(', stripped):
                        in_function = True
                        indent_level = len(line) - len(line.lstrip())
                        new_lines.append(line)
                        declaration_position = len(new_lines)
                    elif in_function and not stripped and not undefined_vars:
                        continue
                    elif in_function and undefined_vars and i == declaration_position:
                        indent = '    ' * (indent_level // 4 + 1)
                        new_lines.extend([f"{indent}{var} = 0" for var in undefined_vars])
                        undefined_vars.clear()
                        new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                code = '\n'.join(new_lines)
            return code
        except Exception:
            lines = code.split('\n')
            new_lines = []
            defined_vars = set(['x'])
            in_function = False
            indent_level = 0
            declaration_position = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if re.match(r'^def\s+\w+\(', stripped):
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                    params = re.search(r'\((.*?)\)', line).group(1).split(',')
                    defined_vars.update(param.strip() for param in params if param.strip())
                    new_lines.append(line)
                    declaration_position = len(new_lines)
                if in_function:
                    print_match = re.search(r'print\s*\(([^\'"\s)][^\s)]*)\)?', line)
                    if print_match:
                        var = print_match.group(1)
                        if (var.isidentifier() and 
                            var not in defined_vars and 
                            var not in dir(__builtins__) and 
                            var not in ['True', 'False', 'None']):
                            indent = '    ' * (indent_level // 4 + 1)
                            new_lines.insert(declaration_position, f"{indent}{var} = 0")
                            defined_vars.add(var)
                            declaration_position += 1
                new_lines.append(line)
            return '\n'.join(new_lines)

    def fix_undefined_returns(self, code: str) -> str:
        """Add return None to functions without returns, at the end of the function."""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            corrected_lines = []
            in_function = False
            indent_level = 0
            has_return = False
            function_end = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if re.match(r'^def\s+\w+\(', stripped):
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                    has_return = False
                    corrected_lines.append(line)
                elif in_function and stripped.startswith('return'):
                    has_return = True
                    corrected_lines.append(line)
                elif in_function and (i + 1 >= len(lines) or len(lines[i + 1]) - len(lines[i + 1].lstrip()) <= indent_level):
                    function_end = i
                    corrected_lines.append(line)
                    if not has_return:
                        corrected_lines.append('    ' * (indent_level // 4) + '    return None')
                    in_function = False
                else:
                    corrected_lines.append(line)

            return '\n'.join(corrected_lines)
        except Exception:
            # Fallback for when AST parsing fails
            lines = code.split('\n')
            corrected_lines = []
            in_function = False
            indent_level = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if re.match(r'^def\s+\w+\(', stripped):
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                    corrected_lines.append(line)
                elif in_function and (i + 1 >= len(lines) or len(lines[i + 1]) - len(lines[i + 1].lstrip()) <= indent_level):
                    corrected_lines.append(line)
                    corrected_lines.append('    ' * (indent_level // 4) + '    return None')
                    in_function = False
                else:
                    corrected_lines.append(line)
            return '\n'.join(corrected_lines)

    def fix_style_issues(self, code: str) -> str:
        """Trim long lines and simplify style errors."""
        lines = code.split('\n')
        corrected_lines = []
        for line in lines:
            if len(line) > 100:
                corrected_lines.append(line[:100] + '  # truncated')
            else:
                corrected_lines.append(line)
        return '\n'.join(corrected_lines)

    def auto_fix_code(self):
        """Run all fixes and display process."""
        print("🚀 Starting Auto-Fix Engine...")
        print("\n❌ Faulty Code:")
        print(self.original_code)

        fixed_code = self.original_code
        for fix, method in [
            ("🔧 Fixing syntax errors", self.auto_fix_syntax_errors),
            ("🔧 Fixing missing brackets", self.fix_missing_brackets),
            ("🔧 Fixing missing quotes", self.fix_missing_quotes),
            ("🔄 Defining undefined variables", self.fix_undefined_variables),
            ("🔄 Replacing undefined returns", self.fix_undefined_returns),
            ("🎯 Fixing style issues", self.fix_style_issues),
            ("✨ Formatting with Black", self.auto_format_with_black)
        ]:
            print(fix + "...")
            fixed_code = method(fixed_code)

        print("\n✅ Corrected and Modified Code:")
        print(fixed_code)
        print("\n✅ Auto-fix completed.")
        return fixed_code

# Test with your example
if __name__ == "__main__":
    faulty_code = """
def test_function(x)
    if x>5
        print y
"""
    fixer = CodeAutoFixEngine(faulty_code)
    fixer.auto_fix_code()