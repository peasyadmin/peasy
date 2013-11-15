from ..toolchain_gcc import toolchain_gcc

class Windows_target(toolchain_gcc):
    extension = ".dll"
    def getBuilderLDFLAGS(self):
        return toolchain_gcc.getBuilderLDFLAGS(self) + ["-shared", "-lwinmm"]
