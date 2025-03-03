import torch

class MemoryManager:
    @staticmethod
    def clear_memory():
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    @staticmethod
    def get_memory_stats():
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**2
            reserved = torch.cuda.memory_reserved() / 1024**2
            return f"Allocated: {allocated:.2f}MB, Reserved: {reserved:.2f}MB"
        return "GPU not available"