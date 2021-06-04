import os, signal, getpass

import psutil
from colorama import Fore, Back, Style


def handler(signum, frame):
    print()


def standardInput(inp):
    inp = inp.split()
    i = 0
    while i < len(inp):
        if inp[i][-1] == "\\":
            inp[i] = inp[i][:-1]
            inp[i] += " "
            if i < len(inp):
                inp[i] += inp[i + 1]
                inp = inp[:i + 1] + inp[i + 2:]
        else:
            i += 1
    i = 0
    while i < len(inp):
        if inp[i][0] == '"':
            inp[i] = inp[i][1:]
            if inp[i][-1] == '"':
                inp[i] = inp[i][:-1]

            j = i + 1
            while j < len(inp):

                if inp[j][-1] == '"':
                    inp[j] = inp[j][:-1]
                    inp[i] += " " + inp[j]
                    j += 1
                    break
                inp[i] += " " + inp[j]
                j += 1
            if j >= len(inp):
                inp = inp[:i + 1]
            else:
                inp = inp[i + 1] + inp[j:]
        i += 1

    return inp


# print(standardInput('mkdir "moh\ amma\ d"'))



signal.signal(signal.SIGTSTP, handler)
signal.signal(signal.SIGTERM, handler)
# signal.signal(signal.SIGCHLD, sigChildHandler)


main_process = os.getpid()
bglist = []
pid = -1
while (True):
    try:
        try:



            if pid != 0:
                inp = input(
                    Fore.LIGHTGREEN_EX + "\n" + getpass.getuser() + "@" + Fore.CYAN + os.getcwd() + "> " + Fore.WHITE)

            if not inp:
                continue
            if inp == "exit":
                os.kill(os.getpid(),signal.SIGTERM)
                print(Fore.YELLOW + "\nSee you :)")
                break
            inp = standardInput(inp)

            if inp[0] == "bglist":
                # updating bglist
                bgtemp = []
                for i in bglist:
                    p = psutil.Process(i)
                    if p.status() == "zombie":
                        continue
                    bgtemp.append(i)
                bglist = bgtemp

                out = ""
                for i in range(len(bglist)):
                    try:
                        p = psutil.Process(bglist[i])
                        if p.status() == "sleeping":
                            out += "(" + str(i + 1) + ") " + str(p.name()) + " " + "running" + "\n"
                        else:
                            out += "(" + str(i + 1) + ") " + str(p.name()+" ") + " " + str(p.status()) + "\n"
                    except:
                        continue
                out += "Total Background jobs: " + str(len(bglist))
                print(out)
                continue

            if inp[0] == "bgkill":
                index = int(inp[1])
                os.kill(bglist[index - 1], signal.SIGTERM)
                # removing pid of process that has been terminated
                pi = bglist.pop(index - 1)
                print("\n\n" + Fore.YELLOW + "The process with pid(" + str(pi) + ") has been terminated")
                if pid <= 0:
                    break
                continue

            if inp[0] == "bgstop":
                index = int(inp[1])
                os.kill(bglist[index - 1], signal.SIGSTOP)
                if pid <= 0:
                    break
                continue

            if inp[0] == "bgstart":
                index = int(inp[1])
                os.kill(bglist[index - 1], signal.SIGCONT)
                if pid <= 0:
                    break
                continue

            if inp[0] == "bg":
                inp = inp[1:]
                # create background process(child process)
                p_id = os.fork()
                if p_id != 0:
                    # in the main process or shell
                    # add last bg process_id to bglist
                    bglist.append(p_id)
                    continue
                else:
                    # in the child process or background process
                    # execute the command
                    os.execvp(inp[0], inp)
                    break
            else:
                # main process child for executing foreground command
                pid = os.fork()

            if inp[0] == "cd":
                try:
                    os.chdir(inp[1])
                except:
                    d = inp[1].split('/')
                    currdir = os.getcwd().split('/')
                    for i in d:
                        if i == "..":
                            currdir = currdir[:-1]
                        else:
                            currdir.append(i)
                    currdir = '/'.join(currdir)
                    os.chdir(currdir)

            # pid greater than 0 represents
            # the parent process
            if pid == 0:
                # in the foreground child process
                if inp[0] != "cd":
                    # pid equal to 0 represnts
                    # the created child process
                    os.execvp(inp[0], inp)
                break
            else:
                # in the main process ( shell )
                # if bglist is empty that mean main process can't do anything and should wait for foreground child
                if pid > 0:
                    os.waitpid(pid, 0)
                else:
                    if len(bglist) == 0:
                        break
                    continue

        except Exception as e:
            print(Fore.RED + "\nUnknown command : %s" % inp[0])
            print(e)
            if pid <= 0:
                break
            continue

    except KeyboardInterrupt:
        if pid == 0:
            break
        else:
            try:
                os.waitpid(pid, 0)
            except:
                continue


