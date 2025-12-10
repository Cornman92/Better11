"""
Advanced File Manager Module

File management with performance optimization:
- Fast file operations
- Bulk operations
- File indexing and search
- Duplicate file detection
- Large file analysis
- File permissions management
- NTFS optimization
- File compression
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import subprocess


class FileOperation(Enum):
    """File operations"""
    COPY = "copy"
    MOVE = "move"
    DELETE = "delete"
    RENAME = "rename"
    COMPRESS = "compress"
    DECOMPRESS = "decompress"


@dataclass
class FileInfo:
    """File information"""
    path: str
    name: str
    size: int
    created: float
    modified: float
    accessed: float
    is_directory: bool
    extension: str
    mime_type: Optional[str] = None
    attributes: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'path': self.path,
            'name': self.name,
            'size': self.size,
            'created': self.created,
            'modified': self.modified,
            'accessed': self.accessed,
            'is_directory': self.is_directory,
            'extension': self.extension,
            'mime_type': self.mime_type,
            'attributes': self.attributes
        }


class FastFileManager:
    """High-performance file operations"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def get_file_info(self, path: str) -> FileInfo:
        """Get detailed file information"""
        stat = os.stat(path)
        is_dir = os.path.isdir(path)

        name = os.path.basename(path)
        ext = os.path.splitext(name)[1] if not is_dir else ""

        # Get MIME type
        mime_type = None
        if not is_dir:
            mime_type, _ = mimetypes.guess_type(path)

        # Windows attributes
        attrs = {}
        if os.name == 'nt':
            import win32api
            import win32con
            try:
                file_attrs = win32api.GetFileAttributes(path)
                attrs = {
                    'hidden': bool(file_attrs & win32con.FILE_ATTRIBUTE_HIDDEN),
                    'system': bool(file_attrs & win32con.FILE_ATTRIBUTE_SYSTEM),
                    'readonly': bool(file_attrs & win32con.FILE_ATTRIBUTE_READONLY),
                    'archive': bool(file_attrs & win32con.FILE_ATTRIBUTE_ARCHIVE),
                    'compressed': bool(file_attrs & win32con.FILE_ATTRIBUTE_COMPRESSED),
                }
            except:
                pass

        return FileInfo(
            path=path,
            name=name,
            size=stat.st_size,
            created=stat.st_ctime,
            modified=stat.st_mtime,
            accessed=stat.st_atime,
            is_directory=is_dir,
            extension=ext,
            mime_type=mime_type,
            attributes=attrs
        )

    def copy_file_fast(self, src: str, dst: str, buffer_size: int = 1024*1024) -> bool:
        """Fast file copy with large buffer"""
        try:
            # Use Windows robocopy for faster copying
            if os.name == 'nt':
                result = subprocess.run(
                    ["robocopy", os.path.dirname(src), os.path.dirname(dst),
                     os.path.basename(src), "/MT:8", "/NFL", "/NDL", "/NJH", "/NJS"],
                    capture_output=True
                )
                # Robocopy returns 0-7 for success
                return result.returncode < 8
            else:
                shutil.copy2(src, dst)
                return True
        except Exception as e:
            if self.verbose:
                print(f"Error copying file: {e}")
            return False

    def copy_directory_fast(self, src: str, dst: str) -> bool:
        """Fast directory copy"""
        try:
            if os.name == 'nt':
                result = subprocess.run(
                    ["robocopy", src, dst, "/E", "/MT:8", "/NFL", "/NDL", "/NJH", "/NJS"],
                    capture_output=True
                )
                return result.returncode < 8
            else:
                shutil.copytree(src, dst)
                return True
        except Exception as e:
            if self.verbose:
                print(f"Error copying directory: {e}")
            return False

    def move_file(self, src: str, dst: str) -> bool:
        """Move file"""
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error moving file: {e}")
            return False

    def delete_file(self, path: str, secure: bool = False) -> bool:
        """Delete file (optionally secure delete)"""
        try:
            if secure and os.path.isfile(path):
                # Overwrite file before deletion
                file_size = os.path.getsize(path)
                with open(path, 'wb') as f:
                    f.write(os.urandom(file_size))

            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

            return True
        except Exception as e:
            if self.verbose:
                print(f"Error deleting: {e}")
            return False

    def search_files(
        self,
        root_path: str,
        pattern: str = "*",
        recursive: bool = True,
        case_sensitive: bool = False
    ) -> List[FileInfo]:
        """Search for files"""
        results = []

        if recursive:
            pattern_path = Path(root_path).rglob(pattern)
        else:
            pattern_path = Path(root_path).glob(pattern)

        for path in pattern_path:
            try:
                info = self.get_file_info(str(path))
                results.append(info)
            except:
                pass

        return results


