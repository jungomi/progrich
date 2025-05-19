import pdb
import sys

try:
    import debugpy  # pyright: ignore[reportMissingImports]
except ImportError:
    debugpy = None


try:
    import torch.distributed as dist  # pyright: ignore[reportMissingImports]
except ImportError:
    dist = None


def is_distributed() -> bool:
    if dist is None:
        return False
    return dist.is_available() and dist.is_initialized()


def get_rank() -> int:
    return 0 if dist is None else dist.get_rank()


class MultiprocessingPdb(pdb.Pdb):
    """
    A multiprocessing version of PDB.
    """

    def __init__(self):
        super().__init__(nosigint=True)

    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open("/dev/stdin")
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin


def breakpoint(msg: str | None = None, port: int = 5678):
    distributed = is_distributed()
    suffix = ""
    if distributed:
        gpu_id = get_rank()
        # Increment port for additional processes
        port += gpu_id
        # Information to which process the debugger connects
        suffix = f" (GPU:{gpu_id})"
    if msg is not None:
        print(file=sys.stderr)
        print(f"🛑 {msg}{suffix} 🛑", file=sys.stderr)
    if debugpy is not None:
        if not debugpy.is_client_connected():
            debugpy.listen(port)
            print(
                f"👀 Waiting for debugger to connect to localhost:{port}{suffix}",
                file=sys.stderr,
            )
            debugpy.wait_for_client()
            print(f"🔬 Debugger connected to localhost:{port}{suffix}", file=sys.stderr)
        debugpy.breakpoint()
    else:
        # Fallback to PDB if debugpy is not installed
        print(
            "debugpy not found, install it by running: pip install debugpy",
            file=sys.stderr,
        )
        print("Falling back to PDB", file=sys.stderr)
        pdb = MultiprocessingPdb()
        pdb.set_trace(sys._getframe().f_back)
