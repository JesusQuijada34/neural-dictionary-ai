from __future__ import annotations
import ast

class CodeExpert:
    """Analizador local y estricto; no ejecuta código recibido del usuario."""
    def analyze(self, text: str) -> dict:
        source = self._extract(text); result = {"language": "python", "safe_to_execute": False, "valid": False, "issues": [], "advice": []}
        try:
            tree = ast.parse(source); result["valid"] = True
            names = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
            imports = [ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            result.update({"definitions": names, "imports": imports, "lines": len(source.splitlines())})
            if any(isinstance(node, (ast.Exec,)) for node in ast.walk(tree)) if hasattr(ast, "Exec") else False: result["issues"].append("instrucción exec detectada")
            if any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"} for node in ast.walk(tree)):
                result["issues"].append("eval/exec no recomendado: puede ejecutar texto arbitrario")
            result["advice"].append("El análisis fue estático; no se ejecutó el programa.")
        except SyntaxError as exc:
            result["issues"].append(f"Error de sintaxis en línea {exc.lineno}: {exc.msg}")
            result["advice"].append("Corrige la sintaxis antes de probar el código.")
        return result

    def _extract(self, text):
        if "```" in text:
            parts = text.split("```")
            return parts[1].removeprefix("python").strip() if len(parts)>1 else text
        return text
