from ..toolchain_gcc import toolchain_gcc

class Linux32Bit_target(toolchain_gcc):
    extension = ".so"
    def getBuilderCFLAGS(self):
        return toolchain_gcc.getBuilderCFLAGS(self) + ["-m32 -fPIC"]
    def getBuilderLDFLAGS(self):
        return toolchain_gcc.getBuilderLDFLAGS(self) + ["-shared", "-lrt"]
