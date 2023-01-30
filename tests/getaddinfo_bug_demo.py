import queue
import socket
import threading

"""
i don't think i can reproduce the bug:

jesssmith@Jesss-Air ~/p/ice (fix-socket-getaddrinfo-on-macos)> /Users/jesssmith/opt/anaconda3/envs/py310/bin/python /Users/jesssmith/projects/ice/ice/agents/demo.py                  (py310)
done
[(<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_DGRAM: 2>, 17, '', ('31.13.71.36', 80)), (<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('31.13.71.36', 80))]
[(<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_DGRAM: 2>, 17, '', ('142.250.65.206', 80)), (<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('142.250.65.206', 80))]
jesssmith@Jesss-Air ~/p/ice (fix-socket-getaddrinfo-on-macos)> uname -a                                                                                                               (py310)
Darwin Jesss-Air 22.1.0 Darwin Kernel Version 22.1.0: Sun Oct  9 20:14:30 PDT 2022; root:xnu-8792.41.9~2/RELEASE_ARM64_T8103 arm64
jesssmith@Jesss-Air ~/p/ice (fix-socket-getaddrinfo-on-macos)>                                                                                                                        (py310)
"""

q: queue.Queue = queue.Queue()  # thread-safe


# and maybe cache this
def f(site):
    x = socket.getaddrinfo(
        site,
        80,
    )
    q.put(x)


t1 = threading.Thread(target=f, args=("google.com",))
t2 = threading.Thread(target=f, args=("facebook.com",))
t1.start()
t2.start()
t1.join()
t2.join()
print("done")
while not q.empty():
    print(q.get_nowait())
