# 校园在线考试系统 Docker 部署教程

本项目已经整理为一套 Docker Compose 部署方式。部署时不需要在主机环境安装 Java、Maven、Node、MySQL、Redis 或 Nginx；主机只需要安装 Docker 和 Docker Compose。

## 项目结构

```text
.
├── docker-compose.yml                  # 一键部署入口
├── online-exam-system-backend/          # Spring Boot 后端
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── sql/                            # MySQL 初始化脚本
└── online-exam-system-frontend/         # Vue 前端
    ├── Dockerfile
    └── nginx.conf
```

## 部署前准备

1. 确认 Docker 已安装并正在运行。
2. 确认下面端口没有被其他程序占用：

| 端口 | 服务 | 用途 |
| --- | --- | --- |
| `9528` | frontend | 前端访问入口 |
| `8080` | backend | 后端接口 |
| `9000` | minio | MinIO 文件服务 API |
| `9001` | minio | MinIO 管理控制台 |

MySQL 和 Redis 默认只在 Docker 网络内部暴露，不占用主机的 `3306` 和 `6379`。

## 一键启动

在项目根目录执行：

```bash
docker compose up -d --build
```

第一次启动会拉取基础镜像并构建前后端镜像，耗时会比较久。后续再次启动通常会快很多。

启动完成后查看容器状态：

```bash
docker compose ps
```

正常情况下应该能看到这些服务处于 `Up` 状态：

- `mysql`
- `redis`
- `minio`
- `backend`
- `frontend`

其中 `mysql`、`redis`、`minio` 会带有健康检查状态。

## 访问地址

| 服务 | 地址 |
| --- | --- |
| 前端系统 | http://localhost:9528 |
| 后端接口 | http://localhost:8080 |
| Swagger 接口文档 | http://localhost:8080/doc.html 或 http://localhost:8080/swagger-ui.html |
| MinIO 控制台 | http://localhost:9001 |

MinIO 控制台账号：

```text
用户名：admin
密码：Aa112211
```

## 默认登录账号

前端登录地址：

```text
http://localhost:9528
```

初始化数据中包含三个默认账号，密码均为：

```text
123456
```

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `123456` |
| 教师 | `teacher` | `123456` |
| 学生 | `student` | `123456` |

登录页需要输入图片验证码。验证码接口已经通过前端 `/api` 代理到后端。

## 部署后建议先做什么

1. 打开前端：`http://localhost:9528`。
2. 先用管理员账号 `admin / 123456` 登录。
3. 进入用户管理，确认管理员、教师、学生账号存在。
4. 进入班级管理，确认初始化班级数据存在。
5. 进入题库、试题、考试管理，确认初始化题目和考试数据存在。
6. 用教师账号 `teacher / 123456` 登录，检查教师端考试、题库、阅卷等功能。
7. 用学生账号 `student / 123456` 登录，检查学生端考试、刷题、错题本等功能。
8. 打开 MinIO 控制台，确认 `online-exam` bucket 已自动创建。
9. 尝试上传图片或生成证书，确认文件上传链路正常。

## 验证部署是否真的可用

可以在项目根目录执行下面命令。

查看服务状态：

```bash
docker compose ps
```

查看后端是否成功启动：

```bash
docker compose logs --tail=200 backend
```

日志中出现类似内容说明后端启动完成：

```text
Started ExamApplication
```

检查前端首页：

```bash
docker run --rm --network online-exam-system_default curlimages/curl:8.10.1 \
  -sS -o /dev/null -w "frontend=%{http_code}\n" http://frontend/
```

正常输出：

```text
frontend=200
```

检查后端接口文档：

```bash
docker run --rm --network online-exam-system_default curlimages/curl:8.10.1 \
  -sS -o /dev/null -w "swagger=%{http_code}\n" http://backend:8080/v2/api-docs
```

正常输出：

```text
swagger=200
```

检查前端到后端的 `/api` 代理和验证码：

```bash
docker run --rm --network online-exam-system_default curlimages/curl:8.10.1 \
  -sS -o /dev/null -w "captcha=%{http_code} %{content_type}\n" http://frontend/api/auths/captcha
```

正常输出类似：

```text
captcha=200 image/jpeg
```

检查数据库初始化：

```bash
docker compose exec -T mysql mysql -uroot -pAa112211 db_exam \
  -e 'SELECT COUNT(*) AS tables_count FROM information_schema.tables WHERE table_schema="db_exam"; SELECT COUNT(*) AS user_count FROM t_user; SELECT COUNT(*) AS exam_count FROM t_exam;'
```

正常情况下会看到数据库表、用户和考试数据已经存在。

## 常用维护命令

查看所有服务日志：

```bash
docker compose logs -f
```

只看后端日志：

```bash
docker compose logs -f backend
```

只看前端日志：

```bash
docker compose logs -f frontend
```

停止服务，但保留数据库、Redis、MinIO 数据卷：

```bash
docker compose down
```

重新启动已有服务：

```bash
docker compose up -d
```

重新构建并启动：

```bash
docker compose up -d --build
```

只重建后端：

```bash
docker compose build backend
docker compose up -d --no-deps --force-recreate backend
```

只重建前端：

```bash
docker compose build frontend
docker compose up -d --no-deps --force-recreate frontend
```

## 重置数据

如果想清空数据库、Redis、MinIO 数据并重新导入 SQL，可以执行：

```bash
docker compose down -v
docker compose up -d --build
```

注意：`down -v` 会删除 Docker 数据卷，数据库、缓存和上传文件都会被清空。只想重启服务时不要加 `-v`。

## 备份目录

后端容器内的备份目录挂载到：

```text
online-exam-system-backend/backups
```

如果使用系统里的数据库备份功能，备份文件会保留在这个目录下。

## 修改配置后如何生效

### 修改后端代码或配置

```bash
docker compose build backend
docker compose up -d --no-deps --force-recreate backend
```

### 修改前端代码或配置

```bash
docker compose build frontend
docker compose up -d --no-deps --force-recreate frontend
```

### 修改 `docker-compose.yml`

```bash
docker compose up -d --build
```

## 常见问题

### 端口被占用

如果 `9528`、`8080`、`9000` 或 `9001` 已经被占用，修改 `docker-compose.yml` 中对应的左侧端口。例如：

```yaml
ports:
  - "19528:80"
```

修改后访问地址变为 `http://localhost:19528`。

### 前端能打开但接口报错

先检查后端是否启动：

```bash
docker compose ps
docker compose logs --tail=200 backend
```

再检查前端代理：

```bash
docker run --rm --network online-exam-system_default curlimages/curl:8.10.1 \
  -sS -o /dev/null -w "%{http_code} %{content_type}\n" http://frontend/api/auths/captcha
```

如果返回 `200 image/jpeg`，说明前端到后端代理正常。

### 数据库没有初始化数据

只有首次创建 MySQL 数据卷时，`online-exam-system-backend/sql/` 下的初始化 SQL 才会自动执行。如果之前已经启动过 MySQL，修改 SQL 后不会自动重新导入。

需要重新导入时执行：

```bash
docker compose down -v
docker compose up -d --build
```

### 首次构建很慢

首次构建需要下载 Maven、Node、Java、Nginx 等基础镜像和依赖。等待完成即可。后续构建会复用 Docker 缓存。

## 当前容器化说明

当前 Compose 会自动启动：

- MySQL 8.0，并初始化 `db_exam` 数据库
- Redis 7
- MinIO，并创建 `online-exam` bucket
- Spring Boot 后端，使用 `dev` profile
- Nginx 前端，代理 `/api` 到后端容器

部署入口统一使用项目根目录的 `docker-compose.yml`。
