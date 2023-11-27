from src import backend_handle


def run_backend(connection) -> None:
    backend = backend_handle.BackendHandle(connection)
    backend.run()
    
    return