## About 



It's a straightforward TCP connect scanner — no raw sockets, no SYN scanning, nothing fancy. It just tries a full TCP handshake on each port one at a time using `connect_ex()`, which is the slowest but most beginner-friendly way to check if a port's open. It's single-threaded right now, so scanning a big range takes a while — that's one of the first things I want to improve.
