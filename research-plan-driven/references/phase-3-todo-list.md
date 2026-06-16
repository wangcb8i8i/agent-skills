# Todo List

> **Language note:** All output artifacts must be written in Chinese (see Critical Rules in SKILL.md).  
> References are in English for readability — do not treat them as a style template for artifacts.

## Purpose

Turn the approved plan into a concrete, reviewable execution checklist before any implementation begins.

## What to do

1. Start from the latest approved version of `docs/<task-slug>.plan.md`.
2. Append a `## Todo List` section to the same file.
3. Break the approved work into concrete, objectively completable steps.
4. Order the todo items by real execution order and dependencies.
5. Include explicit validation tasks.
6. After the todo list, append a `## Things to note` section.
7. Ask the user to review and explicitly approve the embedded todo list before implementation begins.
8. If the user comments on the todo list, follow the Review-Revise Repeat workflow until the embedded todo list is explicitly approved.

## Todo structure

The todo list must:

- fully cover the approved implementation work
- break work into concrete, objectively completable steps
- reflect real execution order and dependencies
- include explicit validation tasks 

Use checkbox-based markdown items inside a `## Todo List` section in `docs/<task-slug>.plan.md`. 

**Todo 示例**

```markdown
## Todo List

### 1. 入口点 <!-- ref§Core Logic -->
- [ ] 在 `src/api/notifications/routes.ts` 中新增路由注册
- [ ] 在 `src/api/notifications/controller.ts` 中新增请求处理器
### 2. 核心逻辑 <!-- ref § SectionB-->
- [ ] 在 `src/api/notifications/controller.ts` 中新增查询当前用户通知的服务方法
- [ ] 在仓库查询中加入已批准的分页和排序逻辑
- [ ] 按照现有 API 响应格式返回
### 3. 安全和边界情况 <!-- ref  § SectionC-->
- [ ] 使用现有认证流程拒绝未认证请求
- [ ] 按照现有惯例处理无效的分页输入
- [ ] 用户无通知时正确返回空列表
### 4. 验证 <!-- ref  § Approach C -->
- [ ] 为正常路径新增或更新 API 测试
- [ ] 为认证失败和用户隔离新增或更新测试
- [ ] 运行类型检查
- [ ] 运行 lint
- [ ] 运行相关测试套件
```

## 注意事项

待办清单后追加 `## 注意事项` 节。

该节需回答当前任务的以下问题：

* 本实现阶段需要关注哪些约束或规范？

使用以下结构：

```markdown
## 注意事项
<上述问题的整理答案>
```

## Constraints

- Do not write implementation code in this phase.
- Do not create the todo list until the plan is explicitly approved.
- Keep the todo list practical and easy to execute mechanically.

## Completion criteria

Leave this phase only when:

- the embedded todo list has been added into `docs/<task-slug>.plan.md`
- the `## Things to note` section has been added after the todo list
- no unresolved review comments left in artifact
- the embedded todo list has been explicitly approved
