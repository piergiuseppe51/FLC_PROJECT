from parser import (
    Number, String, Boolean, Var, BinOp, UnaryOp, 
    AssignStat, PrintStat, IfStat, ForStat, InputExpr, 
    FunctionDecl, FunctionCall, ExprStat, ReturnStat
)
from semantic import SemanticAnalyzer

"""
Helper script to simulate the transpiler logic.
Displays the symbol table state to verify type inference.
Requires manual AST insertion from the parser into the 'ast' list.
"""

def run_manual_test():
    print("--- MANUAL AST TEST---")
    
    # Initialize analyzer
    analyzer = SemanticAnalyzer()

    ast = [
        FunctionDecl(
            name='count_chocolate_squares',
            params=['length', 'width'],
            body=[
                AssignStat(
                    name='total_squares',
                    value=BinOp(
                        left=Var(name='length'),
                        op='*',
                        right=Var(name='width')
                    )
                ),
                ReturnStat(value=Var(name='total_squares'))
            ]
        ),
        AssignStat(name='bar_length', value=Number(value=10)),
        AssignStat(name='bar_width', value=Number(value=5)),
        AssignStat(
            name='deliciousness',
            value=FunctionCall(
                name='count_chocolate_squares',
                args=[Var(name='bar_length'), Var(name='bar_width')]
            )
        ),
        PrintStat(value=Var(name='deliciousness'))
    ]

    # Run analysis
    try:
        analyzer.visit(ast)
        print("Analysis completed without crash.\n")
    except Exception as e:
        print(f"Analysis failed with error: {e}")

    # Print final symbol table state
    print("--- FINAL SYMBOL TABLE STATE ---")
    global_scope = analyzer.symbol_table[0]
    
    for name, value in global_scope.items():
        if isinstance(value, dict) and value.get('tag') == 'function':
            # Check for cache (only visible if using the new semantic analyzer)
            cache = value.get('cache', 'No cache')
            print(f"FUNCTION '{name}' -> Cache: {cache}")
        else:
            print(f"VARIABLE '{name}' -> Type: {value}")

if __name__ == "__main__":
    run_manual_test()