import itertools
import os
from pathlib import Path
import shutil
import sys
from typing import List

from Cython.Build import build_ext
from Cython.Build import cythonize
from Cython.Compiler import Options
import numpy as np
from setuptools import Distribution
from setuptools import Extension


# If DEBUG mode is enabled, skip compiler optimizations (TODO: implement)
DEBUG_MODE = bool(os.getenv("DEBUG_MODE", ""))
# If PROFILING mode is enabled, include traces necessary for coverage and profiling
PROFILING_MODE = bool(os.getenv("PROFILING_MODE", ""))
# Annotation lets Cython compile in a coverage.xml database
ANNOTATION_MODE = bool(os.getenv("ANNOTATION_MODE", ""))
# Skipping the build copy prevents copying built *.so files back into the source tree
SKIP_BUILD_COPY = bool(os.getenv("SKIP_BUILD_COPY", ""))


print(
    f"DEBUG_MODE={DEBUG_MODE}, "
    f"PROFILING_MODE={PROFILING_MODE}, "
    f"ANNOTATION_MODE={ANNOTATION_MODE}"
)

##########################
#  Cython build options  #
##########################
# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html

Options.docstrings = True  # Include docstrings in modules
Options.emit_code_comments = True
Options.annotate = ANNOTATION_MODE  # Create annotated html files for each .pyx
if ANNOTATION_MODE:
    Options.annotate_coverage_xml = "coverage.xml"
Options.fast_fail = True  # Abort compilation on first error
Options.warning_errors = True  # Treat compiler warnings as errors

CYTHON_COMPILER_DIRECTIVES = {
    "language_level": "3",
    "cdivision": True,  # If division is as per C with no check for zero (35% speed up)
    "embedsignature": True,  # If docstrings should be embedded into C signatures
    # If we're profiling, turn on line tracing
    "profile": PROFILING_MODE,
    "linetrace": PROFILING_MODE,
    # TODO: Enable extra warnings. Will require manual linting.
    # **Options.extra_warnings,
}


def _build_extensions() -> List[Extension]:
    # Build Extensions to feed into cythonize()
    # Profiling requires special macro directives
    if PROFILING_MODE or ANNOTATION_MODE:
        define_macros = [("CYTHON_TRACE", "1")]
    else:
        define_macros = None

    return [
        Extension(
            str(pyx.relative_to(".")).replace(os.path.sep, ".")[:-4],
            [str(pyx)],
            include_dirs=[".", np.get_include()],
            define_macros=define_macros,
        )
        for pyx in itertools.chain(
            Path("examples").rglob("*.pyx"),
            Path("nautilus_trader").rglob("*.pyx"),
        )
    ]


def _build_distribution(extensions: List[Extension]) -> Distribution:
    # Build a Distribution using cythonize()
    # Determine the build output directory
    if PROFILING_MODE:
        # For subsequent annotation, the c source needs to be in
        # the same tree as the Cython code.
        build_dir = None
    elif ANNOTATION_MODE:
        build_dir = "build/annotated"
    else:
        build_dir = "build/optimized"

    distribution = Distribution(
        dict(
            name="nautilus_trader",
            ext_modules=cythonize(
                module_list=extensions,
                compiler_directives=CYTHON_COMPILER_DIRECTIVES,
                nthreads=os.cpu_count(),
                build_dir=build_dir,
            ),
            zip_safe=False,
        )
    )
    distribution.package_dir = "nautilus_trader"
    return distribution


def _copy_build_dir_to_project(cmd: build_ext) -> None:
    # Copy built extensions back to the project tree
    for output in cmd.get_outputs():
        relative_extension = os.path.relpath(output, cmd.build_lib)
        if not os.path.exists(output):
            continue

        # Copy the file and set permissions
        print(f"Copying: {output} -> {relative_extension}")
        shutil.copyfile(output, relative_extension)
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)


def build(setup_kwargs):
    """Construct the extensions and distribution."""  # noqa
    extensions = _build_extensions()
    distribution = _build_distribution(extensions)

    # Build and run the command
    cmd: build_ext = build_ext(distribution)
    cmd.parallel = os.cpu_count()
    cmd.ensure_finalized()
    cmd.run()

    # Copy the build back into the project for packaging
    _copy_build_dir_to_project(cmd)

    return setup_kwargs


if __name__ == "__main__":
    print("")

    # Work around a Cython problem in Python 3.8.x on MacOS
    # https://github.com/cython/cython/issues/3262
    if sys.platform == "darwin":
        print("MacOS: Setting multiprocessing method to 'fork'.")
        try:
            # noinspection PyUnresolvedReferences
            import multiprocessing

            multiprocessing.set_start_method("fork", force=True)
        except ImportError:
            print("multiprocessing not available")

    print("Starting build...")
    build({})
