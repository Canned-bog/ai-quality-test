import subprocess
import sys
import os
import io
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_pytest():
    print("\n" + "=" * 50)
    print("运行 AI 测试 (pytest)...")
    print("=" * 50)
    result = subprocess.run([
        "pytest", "test_cases/",
        "-v",
        "--html=reports/ai_test_report.html",
        "--self-contained-html"
    ])
    return result.returncode == 0


def run_performance_test():
    print("\n" + "=" * 50)
    print("运行性能测试 (JMeter)...")
    print("=" * 50)

    # 检查 performance 目录是否存在
    if not os.path.exists("performance"):
        print("错误: performance 目录不存在")
        return False

    # 检查 JMeter 脚本是否存在
    if not os.path.exists("performance/ai_benchmark.jmx"):
        print("错误: performance/ai_benchmark.jmx 不存在")
        return False

    if sys.platform == "win32":
        # Windows: 直接调用 jmeter.bat，而不是 bat 脚本
        jmeter_home = r"C:\Users\Li\Downloads\apache-jmeter-5.6.3\apache-jmeter-5.6.3"
        jmeter_cmd = os.path.join(jmeter_home, "bin", "jmeter.bat")

        if not os.path.exists(jmeter_cmd):
            print(f"错误: 找不到 JMeter: {jmeter_cmd}")
            return False

        cmd = [
            jmeter_cmd,
            "-n",
            "-t", "performance/ai_benchmark.jmx",
            "-l", "reports/result.jtl",
            "-e", "-o", "reports/perf_report/"
        ]
    else:
        cmd = ["bash", "performance/run_perf_test.sh"]

    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=".", shell=True)
        return result.returncode == 0
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return False


def generate_summary(ai_ok, perf_ok):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = f"""# 测试汇总报告

生成时间: {timestamp}

| 测试类型 | 状态 |
|---------|------|
| AI测试 | {'✅ 通过' if ai_ok else '❌ 失败'} |
| 性能测试 | {'✅ 通过' if perf_ok else '❌ 失败'} |

## 报告链接
- [AI测试报告](reports/ai_test_report.html)
- [性能测试报告](reports/perf_report/index.html)
"""
    os.makedirs("ai_quality_test/reports", exist_ok=True)
    with open("ai_quality_test/reports/summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    print("\n汇总报告已生成: reports/summary.md")


def main():
    print("\nAI质量保障测试套件")

    ai_ok = run_pytest()

    print("\n是否运行性能测试？(y/n): ", end="")
    if input().strip().lower() == 'y':
        perf_ok = run_performance_test()
    else:
        print("跳过性能测试")
        perf_ok = True

    generate_summary(ai_ok, perf_ok)

    if ai_ok and perf_ok:
        print("\n✅ 所有测试完成")
    else:
        print("\n⚠️ 部分测试失败，请查看报告")


if __name__ == "__main__":
    main()