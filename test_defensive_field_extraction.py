#!/usr/bin/env python3

"""
=============================================================================
DEFENSIVE FIELD EXTRACTION PATTERN TEST SCRIPT
=============================================================================

This script tests that all post-merge pipeline files (pretty_print.py, 
pretty_conversion.py, monitoring.py) follow the standardized defensive 
field extraction pattern.

TEST CRITERIA:
1. Uses .get() methods for safe field access
2. Uses isinstance() for type validation
3. Uses safe array access with length validation
4. Uses string cleaning with .strip()
5. Uses try/except blocks for error handling
6. Individual field extraction (not lazy mirroring)

PIPELINE FILES TESTED:
- pretty_print.py
- pretty_conversion.py  
- monitoring.py

EXPECTED PATTERNS:
✅ match.get("field_name", default_value)
✅ isinstance(data, expected_type)
✅ len(array) >= X before array[X]
✅ str(value).strip()
✅ try/except blocks around risky operations
✅ Individual field extraction per match

❌ Direct field access: match["field_name"]
❌ No type validation before nested access
❌ Direct array access without length check
❌ Lazy mirroring/copying entire objects
=============================================================================
"""

import ast
import os
import sys
from typing import List, Dict, Any, Tuple

class DefensivePatternAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze defensive programming patterns"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.results = {
            'get_method_usage': [],
            'isinstance_checks': [],
            'safe_array_access': [],
            'string_strip_usage': [],
            'try_except_blocks': [],
            'direct_field_access': [],
            'unsafe_array_access': [],
            'function_definitions': []
        }
        self.current_function = None
        self.in_try_block = False
        
    def visit_FunctionDef(self, node):
        """Track function definitions"""
        self.current_function = node.name
        self.results['function_definitions'].append({
            'name': node.name,
            'line': node.lineno,
            'args': [arg.arg for arg in node.args.args]
        })
        self.generic_visit(node)
        self.current_function = None
        
    def visit_Try(self, node):
        """Track try/except blocks"""
        self.in_try_block = True
        self.results['try_except_blocks'].append({
            'line': node.lineno,
            'function': self.current_function,
            'handlers': len(node.handlers)
        })
        self.generic_visit(node)
        self.in_try_block = False
        
    def visit_Call(self, node):
        """Analyze method calls"""
        # Check for .get() method usage
        if (isinstance(node.func, ast.Attribute) and 
            node.func.attr == 'get' and 
            len(node.args) >= 1):
            
            field_name = None
            default_value = None
            
            if isinstance(node.args[0], ast.Constant):
                field_name = node.args[0].value
            elif isinstance(node.args[0], ast.Str):  # Python < 3.8
                field_name = node.args[0].s
                
            if len(node.args) >= 2:
                if isinstance(node.args[1], ast.Constant):
                    default_value = node.args[1].value
                elif isinstance(node.args[1], ast.Str):
                    default_value = node.args[1].s
                    
            self.results['get_method_usage'].append({
                'line': node.lineno,
                'function': self.current_function,
                'field_name': field_name,
                'default_value': default_value
            })
            
        # Check for isinstance() calls
        elif (isinstance(node.func, ast.Name) and 
              node.func.id == 'isinstance' and 
              len(node.args) >= 2):
            
            self.results['isinstance_checks'].append({
                'line': node.lineno,
                'function': self.current_function,
                'variable': ast.unparse(node.args[0]) if hasattr(ast, 'unparse') else 'unknown',
                'type_check': ast.unparse(node.args[1]) if hasattr(ast, 'unparse') else 'unknown'
            })
            
        # Check for .strip() method usage
        elif (isinstance(node.func, ast.Attribute) and 
              node.func.attr == 'strip'):
            
            self.results['string_strip_usage'].append({
                'line': node.lineno,
                'function': self.current_function
            })
            
        # Check for len() calls (potential safe array access)
        elif (isinstance(node.func, ast.Name) and 
              node.func.id == 'len'):
            
            self.results['safe_array_access'].append({
                'line': node.lineno,
                'function': self.current_function,
                'array_name': ast.unparse(node.args[0]) if hasattr(ast, 'unparse') else 'unknown'
            })
            
        self.generic_visit(node)
        
    def visit_Subscript(self, node):
        """Analyze array/dict access patterns"""
        # Check for direct dictionary access (potentially unsafe)
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            self.results['direct_field_access'].append({
                'line': node.lineno,
                'function': self.current_function,
                'field_name': node.slice.value,
                'object': ast.unparse(node.value) if hasattr(ast, 'unparse') else 'unknown'
            })
        # Check for direct array index access (potentially unsafe)
        elif isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
            self.results['unsafe_array_access'].append({
                'line': node.lineno,
                'function': self.current_function,
                'index': node.slice.value,
                'array': ast.unparse(node.value) if hasattr(ast, 'unparse') else 'unknown'
            })
            
        self.generic_visit(node)

