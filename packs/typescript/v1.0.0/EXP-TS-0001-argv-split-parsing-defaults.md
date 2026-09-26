---
experience_id: EXP-TS-0001
category: runtime_deviation
pattern: "CLI 参数解析对单个 argv 元素做空格切分取下一个参数（`hit.split(' ')[1]`），而 argv 已按空格切分 → 数值与枚举参数永远落到默认值，且没有任何报错"
root_cause: |
  解析器把「一个 argv 元素」当成了「命令行原文」来处理。命令行原文里 `--runs 300` 是
  一个字符串，切成两半就能取值；但进程收到的 `argv` 已经按空格切分过了，`--runs` 与
  `300` 是两个相邻元素 —— 对 `--runs` 这一个元素做空格切分只得到一个元素，取下标 1
  得 `undefined`，于是回落到默认值。

  缺的是「参数名与参数值的关系」这一认识。写成 `split(' ')` 的写法隐含了「值就在同一
  个字符串里」的假设，而这个假设只在 `--name=value` 形式下成立；又因为解析失败没有
  报错、只是静默用默认值，缺陷在最长的一段时间里完全不可见。
detection_trigger: |
  - 多组不同参数的输出内容完全相同（例如按章节分组的校准，各组结果一模一样）
  - 输出 / 日志里的参数字段与传入值不符，恰等于默认值
  - 传入一个明显异常的值（如 `--runs 0`）仍然「正常」跑完
  - `--name=value` 形式解析正确，`--name value` 形式失效
fix_template: |
  用 `indexOf` 定位参数名，取它**之后**的那个 argv 元素，而不是对元素本身做切分；
  同时兼容 `--name=value` 形式；批跑 / 校准前先核对输出里的参数回显字段。

  ```ts
  // ❌ 单个元素内部切分：argv 已按空格切分，值在下一个元素里，不在这里
  const hit = argv.find((a) => a.startsWith('--runs'));
  return Number(hit?.split(' ')[1] ?? fallback);      // 恒为 undefined → fallback

  // ✅ 在 argv 里定位参数名，取其**下一个**元素；兼容 --name=value
  const prefix = '--runs=';
  const inline = argv.find((a) => a.startsWith(prefix));
  if (inline) {
    const v = Number(inline.slice(prefix.length));
    return Number.isFinite(v) ? v : fallback;         // ✅ 不用 || ，避免把 0 也当缺失
  }

  const i = argv.indexOf('--runs');
  if (i === -1 || i + 1 >= argv.length) return fallback;
  const v = Number(argv[i + 1]);
  return Number.isFinite(v) ? v : fallback;           // ✅ 下一个元素即参数值
  ```

  并让「传了但解析不出」与「没传」分开：前者应当报错，而不是静默用默认值。
language: typescript
tags:
  - cli
  - argparse
  - sim
severity: medium
confidence: 0.90
original_confidence: 0.9      # 作者自评（源记录 provenance_weight: 0.8），非导出管道默认值
confidence_rationale: '静态阅读即可判定的解析缺陷；运行时表现确定（恒落默认值）；判别法不需构造特殊环境，传两组参数比较回显即可'
occurrences: 1
audit_source: EXP-s10-sim-argparse
---

## 详细描述

CLI 参数解析有一条通用原则：**取值的动作发生在「参数名」与「参数值」之间，而不是在
单个参数元素内部。** `argv` 已经按空格切分过一次 —— 值在**相邻元素**里；只有在
`--name=value` 这种形式下，名与值才在同一个元素内。

一旦违反这条原则，写法会长成这样：

```ts
// 命令行原文里 `--runs 300` 是一个字符串，于是有人对「元素」做同样的切分
const runs = Number(argv.find((a) => a.startsWith('--runs'))?.split(' ')[1] ?? 300);
```

它在 `--name value` 形式下**永远取不到值**：`--runs` 与 `300` 是两个相邻的 argv 元素，
对 `--runs` 做 `split(' ')` 得到的数组只有一个元素，下标 1 是 `undefined`，于是回落到
默认值。解析器写得很像在解析命令行，实际上解析的是「它自己」。

后果比「少传一个参数」严重：**没有任何报错**。所有走这条路径的参数静默变成默认值，
程序照常跑完、照常输出。源记录里的形态是：一个数值参数（迭代次数）与一个枚举参数
（章节选择）同时失效，于是**按章节分组的校准四组跑出完全相同的结果** —— 校准本身是
「按参数分组比较」，而它实际只在跑同一组配置。

这类缺陷的通用教训有两层：一是上面那条「取值位置」；二是**解析失败必须可见** ——
`undefined` 被 `?? fallback` 无条件吞掉，于是「用户没传」与「传了解析不出来」在代码里
成了同一件事。参数解析的健壮性在于把两种情况分开。

## 根因链

1. **现象层**：不同参数跑出相同结果；输出里的参数回显等于默认值。
2. **直接原因**：对单个 argv 元素做空格切分取「下一段」，而该元素里并没有下一段。
3. **为什么会出现**：把「命令行原文」与「进程收到的 argv」混为一谈。原文里
   `--runs 300` 确实是以空格分隔的整体，切分是合法操作；但 argv 已经完成了一次切分，
   值已落到相邻元素上。写 `split(' ')` 的人假设了「值在同一个字符串里」—— 该假设只在
   `--name=value` 下成立。
