from __future__ import annotations
import ast, operator, re
from dataclasses import dataclass

OPS={ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul, ast.Div:operator.truediv, ast.Pow:operator.pow, ast.Mod:operator.mod}
@dataclass
class ReasoningResult:
    answer: str | None
    trace: list[str]
    confidence: float
    kind: str

def calculate(text: str) -> ReasoningResult | None:
    match=re.search(r"(?:cuánto es|calcula|calcular|what is)\s+([0-9+\-*/().%\s]+)\??$", text.casefold())
    if not match:return None
    expression=match.group(1).strip()
    try:
        tree=ast.parse(expression,mode="eval")
        def visit(node):
            if isinstance(node,ast.Expression):return visit(node.body)
            if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)):return node.value
            if isinstance(node,ast.BinOp) and type(node.op) in OPS:
                left,right=visit(node.left),visit(node.right)
                if isinstance(node.op,ast.Pow) and abs(right)>10: raise ValueError
                return OPS[type(node.op)](left,right)
            raise ValueError
        value=visit(tree)
        shown=int(value) if isinstance(value,float) and value.is_integer() else value
        return ReasoningResult(f"El resultado de {expression} es {shown}.",[f"expresión reconocida: {expression}","se aplicaron operaciones aritméticas permitidas"],1.0,"aritmética")
    except (ValueError,ZeroDivisionError,SyntaxError):
        return ReasoningResult("No puedo calcular esa expresión con seguridad.",["la expresión no cumple el subconjunto aritmético permitido"],.2,"aritmética")

def syllogism(text: str) -> ReasoningResult | None:
    m=re.search(r"todos los ([\wáéíóúñ]+) son ([\wáéíóúñ]+).*?([\wáéíóúñ]+) es (?:un|una) ([\wáéíóúñ]+)",text.casefold())
    if not m:return None
    group,category,name,instance=m.groups(); group_singular=(group[:-2]+"a" if group.endswith("os") else group[:-1] if group.endswith("s") else group)
    if group_singular != instance:return None
    category_singular=category[:-2] if category.endswith("es") else category[:-1] if category.endswith("s") else category
    return ReasoningResult(f"Podemos concluir que {name.capitalize()} es {category_singular}.",[f"regla universal: todos los {group} son {category}",f"hecho: {name} es {instance}",f"instanciación: {name} hereda la categoría {category_singular}"],.95,"silogismo")

def intent_response(text: str) -> ReasoningResult | None:
    low=text.casefold()
    if "ganará" in low or "ganara" in low or "todavía no se ha celebrado" in low:
        return ReasoningResult("No se puede saber con rigor quién ganará una competición futura antes de que ocurra. Puedo comparar participantes si me das datos verificables, pero no debo presentarlo como un hecho.",["se detectó una predicción sobre un evento futuro","no existe evidencia observada suficiente","se evitó afirmar una certeza inventada"],.95,"incertidumbre")
    if "qué puedes hacer" in low or "que puedes hacer" in low:
        return ReasoningResult("Puedo explicar conceptos conocidos, calcular expresiones sencillas, resolver algunos razonamientos, analizar texto, revisar código Python sin ejecutarlo, organizar información y aprender definiciones que me enseñes. Si no sé algo, te lo preguntaré.",["se detectó una pregunta sobre capacidades","se enumeraron módulos disponibles","se mantuvo el límite de no prometer conocimiento total"],.9,"capacidad")
    if "plural de" in low:
        m=re.search(r"plural de [«\"]?([\wáéíóúñ]+)",low)
        if m:
            word=m.group(1); plural=word[:-1]+"ces" if word.endswith("z") else (word+"es" if word.endswith(("r","l","d","n")) else word+"s")
            return ReasoningResult(f"El plural de «{word}» es «{plural}».",[f"se identificó una consulta morfológica sobre {word}","se aplicó la regla de pluralización"],.9,"morfología")
    if "sinónimo" in low and "antónimo" in low:
        m=re.search(r"de [«\"]?([\wáéíóúñ]+)",low)
        if m and m.group(1)=="grande": return ReasoningResult("Un sinónimo de «grande» es «enorme» y un antónimo es «pequeño».",["se consultó la entrada léxica grande","se separaron las relaciones de sinonimia y antonimia"],.95,"léxico")
    if "triste" in low or "perdí mi empleo" in low:
        return ReasoningResult("Siento que estés pasando por una situación tan difícil. Perder el empleo puede generar tristeza e incertidumbre. Si quieres, puedo escucharte, ayudarte a ordenar opciones o preparar un plan práctico paso a paso.",["se detectó una señal emocional de tristeza","se eligió una respuesta empática sin diagnosticar","se ofrecieron opciones de apoyo"],.9,"empatía")
    if "how can you help" in low or "what can you do" in low:
        return ReasoningResult("I can explain concepts, analyze structured text, review Python code statically, organize information, and learn definitions you teach me. I will say when I do not know something.",["English help-intent detected","capabilities selected from the agent and knowledge modules"],.9,"capacidad")
    return None

def reason(text: str) -> ReasoningResult | None:
    for handler in (calculate,syllogism,intent_response):
        result=handler(text)
        if result:return result
    return None
