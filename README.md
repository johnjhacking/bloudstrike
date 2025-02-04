# bloudstrike - a (semi-retired) CS bypass loader
During several engagements, I dealt with CS on Linux servers. It was annoying because post-exploitation enumeration scripts would instantly be killed, and manual techniques were returning wack information. The script is insanely simple, and this isn't a profound or new method of execution by any means - but it helped me work around limited execution & detection. I didn't even expect ```memfd_create``` to work as opposed to other methods that are more stealthy. I can't speak for the specifics of detections, I just know my clients were telling me that it wasn't being detected by CS - and tbh that was good enough for me.

I have used this technique a lot over the course of the last year and a half, however, as of two months ago, this stopped working as an adequate bypass. In some cases, you can run it more than once and it still works - getting you to the point of being able to execute subsequent tools, but at that marker, you've already produced a lot of detection events.

I'm publishing this because it could give you an idea of some other techniques that might work. Since I don't have access to CS Linux, I can't test my latest techniques - but I've already started to use a different method.

# Technical Details
The script leverages fileless execution using ```memfd_create``` to load ELF binaries directly into memory. It does so by calling linux syscall ```319``` to allocate a memory-only file descriptor ```(FD)```. This prevents writing the malware on disk.

A target ELF binary, is downloaded from a remote URL using ```urllib.request```and writes the ELF binary contents into the in-memory FD ``/proc/self/fd/{fd}``. 

Lastly, a new process is spawned by calling ```os.fork``` and subsequently calling```os.execve()```to directly load the binary from memory into the new process and execute it.

# Limitations
You shouldn't have any issues running it as a regular user, since ```os.fork()``` will create a process that is an exact same copy of the parent loader, and inherit the same UID, GID, and privs. However, you might run into some prevention methodology. I don't want to get into the heuristics of all of the detection mechanisms in place that can stop this from working, as it might affect my other loaders. However, keep in mind that EDR is now the main limitation. In some cases there *could* be AppArmor/SELinux rules that prevent this from running, but ya know - there's ways around that.

# OS Support (Tested)
- Ubuntu 20.04, 22.04
- Debian 10, 11
- Kali Linux
# Probably Works On
- Most Linux distros with Kernel 3.17+, Alpine Linux (with ```glibc```), CentOS 7+ if you can enable ```memfd_create```
# Probably Wont Work On
- Older Linux Kernels <3.17
- Qubes OS or Hardened Alpine Linux builds
- Probably if you're running inside of Docker, LXC, or Kubernetes.

## Usage
The utilization of the script is very simple.
