# from testObject import Test
from newTestObject import Test
t = Test("A01", "Reboot", "import time\nfor i in range(2):\n    print(\"start\")\n    time.sleep(2)\n    print(\"end\")")
a = t.run()
print(a['log'])

# with open("terminal.txt", "w") as f:
#     f.write("Hello")
