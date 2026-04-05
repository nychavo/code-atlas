"""Python source-code structure extractor using the ``ast`` module."""

import ast
from pathlib import Path
from typing import Any

from codeatlas.analyzers.base.structure_extractor import BaseStructureExtractor


class PythonAstExtractor(BaseStructureExtractor):
    """Extracts structural information from Python source using the ``ast`` module."""

    def extract(self, file_path: Path, source_code: str) -> dict[str, Any]:
        """Parse *source_code* and return a rich structure dictionary."""
        try:
            tree = ast.parse(source_code, filename=str(file_path))
        except SyntaxError as exc:
            return {
                "error": str(exc),
                "imports": [],
                "classes": [],
                "functions": [],
                "constants": [],
                "globals": [],
                "docstring": None,
                "file_stats": self._compute_file_stats(source_code),
            }

        return {
            "docstring": ast.get_docstring(tree),
            "imports": self._extract_imports(tree),
            "classes": self._extract_classes(tree),
            "functions": self._extract_functions(tree),
            "constants": self._extract_constants(tree),
            "globals": self._extract_globals(tree),
            "file_stats": self._compute_file_stats(source_code),
        }

    # ------------------------------------------------------------------
    # Imports
    # ------------------------------------------------------------------

    def _extract_imports(self, tree: ast.Module) -> list[dict[str, Any]]:
        imports: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "module": alias.name,
                            "names": [alias.name],
                            "alias": alias.asname,
                            "is_from_import": False,
                            "is_relative": False,
                            "line_number": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = node.level
                names = [alias.name for alias in node.names]
                imports.append(
                    {
                        "module": ("." * level) + module,
                        "names": names,
                        "alias": node.names[0].asname if len(node.names) == 1 else None,
                        "is_from_import": True,
                        "is_relative": level > 0,
                        "line_number": node.lineno,
                    }
                )
        return imports

    # ------------------------------------------------------------------
    # Classes
    # ------------------------------------------------------------------

    def _extract_classes(self, tree: ast.Module) -> list[dict[str, Any]]:
        return [
            self._extract_class(node)
            for node in ast.iter_child_nodes(tree)
            if isinstance(node, ast.ClassDef)
        ]

    def _extract_class(self, node: ast.ClassDef) -> dict[str, Any]:
        decorators = [self._unparse_decorator(d) for d in node.decorator_list]
        base_classes = [ast.unparse(b) for b in node.bases]
        methods: list[dict[str, Any]] = []
        class_vars: list[str] = []
        instance_vars: list[str] = []

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_method(child))
                if child.name == "__init__":
                    instance_vars.extend(self._extract_instance_variables(child))
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        class_vars.append(target.id)
            elif isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name):
                    class_vars.append(child.target.id)

        return {
            "name": node.name,
            "qualified_name": node.name,
            "docstring": ast.get_docstring(node),
            "decorators": decorators,
            "base_classes": base_classes,
            "methods": methods,
            "class_variables": list(set(class_vars)),
            "instance_variables": list(set(instance_vars)),
            "line_start": node.lineno,
            "line_end": node.end_lineno or node.lineno,
            "is_dataclass": "dataclass" in decorators,
            "is_abstract": (
                any("ABC" in b or "Abstract" in b for b in base_classes)
                or any("abstractmethod" in d for d in decorators)
            ),
        }

    def _extract_method(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
        decorators = [self._unparse_decorator(d) for d in node.decorator_list]
        return {
            "name": node.name,
            "qualified_name": node.name,
            "docstring": ast.get_docstring(node),
            "decorators": decorators,
            "parameters": self._extract_parameters(node.args),
            "return_annotation": ast.unparse(node.returns) if node.returns else None,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "is_classmethod": "classmethod" in decorators,
            "is_staticmethod": "staticmethod" in decorators,
            "is_property": "property" in decorators,
            "is_abstract": "abstractmethod" in decorators,
            "line_start": node.lineno,
            "line_end": node.end_lineno or node.lineno,
            "local_variables": self._extract_local_variables(node),
        }

    # ------------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------------

    def _extract_functions(self, tree: ast.Module) -> list[dict[str, Any]]:
        functions = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = [self._unparse_decorator(d) for d in node.decorator_list]
                functions.append(
                    {
                        "name": node.name,
                        "qualified_name": node.name,
                        "docstring": ast.get_docstring(node),
                        "decorators": decorators,
                        "parameters": self._extract_parameters(node.args),
                        "return_annotation": ast.unparse(node.returns) if node.returns else None,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "local_variables": self._extract_local_variables(node),
                    }
                )
        return functions

    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    def _extract_parameters(self, args: ast.arguments) -> list[dict[str, Any]]:
        params: list[dict[str, Any]] = []

        for arg in args.args:
            params.append(
                {
                    "name": arg.arg,
                    "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
                    "default": None,
                    "kind": "positional",
                }
            )

        if args.vararg:
            params.append(
                {
                    "name": args.vararg.arg,
                    "annotation": ast.unparse(args.vararg.annotation) if args.vararg.annotation else None,
                    "default": None,
                    "kind": "var_positional",
                }
            )

        for arg in args.kwonlyargs:
            params.append(
                {
                    "name": arg.arg,
                    "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
                    "default": None,
                    "kind": "keyword_only",
                }
            )

        if args.kwarg:
            params.append(
                {
                    "name": args.kwarg.arg,
                    "annotation": ast.unparse(args.kwarg.annotation) if args.kwarg.annotation else None,
                    "default": None,
                    "kind": "var_keyword",
                }
            )

        # Attach defaults to positional parameters (right-aligned)
        positional = [p for p in params if p["kind"] == "positional"]
        for i, default in enumerate(reversed(args.defaults)):
            idx = len(positional) - 1 - i
            if 0 <= idx < len(positional):
                positional[idx]["default"] = ast.unparse(default)

        # Attach keyword-only defaults
        kw_only = [p for p in params if p["kind"] == "keyword_only"]
        for arg, default in zip(args.kwonlyargs, args.kw_defaults):
            for p in kw_only:
                if p["name"] == arg.arg and default is not None:
                    p["default"] = ast.unparse(default)

        return params

    # ------------------------------------------------------------------
    # Constants and globals
    # ------------------------------------------------------------------

    def _extract_constants(self, tree: ast.Module) -> list[dict[str, Any]]:
        constants = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append(
                            {
                                "name": target.id,
                                "value_repr": ast.unparse(node.value),
                                "annotation": None,
                                "line_number": node.lineno,
                            }
                        )
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id.isupper():
                    constants.append(
                        {
                            "name": node.target.id,
                            "value_repr": ast.unparse(node.value) if node.value else "None",
                            "annotation": ast.unparse(node.annotation),
                            "line_number": node.lineno,
                        }
                    )
        return constants

    def _extract_globals(self, tree: ast.Module) -> list[dict[str, Any]]:
        globals_list: list[dict[str, Any]] = []
        class_names = {n.name for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)}
        func_names = {
            n.name
            for n in ast.iter_child_nodes(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and not target.id.isupper()
                        and target.id not in class_names
                        and target.id not in func_names
                    ):
                        globals_list.append(
                            {
                                "name": target.id,
                                "value_repr": ast.unparse(node.value),
                                "annotation": None,
                                "line_number": node.lineno,
                            }
                        )
            elif isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Name)
                    and not node.target.id.isupper()
                    and node.target.id not in class_names
                ):
                    globals_list.append(
                        {
                            "name": node.target.id,
                            "value_repr": ast.unparse(node.value) if node.value else None,
                            "annotation": ast.unparse(node.annotation),
                            "line_number": node.lineno,
                        }
                    )
        return globals_list

    # ------------------------------------------------------------------
    # Variable helpers
    # ------------------------------------------------------------------

    def _extract_instance_variables(
        self, init_method: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[str]:
        ivars: list[str] = []
        for node in ast.walk(init_method):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                    ):
                        ivars.append(target.attr)
            elif isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Attribute)
                    and isinstance(node.target.value, ast.Name)
                    and node.target.value.id == "self"
                ):
                    ivars.append(node.target.attr)
        return ivars

    def _extract_local_variables(
        self, func: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[str]:
        locals_set: set[str] = set()
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        locals_set.add(target.id)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    locals_set.add(node.target.id)
        param_names = {arg.arg for arg in func.args.args}
        return list(locals_set - param_names)

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unparse_decorator(node: ast.expr) -> str:
        return ast.unparse(node)

    @staticmethod
    def _compute_file_stats(source_code: str) -> dict[str, int]:
        lines = source_code.splitlines()
        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())
        comment = sum(1 for line in lines if line.strip().startswith("#"))
        return {
            "size_bytes": len(source_code.encode("utf-8")),
            "line_count": total,
            "blank_line_count": blank,
            "comment_line_count": comment,
            "code_line_count": total - blank - comment,
        }