def analyze_file(filepath: str) -> Dict[str, Any]:
    """Analyze a Python file for defensive programming patterns"""
    
    if not os.path.exists(filepath):
        return {
            'file': filepath,
            'exists': False,
            'error': f"File not found: {filepath}"
        }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tree = ast.parse(content)
        analyzer = DefensivePatternAnalyzer(filepath)
        analyzer.visit(tree)
        
        return {
            'file': filepath,
            'exists': True,
            'patterns': analyzer.results,
            'line_count': len(content.split('\n'))
        }
        
    except Exception as e:
        return {
            'file': filepath,
            'exists': True,
            'error': f"Analysis failed: {e}"
        }

def evaluate_defensive_patterns(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate how well a file follows defensive patterns"""
    
    if not analysis.get('exists') or 'error' in analysis:
        return {
            'score': 0,
            'issues': [analysis.get('error', 'Unknown error')],
            'strengths': []
        }
    
    patterns = analysis['patterns']
    issues = []
    strengths = []
    score = 0
    
    # Check for .get() method usage (CRITICAL)
    get_usage = len(patterns['get_method_usage'])
    if get_usage >= 10:
        strengths.append(f"✅ Excellent .get() usage: {get_usage} instances")
        score += 25
    elif get_usage >= 5:
        strengths.append(f"✅ Good .get() usage: {get_usage} instances")
        score += 20
    elif get_usage >= 1:
        strengths.append(f"⚠️ Limited .get() usage: {get_usage} instances")
        score += 10
    else:
        issues.append(f"❌ No .get() method usage found - CRITICAL defensive pattern missing")
    
    # Check for isinstance() validation (IMPORTANT)
    isinstance_usage = len(patterns['isinstance_checks'])
    if isinstance_usage >= 5:
        strengths.append(f"✅ Excellent type validation: {isinstance_usage} isinstance() checks")
        score += 20
    elif isinstance_usage >= 2:
        strengths.append(f"✅ Good type validation: {isinstance_usage} isinstance() checks")
        score += 15
    elif isinstance_usage >= 1:
        strengths.append(f"⚠️ Limited type validation: {isinstance_usage} isinstance() checks")
        score += 5
    else:
        issues.append(f"❌ No isinstance() type validation found")
    
    # Check for safe array access (len() usage)
    len_usage = len(patterns['safe_array_access'])
    if len_usage >= 3:
        strengths.append(f"✅ Good array safety: {len_usage} length checks")
        score += 15
    elif len_usage >= 1:
        strengths.append(f"⚠️ Limited array safety: {len_usage} length checks")
        score += 5
    else:
        issues.append(f"❌ No array length validation found")
    
    # Check for string cleaning (.strip() usage)
    strip_usage = len(patterns['string_strip_usage'])
    if strip_usage >= 3:
        strengths.append(f"✅ Good string cleaning: {strip_usage} .strip() calls")
        score += 10
    elif strip_usage >= 1:
        strengths.append(f"⚠️ Limited string cleaning: {strip_usage} .strip() calls")
        score += 5
    
    # Check for error handling (try/except blocks)
    try_except_usage = len(patterns['try_except_blocks'])
    if try_except_usage >= 3:
        strengths.append(f"✅ Good error handling: {try_except_usage} try/except blocks")
        score += 15
    elif try_except_usage >= 1:
        strengths.append(f"⚠️ Limited error handling: {try_except_usage} try/except blocks")
        score += 5
    else:
        issues.append(f"❌ No try/except error handling found")
    
    # Check for risky patterns (direct field access)
    direct_access = len(patterns['direct_field_access'])
    if direct_access > 10:
        issues.append(f"⚠️ High direct field access: {direct_access} instances (prefer .get())")
        score -= 5
    elif direct_access > 5:
        issues.append(f"⚠️ Moderate direct field access: {direct_access} instances")
    
    # Check for unsafe array access
    unsafe_arrays = len(patterns['unsafe_array_access'])
    if unsafe_arrays > 10:
        issues.append(f"⚠️ High unsafe array access: {unsafe_arrays} instances (check length first)")
        score -= 5
    elif unsafe_arrays > 5:
        issues.append(f"⚠️ Moderate unsafe array access: {unsafe_arrays} instances")
    
    # Check for required functions
    functions = [f['name'] for f in patterns['function_definitions']]
    required_functions = ['extract_match_fields', 'main']
    
    for func in required_functions:
        if func in functions:
            strengths.append(f"✅ Required function found: {func}()")
            score += 5
        else:
            issues.append(f"❌ Required function missing: {func}()")
    
    return {
        'score': max(0, min(100, score)),
        'issues': issues,
        'strengths': strengths,
        'pattern_counts': {
            'get_usage': get_usage,
            'isinstance_checks': isinstance_usage,
            'len_checks': len_usage,
            'strip_usage': strip_usage,
            'try_except': try_except_usage,
            'direct_access': direct_access,
            'unsafe_arrays': unsafe_arrays
        }
    }

def test_pipeline_files():
    """Test all pipeline files for defensive patterns"""
    
    files_to_test = [
        '/workspaces/TMUX_FINAL_SPORTS/pretty_print.py',
        '/workspaces/TMUX_FINAL_SPORTS/pretty_conversion.py',
        '/workspaces/TMUX_FINAL_SPORTS/monitoring.py'
    ]
    
    print("=" * 80)
    print("DEFENSIVE FIELD EXTRACTION PATTERN TEST")
    print("=" * 80)
    print()
    
    results = {}
    total_score = 0
    
    for filepath in files_to_test:
        filename = os.path.basename(filepath)
        print(f"🔍 TESTING: {filename}")
        print("-" * 50)
        
        # Analyze file
        analysis = analyze_file(filepath)
        evaluation = evaluate_defensive_patterns(analysis)
        
        results[filename] = {
            'analysis': analysis,
            'evaluation': evaluation
        }
        
        score = evaluation['score']
        total_score += score
        
        print(f"SCORE: {score}/100")
        print()
        
        # Print strengths
        if evaluation['strengths']:
            print("STRENGTHS:")
            for strength in evaluation['strengths']:
                print(f"  {strength}")
            print()
        
        # Print issues
        if evaluation['issues']:
            print("ISSUES:")
            for issue in evaluation['issues']:
                print(f"  {issue}")
            print()
        
        # Print pattern summary
        patterns = evaluation['pattern_counts']
        print("PATTERN SUMMARY:")
        print(f"  .get() usage: {patterns['get_usage']}")
        print(f"  isinstance() checks: {patterns['isinstance_checks']}")
        print(f"  len() checks: {patterns['len_checks']}")
        print(f"  .strip() usage: {patterns['strip_usage']}")
        print(f"  try/except blocks: {patterns['try_except']}")
        print(f"  Direct field access: {patterns['direct_access']}")
        print(f"  Unsafe array access: {patterns['unsafe_arrays']}")
        print()
        print("=" * 50)
        print()
    
    # Overall summary
    avg_score = total_score / len(files_to_test)
    print(f"OVERALL PIPELINE SCORE: {avg_score:.1f}/100")
    print()
    
    if avg_score >= 90:
        print("🎉 EXCELLENT: Pipeline follows defensive patterns consistently!")
    elif avg_score >= 75:
        print("✅ GOOD: Pipeline follows most defensive patterns")
    elif avg_score >= 60:
        print("⚠️ MODERATE: Pipeline needs improvement in defensive patterns")
    else:
        print("❌ POOR: Pipeline lacks critical defensive patterns")
    
    print()
    print("RECOMMENDATIONS:")
    print("1. Ensure ALL field access uses .get() with fallback defaults")
    print("2. Add isinstance() checks before accessing nested objects")
    print("3. Check array length before accessing elements")
    print("4. Use .strip() for string cleaning")
    print("5. Wrap risky operations in try/except blocks")
    print("6. Follow individual field extraction pattern (not lazy mirroring)")
    
    return results

if __name__ == "__main__":
    results = test_pipeline_files()
    
    # Exit with appropriate code
    total_issues = sum(len(r['evaluation']['issues']) for r in results.values())
    if total_issues == 0:
        print("\n✅ ALL TESTS PASSED - Pipeline follows defensive patterns!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total_issues} ISSUES FOUND - Review and fix defensive patterns")
        sys.exit(1)