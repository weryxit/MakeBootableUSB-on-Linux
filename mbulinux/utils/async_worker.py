"""
Async worker using QThread.
"""

from PySide6.QtCore import QThread, Signal, QObject


class AsyncWorker(QThread):
    """Worker thread for async operations."""
    
    progress = Signal(int, str)  # percent, message
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error message
    
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.is_cancelled = False
    
    def run(self):
        """Run the task."""
        try:
            # Connect progress callback if task supports it
            if hasattr(self.task_func, '__code__'):
                # Check if task function accepts progress_callback parameter
                import inspect
                sig = inspect.signature(self.task_func)
                if 'progress_callback' in sig.parameters:
                    self.kwargs['progress_callback'] = self.progress.emit
            
            # Execute task
            result = self.task_func(*self.args, **self.kwargs)
            
            if isinstance(result, tuple):
                success, message = result
            elif isinstance(result, bool):
                success, message = result, "Operation completed"
            else:
                success, message = True, str(result)
            
            if not self.is_cancelled:
                self.finished.emit(success, message)
                
        except Exception as e:
            if not self.is_cancelled:
                self.error.emit(str(e))
    
    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True
        self.terminate()
        self.wait()


class WorkerManager(QObject):
    """Manage worker threads."""
    
    def __init__(self):
        super().__init__()
        self.workers = []
    
    def start_worker(self, task_func, *args, **kwargs):
        """Start a new worker thread."""
        worker = AsyncWorker(task_func, *args, **kwargs)
        self.workers.append(worker)
        
        # Clean up when worker finishes
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.error.connect(lambda e: self._cleanup_worker(worker))
        
        worker.start()
        return worker
    
    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self.workers:
            self.workers.remove(worker)
            worker.deleteLater()
    
    def stop_all(self):
        """Stop all workers."""
        for worker in self.workers[:]:
            worker.cancel()
            self._cleanup_worker(worker)