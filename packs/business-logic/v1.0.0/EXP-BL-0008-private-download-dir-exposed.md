---
experience_id: EXP-BL-0008
category: contract_gap
pattern: "下载计数服务的压缩包私有目录被 Nginx 静态 location 暴露，用户绕过计数端点直接 GET 压缩包，计数失效"
root_cause: |
  压缩包目录与 API 入口文件同级（`<app_root>/downloads/` 与 `<entry>.py` 并列），
  若运维为其误加 alias / root 静态映射，`/<prefix>/downloads/...` 即可直达文件，
  绕过计数函数。

  计数端点与静态文件路径对「下载必经何处」的契约不一致：应用侧假定「所有下载都经过
  计数端点」，而部署侧同时提供了一条不经过它的通路。两边都不知道对方存在。
detection_trigger: |
  - 部署后 `curl -i https://example.com/<prefix>/downloads/...` 返回 200（本应 404）
  - 或 download 端点计数不再增长，但下载流量仍在
  - 计数查询端点 `/<prefix>/api/downloads/<id>` 可作为健康信号定期检查
fix_template: |
  1. 压缩包只放 API 私有目录（`<app_root>/downloads/`），且 Nginx 仅保留
     `location /<prefix>/api/ { proxy_pass ...; }`，**禁止**为 `downloads/` 建静态
     location。
  2. 部署后验证：`curl -i https://example.com/<prefix>/downloads/...` 应 404。
  3. 用计数查询端点 `/<prefix>/api/downloads/<id>` 作为健康信号定期检查。
language: python
tags:
  - nginx
  - private-directory
  - download-counter
  - deployment-exposure
severity: high
confidence: 0.80
occurrences: 1
audit_source: EXP-6b7f66805397
---

## 详细描述

一个带下载计数的服务：用户通过计数端点领取压缩包，端点负责落计数并把文件发出去。
压缩包存放在 API 的私有目录 `<app_root>/downloads/` 下 —— 这个目录与应用入口
`<entry>.py` 同级，也就是说它在应用的私有区域内。

缺陷出现在部署面：Nginx 若为该目录加了一条静态映射（`alias` 或 `root`），
`https://example.com/<prefix>/downloads/...` 就直接返回文件本身。用户（或任何知道
文件名的人）可以从这条路径直接 GET 压缩包，完全不经过计数端点。

后果不是「下载失败」而是**计数失真**：下载照常发生，流量照常消耗，只有计数端点上的
数字不再增长。这类失真是静默的 —— 没有任何请求失败，没有任何异常日志，唯一的异常
信号是「计数不涨了」，而它需要有人主动去比对流量与计数才能发现。

## 根因链

1. **现象层**：压缩包可被直接 GET（本应 404），计数与实际下载量脱钩。
2. **直接原因**：Nginx 为私有目录建了静态 location，提供了一条绕过计数端点的通路。
3. **为什么应用侧防不住**：目录与应用入口同级，从代码结构上看它是「私有」的；应用侧
   对「下载必经计数端点」的假定只在自己这一侧成立。部署面的静态映射对应用完全不可见
   —— 应用不知道它存在，也不会因为它而改变行为。
4. **本质原因**：这是一个**部署暴露面**问题：仅凭应用代码无法保证「只有一条通路」。
   只要文件放在任何 HTTP 服务器可以映射到的位置，暴露面就由部署配置单方面决定。
   计数的正确性因此依赖一条应用侧无法强制、也无法观测的外部约定 —— 这正是契约断层的
   形态：一侧声明「下载必经此处」，另一侧不知情地提供旁路。

## 代码示例

### ❌ 错误示例

```nginx
# Nginx：为私有下载目录建静态映射
location /<prefix>/api/ {
    proxy_pass http://127.0.0.1:8000;      # 计数端点（唯一应存在的通路）
}

location /<prefix>/downloads/ {
    alias <app_root>/downloads/;            # ❌ 旁路：直达文件，绕过计数
    # 用户 GET 这里 → 200 + 文件；计数端点上的数字不变
}
```

