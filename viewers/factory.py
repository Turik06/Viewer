"""!
@file viewers/factory.py
@brief Factory and registry for mapping file extensions and names to viewer widgets.
"""

import os
from collections.abc import Iterable
from typing import Callable
from PyQt6.QtWidgets import QWidget

from viewers.base import BaseViewerWidget, MessageViewerWidget


class ViewerFactory:
    """!
    @brief Factory and registry for creating file viewer widgets.
    @details Implements Registry and Factory patterns to associate file extensions
             and specific filenames with BaseViewerWidget implementations.
    """

    _registry: dict[str, type[BaseViewerWidget]] = {}
    _default_viewer_class: type[BaseViewerWidget] | None = None

    @classmethod
    def _normalize_key(cls, key: str) -> str:
        """!
        @brief Normalize an extension or filename key for uniform dictionary lookups.
        @param key File extension (e.g. '.txt', 'txt') or filename (e.g. 'Dockerfile').
        @return Lowercased string representation.
        """
        return key.strip().lower()

    @classmethod
    def register(
        cls,
        extensions: str | Iterable[str],
        viewer_cls: type[BaseViewerWidget] | None = None,
    ) -> Callable[[type[BaseViewerWidget]], type[BaseViewerWidget]] | None:
        """!
        @brief Register a viewer class for one or multiple file extensions/names.
        @details Can be called directly or used as a class decorator.
        @param extensions A single extension/filename or an iterable of extensions/filenames.
        @param viewer_cls Subclass of BaseViewerWidget to register. If None, returns a decorator.
        @return Decorator function if viewer_cls is None, otherwise None.
        """
        if isinstance(extensions, str):
            ext_list = [extensions]
        else:
            ext_list = list(extensions)

        def decorator(target_cls: type[BaseViewerWidget]) -> type[BaseViewerWidget]:
            for item in ext_list:
                norm = cls._normalize_key(item)
                cls._registry[norm] = target_cls
                # Also register with leading dot if it is an extension without one
                if not norm.startswith(".") and not any(sep in norm for sep in ("/", "\\")):
                    cls._registry[f".{norm}"] = target_cls
            return target_cls

        if viewer_cls is not None:
            decorator(viewer_cls)
            return None
        return decorator

    @classmethod
    def unregister(cls, extension: str) -> bool:
        """!
        @brief Unregister a file extension or filename.
        @param extension Extension or filename to unregister.
        @return True if key was found and removed, False otherwise.
        """
        norm = cls._normalize_key(extension)
        removed = False
        if norm in cls._registry:
            del cls._registry[norm]
            removed = True
        dot_variant = f".{norm}" if not norm.startswith(".") else norm.lstrip(".")
        if dot_variant in cls._registry:
            del cls._registry[dot_variant]
            removed = True
        return removed

    @classmethod
    def clear_registry(cls) -> None:
        """!
        @brief Clear all registered viewer classes and reset default viewer.
        """
        cls._registry.clear()
        cls._default_viewer_class = None

    @classmethod
    def register_default(cls, viewer_cls: type[BaseViewerWidget] | None) -> None:
        """!
        @brief Set default fallback viewer class when no specific viewer matches.
        @param viewer_cls BaseViewerWidget subclass or None to clear default.
        """
        cls._default_viewer_class = viewer_cls

    @classmethod
    def get_default_viewer_class(cls) -> type[BaseViewerWidget] | None:
        """!
        @brief Get default fallback viewer class.
        @return BaseViewerWidget subclass or None if not set.
        """
        return cls._default_viewer_class

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """!
        @brief Get sorted list of all registered extensions and filenames.
        @return List of registered extension/filename strings.
        """
        return sorted(cls._registry.keys())

    @classmethod
    def get_viewer_class(cls, filepath_or_ext: str) -> type[BaseViewerWidget] | None:
        """!
        @brief Resolve viewer class for a given file path or extension.
        @param filepath_or_ext Path to file or extension string.
        @return Matching BaseViewerWidget subclass, default viewer class, or None.
        """
        raw = cls._normalize_key(filepath_or_ext)

        # 1. Direct match in registry (e.g. '.txt', 'dockerfile')
        if raw in cls._registry:
            return cls._registry[raw]

        # 2. Match with dot prefix if raw has no separators and no dot
        if not raw.startswith(".") and not any(sep in raw for sep in ("/", "\\")):
            with_dot = f".{raw}"
            if with_dot in cls._registry:
                return cls._registry[with_dot]

        # 3. Extract filename
        filename = os.path.basename(raw)
        if filename in cls._registry:
            return cls._registry[filename]

        # 4. Multi-part extension matching (e.g. file.tar.gz -> .tar.gz, then .gz)
        parts = filename.split(".")
        if len(parts) > 1:
            for i in range(1, len(parts)):
                compound_ext = "." + ".".join(parts[i:])
                if compound_ext in cls._registry:
                    return cls._registry[compound_ext]

        # 5. Default fallback viewer
        return cls._default_viewer_class

    @classmethod
    def create_viewer(
        cls,
        filepath: str,
        parent: QWidget | None = None,
    ) -> BaseViewerWidget | None:
        """!
        @brief Instantiate the registered viewer for a given file path.
        @param filepath Path to the file.
        @param parent Optional parent widget.
        @return Instantiated BaseViewerWidget subclass or None if not supported/failed.
        """
        viewer_cls = cls.get_viewer_class(filepath)
        if viewer_cls is None:
            return None
        try:
            return viewer_cls(parent=parent)
        except Exception:
            return None

    @classmethod
    def create_viewer_or_fallback(
        cls,
        filepath: str,
        parent: QWidget | None = None,
    ) -> BaseViewerWidget:
        """!
        @brief Instantiate registered viewer, or fallback MessageViewerWidget if unsupported.
        @param filepath Path to the file.
        @param parent Optional parent widget.
        @return BaseViewerWidget instance ready to be displayed.
        """
        viewer = cls.create_viewer(filepath, parent=parent)
        if viewer is not None:
            return viewer

        filename = os.path.basename(filepath)
        message = f"Формат файла '{filename}' не поддерживается"
        fallback = MessageViewerWidget(message=message, parent=parent)
        return fallback
