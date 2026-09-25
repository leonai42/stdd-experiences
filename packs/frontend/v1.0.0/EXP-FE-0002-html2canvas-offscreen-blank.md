---
experience_id: EXP-FE-0002
category: runtime_deviation
pattern: "html2canvas 捕获被 left:-10000px 移到视口外的元素时，输出全白（或全透明）的 PNG，且不抛任何异常 —— 生产环境表现为「导出的报告是一张白图」，而测试因为是 mock 掉该库的，完全看不见"
root_cause: |
  html2canvas 的默认渲染策略是**按当前视口渲染，再裁剪到目标元素的 bounding rect**。
  一个被 left:-10000px 推到视口外的元素，其 bounding rect 与视口完全没有交集，
  于是裁剪区域是空的，输出图像自然全白。

  这里真正的陷阱是**失败是静默的**：不抛异常、不返回错误码、也没有控制台警告，
  返回的就是一张合法的 PNG —— 只是内容是空的。调用方拿到的数据结构完全正常，
  没有任何信号提示它「你导出的东西是空的」。

  第二层原因在测试策略上：导出功能往往依赖第三方库，测试里该库被 mock 掉了，
  于是「该库在真实环境下的渲染约束」这一整类缺陷都落在测试视野之外。
detection_trigger: |
  - 生产环境点击「导出报告」，下载得到的 PNG 是白图（约 800px 高的空白），无任何报错
  - 本地开发环境中该元素可见（未被移出视口）时导出正常，形成「我这里没问题」的错觉
  - 单元测试全绿：测试对该库做了 mock，测的是「调用是否发生」，不是「画布上有没有东西」
  - 该元素被以 left:-10000px / top:-9999px 之类的离屏手法隐藏时更易触发
fix_template: |
  两种修法，推荐第一种：

  1. **导出时把目标容器临时渲染在屏幕内**：用一个 fixed 定位的 overlay 容器承载
     报告内容（可辅以 opacity 或 z-index 让它不可见但不离屏），在屏幕内完成捕获，
     捕获结束后再移除。
  2. **显式传入视口尺寸并对克隆体归位**：传 windowWidth / windowHeight 扩大渲染面，
     同时在 onclone 回调里把克隆出来的离屏元素重新定位回原点，使裁剪区域非空。

  无论用哪种，都要补一条**能证伪的**测试：断言导出产物的像素不是全白 / 字节数
  不在「空图」量级，而不是只断言导出函数被调用过。
language: typescript
tags:
  - html2canvas
  - report-export
  - silent-failure
  - offscreen-rendering
severity: medium
confidence: 0.85
occurrences: 1
audit_source: EXP-e20bb17480cc
---

## 详细描述

报告导出功能在生产环境点击后，下载得到的是一张 800px 高的纯白 PNG。没有报错、
没有异常、没有警告，浏览器控制台也是干净的。而本地开发时导出是正常的 —— 差异
在于生产环境的报告容器被以 `left:-10000px` 的方式移到了视口之外（一种常见的
「先渲染好但不让用户看见」的手法）。

这个缺陷的价值不在于「html2canvas 有个坑」，而在于它演示了一类**静默的数据产出失败**：
函数成功返回了一个格式合法、内容为空的产物，调用方无从分辨「导出成功」与
「导出了一张空图」。

## 根因链

1. **直接原因**：html2canvas 默认按视口渲染并裁剪到目标元素的 bounding rect；
   元素完全在视口外时裁剪区域为空，画布上什么也没有。
2. **深层原因**：把「元素在 DOM 里存在」等同于「元素能被渲染捕获」。离屏定位
   （`left:-10000px`）是一种**视觉存在但几何上不可达**的状态，而该库的渲染模型
   依赖几何可达性。
3. **系统性原因**：这一整类缺陷在测试里不可见，因为测试 mock 掉了该库。mock 保留
   了「被调用」这个契约，丢掉了「渲染约束」这个契约 —— 于是测试断言的是调用发生，
   而非产物有内容。这属于**测试替身制造成功幻觉**：消费者逻辑被测到了，生产者
   是否真的产出数据没被验证。

## 代码示例

### ❌ 错误示例

```typescript
// 隐藏用的离屏容器 —— 元素在 DOM 中，但几何上落在视口外
const OffscreenReport: React.FC<Props> = ({ data }) => (
  <div style={{ position: 'absolute', left: -10000, top: 0 }}>
    <ReportContent data={data} />
  </div>
);

const exportReport = async (el: HTMLElement) => {
  // html2canvas 按视口渲染并裁剪到 el 的 bounding rect；
  // el 在视口外 → 裁剪区域为空 → 得到一张合法但全白的 PNG，且不报错
  const canvas = await html2canvas(el);
  downloadPng(canvas.toDataURL('image/png'));
};
```

### ✅ 正确示例

```typescript
// 修法一（推荐）：导出时用 fixed overlay 把内容渲染在屏幕内，捕获后再移除
const exportReport = async (data: Props) => {
  const host = document.createElement('div');
  host.style.cssText =
    'position:fixed; inset:0 auto auto 0; z-index:-1; opacity:0; pointer-events:none';
  document.body.appendChild(host);

  const root = createRoot(host);
  root.render(<ReportContent data={data} />);
  await new Promise((r) => requestAnimationFrame(() => r(null)));

  try {
    const canvas = await html2canvas(host.firstElementChild as HTMLElement);
    // 断言产物非空，让「导出白图」这一失效模式当场暴露，而不是等用户反馈
    assertNotBlank(canvas);
    downloadPng(canvas.toDataURL('image/png'));
  } finally {
    root.unmount();
    host.remove();
  }
};

// 修法二：显式扩大渲染面，并在 onclone 里把克隆体归位
const canvas = await html2canvas(el, {
  windowWidth: document.documentElement.scrollWidth,
  windowHeight: document.documentElement.scrollHeight,
  onclone: (_doc, clonedEl) => {
    clonedEl.style.left = '0px';
    clonedEl.style.top = '0px';
  },
});
```

## 对应失败模式

对应 `runtime_deviation`（运行时偏离）。源代码本身没有任何语法或逻辑错误，静态检查
也看不出问题；偏离发生在**运行时环境与库的渲染模型交互**这一层 —— 元素的位置
（运行时的几何状态）使库走进了与预期不同的渲染分支。不归 `content_quality`，
是因为问题不是产物格式不合规（PNG 完全合法），而是产物内容为空。

**置信度说明**：给 0.85。根因（按视口渲染 + 裁剪到 bounding rect）是对该库渲染
模型的准确描述，触发条件（元素完全在视口外）明确且可确定性复现，修法有两种且都
具体。未给更高分是因为源记录只记了 1 次发生，且未附复现用的最小页面。

## 改进方向

**短期**：按上面任一修法改造导出路径，并在捕获后加一条非空断言，把静默白图变成
当场可见的失败。

**长期**：
- **给「静默产出空产物」这一失效模式建通用护栏**：凡是产出图像 / 文件 / 报告的路径，
  都补一条断言产物「不是空」的检查（像素非全白、字节数不在空图量级、行数不为 0）。
  这类断言的性价比极高，因为它拦住的是一整类静默失败，而不是一个具体 bug。
- **审视为导出功能而写的 mock**：确认测试断言的是「产物有内容」而不只是「库被调用了」。
  mock 掉的库，其真实环境约束必须由别的手段（集成测试或真实渲染的冒烟测试）补上。