```python
# 应用侧：计数只发生在端点里，无法感知旁路存在
@app.get("/<prefix>/api/downloads/<id>")
def download(id):
    path = os.path.join(APP_ROOT, "downloads", f"{id}.zip")
    record_download(id)             # ❌ 只有走这条路的下载才会被计数
    return send_file(path)
```

### ✅ 正确示例

```nginx
# ✅ 只保留 API 前缀的 proxy_pass；禁止为 downloads/ 建静态 location
location /<prefix>/api/ {
    proxy_pass http://127.0.0.1:8000;
}

location /<prefix>/downloads/ {
    return 404;                     # ✅ 显式 404，而不是靠「不写配置」
}
```

```bash
# ✅ 部署后验证：本应 404
curl -i "https://example.com/<prefix>/downloads/<id>.zip"
# 期望：HTTP/1.1 404 Not Found

# ✅ 健康信号：计数查询端点随下载一起增长
curl -s "https://example.com/<prefix>/api/downloads/<id>" | jq .count
# 若此值不再增长而下载流量仍在 → 存在旁路
```

```python
# ✅ 补一条会红的契约用例：任何绕开端点的静态路径都不得存在
def test_private_download_dir_is_not_statically_served():
    resp = requests.get(f"https://example.com/<prefix>/downloads/<id>.zip")
    assert resp.status_code == 404, "private download dir is exposed via static location"
```

注意「显式 `return 404`」与「干脆不写配置」的区别：不写配置时，任何一次运维改动都可能
无意间补上一条静态映射，且没有任何检查会发现；显式 404 让「这条路径必须不可达」成为
部署配置里的一条可审查的声明。

## 对应失败模式

**(k) 契约断层（contract_gap）**：应用侧与部署侧对「压缩包只能通过哪条路径取得」的
契约不一致。应用侧假定「所有下载都经过计数端点」（并据此实现计数），部署侧则同时
提供了一条不经过计数端点的静态通路；两侧各自都工作正常，接口处的契约（下载必经计数）
在真实请求路径上不成立。归到 contract_gap 而不是 hallucination 或 tool_misuse，是因为
这里不存在用错工具或凭空发明 API 的问题 —— 代码和配置都忠实执行了各自的意图，失效
发生在两侧的**交界处**，且该交界处没有任何一方在检查。

**置信度说明**：给 0.80。源记录给出了可直接执行的部署后验证（`curl -i` 期望 404）
与一个可长期使用的健康信号（计数端点随下载增长），使这个模式既能一次验证、也能持续
监控，可操作性高。未给更高分有两个原因：一是源记录只记了 1 次发生；二是仅凭应用代码
无法保证该契约成立（静态映射属于部署配置），因此它的落地依赖部署侧的配合 —— 修复
动作有一部分在本条经验所属的代码边界之外。

## 改进方向

**短期**：
- 立即执行一次部署后验证：对所有「有计数 / 有权限控制」的下载路径逐一 `curl -i`，
  确认返回 404。凡返回 200 的，先移除静态 location。
- 把计数查询端点纳入例行健康检查：计数不增长而流量仍在，是本模式唯一可观测的信号。
- 在 Nginx 配置里为私有目录写明显式 `return 404`，让「此处不可达」成为一条可审查的
  声明，而不是依赖「没写配置」这个默认状态。

**长期**：
- 确立部署约定：API 私有目录不得出现在任何静态 location 的通配范围内；静态映射的对象
  只允许是公开的静态资源目录。
- 把「下载必经计数端点」写成一条端到端用例：既有正向证明（走端点会计数），也有反向
  证明（绕开端点不可达）。只有正向证明时，旁路不会被发现。
- 对计数类指标补一条交叉校验：计数增长与服务器出口流量（或文件访问计数）应同向变化。
  计数是业务侧自报的数字，需要与一个独立来源对账，否则它无法自证完整。
