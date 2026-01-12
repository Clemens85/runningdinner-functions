from pathlib import Path
from typing import Union

def build_absolute_path(relative_path: str) -> str:
    return str(Path(__file__).parent / relative_path)

PathLike = Union[str, Path]
def ensure_subfolder(root_path: PathLike, sub_folder: PathLike, delete_files: bool = False) -> Path:
    """
    Ensure the subfolder exists under the given root path.
    Returns the Path to the ensured subfolder.

    Example:
      ensure_subfolder('/tmp/myroot', 'data/cache')
      ensure_subfolder(Path('/tmp/myroot'), Path('data/cache'))
    """
    root = Path(root_path)
    target = root / sub_folder
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        # Re-raise with context so caller can handle/log
        raise OSError(f"Unable to create directory `{target}`: {exc}") from exc

    if not delete_files:
        return target

    if not target.is_dir():
        raise NotADirectoryError(f"`{target}` exists and is not a directory")
    try:
        for child in target.iterdir():
            # Remove regular files and symlinks, but skip directories
            if child.is_file() or child.is_symlink():
                child.unlink()
    except OSError as exc:
        raise OSError(f"Unable to clean files in directory `{target}`: {exc}") from exc



    return target