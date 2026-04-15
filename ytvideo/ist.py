import subprocess

def check_speedtest_cli():
    result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    check_speedtest_cli()