4. **为什么长期不可见**：解析失败没有报错，只是回落到默认值。默认值让程序继续跑完并
   产出「看起来正常」的结果。**静默回落把解析缺陷伪装成了配置选择。**
5. **为什么检查没兜住**：发现它需要一个「参数回显」观测点 —— 输出里带上实际生效的
   参数值。没有回显时，唯一的方法是注意到多组参数产出完全相同的输出，而这要求人主动
   去比。
6. **本质原因**：**解析器没有对「解析失败」做出区分。** 参数解析的语义只有三种状态
   （未传 / 传了且可解析 / 传了但解析不出），代码把它们压缩成了两种，第三种被默认值
   吸收 —— 而第三种恰恰是唯一需要报错的。

## 代码示例

### ❌ 错误示例

```ts
// <project>/<module>/cli.ts

function argNum(argv: string[], name: string, fallback: number): number {
  // ❌ 在单个元素内部切分：argv 已按空格切分，值在**下一个元素**里
  const hit = argv.find((a) => a.startsWith(`--${name}`));
  return Number(hit?.split(' ')[1] ?? fallback);   // 恒为 undefined → fallback
}

function argStr(argv: string[], name: string, fallback: string): string {
  // ❌ 同一个写法，枚举型参数一并失效
  const hit = argv.find((a) => a.startsWith(`--${name}`));
  return hit?.split(' ')[1] ?? fallback;
}

async function main(argv: string[]) {
  const runs = argNum(argv, 'runs', 100);          // 传 --runs 300 → 实际总是 100
  const chapter = argStr(argv, 'chapter', 'ch1');  // 传 --chapter ch3 → 实际总是 ch1
  await calibrate({ runs, chapter });              // ❌ 多组参数跑出同一份结果
}
```

### ✅ 正确示例

```ts
// <project>/<module>/cli.ts

function argNum(argv: string[], name: string, fallback: number): number {
  const prefix = `--${name}=`;
  const inline = argv.find((a) => a.startsWith(prefix));
  if (inline) {
    const v = Number(inline.slice(prefix.length));  // ✅ 兼容 --name=value
    return Number.isFinite(v) ? v : fallback;
  }

  const i = argv.indexOf(`--${name}`);              // ✅ 定位参数名本身
  if (i === -1 || i + 1 >= argv.length) return fallback;
  const v = Number(argv[i + 1]);                    // ✅ 取值：**下一个** argv 元素
  return Number.isFinite(v) ? v : fallback;         // ✅ 只在值非法时回落
}

function argStr(argv: string[], name: string, fallback: string): string {
  const prefix = `--${name}=`;
  const inline = argv.find((a) => a.startsWith(prefix));
  if (inline) return inline.slice(prefix.length);

  const i = argv.indexOf(`--${name}`);
  if (i === -1 || i + 1 >= argv.length) return fallback;
  return argv[i + 1];                               // ✅ 下一个元素即参数值
}

async function main(argv: string[]) {
  const runs = argNum(argv, 'runs', 100);
  const chapter = argStr(argv, 'chapter', 'ch1');
  console.log(JSON.stringify({ runs, chapter }));   // ✅ 参数回显：实际生效值可见
  await calibrate({ runs, chapter });
}
```

判别法：用两组不同的参数各跑一次，比较输出里的参数回显 —— 若完全相同（且等于默认值），
即是本模式。若要把「解析不出」与「没传」分开，可让 `argNum` 在值非法时抛错而不是回落
（`throw new Error(\`--${name} 需要一个数值\`)`），把静默失败变成响亮失败。

## 对应失败模式

对应 `runtime_deviation`（运行时偏离）。实现声称的行为是「读 `--runs <n>`」，运行时行为
是「永远用默认值」—— 两者在**没有报错**的情况下偏离：解析器把「值不存在」与「用户没传」
合并处理，于是偏离被伪装成默认配置。不归 `tool_misuse`：这里没有用错工具，而是参数
解析的写法与 argv 的结构不匹配。

**置信度说明**：给 0.90。缺陷可由静态阅读判定（对单元素切分取下一段），运行时表现确定
（恒落默认值），判别法不需要构造特殊环境（传两组不同参数比较回显）。审计在落包复核时
确认：本条**不属于判据 / 护栏失效主题**，此前被归入通用化改写桶（B 桶）**属误分** ——
它本就通用、可直接发布，故改写后单独进入本包，按其技术领域归档。`original_confidence`
取作者自评的 0.90（源记录 `provenance_weight: 0.8`），本批改写的 `confidence` 与之一致。
未给 1.0 是因为 `occurrences: 1`，尚未跨项目复现。

## 改进方向

**短期**：把 `split(' ')[1]` 换成「`indexOf(name)` 取下一个 argv 元素」，并兼容
`--name=value` 形式；批跑 / 校准前先打印参数回显。

**长期**：
- 交给自己维护的 CLI 一律用统一的参数解析（成熟解析库），不要手写；手写时把「没传」与
  「传了解析不出」分开处理，后者报错。
- 任何「按参数分组比较」的流程，先断言各组输入**确实不同**（回显校验）—— 否则对照组
  可能全是同一组，整个比较结论不成立。
- 把「静默回落默认值」当作一类风险：凡是 `?? default` / `|| default` 出现在解析路径上，
  都要问一句「这里会不会把解析失败也吞掉」。
