"""Python artifact builder — assembles Artifact objects from extracted data."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codeatlas.analyzers.base.artifact_builder import BaseArtifactBuilder
from codeatlas.core.enums import ArtifactType, Language, SymbolKind
from codeatlas.models.artifact_models import (
    Artifact,
    ClassRecord,
    ConstantRecord,
    DependencyRecord,
    ExportRecord,
    FileStats,
    FunctionRecord,
    GlobalRecord,
    ImportRecord,
    MetadataRecord,
    MethodRecord,
    ParameterRecord,
    SummaryRecord,
)
from codeatlas.utils.artifact_id_helper import ArtifactIdHelper
from codeatlas.utils.hash_helper import HashHelper
from codeatlas.utils.module_name_helper import ModuleNameHelper
from codeatlas.utils.symbol_id_helper import SymbolIdHelper


class PythonArtifactBuilder(BaseArtifactBuilder):
    """Builds :class:`~codeatlas.models.artifact_models.Artifact` objects for Python files."""

    def __init__(self, settings: Any, project_id: str) -> None:
        self.settings = settings
        self.project_id = project_id

    def build(
        self,
        file_path: Path,
        raw_structure: dict[str, Any],
        dependencies: list[DependencyRecord],
    ) -> Artifact:
        """Assemble and return a complete Artifact for *file_path*."""
        root_path = self.settings.root_path
        rel_path = file_path.relative_to(root_path)
        module_name = ModuleNameHelper.derive_module_name(file_path, root_path)
        artifact_id = ArtifactIdHelper.generate(self.project_id, str(rel_path))
        file_hash = HashHelper.hash_file(file_path)

        file_stats = self._build_file_stats(raw_structure.get("file_stats", {}))
        imports = [self._build_import(imp, artifact_id) for imp in raw_structure.get("imports", [])]
        classes = [self._build_class(cls, artifact_id, module_name) for cls in raw_structure.get("classes", [])]
        functions = [self._build_function(fn, artifact_id, module_name) for fn in raw_structure.get("functions", [])]
        constants = [self._build_constant(c, artifact_id) for c in raw_structure.get("constants", [])]
        globals_list = [self._build_global(g, artifact_id) for g in raw_structure.get("globals", [])]
        exports = self._build_exports(classes, functions, constants, module_name)

        summary = raw_structure.get(
            "summary",
            SummaryRecord(
                purpose="",
                architectural_layer="unknown",
                key_dependencies=[],
                key_exports=[],
                unresolved_areas=[],
                complexity_notes=[],
            ),
        )

        return Artifact(
            schema_version=self.settings.schema_version,
            project_id=self.project_id,
            artifact_id=artifact_id,
            artifact_type=ArtifactType.FILE.value,
            language=Language.PYTHON.value,
            path=str(file_path),
            relative_path=str(rel_path),
            module_name=module_name,
            hash=file_hash,
            file_stats=file_stats,
            docstring=raw_structure.get("docstring"),
            summary=summary,
            imports=imports,
            exports=exports,
            classes=classes,
            functions=functions,
            constants=constants,
            globals=globals_list,
            dependencies=dependencies,
            references=[],
            metadata=MetadataRecord(
                created_at=datetime.now(timezone.utc).isoformat(),
                analyzer_version="0.1.0",
                schema_version=self.settings.schema_version,
                language=Language.PYTHON.value,
            ),
        )

    # ------------------------------------------------------------------
    # Sub-builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_file_stats(data: dict[str, Any]) -> FileStats:
        return FileStats(
            size_bytes=data.get("size_bytes", 0),
            line_count=data.get("line_count", 0),
            blank_line_count=data.get("blank_line_count", 0),
            comment_line_count=data.get("comment_line_count", 0),
            code_line_count=data.get("code_line_count", 0),
        )

    @staticmethod
    def _build_import(imp: dict[str, Any], artifact_id: str) -> ImportRecord:
        module = imp.get("module", "")
        symbol_id = SymbolIdHelper.generate(artifact_id, module, SymbolKind.IMPORT.value)
        return ImportRecord(
            import_id=symbol_id,
            module=module,
            names=imp.get("names", []),
            alias=imp.get("alias"),
            is_from_import=imp.get("is_from_import", False),
            is_stdlib=imp.get("is_stdlib", False),
            is_relative=imp.get("is_relative", False),
            line_number=imp.get("line_number", 0),
            confidence=imp.get("confidence", 1.0),
        )

    @staticmethod
    def _build_class(cls: dict[str, Any], artifact_id: str, module_name: str) -> ClassRecord:
        class_id = SymbolIdHelper.generate(artifact_id, cls["name"], SymbolKind.CLASS.value)
        qualified = f"{module_name}.{cls['name']}"
        methods = [
            PythonArtifactBuilder._build_method(m, artifact_id, qualified)
            for m in cls.get("methods", [])
        ]
        is_pydantic = any("BaseModel" in b for b in cls.get("base_classes", []))
        return ClassRecord(
            class_id=class_id,
            name=cls["name"],
            qualified_name=qualified,
            docstring=cls.get("docstring"),
            decorators=cls.get("decorators", []),
            base_classes=cls.get("base_classes", []),
            resolved_base_classes=cls.get("resolved_base_classes", cls.get("base_classes", [])),
            methods=methods,
            class_variables=cls.get("class_variables", []),
            instance_variables=cls.get("instance_variables", []),
            line_start=cls.get("line_start", 0),
            line_end=cls.get("line_end", 0),
            is_abstract=cls.get("is_abstract", False),
            is_dataclass=cls.get("is_dataclass", False),
            is_pydantic=is_pydantic,
        )

    @staticmethod
    def _build_method(method: dict[str, Any], artifact_id: str, class_qualified: str) -> MethodRecord:
        method_id = SymbolIdHelper.generate(artifact_id, f"{class_qualified}.{method['name']}", SymbolKind.METHOD.value)
        params = [ParameterRecord(**p) for p in method.get("parameters", [])]
        return MethodRecord(
            method_id=method_id,
            name=method["name"],
            qualified_name=f"{class_qualified}.{method['name']}",
            docstring=method.get("docstring"),
            decorators=method.get("decorators", []),
            parameters=params,
            return_annotation=method.get("return_annotation"),
            is_async=method.get("is_async", False),
            is_classmethod=method.get("is_classmethod", False),
            is_staticmethod=method.get("is_staticmethod", False),
            is_property=method.get("is_property", False),
            is_abstract=method.get("is_abstract", False),
            line_start=method.get("line_start", 0),
            line_end=method.get("line_end", 0),
            local_variables=method.get("local_variables", []),
        )

    @staticmethod
    def _build_function(fn: dict[str, Any], artifact_id: str, module_name: str) -> FunctionRecord:
        fn_id = SymbolIdHelper.generate(artifact_id, fn["name"], SymbolKind.FUNCTION.value)
        params = [ParameterRecord(**p) for p in fn.get("parameters", [])]
        return FunctionRecord(
            function_id=fn_id,
            name=fn["name"],
            qualified_name=f"{module_name}.{fn['name']}",
            docstring=fn.get("docstring"),
            decorators=fn.get("decorators", []),
            parameters=params,
            return_annotation=fn.get("return_annotation"),
            is_async=fn.get("is_async", False),
            line_start=fn.get("line_start", 0),
            line_end=fn.get("line_end", 0),
            local_variables=fn.get("local_variables", []),
        )

    @staticmethod
    def _build_constant(c: dict[str, Any], artifact_id: str) -> ConstantRecord:
        cid = SymbolIdHelper.generate(artifact_id, c["name"], SymbolKind.CONSTANT.value)
        return ConstantRecord(
            constant_id=cid,
            name=c["name"],
            value_repr=c.get("value_repr", ""),
            annotation=c.get("annotation"),
            line_number=c.get("line_number", 0),
        )

    @staticmethod
    def _build_global(g: dict[str, Any], artifact_id: str) -> GlobalRecord:
        gid = SymbolIdHelper.generate(artifact_id, g["name"], SymbolKind.GLOBAL.value)
        return GlobalRecord(
            global_id=gid,
            name=g["name"],
            value_repr=g.get("value_repr"),
            annotation=g.get("annotation"),
            line_number=g.get("line_number", 0),
        )

    @staticmethod
    def _build_exports(
        classes: list[ClassRecord],
        functions: list[FunctionRecord],
        constants: list[ConstantRecord],
        module_name: str,
    ) -> list[ExportRecord]:
        exports: list[ExportRecord] = []
        for cls in classes:
            is_public = not cls.name.startswith("_")
            exports.append(
                ExportRecord(
                    export_id=cls.class_id,
                    name=cls.name,
                    kind=SymbolKind.CLASS.value,
                    line_number=cls.line_start,
                    is_public=is_public,
                )
            )
        for fn in functions:
            is_public = not fn.name.startswith("_")
            exports.append(
                ExportRecord(
                    export_id=fn.function_id,
                    name=fn.name,
                    kind=SymbolKind.FUNCTION.value,
                    line_number=fn.line_start,
                    is_public=is_public,
                )
            )
        for const in constants:
            exports.append(
                ExportRecord(
                    export_id=const.constant_id,
                    name=const.name,
                    kind=SymbolKind.CONSTANT.value,
                    line_number=const.line_number,
                    is_public=True,
                )
            )
        return exports