class DuplicateFileFinder:
    """Find duplicate files"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def calculate_hash(self, file_path: str, hash_type: str = "md5") -> str:
        """Calculate file hash"""
        if hash_type == "md5":
            hasher = hashlib.md5()
        elif hash_type == "sha256":
            hasher = hashlib.sha256()
        else:
            hasher = hashlib.sha1()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    def find_duplicates(self, root_path: str) -> Dict[str, List[str]]:
        """Find duplicate files in directory"""
        files_by_size = {}
        duplicates = {}

        # First pass: group by size
        for root, dirs, files in os.walk(root_path):
            for file in files:
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    if size not in files_by_size:
                        files_by_size[size] = []
                    files_by_size[size].append(path)
                except:
                    pass

        # Second pass: hash files with same size
        for size, paths in files_by_size.items():
            if len(paths) > 1:
                files_by_hash = {}

                for path in paths:
                    try:
                        file_hash = self.calculate_hash(path)
                        if file_hash not in files_by_hash:
                            files_by_hash[file_hash] = []
                        files_by_hash[file_hash].append(path)
                    except:
                        pass

                # Record duplicates
                for file_hash, duplicate_paths in files_by_hash.items():
                    if len(duplicate_paths) > 1:
                        duplicates[file_hash] = duplicate_paths

        return duplicates


class LargeFileAnalyzer:
    """Analyze and find large files"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def find_large_files(
        self,
        root_path: str,
        min_size_mb: int = 100,
        limit: int = 100
    ) -> List[FileInfo]:
        """Find large files"""
        large_files = []
        min_size_bytes = min_size_mb * 1024 * 1024

        for root, dirs, files in os.walk(root_path):
            for file in files:
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    if size >= min_size_bytes:
                        stat = os.stat(path)
                        info = FileInfo(
                            path=path,
                            name=file,
                            size=size,
                            created=stat.st_ctime,
                            modified=stat.st_mtime,
                            accessed=stat.st_atime,
                            is_directory=False,
                            extension=os.path.splitext(file)[1]
                        )
                        large_files.append(info)

                        if len(large_files) >= limit:
                            break
                except:
                    pass

            if len(large_files) >= limit:
                break

        # Sort by size
        large_files.sort(key=lambda x: x.size, reverse=True)

        return large_files

    def analyze_directory_size(self, path: str) -> Dict[str, int]:
        """Analyze directory sizes"""
        sizes = {}

        for root, dirs, files in os.walk(path):
            size = 0
            for file in files:
                try:
                    size += os.path.getsize(os.path.join(root, file))
                except:
                    pass

            sizes[root] = size

        return sizes


