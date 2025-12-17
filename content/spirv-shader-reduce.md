Title: 一种基于SPIR-V字节码消除的Shader变体方案
Date: 2025-12-17
Modified: 2025-12-17
Category: Shader
Tags: Shader, Vulkan
Slug: spirv-shader-reduce
Author: HaokunZheng
Summary: 减少shader变体，缩小包体


# 背景

在实时渲染项目中，Shader 变体（Shader Variants）几乎无处不在：同一份Shader代码会因不同的宏开关、渲染路径、平台能力与材质选项，被编译成大量 “看起来相似却各不相同” 的版本。它让我们能够以较低的代码维护成本覆盖丰富的功能组合，以及更快的执行速度。但也带来了典型的工程痛点 —— 变体数量呈指数增长，导致编译时间拉长、包体膨胀、加载与内存压力上升。

传统的Shader变体解决方案是通过在Shader源码中添加条件编译语句 `#ifdef`，基于源码预处理的方式来生成不同的Shader变体代码。这种方案的缺点是需要Shader源代码。另一种方案是使用 `Vulkan Specialization Constant`，在运行期由驱动生成不同的shader变体。优点是，同样不需要源码，使用简单。缺点则是运行期生成会造成卡顿。

有没有一种不需要Shader源码就能实现变体功能的技术方案？有，那就是结合 `Vulkan Specialization Constant`和 `SPIR-V字节码消除`的Shader变体方案。


# 技术原理

Vulkan GLSL Shader经过编译后的产物是SPIR-V字节码。下面是一段简单的Vulkan GLSL Shader源码。该代码包含一个Vulkan Specialization Constant变量 `test`。

```OpenGL
// test.frag

#version 310 es

layout (constant_id = 0) const int test = 0;

layout(location = 0) out mediump vec4 outColor;

void main() {
    if (test > 0) {
        outColor.a = 3.0f;
    }
}
```

通过命令 `glslang.exe -V .\test.frag.spv`编译后得到以下产物：

```C++
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 22
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %test "test"
               OpName %outColor "outColor"
               OpDecorate %test RelaxedPrecision
               OpDecorate %test SpecId 0
               OpDecorate %outColor RelaxedPrecision
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
       %test = OpSpecConstant %int 0
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
         %10 = OpSpecConstantOp %bool SGreaterThan %test %int_0
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_3 = OpConstant %float 3
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpSelectionMerge %12 None
               OpBranchConditional %10 %11 %12
         %11 = OpLabel
         %21 = OpAccessChain %_ptr_Output_float %outColor %uint_3
               OpStore %21 %float_3
               OpBranch %12
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

从上面的SPIR-V代码中，我们可以看到 `if (test > 0)`被编译成了 `OpSpecConstantOp`和 `OpBranchConditional`指令。我们可以通过以下编译命令给 `test`变量赋予具体的值 `0`，

```PowerShell
spirv-opt.exe \
    --freeze-spec-const \
    --set-spec-const-default-value=0:0 \
    --fold-spec-const-op-composite \
    --eliminate-dead-branches \
    test.frag.spv \
    -o test.frag.optimized.spv
```

我们得到以下的SPIR-V字节码：

```PowerShell
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 23
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Fragment %main "main" %outColor
               OpExecutionMode %main OriginUpperLeft
               OpSource ESSL 310
               OpName %main "main"
               OpName %test "test"
               OpName %outColor "outColor"
               OpDecorate %test RelaxedPrecision
               OpDecorate %outColor RelaxedPrecision
               OpDecorate %outColor Location 0
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
        %int = OpTypeInt 32 1
       %test = OpConstant %int 0
      %int_0 = OpConstant %int 0
       %bool = OpTypeBool
      %false = OpConstantFalse %bool
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Output_v4float = OpTypePointer Output %v4float
   %outColor = OpVariable %_ptr_Output_v4float Output
    %float_3 = OpConstant %float 3
       %uint = OpTypeInt 32 0
     %uint_3 = OpConstant %uint 3
%_ptr_Output_float = OpTypePointer Output %float
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpBranch %12
         %12 = OpLabel
               OpReturn
               OpFunctionEnd
```

当 `test`等于 `0`时，`if (test > 0)`结果为 `false`，相关代码不会执行。从上面的SPIR-V字节码中我们也看到了已经没有了 `OpSpecConstantOp`和 `OpBranchConditional`指令。`outColor.a = 3.0f;`相关的指令也没有了。

通过对包含 `Vulkan Specialization Constant`的SPIR-V字节码进行预处理，我们就能在不需要Shader源码的情况下，提前编译出不同Shader变体。甚至可以在运行期动态生成。

# 结语

Shader变体相关问题是一个复杂且难以解决的工程问题。没有任何一个方案是完美的。需要根据项目的需求，在内存占用、渲染延迟、渲染效果、执行速度等方面进行平衡和适当地妥协。
