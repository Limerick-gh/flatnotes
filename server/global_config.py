import json
import os
import sys
from enum import Enum

from helpers import CustomBaseModel, get_env
from logger import logger


class GlobalConfig:
    def __init__(self) -> None:
        logger.debug("Loading global config...")
        self.auth_type: AuthType = self._load_auth_type()
        self.quick_access_hide: bool = self._quick_access_hide()
        self.quick_access_title: str = self._quick_access_title()
        self.quick_access_term: str = self._quick_access_term()
        self.quick_access_sort: str = self._quick_access_sort()
        self.quick_access_limit: int = self._quick_access_limit()
        self.tag_hierarchy: dict[str, list[str]] = self._tag_hierarchy()
        self.path_prefix: str = self._load_path_prefix()

    def load_auth(self):
        if self.auth_type in (AuthType.NONE, AuthType.READ_ONLY):
            return None
        elif self.auth_type in (AuthType.PASSWORD, AuthType.TOTP):
            from auth.local import LocalAuth

            return LocalAuth()

    def load_note_storage(self):
        from notes.file_system import FileSystemNotes

        return FileSystemNotes()

    def load_attachment_storage(self):
        from attachments.file_system import FileSystemAttachments

        return FileSystemAttachments()

    def _load_auth_type(self):
        key = "FLATNOTES_AUTH_TYPE"
        auth_type = get_env(
            key, mandatory=False, default=AuthType.PASSWORD.value
        )
        try:
            auth_type = AuthType(auth_type.lower())
        except ValueError:
            logger.error(
                f"Invalid value '{auth_type}' for {key}. "
                + "Must be one of: "
                + ", ".join([auth_type.value for auth_type in AuthType])
                + "."
            )
            sys.exit(1)
        return auth_type

    def _quick_access_hide(self):
        key = "FLATNOTES_QUICK_ACCESS_HIDE"
        value = get_env(key, mandatory=False, default=False, cast_bool=True)
        if value is False:
            depricated_key = "FLATNOTES_HIDE_RECENTLY_MODIFIED"
            value = get_env(
                depricated_key, mandatory=False, default=False, cast_bool=True
            )
            if value is True:
                logger.warning(
                    f"{depricated_key} is depricated. Please use {key} instead."
                )
        return value

    def _quick_access_title(self):
        key = "FLATNOTES_QUICK_ACCESS_TITLE"
        return get_env(key, mandatory=False, default="RECENTLY MODIFIED")

    def _quick_access_term(self):
        key = "FLATNOTES_QUICK_ACCESS_TERM"
        return get_env(key, mandatory=False, default="*")

    def _quick_access_sort(self):
        key = "FLATNOTES_QUICK_ACCESS_SORT"
        value = get_env(key, mandatory=False, default="lastModified")
        valid_values = ["score", "title", "lastModified"]
        if value not in valid_values:
            logger.error(
                f"Invalid value '{value}' for {key}. "
                + "Must be one of: "
                + ", ".join(valid_values)
            )
            sys.exit(1)
        return value

    def _quick_access_limit(self):
        key = "FLATNOTES_QUICK_ACCESS_LIMIT"
        return get_env(key, mandatory=False, default=4, cast_int=True)

    def _tag_hierarchy(self):
        key = "FLATNOTES_TAG_HIERARCHY"
        value = get_env(key, mandatory=False, default="{}")
        try:
            hierarchy = json.loads(value)
            if not isinstance(hierarchy, dict) or any(
                not isinstance(parent, str)
                or not isinstance(children, list)
                or not all(isinstance(child, str) for child in children)
                for parent, children in hierarchy.items()
            ):
                raise ValueError
            hierarchy = {
                parent.lower(): [child.lower() for child in children]
                for parent, children in hierarchy.items()
            }
            hierarchy_file = self._tag_hierarchy_file()
            if os.path.isfile(hierarchy_file):
                with open(hierarchy_file, "r", encoding="utf-8") as file:
                    hierarchy = json.load(file)
                self._validate_tag_hierarchy_format(hierarchy)
            for parent in hierarchy:
                self._validate_tag_hierarchy(hierarchy, parent, set())
            return hierarchy
        except (TypeError, json.JSONDecodeError, ValueError):
            logger.error(
                f"Invalid value '{value}' for {key}. Must be a JSON object "
                + "mapping parent tags to child tag arrays."
            )
            sys.exit(1)

    def save_tag_hierarchy(self, hierarchy):
        self._validate_tag_hierarchy_format(hierarchy)
        hierarchy = {
            parent.lower(): [child.lower() for child in children]
            for parent, children in hierarchy.items()
        }
        for parent in hierarchy:
            self._validate_tag_hierarchy(hierarchy, parent, set())
        with open(self._tag_hierarchy_file(), "w", encoding="utf-8") as file:
            json.dump(hierarchy, file, indent=2)
        self.tag_hierarchy = hierarchy

    @staticmethod
    def _validate_tag_hierarchy_format(hierarchy):
        if not isinstance(hierarchy, dict) or any(
            not isinstance(parent, str)
            or not isinstance(children, list)
            or not all(isinstance(child, str) for child in children)
            for parent, children in hierarchy.items()
        ):
            raise ValueError

    def _tag_hierarchy_file(self):
        path = get_env("FLATNOTES_PATH", mandatory=True)
        return os.path.join(path, ".flatnotes-tag-hierarchy.json")

    @staticmethod
    def _validate_tag_hierarchy(hierarchy, tag, ancestors):
        if tag in ancestors:
            raise ValueError
        for child in hierarchy.get(tag, []):
            GlobalConfig._validate_tag_hierarchy(
                hierarchy, child, ancestors | {tag}
            )

    def _load_path_prefix(self):
        key = "FLATNOTES_PATH_PREFIX"
        value = get_env(key, mandatory=False, default="")
        if value and (not value.startswith("/") or value.endswith("/")):
            logger.error(
                f"Invalid value '{value}' for {key}. "
                + "Must start with '/' and not end with '/'."
            )
            sys.exit(1)
        return value


class AuthType(str, Enum):
    NONE = "none"
    READ_ONLY = "read_only"
    PASSWORD = "password"
    TOTP = "totp"


class GlobalConfigResponseModel(CustomBaseModel):
    auth_type: AuthType
    quick_access_hide: bool
    quick_access_title: str
    quick_access_term: str
    quick_access_sort: str
    quick_access_limit: int
    tag_hierarchy: dict[str, list[str]]