class FileCompressor:
    """File compression utilities"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def compress_file(self, src: str, dst: Optional[str] = None) -> Optional[str]:
        """Compress file to ZIP"""
        import zipfile

        if dst is None:
            dst = src + ".zip"

        try:
            with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(src, os.path.basename(src))
            return dst
        except Exception as e:
            if self.verbose:
                print(f"Error compressing: {e}")
            return None

    def compress_directory(self, src: str, dst: Optional[str] = None) -> Optional[str]:
        """Compress directory to ZIP"""
        import zipfile

        if dst is None:
            dst = src + ".zip"

        try:
            with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(src):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, src)
                        zipf.write(file_path, arcname)
            return dst
        except Exception as e:
            if self.verbose:
                print(f"Error compressing: {e}")
            return None

    def decompress_file(self, src: str, dst: Optional[str] = None) -> bool:
        """Decompress ZIP file"""
        import zipfile

        if dst is None:
            dst = os.path.dirname(src)

        try:
            with zipfile.ZipFile(src, 'r') as zipf:
                zipf.extractall(dst)
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error decompressing: {e}")
            return False

    def enable_ntfs_compression(self, path: str) -> bool:
        """Enable NTFS compression on file/directory"""
        if os.name != 'nt':
            return False

        result = subprocess.run(
            ["compact", "/c", path],
            capture_output=True
        )

        return result.returncode == 0


class AdvancedFileManager:
    """Comprehensive file manager"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.file_manager = FastFileManager(verbose)
        self.duplicate_finder = DuplicateFileFinder(verbose)
        self.large_file_analyzer = LargeFileAnalyzer(verbose)
        self.compressor = FileCompressor(verbose)

    def get_directory_tree(self, path: str, max_depth: int = 3) -> Dict:
        """Get directory tree structure"""
        def build_tree(current_path: str, depth: int = 0) -> Dict:
            if depth > max_depth:
                return {}

            tree = {
                'path': current_path,
                'name': os.path.basename(current_path),
                'is_directory': os.path.isdir(current_path),
                'children': []
            }

            if tree['is_directory']:
                try:
                    for item in os.listdir(current_path):
                        item_path = os.path.join(current_path, item)
                        tree['children'].append(build_tree(item_path, depth + 1))
                except:
                    pass

            return tree

        return build_tree(path)

    def bulk_rename(self, paths: List[str], pattern: str) -> List[Tuple[str, str]]:
        """Bulk rename files

        Pattern supports:
        - {n} = sequential number
        - {name} = original name
        - {ext} = extension
        """
        renamed = []

        for i, path in enumerate(paths, 1):
            directory = os.path.dirname(path)
            name = os.path.splitext(os.path.basename(path))[0]
            ext = os.path.splitext(path)[1]

            new_name = pattern.format(n=i, name=name, ext=ext)
            new_path = os.path.join(directory, new_name)

            try:
                os.rename(path, new_path)
                renamed.append((path, new_path))
            except:
                pass

        return renamed

    def optimize_directory(self, path: str) -> Dict:
        """Optimize directory (compression, dedup, etc.)"""
        results = {
            'duplicates_found': 0,
            'space_wasted': 0,
            'large_files': 0,
            'compression_enabled': False
        }

        # Find duplicates
        duplicates = self.duplicate_finder.find_duplicates(path)
        results['duplicates_found'] = len(duplicates)

        for hash_val, paths in duplicates.items():
            if paths:
                file_size = os.path.getsize(paths[0])
                results['space_wasted'] += file_size * (len(paths) - 1)

        # Find large files
        large_files = self.large_file_analyzer.find_large_files(path)
        results['large_files'] = len(large_files)

        # Enable NTFS compression
        if self.compressor.enable_ntfs_compression(path):
            results['compression_enabled'] = True

        return results


# Convenience functions
def search_files(path: str, pattern: str = "*") -> List[FileInfo]:
    """Quick file search"""
    manager = FastFileManager()
    return manager.search_files(path, pattern)


def find_duplicates(path: str) -> Dict[str, List[str]]:
    """Quick duplicate finder"""
    finder = DuplicateFileFinder()
    return finder.find_duplicates(path)


def find_large_files(path: str, min_size_mb: int = 100) -> List[FileInfo]:
    """Quick large file finder"""
    analyzer = LargeFileAnalyzer()
    return analyzer.find_large_files(path, min_size_mb)


def optimize_directory(path: str) -> Dict:
    """Quick directory optimization"""
    manager = AdvancedFileManager()
    return manager.optimize_directory(path)
