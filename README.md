## 性能测试

本项目包含 JMeter 性能测试脚本，位于 `performance/` 目录。

### 本地运行

1. 安装 JMeter
2. 启动本地服务器：`python local_server.py`
3. 运行测试：`jmeter -n -t performance/ai_benchmark.jmx -l result.jtl -e -o reports/perf_report/`

### CI 说明

性能测试不在 CI 中自动运行（避免资源消耗），但脚本存在性会被检查。
