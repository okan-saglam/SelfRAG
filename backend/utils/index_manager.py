import os
import hashlib
from typing import List
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent

class IndexManager:
    def __init__(self, base_index_dir: str = None):
        """
        Initialize IndexManager with base directory for storing indices.
        
        :param base_index_dir: Base directory where indices will be stored.
        """
        if base_index_dir is None:
            base_index_dir = str(BACKEND_DIR / "indices")
        self.base_index_dir = base_index_dir
        os.makedirs(self.base_index_dir, exist_ok=True)
    
    def get_index_path(self, pdf_paths: List[str]) -> str:
        """
        Generate a unique index path based on PDF files and their modification times.
        
        :param pdf_paths: List of PDF file paths.
        :return: Unique index directory path.
        """
        # Create a hash based on file paths and modification times
        hash_input = []
        for path in sorted(pdf_paths):  # Sort for consistency
            if os.path.exists(path):
                mtime = os.path.getmtime(path)
                size = os.path.getsize(path)
                hash_input.append(f"{path}:{mtime}:{size}")
        
        hash_str = "|".join(hash_input)
        index_hash = hashlib.md5(hash_str.encode()).hexdigest()[:8]
        
        return os.path.join(self.base_index_dir, f"index_{index_hash}")
    
    def should_rebuild_index(self, pdf_paths: List[str], index_path: str) -> bool:
        """
        Check if index should be rebuilt based on file changes.
        
        :param pdf_paths: List of PDF file paths.
        :param index_path: Path to the index directory.
        :return: True if index should be rebuilt, False otherwise.
        """
        # If index doesn't exist, rebuild
        if not os.path.exists(index_path):
            return True
        
        # Check if any PDF file is newer than the index
        try:
            index_mtime = os.path.getmtime(index_path)
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path) and os.path.getmtime(pdf_path) > index_mtime:
                    return True
        except OSError:
            return True
        
        return False
    
    def list_indices(self) -> List[str]:
        """
        List all available indices in the base directory.
        
        :return: List of index directory names.
        """
        if not os.path.exists(self.base_index_dir):
            return []
        
        indices = []
        for item in os.listdir(self.base_index_dir):
            index_path = os.path.join(self.base_index_dir, item)
            if os.path.isdir(index_path):
                indices.append(item)
        
        return indices
    
    def cleanup_old_indices(self, keep_latest: int = 3) -> None:
        """
        Clean up old indices, keeping only the latest ones.
        
        :param keep_latest: Number of latest indices to keep.
        """
        indices = self.list_indices()
        if len(indices) <= keep_latest:
            return
        
        # Sort by modification time
        index_paths = [(idx, os.path.join(self.base_index_dir, idx)) for idx in indices]
        index_paths.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
        
        # Remove old indices
        for idx_name, idx_path in index_paths[keep_latest:]:
            import shutil
            try:
                shutil.rmtree(idx_path)
                print(f"🗑️ Removed old index: {idx_name}")
            except Exception as e:
                print(f"⚠️ Could not remove index {idx_name}: {e}")